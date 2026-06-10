#!/usr/bin/env python3
"""Build a standalone Maestro variant bundle from a variants/<name>.yaml manifest.

Each template is a self-contained framework folder under maestro/templates/<name>/ (own CLAUDE.md, .claude/, .maestro/) with a
purpose-specific behavior profile, default methodology, and skill subset. Bundles are GENERATED —
never edit them by hand; change the platform or the manifest and rebuild.

Usage:
  python3 scripts/build-variant.py sdlc            # build one variant
  python3 scripts/build-variant.py --all           # build every variants/*.yaml
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ROOT / "variants"

def COPY_IGNORE(dir_: str, names: list[str]) -> set[str]:
    """copytree ignore: junk everywhere; platform-only items ONLY at the repo root (so e.g.
    .maestro/engine/templates is never confused with the top-level templates/ output dir)."""
    ignored = {n for n in names if n in {".git", "__pycache__", ".DS_Store"} or n.endswith(".pyc")}
    d = Path(dir_)
    if d == ROOT:
        ignored |= {n for n in names if n in {"templates", "variants"}}
    if d == ROOT / "scripts":
        ignored |= {n for n in names if n == "build-variant.py"}
    return ignored

# Structure groups: folders a template carries only when its manifest selects them. Right-sizes each
# template so e.g. lite/brownfield do not ship enterprise scaffolding (R-018 single source: the
# platform keeps everything; templates prune).
STRUCTURE_GROUPS: dict[str, dict] = {
    "component-roots": {
        "dirs": ["apps", "services", "packages", "infra", "tests"],
        "hc": ["apps/README.md", "services/README.md", "packages/README.md", "infra/README.md", "tests/README.md"],
    },
    "inputs": {"dirs": ["inputs"], "hc": []},
    "docs-delivery": {"dirs": ["docs/product", "docs/requirements", "docs/quality", "docs/delivery", "docs/architecture"], "hc": []},
    "docs-experience": {"dirs": ["docs/experience"], "hc": []},
    "docs-operations": {"dirs": ["docs/operations"], "hc": []},
    "docs-enterprise": {"dirs": ["docs/governance/enterprise-agent-governance", "docs/governance/agentic-enterprise"], "hc": []},
    "design-decision": {"dirs": [".maestro/design", ".maestro/decision"], "hc": [".maestro/design/index.yaml", ".maestro/decision/index.yaml"]},
    "observability": {"dirs": [".maestro/observability"], "hc": [".maestro/observability/index.yaml"], "instr": "observability/index.yaml"},
    "governance": {"dirs": [".maestro/governance"], "hc": [".maestro/governance/index.yaml"], "instr": "governance/index.yaml"},
    "work-program": {"dirs": [".maestro/work/initiatives", ".maestro/work/epics"], "hc": []},
}


def parse_manifest(path: Path) -> dict:
    """Minimal parser for the variant manifest format (scalars, inline lists, profile: | block)."""
    text = path.read_text(encoding="utf-8")
    data: dict = {"skills": {"categories": "all", "include": [], "exclude": []}}

    def scalar(key: str) -> str | None:
        m = re.search(rf"(?m)^{key}:\s*\"?([^\"\n]+)\"?\s*$", text)
        return m.group(1).strip() if m else None

    for key in ("name", "display_name", "output", "purpose", "methodology_default"):
        val = scalar(key)
        if val:
            data[key] = val

    skills_m = re.search(r"(?ms)^skills:\n(.*?)(?=^\S|\Z)", text)
    if skills_m:
        body = skills_m.group(1)
        cat_m = re.search(r"categories:\s*(\[[^\]]*\]|all)", body)
        if cat_m:
            raw = cat_m.group(1)
            data["skills"]["categories"] = (
                "all" if raw == "all" else [c.strip() for c in raw.strip("[]").split(",") if c.strip()]
            )
        for lk in ("include", "exclude"):
            lm = re.search(rf"{lk}:\s*\[([^\]]*)\]", body)
            if lm:
                data["skills"][lk] = [c.strip() for c in lm.group(1).split(",") if c.strip()]

    st_m = re.search(r"structure:\s*(\[[^\]]*\]|full)", text)
    if st_m:
        raw = st_m.group(1)
        data["structure"] = "full" if raw == "full" else [c.strip() for c in raw.strip("[]").split(",") if c.strip()]
    else:
        data["structure"] = "full"

    prof_m = re.search(r"(?ms)^profile:\s*\|\n(.*)\Z", text)
    if prof_m:
        lines = prof_m.group(1).splitlines()
        data["profile"] = "\n".join(l[2:] if l.startswith("  ") else l for l in lines).strip() + "\n"
    return data


def taxonomy_categories() -> dict[str, list[str]]:
    """category -> [skill names] from the generated skill taxonomy."""
    text = (ROOT / ".maestro" / "registry" / "skill-taxonomy.yaml").read_text(encoding="utf-8")
    cats: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"^  ([a-z0-9-]+):\s*$", line)
        if m:
            current = m.group(1)
            cats[current] = []
            continue
        m = re.match(r'^      - "([^"]+)"\s*$', line)
        if m and current:
            cats[current].append(m.group(1))
    return cats


def resolve_keep_skills(manifest: dict) -> set[str] | None:
    """None = keep everything."""
    sk = manifest["skills"]
    if sk["categories"] == "all" and not sk["exclude"]:
        return None
    cats = taxonomy_categories()
    keep: set[str] = set()
    selected = cats.keys() if sk["categories"] == "all" else sk["categories"]
    for cat in selected:
        if cat not in cats:
            sys.exit(f"ERROR: manifest category '{cat}' not in skill-taxonomy.yaml ({sorted(cats)})")
        keep.update(cats[cat])
    keep.update(sk["include"])
    keep.difference_update(sk["exclude"])
    keep.update(c for cat in cats.values() for c in cat if c.startswith("skill-"))  # engine skills always
    return keep


def prune_skill_registry(bundle: Path, keep: set[str]) -> None:
    """Drop registry catalog entries whose skill folder was pruned."""
    reg = bundle / ".maestro" / "registry" / "skills.yaml"
    lines = reg.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []
    in_catalog = False
    skipping = False
    for line in lines:
        if re.match(r"^catalog:\s*$", line):
            in_catalog = True
            out.append(line)
            continue
        if in_catalog and re.match(r"^\S", line):       # next top-level key ends the catalog
            in_catalog = False
            skipping = False
        if in_catalog:
            m = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
            if m:
                skipping = m.group(1) not in keep
            if skipping:
                continue
        out.append(line)
    reg.write_text("".join(out), encoding="utf-8")


def patch(path: Path, subs: list[tuple[str, str]], regex: bool = False) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in subs:
        text = re.sub(old, new, text) if regex else text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def run(cmd: list[str], cwd: Path) -> None:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(f"ERROR running {' '.join(cmd)} in {cwd}:\n{res.stdout}\n{res.stderr}")


def build(manifest_path: Path) -> None:
    m = parse_manifest(manifest_path)
    out = (ROOT / m["output"]).resolve()
    print(f"== {m['name']} -> {out}")

    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(ROOT, out, ignore=COPY_IGNORE, symlinks=False)
    # generated codex skill copies are rebuilt below
    for p in (out / ".codex" / "marketplace" / "plugins").glob("*/skills"):
        shutil.rmtree(p)

    keep = resolve_keep_skills(m)
    if keep is not None:
        skills_dir = out / ".claude" / "skills"
        removed = 0
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir() and d.name not in keep:
                shutil.rmtree(d)
                removed += 1
        prune_skill_registry(out, keep)
        print(f"   skills pruned: {removed} removed, {len(list(skills_dir.iterdir()))} kept")

    n_skills = len(list((out / ".claude" / "skills").rglob("SKILL.md")))

    # structure pruning: drop folder groups the manifest does not select (right-size per purpose)
    pruned_groups: list[str] = []
    if m["structure"] != "full":
        selected = set(m["structure"])
        unknown = selected - set(STRUCTURE_GROUPS)
        if unknown:
            sys.exit(f"ERROR: unknown structure group(s) {sorted(unknown)} (have: {sorted(STRUCTURE_GROUPS)})")
        hc_drop: list[str] = []
        instr_drop: list[str] = []
        for group, spec in STRUCTURE_GROUPS.items():
            if group in selected:
                continue
            pruned_groups.append(group)
            for d in spec["dirs"]:
                target = out / d
                if target.is_dir():
                    shutil.rmtree(target)
            hc_drop.extend(spec.get("hc", []))
            if spec.get("instr"):
                instr_drop.append(spec["instr"])
        # bundle health-check must not demand pruned paths
        hc_file = out / "scripts" / "architecture-health-check.py"
        hc_text = hc_file.read_text(encoding="utf-8")
        for path_str in hc_drop:
            hc_text = hc_text.replace(f'    "{path_str}",\n', "")
        hc_file.write_text(hc_text, encoding="utf-8")
        # INSTRUCTIONS read-order: drop pruned index lines, renumber the ordered list
        instr_file = out / ".maestro" / "INSTRUCTIONS.md"
        ilines = instr_file.read_text(encoding="utf-8").splitlines(keepends=True)
        kept = [l for l in ilines if not any(d in l for d in instr_drop)]
        n = 0
        for i, l in enumerate(kept):
            mm = re.match(r"^(\d+)\. ", l)
            if mm:
                n += 1
                kept[i] = re.sub(r"^\d+\. ", f"{n}. ", l)
        itxt = "".join(kept)
        if "component-roots" not in selected:
            itxt = itxt.replace(
                "Product code belongs in `apps/`, `services/`, `packages/`, `infra/`, and `tests/`.",
                "Product code stays where the project keeps it; register component paths in `.maestro/registry/components.yaml`.",
            )
            # roots are project-defined: empty scan_roots + registry-driven root check
            comp = out / ".maestro" / "registry" / "components.yaml"
            ctext = comp.read_text(encoding="utf-8")
            ctext = re.sub(r"(?ms)^(\s*)scan_roots:\n(?:\s+- [^\n]*\n)+", r"\1scan_roots: []\n", ctext)
            comp.write_text(ctext, encoding="utf-8")
            hc_text2 = hc_file.read_text(encoding="utf-8")
            hc_text2 = hc_text2.replace(
                '    required_roots = {"apps", "services", "packages", "infra", "tests"}',
                "    required_roots = registered_roots  # component roots are project-defined in this template",
            )
            hc_file.write_text(hc_text2, encoding="utf-8")
        instr_file.write_text(itxt, encoding="utf-8")
        print(f"   structure pruned: {', '.join(pruned_groups)}")

    # identity + defaults
    patch(out / ".maestro" / "project.yaml", [
        (r'(?m)^  id: "maestro"$', f'  id: "{m["name"]}"'),
        (r'(?m)^  name: "maestro"$', f'  name: "{m["name"]}"'),
    ], regex=True)
    patch(out / ".maestro" / "methodology.yaml", [
        (r'(?m)^methodology: "[^"]+"$', f'methodology: "{m["methodology_default"]}"'),
    ], regex=True)

    # CLAUDE.md: variant banner + profile right after the language-policy line
    claude = out / "CLAUDE.md"
    text = claude.read_text(encoding="utf-8")
    banner = (
        f"\n> **Variant: {m['display_name']}** — {m['purpose']}\n"
        f"> Generated bundle — do not edit by hand; rebuild from the maestro platform (variants/{manifest_path.stem}.yaml).\n"
        f"\n{m.get('profile', '')}"
    )
    lines = text.splitlines(keepends=True)
    for i, l in enumerate(lines):
        if l.startswith("> Language policy"):
            lines.insert(i + 1, banner)
            break
    claude.write_text("".join(lines), encoding="utf-8")

    # .maestro/INSTRUCTIONS.md: same banner + profile, so a project that copies this template
    # inherits the variant behavior + identity.
    instr = out / ".maestro" / "INSTRUCTIONS.md"
    itext = instr.read_text(encoding="utf-8")
    marker = "Read in this order:"
    if marker in itext:
        itext = itext.replace(marker, banner.lstrip("\n") + "\n" + marker, 1)
        instr.write_text(itext, encoding="utf-8")

    # counts in docs + health-check
    tech = n_skills - 12
    for doc in ("CLAUDE.md", "AGENTS.md", "README.md", "GUIDELINES.md"):
        p = out / doc
        if p.is_file():
            patch(p, [("231 skills", f"{n_skills} skills"), ("219 technical", f"{tech} technical"),
                      ("all 231 skills", f"all {n_skills} skills")])
    patch(out / "scripts" / "architecture-health-check.py", [
        ('    "skills": 231,', f'    "skills": {n_skills},'),
    ])

    # regenerate derived artifacts inside the bundle
    run([sys.executable, "scripts/build-skill-catalog.py"], out)   # taxonomy + catalog doc
    run([sys.executable, "scripts/build-plugin.py", "--force"], out)   # plugin wrapper jsons (counts)
    run([sys.executable, "scripts/build-codex-plugin.py"], out)    # codex marketplace (skills copy)
    run([sys.executable, "scripts/build-codex-prompts.py"], out)   # codex prompts

    (out / "VARIANT.yaml").write_text(
        f"name: {m['name']}\ndisplay_name: \"{m['display_name']}\"\n"
        f"purpose: \"{m['purpose']}\"\nmethodology_default: {m['methodology_default']}\n"
        f"skills: {n_skills}\nstructure: {m['structure'] if m['structure']=='full' else sorted(set(m['structure']))}\npruned_groups: {sorted(pruned_groups)}\ngenerated_at: \"{datetime.now(timezone.utc).isoformat()}\"\n"
        f"source: maestro platform (variants/{manifest_path.stem}.yaml)\n"
        f"note: GENERATED bundle - do not edit by hand; rebuild with scripts/build-variant.py\n",
        encoding="utf-8",
    )

    res = subprocess.run([sys.executable, "scripts/architecture-health-check.py", "--strict"],
                         cwd=out, capture_output=True, text=True)
    tail = "\n".join(res.stdout.strip().splitlines()[-6:])
    print(f"   health-check:\n{tail}\n")
    if res.returncode != 0:
        print(f"   WARNING: health-check failed for {m['name']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("variant", nargs="?", help="variant name (variants/<name>.yaml)")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    targets = sorted(VARIANTS.glob("*.yaml")) if args.all else [VARIANTS / f"{args.variant}.yaml"]
    if not args.all and (not args.variant or not targets[0].is_file()):
        sys.exit(f"Usage: build-variant.py <name>|--all  (have: {[p.stem for p in VARIANTS.glob('*.yaml')]})")
    for t in targets:
        build(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
