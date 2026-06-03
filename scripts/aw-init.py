#!/usr/bin/env python3
"""Scaffold the agent-workspace full-flow files into a target project.

A plugin delivers only the Claude/Codex tool layer (agents, skills, commands, hooks). The full
coordinator-driven flow also needs the tool-neutral source (`.agent/`), the runtime state tree
(`.runtime/`), and `CLAUDE.md` precedence — none of which a plugin can install. This script copies
those from the framework root into the current project so the flow actually runs.

It is invoked by the `/aw-init` command (which passes the framework root). When installed as a
plugin, the framework root is the plugin install dir; in the repo itself it is the repo root.

Behavior:
  - Copies `.agent/` (tool-neutral source: workflow.md, rules, templates, docs).
  - Creates the `.runtime/` tree and seeds context YAML from `.agent/templates/*.template.yaml`
    (falls back to copying the framework's own `.runtime/context/*.yaml` seed when no template).
  - Copies `CLAUDE.md`.
  - NEVER overwrites an existing file/dir unless --force; reports what it skipped.

Usage:
  python3 aw-init.py --from <framework-root> [--to <project-dir>] [--force] [--dry-run]
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

# Runtime context files to seed and their template source (when present).
CONTEXT_SEED = {
    "workflow-state.yaml": "workflow-state.template.yaml",
    "project-brain.yaml": "project-brain.template.yaml",
    "agent-registry.yaml": "agent-registry.template.yaml",
    "model-routing.yaml": "model-routing.template.yaml",
    "response-ui.yaml": "response-ui.template.yaml",
    "agent-activity.yaml": "agent-activity.template.yaml",
}
# Context files with no template — copy the framework's own seed verbatim.
CONTEXT_COPY = [
    "service-catalog.yaml", "test-policy.yaml", "skill-registry.yaml",
    "skill-taxonomy.yaml", "index.yaml", "inputs-index.yaml",
]
RUNTIME_DIRS = [
    ".runtime", ".runtime/context", ".runtime/context/services",
    ".runtime/context/feedback", ".runtime/context/common",
    ".runtime/tasks", ".runtime/bugs", ".runtime/bugs/blockers", ".runtime/bugs/non-blockers",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", required=True, help="framework root (plugin install dir or repo)")
    ap.add_argument("--to", dest="dst", default=".", help="target project dir (default: cwd)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    ap.add_argument("--dry-run", action="store_true", help="print actions, write nothing")
    args = ap.parse_args()

    src = Path(args.src).resolve()
    dst = Path(args.dst).resolve()
    if not (src / ".agent" / "workflow.md").is_file():
        print(f"❌ --from {src} is not an agent-workspace root (missing .agent/workflow.md)")
        return 1
    if src == dst:
        print("❌ refusing to scaffold a framework into itself (--from == --to)")
        return 1

    created, skipped = [], []

    def write(rel: str, content: str) -> None:
        target = dst / rel
        if target.exists() and not args.force:
            skipped.append(rel); return
        created.append(rel)
        if args.dry_run:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def copy_tree(rel: str) -> None:
        s, d = src / rel, dst / rel
        if d.exists() and not args.force:
            skipped.append(rel + "/"); return
        created.append(rel + "/")
        if args.dry_run:
            return
        shutil.copytree(s, d, dirs_exist_ok=args.force)

    # 1. tool-neutral source
    if (src / ".agent").is_dir():
        copy_tree(".agent")
    # 2. CLAUDE.md precedence
    if (src / "CLAUDE.md").is_file():
        write("CLAUDE.md", (src / "CLAUDE.md").read_text(encoding="utf-8"))
    # 3. runtime tree
    for d in RUNTIME_DIRS:
        target = dst / d
        if not target.exists():
            created.append(d + "/")
            if not args.dry_run:
                target.mkdir(parents=True, exist_ok=True)
            (dst / d / ".gitkeep").parent.mkdir(parents=True, exist_ok=True) if not args.dry_run else None
    # 4. seed context from templates, then fill the rest from the framework seed
    tdir = src / ".agent" / "templates"
    for name, tmpl in CONTEXT_SEED.items():
        tp = tdir / tmpl
        if tp.is_file():
            write(f".runtime/context/{name}", tp.read_text(encoding="utf-8"))
    for name in CONTEXT_COPY:
        sp = src / ".runtime" / "context" / name
        if sp.is_file():
            write(f".runtime/context/{name}", sp.read_text(encoding="utf-8"))

    verb = "Would create" if args.dry_run else "Created"
    print(f"{verb} {len(created)} item(s) in {dst}")
    for c in created:
        print(f"  + {c}")
    if skipped:
        print(f"Skipped {len(skipped)} existing item(s) (use --force to overwrite):")
        for s in skipped[:20]:
            print(f"  = {s}")
    print("\nNext: open this project and run /coord (or '/onboard') — the coordinator now has "
          ".agent/workflow.md, .runtime/ state, and CLAUDE.md to run the full flow.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
