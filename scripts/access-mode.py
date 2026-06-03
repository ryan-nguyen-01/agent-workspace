#!/usr/bin/env python3
"""Switch the harness tool-execution permission posture (access_mode).

access_mode is ONLY about whether ordinary tool calls (terminal commands, file reads/edits) prompt
for permission. It does NOT change the workflow approval gates (R-011) or any hook — the pipeline
still asks for everything it must ask, and scope/secret/destructive guards still block (R-011-14).

  guarded    (default): the fullaccess allowlist is removed; tool calls prompt as normal.
  fullaccess          : .claude/settings.json permissions.allow grants Bash/file tools so they run
                        without a per-call prompt. Workflow gates + hooks unchanged.

IMPORTANT: fullaccess uses a permission ALLOWLIST, not bypassPermissions / --dangerously-skip-
permissions. The bypass mode is refused by Claude Code under root/sudo; the allowlist works for all
users (including root) and is safer because each tool is explicitly allowed and the PreToolUse hooks
still run (destructive/secret/scope guards keep blocking).

This writes both:
  - .claude/settings.json   permissions.allow   (+ removes any legacy defaultMode=bypassPermissions)
  - .runtime/context/workflow-state.yaml   access_mode   (for /status visibility)

Usage:
  python3 scripts/access-mode.py --status
  python3 scripts/access-mode.py --set full
  python3 scripts/access-mode.py --set guarded
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / ".claude" / "settings.json"
STATE = ROOT / ".runtime" / "context" / "workflow-state.yaml"

# Tools auto-approved in fullaccess. Bare tool names match all invocations of that tool.
# PreToolUse hooks still run on allowed tools, so destructive/secret/scope guards keep blocking.
FULLACCESS_ALLOW = ["Bash", "Read", "Edit", "Write", "MultiEdit", "NotebookEdit", "Glob", "Grep"]


def read_status() -> dict:
    out = {"access_mode": "guarded", "allow_count": 0, "legacy_bypass": False}
    try:
        s = json.loads(SETTINGS.read_text(encoding="utf-8"))
        perms = s.get("permissions", {})
        allow = perms.get("allow", [])
        out["allow_count"] = sum(1 for a in allow if a in FULLACCESS_ALLOW)
        out["legacy_bypass"] = perms.get("defaultMode") == "bypassPermissions"
    except Exception:
        pass
    try:
        m = re.search(r"^access_mode:\s*[\"']?(\w+)", STATE.read_text(encoding="utf-8"), re.M)
        if m:
            out["access_mode"] = m.group(1)
    except Exception:
        pass
    return out


def apply_settings(mode: str) -> None:
    data = json.loads(SETTINGS.read_text(encoding="utf-8"))
    perms = data.setdefault("permissions", {})
    # Always drop the unsafe legacy bypass mode (rejected under root).
    if perms.get("defaultMode") == "bypassPermissions":
        perms.pop("defaultMode", None)
    existing = [a for a in perms.get("allow", []) if a not in FULLACCESS_ALLOW]
    if mode == "fullaccess":
        perms["allow"] = existing + FULLACCESS_ALLOW
    else:
        perms["allow"] = existing
        if not perms["allow"]:
            perms.pop("allow", None)
    if not perms:
        data.pop("permissions", None)
    SETTINGS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def set_state(mode: str) -> None:
    if not STATE.is_file():
        return
    text = STATE.read_text(encoding="utf-8")
    if re.search(r"^access_mode:", text, re.M):
        text = re.sub(r"^access_mode:.*$", f'access_mode: "{mode}"', text, count=1, flags=re.M)
    elif re.search(r"^distribution_mode:", text, re.M):
        text = re.sub(r"^(distribution_mode:.*)$", rf'\1\naccess_mode: "{mode}"', text, count=1, flags=re.M)
    else:
        text = f'access_mode: "{mode}"\n' + text
    STATE.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=["full", "fullaccess", "guarded"], help="switch access mode")
    ap.add_argument("--status", action="store_true", help="print current access mode")
    args = ap.parse_args()

    if args.status or not args.set:
        st = read_status()
        print(f"access_mode: {st['access_mode']}")
        print(f"fullaccess allowlist active: {st['allow_count']}/{len(FULLACCESS_ALLOW)} tools")
        if st["legacy_bypass"]:
            print("  ⚠️ legacy permissions.defaultMode=bypassPermissions present (breaks `claude` as root)."
                  " Run: python3 scripts/access-mode.py --set guarded")
        print("  guarded = prompt as normal · fullaccess = allowlist (workflow gates + hooks unchanged)")
        return 0

    mode = "fullaccess" if args.set in ("full", "fullaccess") else "guarded"
    apply_settings(mode)
    set_state(mode)
    print(f"access_mode -> {mode}")
    if mode == "fullaccess":
        print(f"  permissions.allow grants: {', '.join(FULLACCESS_ALLOW)} (no per-call prompt)")
        print("  Uses an allowlist (NOT bypassPermissions) — works under root; hooks still block.")
    else:
        print("  fullaccess allowlist removed; tool calls prompt as normal.")
    print("Workflow approval gates (R-011) and scope/secret/destructive hooks are UNCHANGED.")
    print("Applies to new sessions; for the current session use the harness permission UI (Shift+Tab).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
