#!/usr/bin/env python3
"""Scaffold the maestro product-development control plane.

The Claude plugin supplies agents, skills, commands, and hooks. This script installs the tool-neutral
`.maestro/` control plane, official documentation roots, component roots, and the root instruction entrypoint.

Usage:
  python3 maestro-init.py --from <framework-root> [--to <project-dir>]
      [--project-key <key>] [--project-name <name>] [--methodology <name>]
      [--force] [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


CLAUDE_BLOCK = """# >>> maestro (auto) >>>
@.maestro/INSTRUCTIONS.md
# <<< maestro (auto) <<<"""

AGENTS_BLOCK = """# >>> maestro (auto) >>>
Read and follow `.maestro/INSTRUCTIONS.md` before starting work.
# <<< maestro (auto) <<<"""

GITIGNORE_BLOCK = """# >>> maestro local runtime >>>
.maestro/runtime/*
!.maestro/runtime/README.md
.maestro/memory/sessions/*
!.maestro/memory/sessions/README.md
# <<< maestro local runtime <<<"""

SYNC_MANIFEST = ".maestro/runtime/cache/sync.json"
FRAMEWORK_FILES = {".maestro/INSTRUCTIONS.md", ".maestro/runtime/README.md"}

TEMPLATE_OUTPUTS = {
    ".maestro/runtime/workflow-state.yaml": "workflow-state.template.yaml",
    ".maestro/runtime/active-context.yaml": "active-context.template.yaml",
    ".maestro/config/model-routing.yaml": "model-routing.template.yaml",
    ".maestro/config/response-ui.yaml": "response-ui.template.yaml",
    ".maestro/runtime/agent-activity.yaml": "agent-activity.template.yaml",
    ".maestro/knowledge/project.yaml": "project.template.yaml",
    ".maestro/registry/agents.yaml": "agents.template.yaml",
    ".maestro/work/index.yaml": "work-index.template.yaml",
    ".maestro/design/index.yaml": "design-index.template.yaml",
    ".maestro/decision/index.yaml": "decision-index.template.yaml",
}

COPY_FILES = [
    ".maestro/INSTRUCTIONS.md",
    ".maestro/manifest.yaml",
    ".maestro/observability/README.md",
    ".maestro/observability/index.yaml",
    ".maestro/observability/traces/README.md",
    ".maestro/observability/evals/README.md",
    ".maestro/observability/reports/README.md",
    ".maestro/observability/audit/README.md",
    ".maestro/governance/README.md",
    ".maestro/governance/index.yaml",
    ".maestro/governance/agents/README.md",
    ".maestro/governance/approvals/README.md",
    ".maestro/governance/risk/README.md",
    ".maestro/registry/components.yaml",
    ".maestro/registry/skills.yaml",
    ".maestro/registry/skill-taxonomy.yaml",
    ".maestro/registry/inputs.yaml",
    ".maestro/registry/artifacts.yaml",
    ".maestro/knowledge/index.yaml",
    ".maestro/knowledge/test-policy.yaml",
    ".maestro/knowledge/architecture.md",
    ".maestro/knowledge/conventions.md",
    ".maestro/knowledge/environments.md",
    ".maestro/knowledge/summary.md",
    ".maestro/memory/tasks/index.yaml",
    ".maestro/memory/sessions/README.md",
    ".maestro/history/timeline.md",
    ".maestro/runtime/README.md",
    ".maestro/work/README.md",
    ".maestro/work/runs/README.md",
    ".maestro/work/runs/index.yaml",
    ".maestro/work/initiatives/README.md",
    ".maestro/work/epics/README.md",
    "docs/README.md",
    "docs/product/README.md",
    "docs/requirements/README.md",
    "docs/experience/README.md",
    "docs/architecture/README.md",
    "docs/quality/README.md",
    "docs/delivery/README.md",
    "docs/operations/README.md",
    "docs/governance/README.md",
    "docs/governance/agentic-enterprise/README.md",
    "docs/governance/enterprise-agent-governance/README.md",
    "docs/governance/methodologies/README.md",
    "docs/governance/methodologies/adaptive.md",
    "docs/governance/methodologies/adlc.md",
    "docs/governance/methodologies/agentic-enterprise.md",
    "docs/governance/methodologies/ai-native.md",
    "docs/governance/methodologies/risk-based-routing.md",
    "docs/governance/methodologies/spec-driven-development.md",
    "docs/governance/methodologies/eval-driven-ai.md",
    "docs/governance/methodologies/enterprise-agent-governance.md",
    "docs/governance/methodologies/industry-alignment.md",
    "docs/governance/methodologies/selection-matrix.md",
    "apps/README.md",
    "services/README.md",
    "packages/README.md",
    "infra/README.md",
    "tests/README.md",
]

COPY_TREES = [
    ".maestro/engine",
    ".maestro/memory/project",
]

DIRECTORIES = [
    ".maestro/knowledge/components",
    ".maestro/work/initiatives",
    ".maestro/work/epics",
    ".maestro/work/tasks",
    ".maestro/work/bugs/blockers",
    ".maestro/work/bugs/non-blockers",
    ".maestro/memory/tasks",
    ".maestro/memory/sessions",
    ".maestro/history/snapshots",
    ".maestro/runtime/locks",
    ".maestro/runtime/cache",
    ".maestro/runtime/reports",
    "docs/product/prds",
    "docs/requirements/features",
    "docs/requirements/user-stories",
    "docs/requirements/use-cases",
    "docs/requirements/non-functional",
    "docs/experience/user-journeys",
    "docs/experience/user-flows",
    "docs/experience/wireframes",
    "docs/experience/ui-specifications",
    "docs/architecture/high-level-design",
    "docs/architecture/low-level-design",
    "docs/architecture/decisions",
    "docs/governance/enterprise-agent-governance/policies",
    "docs/governance/enterprise-agent-governance/missions",
    "docs/governance/enterprise-agent-governance/behavior-contracts",
    "docs/governance/enterprise-agent-governance/autonomy-policies",
    "docs/governance/enterprise-agent-governance/agent-definitions",
    "docs/governance/enterprise-agent-governance/eval-suites",
    "docs/governance/enterprise-agent-governance/audit-logs",
    "docs/governance/enterprise-agent-governance/interaction-protocols",
    "docs/operations/runbooks",
]


def configure_project(text: str, key: str | None, name: str | None) -> str:
    if not key and not name:
        return text
    product_key = key or re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")
    display_name = name or product_key
    text = re.sub(r"(?m)^  id: null$", f'  id: "{product_key}"', text, count=1)
    text = re.sub(r"(?m)^  key: null$", f'  key: "{product_key}"', text, count=1)
    text = re.sub(r"(?m)^  display_name: null$", f'  display_name: "{display_name}"', text, count=1)
    text = re.sub(r'(?m)^  status: "not-configured"$', '  status: "configured"', text, count=1)
    text = re.sub(r"(?m)^  component_namespace: null$", f'  component_namespace: "{product_key}"', text, count=1)
    return text


METHODOLOGY_ALIASES = {
    "adaptive": "risk-based-routing",
    "risk-based-routing": "risk-based-routing",
    "adlc": "spec-driven-development",
    "spec-driven-development": "spec-driven-development",
    "ai-native": "eval-driven-ai",
    "eval-driven-ai": "eval-driven-ai",
    "agentic-enterprise": "enterprise-agent-governance",
    "ae": "enterprise-agent-governance",
    "enterprise-agent-governance": "enterprise-agent-governance",
}


def configure_methodology(text: str, methodology: str) -> str:
    canonical = METHODOLOGY_ALIASES[methodology]
    return re.sub(r'(?m)^methodology: "[^"]+"$', f'methodology: "{canonical}"', text, count=1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", required=True, help="framework root (plugin install dir or repo)")
    ap.add_argument("--to", dest="dst", default=".", help="target workspace dir (default: cwd)")
    ap.add_argument("--project-key", help="stable product namespace, for example nova")
    ap.add_argument("--project-name", help="human-readable product name")
    ap.add_argument(
        "--methodology",
        default="risk-based-routing",
        choices=sorted(METHODOLOGY_ALIASES),
    )
    ap.add_argument("--force", action="store_true", help="overwrite existing framework-owned files")
    ap.add_argument("--dry-run", action="store_true", help="print actions, write nothing")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--attach", action="store_true", help="only attach entrypoint and local-runtime ignore blocks")
    mode.add_argument("--sync", action="store_true", help="refresh framework-owned .maestro/engine and entrypoint files")
    args = ap.parse_args()
    args.methodology = METHODOLOGY_ALIASES[args.methodology]

    src = Path(args.src).resolve()
    dst = Path(args.dst).resolve()
    if not (src / ".maestro" / "engine" / "workflow.md").is_file():
        print(f"ERROR: --from {src} is not an maestro root (missing .maestro/engine/workflow.md)")
        return 1
    if src == dst and not (args.attach or args.sync):
        print("ERROR: refusing to initialize a framework into itself; use --attach or --sync")
        return 1
    if src == dst and args.sync:
        args.sync = False
        args.attach = True
    if args.project_key and not re.fullmatch(r"[a-z][a-z0-9-]*", args.project_key):
        print("ERROR: --project-key must be kebab-case and start with a letter")
        return 1

    created: list[str] = []
    skipped: list[str] = []
    manual_conflicts: list[str] = []
    sync_manifest_path = dst / SYNC_MANIFEST
    try:
        sync_manifest = json.loads(sync_manifest_path.read_text(encoding="utf-8"))
    except Exception:
        sync_manifest = {}

    def digest_bytes(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def record_sync_hash(rel: str, content: bytes) -> None:
        sync_manifest[rel] = {"sha256": digest_bytes(content), "source": "maestro"}

    def write(rel: str, content: str, *, framework_owned: bool = False) -> None:
        target = dst / rel
        encoded = content.encode("utf-8")
        if args.sync and framework_owned and target.is_file() and not args.force:
            disk_hash = digest_bytes(target.read_bytes())
            source_hash = digest_bytes(encoded)
            recorded_hash = sync_manifest.get(rel, {}).get("sha256")
            if disk_hash != source_hash and disk_hash != recorded_hash:
                manual_conflicts.append(rel)
                skipped.append(rel + " (manual edit)")
                return
        if target.exists() and not (args.force or (args.sync and framework_owned)):
            skipped.append(rel)
            return
        created.append(rel)
        if args.dry_run:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        if framework_owned:
            record_sync_hash(rel, encoded)

    def copy_file(rel: str) -> None:
        source = src / rel
        if source.is_file():
            write(
                rel,
                source.read_text(encoding="utf-8"),
                framework_owned=rel in FRAMEWORK_FILES,
            )

    def copy_tree(rel: str) -> None:
        source, target = src / rel, dst / rel
        if args.sync:
            changed = False
            for source_file in sorted(p for p in source.rglob("*") if p.is_file()):
                relative_file = source_file.relative_to(src).as_posix()
                target_file = dst / relative_file
                source_bytes = source_file.read_bytes()
                source_hash = digest_bytes(source_bytes)
                if target_file.is_file():
                    disk_hash = digest_bytes(target_file.read_bytes())
                    if disk_hash == source_hash:
                        record_sync_hash(relative_file, source_bytes)
                        continue
                    recorded_hash = sync_manifest.get(relative_file, {}).get("sha256")
                    if not args.force and disk_hash != recorded_hash:
                        manual_conflicts.append(relative_file)
                        continue
                changed = True
                if not args.dry_run:
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    target_file.write_bytes(source_bytes)
                    record_sync_hash(relative_file, source_bytes)
            if changed:
                created.append(rel + "/")
            else:
                skipped.append(rel + "/ (current or guarded)")
            return
        overwrite = args.force or args.sync
        if target.exists() and not overwrite:
            skipped.append(rel + "/")
            return
        created.append(rel + "/")
        if args.dry_run:
            return
        shutil.copytree(source, target, dirs_exist_ok=overwrite)
        if rel == ".maestro/engine":
            for source_file in sorted(p for p in source.rglob("*") if p.is_file()):
                record_sync_hash(
                    source_file.relative_to(src).as_posix(),
                    source_file.read_bytes(),
                )

    def upsert_block(rel: str, block: str, marker: str) -> None:
        target = dst / rel
        original = target.read_text(encoding="utf-8") if target.is_file() else ""
        pattern = re.compile(
            rf"(?ms)^# >>> {re.escape(marker)}.*?^# <<< {re.escape(marker)}.*?<<<\s*"
        )
        if pattern.search(original):
            updated = pattern.sub(block + "\n", original).rstrip() + "\n"
        else:
            updated = (original.rstrip() + "\n\n" if original.strip() else "") + block + "\n"
        if updated == original:
            skipped.append(rel + " (managed block current)")
            return
        created.append(rel + " (managed block)")
        if args.dry_run:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(updated, encoding="utf-8")

    if args.attach:
        if not (dst / ".maestro" / "INSTRUCTIONS.md").is_file():
            print("ERROR: --attach requires an existing .maestro/INSTRUCTIONS.md in the target workspace")
            return 1
    else:
        trees = [".maestro/engine"] if args.sync else COPY_TREES
        for rel in trees:
            copy_tree(rel)

        if not args.sync:
            project_text = (src / ".maestro" / "project.yaml").read_text(encoding="utf-8")
            write(".maestro/project.yaml", configure_project(project_text, args.project_key, args.project_name))
            methodology_text = (src / ".maestro" / "methodology.yaml").read_text(encoding="utf-8")
            write(".maestro/methodology.yaml", configure_methodology(methodology_text, args.methodology))

            for rel in COPY_FILES:
                copy_file(rel)
        else:
            for rel in (".maestro/INSTRUCTIONS.md", ".maestro/runtime/README.md"):
                copy_file(rel)

        if not args.sync:
            template_dir = src / ".maestro" / "engine" / "templates"
            for output, template in TEMPLATE_OUTPUTS.items():
                template_path = template_dir / template
                if template_path.is_file():
                    write(output, template_path.read_text(encoding="utf-8"))

            for rel in DIRECTORIES:
                target = dst / rel
                if target.exists():
                    continue
                created.append(rel + "/")
                if not args.dry_run:
                    target.mkdir(parents=True, exist_ok=True)

    upsert_block("CLAUDE.md", CLAUDE_BLOCK, "maestro (auto)")
    upsert_block("AGENTS.md", AGENTS_BLOCK, "maestro (auto)")
    upsert_block(".gitignore", GITIGNORE_BLOCK, "maestro local runtime")

    if not (args.attach or args.sync):
        event = (
            '{"at":null,"actor":"maestro-init","event":"workspace.initialized",'
            f'"target":"{args.project_key or "unconfigured"}","methodology":"{args.methodology}"}}\n'
        )
        write(".maestro/history/events.jsonl", event)

    verb = "Would create" if args.dry_run else "Created"
    print(f"{verb} {len(created)} item(s) in {dst}")
    for rel in created:
        print(f"  + {rel}")
    if skipped:
        print(f"Skipped {len(skipped)} existing item(s) (use --force to overwrite):")
        for rel in skipped[:30]:
            print(f"  = {rel}")
    if manual_conflicts:
        print("Refused to overwrite framework files with manual edits (use --force):")
        for rel in manual_conflicts[:30]:
            print(f"  ! {rel}")
    if not args.dry_run and sync_manifest:
        sync_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        sync_manifest_path.write_text(
            json.dumps(sync_manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print("\nNext: configure .maestro/project.yaml if needed, then run /onboard or /coord.")
    return 1 if manual_conflicts else 0


if __name__ == "__main__":
    raise SystemExit(main())
