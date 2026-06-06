#!/usr/bin/env python3
"""Generate the Codex plugin marketplace under .codex/marketplace/ — single source = .claude/skills/.

Codex plugins differ from Claude plugins: the CLI COPIES the plugin into its cache and does NOT
follow symlinks or path-overrides outside the plugin root. So the skills must exist as real files
inside the plugin. To avoid bloating git, the copy is gitignored — `.claude/skills/` stays the
single source of truth; users run this generator before installing.

Everything lives under `.codex/marketplace/` (grouped with the other Codex adapter files) so the
repo root stays clean and there is no `.agents/` vs `.agent/` name collision:

  .codex/marketplace/.agents/plugins/marketplace.json            (Codex marketplace manifest)
  .codex/marketplace/plugins/agent-workspace/.codex-plugin/plugin.json
  .codex/marketplace/plugins/agent-workspace/skills/             (COPIED from .claude/skills, gitignored)

Install (Codex CLI):
  python3 scripts/build-codex-plugin.py
  codex plugin marketplace add "$(pwd)/.codex/marketplace"
  codex plugin add agent-workspace@agent-workspace

Usage:
  python3 scripts/build-codex-plugin.py            # copy skills + write manifests
  python3 scripts/build-codex-plugin.py --check     # verify manifests in sync (no copy), CI/drift
  python3 scripts/build-codex-plugin.py --clean     # remove the generated marketplace tree
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / ".claude" / "settings.json"
SKILLS_SRC = ROOT / ".claude" / "skills"
MARKET_ROOT = ROOT / ".codex" / "marketplace"
PLUGIN_DIR = MARKET_ROOT / "plugins" / "agent-workspace"
SKILLS_DST = PLUGIN_DIR / "skills"
PLUGIN_MANIFEST = PLUGIN_DIR / ".codex-plugin" / "plugin.json"
MARKETPLACE = MARKET_ROOT / ".agents" / "plugins" / "marketplace.json"


def version() -> str:
    try:
        return str(json.loads(SETTINGS.read_text(encoding="utf-8")).get("framework", {}).get("version", "0.0.0"))
    except Exception:
        return "0.0.0"


def manifest(v: str) -> dict:
    return {
        "name": "agent-workspace",
        "version": v,
        "description": (
            "Coordinator-driven multi-agent workflow skills for software engineering: 231 skills "
            "across frameworks, databases, cloud, security, testing, and the agent-workspace workflow."
        ),
        "author": {"name": "agent-workspace"},
        "homepage": "https://github.com/ryan-nguyen-01/agent-workspace",
        "repository": "https://github.com/ryan-nguyen-01/agent-workspace",
        "license": "MIT",
        "keywords": ["workflow", "multi-agent", "coordinator", "skills", "code-review", "specialists"],
        "skills": "./skills/",
        "interface": {
            "displayName": "Agent Workspace",
            "shortDescription": "Multi-agent workflow skills",
            "longDescription": (
                "The skill layer of the agent-workspace framework: 231 composable skills (frameworks, "
                "databases, cloud, security, testing) plus the 12 workflow skills. Use inside the "
                "agent-workspace repo for the full coordinator-driven workflow."
            ),
            "developerName": "agent-workspace",
            "category": "Developer Tools",
            "capabilities": ["Interactive", "Write"],
            "defaultPrompt": [
                "Analyze this project and build the workspace brain",
                "Add a feature through the coordinator workflow",
                "Review the current change for correctness and quality",
            ],
            "screenshots": [],
        },
    }


def marketplace() -> dict:
    return {
        "name": "agent-workspace",
        "plugins": [
            {
                "name": "agent-workspace",
                "source": {"source": "local", "path": "./plugins/agent-workspace"},
                "category": "Developer Tools",
            }
        ],
    }


def dump(d: dict) -> str:
    return json.dumps(d, indent=2, ensure_ascii=False) + "\n"


def clean() -> None:
    if MARKET_ROOT.exists():
        shutil.rmtree(MARKET_ROOT)
    print(f"Removed {MARKET_ROOT.relative_to(ROOT)}/")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify manifests in sync, no copy")
    ap.add_argument("--clean", action="store_true", help="remove generated marketplace tree")
    ap.add_argument("--force", action="store_true", help="overwrite even hand-edited manifests")
    args = ap.parse_args()
    from _genlib import Generator

    if args.clean:
        clean()
        return 0

    v = version()
    manifests = {
        PLUGIN_MANIFEST: dump(manifest(v)),
        MARKETPLACE: dump(marketplace()),
    }

    if args.check:
        drift = [p.relative_to(ROOT).as_posix() for p, exp in manifests.items()
                 if (p.read_text(encoding="utf-8") if p.is_file() else None) != exp]
        if drift:
            print(f"[check] codex plugin manifests out of sync: {drift} — run scripts/build-codex-plugin.py")
            return 1
        src = len(list(SKILLS_SRC.rglob("SKILL.md")))
        dst = len(list(SKILLS_DST.rglob("SKILL.md"))) if SKILLS_DST.exists() else 0
        note = "" if src == dst else f"  ⚠️ skills copy stale: src={src} copy={dst} (rerun without --check)"
        print(f"[check] codex plugin manifests in sync (v{v}, skills src={src} copy={dst}){note}")
        return 0

    gen = Generator("build-codex-plugin", force=args.force)
    for path, content in manifests.items():
        gen.write(path, content)
    gen.flush()

    # Real copy of skills into the plugin root (Codex won't follow symlinks).
    if SKILLS_DST.exists():
        shutil.rmtree(SKILLS_DST)
    shutil.copytree(SKILLS_SRC, SKILLS_DST)
    n = len(list(SKILLS_DST.rglob("SKILL.md")))
    print(f"Codex marketplace (v{v}); copied {n} skills into {SKILLS_DST.relative_to(ROOT)}/ (gitignored)")
    print('  install: codex plugin marketplace add "$(pwd)/.codex/marketplace" && codex plugin add agent-workspace@agent-workspace')
    return gen.report()


if __name__ == "__main__":
    raise SystemExit(main())
