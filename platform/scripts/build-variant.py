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
        ignored |= {n for n in names if n == "variants" or n.startswith("maestro-")}
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
    "deliverables": {"dirs": ["deliverables"], "hc": ["deliverables/README.md"]},
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

    data["specialists_none"] = bool(re.search(r"(?m)^agents:\n  specialists: none", text))
    se_m = re.search(r"(?m)^  specialists_exclude:\s*\[([^\]]*)\]", text)
    data["specialists_exclude"] = [c.strip() for c in se_m.group(1).split(",") if c.strip()] if se_m else []
    ce_m = re.search(r"(?m)^commands_exclude:\s*\[([^\]]*)\]", text)
    data["commands_exclude"] = [c.strip() for c in ce_m.group(1).split(",") if c.strip()] if ce_m else []
    r_m = re.search(r"(?m)^roots:\s*\[([^\]]*)\]", text)
    data["roots"] = [c.strip() for c in r_m.group(1).split(",") if c.strip()] if r_m else []
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
            ctext = re.sub(r"(?m)^  scan_roots:\n(?:    .*\n)+", "  scan_roots: []\n", ctext)
            comp.write_text(ctext, encoding="utf-8")
            hc_text2 = hc_file.read_text(encoding="utf-8")
            hc_text2 = hc_text2.replace(
                '    required_roots = {"apps", "services", "packages", "infra", "tests"}',
                "    required_roots = registered_roots  # component roots are project-defined in this template",
            )
            hc_file.write_text(hc_text2, encoding="utf-8")
        instr_file.write_text(itxt, encoding="utf-8")
        print(f"   structure pruned: {', '.join(pruned_groups)}")


    # ---- standardize template contents: drop framework-maintenance machinery ----
    for rel in (".claude-plugin", ".vscode", "scripts/build-plugin.py",
                "CHANGELOG.md", "PLUGIN.md", "SETUP.md", "QUICKSTART.md", "GUIDELINES.md"):
        target = out / rel
        if target.is_dir():
            shutil.rmtree(target)
        elif target.is_file():
            target.unlink()
    hc_file = out / "scripts" / "architecture-health-check.py"
    patch(hc_file, [("    check_plugin_wrapper(findings)\n", "")])
    # entry docs: drop links/rows to removed files; plugin section now points upstream
    for doc in ("AGENTS.md", "CLAUDE.md"):
        dp = out / doc
        dt = dp.read_text(encoding="utf-8")
        dt = re.sub(r"(?m)^.*\((?:QUICKSTART|SETUP|PLUGIN|CHANGELOG|GUIDELINES)\.md\).*\n", "", dt)
        dt = re.sub(r"(?m)^.*\b(?:QUICKSTART|SETUP|GUIDELINES)\.md\b.*\n", "", dt)
        dp.write_text(dt, encoding="utf-8")
    patch(out / "CLAUDE.md", [(
        "The Claude tool layer is packaged as a Claude Code plugin at `.claude-plugin/`. Install it to use Maestro's agents, skills, commands, and hooks in any project. To adopt a full\nworkflow template, copy one of the root `maestro-*` folders (see [variants/README.md](variants/README.md)). Details: [PLUGIN.md](PLUGIN.md).",
        "This workspace reads `.claude/` natively (agents, skills, commands, hooks) — no plugin install needed here. Plugin packaging lives upstream in the maestro repo.")])
    # skills-lock: keep only shipped skills
    if keep is not None:
        lock = out / "skills-lock.json"
        if lock.is_file():
            import json
            data_lock = json.loads(lock.read_text(encoding="utf-8"))
            sk_map = data_lock.get("skills", {})
            data_lock["skills"] = {k: v for k, v in sk_map.items() if k in keep}
            lock.write_text(json.dumps(data_lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # agents: optionally drop the specialist advisors (e.g. lite)
    if m.get("specialists_none"):
        spec_dir = out / ".claude" / "agents" / "specialists"
        if spec_dir.is_dir():
            shutil.rmtree(spec_dir)
        spec_dir.mkdir(parents=True, exist_ok=True)
        (spec_dir / "README.md").write_text(
            "# Specialist Advisors\n\nNot included in this template (see the maestro platform for the full advisor set).\n",
            encoding="utf-8")
        patch(hc_file, [
            ("EXPECTED_SPECIALIST_COUNT = 19", "EXPECTED_SPECIALIST_COUNT = 0"),
            ('    "agents": 34,', '    "agents": 15,'),
        ])
        for mr in (out / ".maestro" / "config" / "model-routing.yaml",
                   out / ".maestro" / "engine" / "templates" / "model-routing.template.yaml"):
            mt = mr.read_text(encoding="utf-8")
            mt = re.sub(r"(?m)^  specialist_advisors:\n(?:    .*\n)+", "  specialist_advisors: {}\n", mt)
            mr.write_text(mt, encoding="utf-8")
        ct = (out / "CLAUDE.md").read_text(encoding="utf-8")
        ct = re.sub(r"(?ms)^## Specialist Advisors \(19 advisors\)\n.*?(?=^## )",
                    "## Specialist Advisors\n\nNot included in this template.\n\n", ct)
        (out / "CLAUDE.md").write_text(ct, encoding="utf-8")
        at = (out / "AGENTS.md").read_text(encoding="utf-8")
        at = re.sub(r"(?m)^- 19 specialist advisors.*\n", "", at)
        (out / "AGENTS.md").write_text(at, encoding="utf-8")


    # ---- per-variant agent/command pruning (each template keeps only what its purpose needs) ----
    hcf = out / "scripts" / "architecture-health-check.py"
    if m["specialists_exclude"]:
        removed_sp = []
        for sp in m["specialists_exclude"]:
            hits = list((out / ".claude" / "agents" / "specialists").rglob(f"{sp}.agent.md"))
            for h in hits:
                h.unlink(); removed_sp.append(sp)
        n_sp = len(list((out / ".claude" / "agents" / "specialists").rglob("*.agent.md")))
        n_agents = 12 + 3 + n_sp
        ht = hcf.read_text(encoding="utf-8")
        ht = ht.replace("EXPECTED_SPECIALIST_COUNT = 19", f"EXPECTED_SPECIALIST_COUNT = {n_sp}")
        ht = ht.replace('    "agents": 34,', f'    "agents": {n_agents},')
        hcf.write_text(ht, encoding="utf-8")
        for mr in (out / ".maestro" / "config" / "model-routing.yaml",
                   out / ".maestro" / "engine" / "templates" / "model-routing.template.yaml"):
            mt = mr.read_text(encoding="utf-8")
            for sp in m["specialists_exclude"]:
                mt = re.sub(rf"(?m)^    {re.escape(sp)}:\n(?:      .*\n)+", "", mt)
            mr.write_text(mt, encoding="utf-8")
        cat = out / ".claude" / "agents" / "specialists" / "README.md"
        if cat.is_file():
            ctext2 = cat.read_text(encoding="utf-8")
            for sp in m["specialists_exclude"]:
                ctext2 = re.sub(rf"(?m)^.*`{re.escape(sp)}`.*\n", "", ctext2)
            ctext2 = ctext2.replace("19 domain experts", f"{n_sp} domain experts")
            cat.write_text(ctext2, encoding="utf-8")
        for doc in ("CLAUDE.md", "AGENTS.md"):
            dp = out / doc
            dt = dp.read_text(encoding="utf-8")
            dt = dt.replace("19 specialist advisors", f"{n_sp} specialist advisors").replace("(19 advisors)", f"({n_sp} advisors)")
            dp.write_text(dt, encoding="utf-8")
        print(f"   specialists pruned: {', '.join(sorted(set(removed_sp)))} -> {n_sp} advisors, {n_agents} agents")
    if m["commands_exclude"]:
        for c in m["commands_exclude"]:
            f = out / ".claude" / "commands" / f"{c}.md"
            if f.is_file():
                f.unlink()
            pr = out / ".codex" / "prompts" / f"{c}.md"
            if pr.is_file():
                pr.unlink()
        n_cmd = len([x for x in (out / ".claude" / "commands").glob("*.md") if x.name != "README.md"])
        ht = hcf.read_text(encoding="utf-8")
        ht = re.sub(r'(?m)^    "commands": \d+,$', f'    "commands": {n_cmd},', ht)
        hcf.write_text(ht, encoding="utf-8")
        for doc in ("CLAUDE.md", "COMMAND.md", "AGENTS.md", ".claude/commands/README.md", ".codex/AGENTS.md"):
            dp = out / doc
            if not dp.is_file():
                continue
            dt = dp.read_text(encoding="utf-8")
            for c in m["commands_exclude"]:
                dt = re.sub(rf"(?m)^.*[|/ ]{re.escape(c)}\b.*\n", "", dt)
            dt = re.sub(r"(?m)^## Commands \(\d+ commands\)$", f"## Commands ({n_cmd} commands)", dt)
            dp.write_text(dt, encoding="utf-8")
        print(f"   commands pruned: {', '.join(m['commands_exclude'])} -> {n_cmd} commands")

    # generated per-template README
    (out / "README.md").write_text(
        f"# {m['display_name']}\n\n{m['purpose']}\n\n"
        "A self-contained Maestro workspace. Copy this folder anywhere, put your source code inside\n"
        "(`services/`, `apps/` — or register existing paths in `.maestro/registry/components.yaml`),\n"
        "then run `claude` (or `codex`) in this folder. Start with `/coord` (or `/ship` for autonomous\n"
        "build-to-done); `/overview` prints the full project briefing.\n\n"
        "Entry points: `CLAUDE.md` (Claude) - `AGENTS.md` (Codex) - `COMMAND.md` (commands)\n"
        "- `.maestro/INSTRUCTIONS.md` (workflow brain).\n\n"
        "Generated from the maestro platform - do not edit framework files by hand (see VARIANT.yaml).\n",
        encoding="utf-8")


    # ---- custom roots: each template declares its own top-level dirs (per-purpose, not one fixed shape) ----
    CODE_ROOT_KINDS = {
        "apps": ["application"], "services": ["service", "worker", "gateway"],
        "packages": ["package", "design-system", "contract-library"],
        "infra": ["infrastructure"], "tests": ["test-suite"],
    }
    ROOT_READMES = {
        "services": "# Services\n\nPut ALL service source code here (one folder per service). Register each in `.maestro/registry/components.yaml`; onboarding scans this root.\n",
        "docs": "# Docs & Info\n\nDrop ANY project material here: specs, notes, bug reports, error logs, screenshots, dumps.\nRun `/intake` (or `/onboard`, which triages first): every file is classified and indexed in\n`docs/INDEX.md` — nothing is moved or edited without your approval.\n\nWARNING: do NOT drop real secrets (.env, credentials, tokens, dumps with passwords). Intake flags\nthem and their contents are never quoted into any artifact (R-013) — but the safest secret is one\nthat never lands here.\n\n(`governance/methodologies/` is framework reference material — leave it.)\n",
        "apps": "# Applications\n\nUser-facing applications live here. Register each in `.maestro/registry/components.yaml`.\n",
        "tests": "# Tests\n\nCross-component integration and E2E suites.\n",
        "ai": "# AI Assets\n\nAI-specific assets for this product:\n\n- `prompts/`  prompt templates and system prompts (versioned)\n- `evals/`    eval datasets + graders (the EVAL GATE runs from here)\n- `datasets/` training/RAG source data (synthetic or licensed only, R-013)\n",
    }
    if m["roots"]:
        hc_file = out / "scripts" / "architecture-health-check.py"
        for r in m["roots"]:
            d = out / r
            d.mkdir(parents=True, exist_ok=True)
            (d / "README.md").write_text(ROOT_READMES.get(r, f"# {r}\n"), encoding="utf-8")
            if r == "ai":
                for sub in ("prompts", "evals", "datasets"):
                    (d / sub).mkdir(exist_ok=True)
                    (d / sub / ".gitkeep").write_text("", encoding="utf-8")
        code_roots = [r for r in m["roots"] if r in CODE_ROOT_KINDS]
        if code_roots:
            comp = out / ".maestro" / "registry" / "components.yaml"
            ctext = comp.read_text(encoding="utf-8")
            entries = "".join(f'    - path: "{r}"\n      kinds: {CODE_ROOT_KINDS[r]}\n'.replace("'", '"') for r in code_roots)
            ctext = ctext.replace("  scan_roots: []", "  scan_roots:\n" + entries)
            comp.write_text(ctext, encoding="utf-8")
            # health-check root README check follows the registry (registered_roots)
            hc2 = hc_file.read_text(encoding="utf-8")
            hc2 = hc2.replace('    required_roots = {"apps", "services", "packages", "infra", "tests"}',
                              "    required_roots = registered_roots  # roots are template-defined")
            hc_file.write_text(hc2, encoding="utf-8")
        # INSTRUCTIONS: state where code/info lives for THIS template
        instr2 = out / ".maestro" / "INSTRUCTIONS.md"
        it2 = instr2.read_text(encoding="utf-8")
        sentence = "Product code belongs in " + ", ".join(f"`{r}/`" for r in code_roots) + "." if code_roots else ""
        it2 = re.sub(r"(?m)^Product code (belongs|stays)[^\n]*$", sentence or "Product code location is registered in `.maestro/registry/components.yaml`.", it2)
        instr2.write_text(it2, encoding="utf-8")
        print(f"   roots created: {', '.join(m['roots'])}")

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


    # ---- resolved identity: concrete variant name, exact expected answer (fixes "who are you") ----
    ident_block = (
        "## Identity (MANDATORY — answer exactly when asked who you are)\n\n"
        f"You are **{m['display_name']}** — not a generic AI assistant. When the user asks "
        "\"bạn là ai\" / \"who are you\" / \"what are you\", answer in the user's language with ALL of:\n\n"
        "```text\n"
        f"1. Tôi là {m['display_name']} — hệ thống điều phối đa-agent (analysis -> build -> QC).\n"
        "2. Dự án đang vận hành: <product.display_name trong .maestro/project.yaml; nếu null: 'chưa cấu hình'>.\n"
        f"3. Methodology: {m['methodology_default']} | trạng thái: <current_state trong .maestro/runtime/workflow-state.yaml>.\n"
        "```\n\n"
        "Keep this identity the whole session, in every adapter (Claude, Codex). Never introduce yourself\n"
        "as Claude/Codex/a generic assistant while operating this workspace.\n"
    )
    ct = claude.read_text(encoding="utf-8")
    ct = re.sub(r"(?ms)^## Identity\n.*?(?=^---|^## )", ident_block + "\n", ct, count=1)
    claude.write_text(ct, encoding="utf-8")
    for adoc in (out / "AGENTS.md", out / ".codex" / "AGENTS.md"):
        if adoc.is_file():
            at = adoc.read_text(encoding="utf-8")
            at = re.sub(r"(?ms)^## Identity\n.*?(?=^## )", "", at)  # drop old generic block if present
            lines2 = at.splitlines(keepends=True)
            for i2, l2 in enumerate(lines2):
                if l2.startswith("# "):
                    lines2.insert(i2 + 1, "\n" + ident_block)
                    break
            adoc.write_text("".join(lines2), encoding="utf-8")

    # counts in docs + health-check
    tech = n_skills - 12
    for doc in ("CLAUDE.md", "AGENTS.md", "README.md", "GUIDELINES.md"):
        p = out / doc
        if p.is_file():
            patch(p, [("233 skills", f"{n_skills} skills"), ("221 technical", f"{tech} technical"),
                      ("all 233 skills", f"all {n_skills} skills")])
    patch(out / "scripts" / "architecture-health-check.py", [
        (r'(?m)^    "skills": \d+,$', f'    "skills": {n_skills},'),
    ], regex=True)

    # regenerate derived artifacts inside the bundle
    run([sys.executable, "scripts/build-skill-catalog.py"], out)   # taxonomy + catalog doc
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
