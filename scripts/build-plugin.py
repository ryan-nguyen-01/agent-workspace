#!/usr/bin/env python3
"""Generate the Claude Code plugin wrapper from the repo — single source of truth.

agent-workspace is primarily a clone-and-work-inside workspace (it needs root CLAUDE.md,
`.agent/`, `.runtime/`, and the multi-tool adapters that a plugin cannot ship). This script
packages the *Claude tool layer* (agents + skills + commands + hooks) as an installable plugin
WITHOUT duplicating content: the repo root itself becomes the plugin, and `plugin.json` points
its component paths at the existing `.claude/` directories.

It generates three files under `.claude-plugin/`:
  - plugin.json       — manifest with path overrides into .claude/ + hooks
  - hooks.json        — PreToolUse hooks translated from .claude/settings.json
                        ($CLAUDE_PROJECT_DIR -> ${CLAUDE_PLUGIN_ROOT})
  - marketplace.json  — single-plugin marketplace so `/plugin marketplace add <repo>` works

Usage:
  python3 scripts/build-plugin.py           # (re)generate the plugin wrapper
  python3 scripts/build-plugin.py --check    # verify wrapper is in sync (CI/drift), no writes

Install (for users, once published to a git remote):
  /plugin marketplace add <git-url-or-local-path>
  /plugin install agent-workspace@agent-workspace

Note: the plugin delivers the Claude-facing agents/skills/commands/hooks. The full stateful
workflow (project brain, task artifacts, CLAUDE.md precedence) still requires the workspace repo.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = ROOT / ".claude-plugin"
SETTINGS = ROOT / ".claude" / "settings.json"


def framework_version() -> str:
    try:
        data = json.loads(SETTINGS.read_text(encoding="utf-8"))
        return str(data.get("framework", {}).get("version", "0.0.0"))
    except Exception:
        return "0.0.0"


def counts() -> dict[str, int]:
    agents = len(list((ROOT / ".claude" / "agents").rglob("*.agent.md")))
    skills = len(list((ROOT / ".claude" / "skills").rglob("SKILL.md")))
    commands = len([p for p in (ROOT / ".claude" / "commands").glob("*.md") if p.name != "README.md"])
    return {"agents": agents, "skills": skills, "commands": commands}


def translate_hooks() -> dict:
    """Build plugin hooks.json from .claude/settings.json, rebasing script paths to the plugin root."""
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    hooks = settings.get("hooks", {})
    text = json.dumps(hooks)
    # In a plugin, the hook scripts ship inside the plugin (= repo root). Rebase from the
    # project-dir variable used in settings.json to the plugin-root variable.
    text = text.replace("$CLAUDE_PROJECT_DIR", "${CLAUDE_PLUGIN_ROOT}")
    return json.loads(text)


def build_manifest(version: str, c: dict[str, int]) -> dict:
    return {
        "name": "agent-workspace",
        "version": version,
        "description": (
            "Coordinator-driven multi-agent workflow for software engineering: "
            f"{c['agents']} agents (12 workflow + 2 built-in coders + 19 specialist advisors), "
            f"{c['skills']} skills, {c['commands']} commands, and deterministic scope/secret/"
            "destructive hooks. Claude tool layer of the agent-workspace framework."
        ),
        "author": {"name": "agent-workspace"},
        "keywords": [
            "workflow", "multi-agent", "coordinator", "specialists",
            "code-review", "hooks", "skills",
        ],
        "license": "MIT",
        # Path overrides: reuse the existing .claude/ tree so there is no duplicated content.
        "commands": "./.claude/commands",
        "agents": "./.claude/agents",
        "skills": "./.claude/skills",
        "hooks": "./.claude-plugin/hooks.json",
    }


def build_marketplace(version: str) -> dict:
    return {
        "name": "agent-workspace",
        "owner": {"name": "agent-workspace"},
        "metadata": {"description": "agent-workspace framework — Claude tool layer.", "version": version},
        "plugins": [
            {
                "name": "agent-workspace",
                "source": "./",
                "description": "Agents, skills, commands, and enforcement hooks for the agent-workspace workflow.",
            }
        ],
    }


def dump(path: Path, data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify wrapper matches source, no writes")
    args = ap.parse_args()

    version = framework_version()
    c = counts()
    artifacts = {
        PLUGIN_DIR / "plugin.json": dump(PLUGIN_DIR / "plugin.json", build_manifest(version, c)),
        PLUGIN_DIR / "hooks.json": dump(PLUGIN_DIR / "hooks.json", translate_hooks()),
        PLUGIN_DIR / "marketplace.json": dump(PLUGIN_DIR / "marketplace.json", build_marketplace(version)),
    }

    if args.check:
        drift = []
        for path, expected in artifacts.items():
            actual = path.read_text(encoding="utf-8") if path.is_file() else None
            if actual != expected:
                drift.append(path.relative_to(ROOT).as_posix())
        if drift:
            print(f"[check] plugin wrapper out of sync: {drift} — run scripts/build-plugin.py")
            return 1
        print(f"[check] plugin wrapper in sync (v{version}, agents={c['agents']} skills={c['skills']} commands={c['commands']})")
        return 0

    PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
    for path, content in artifacts.items():
        path.write_text(content, encoding="utf-8")
    print(f"Wrote plugin wrapper to {PLUGIN_DIR.relative_to(ROOT)}/ (v{version})")
    print(f"  agents={c['agents']} skills={c['skills']} commands={c['commands']}")
    print("  install: /plugin marketplace add <repo> && /plugin install agent-workspace@agent-workspace")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
