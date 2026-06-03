#!/usr/bin/env python3
"""Switch the harness tool-execution permission posture (access_mode).

access_mode is ONLY about whether ordinary tool calls (terminal commands, file reads/edits) prompt
for permission. It does NOT change the workflow approval gates (R-011) or any hook — the pipeline
still asks for everything it must ask, and scope/secret/destructive guards still block (R-011-14).

  guarded    (default): .claude/settings.json permissions follow the allowlist (prompt as configured).
  fullaccess          : permissions.defaultMode = "bypassPermissions" — read files / run terminal
                        commands without a per-call prompt. Workflow gates + hooks unchanged.

This writes both:
  - .claude/settings.json   permissions.defaultMode
  - .runtime/context/workflow-state.yaml   access_mode   (for /status visibility)

A settings.json permission-mode change applies to NEW sessions; in the current session use the
harness permission UI (e.g. Shift+Tab) if you need it to take effect immediately.

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

MODE_TO_DEFAULTMODE = {"fullaccess": "bypassPermissions", "guarded": "default"}


def read_status() -> dict:
    out = {"access_mode": "guarded", "settings_default_mode": "default"}
    try:
        s = json.loads(SETTINGS.read_text(encoding="utf-8"))
        out["settings_default_mode"] = s.get("permissions", {}).get("defaultMode", "default")
    except Exception:
        pass
    try:
        m = re.search(r"^access_mode:\s*[\"']?(\w+)", STATE.read_text(encoding="utf-8"), re.M)
        if m:
            out["access_mode"] = m.group(1)
    except Exception:
        pass
    return out


def set_settings(default_mode: str) -> None:
    data = json.loads(SETTINGS.read_text(encoding="utf-8"))
    perms = data.setdefault("permissions", {})
    if default_mode == "default":
        perms.pop("defaultMode", None)  # default posture = follow allowlist
    else:
        perms["defaultMode"] = default_mode
    SETTINGS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def set_state(mode: str) -> None:
    if not STATE.is_file():
        return
    text = STATE.read_text(encoding="utf-8")
    if re.search(r"^access_mode:", text, re.M):
        text = re.sub(r"^access_mode:.*$", f'access_mode: "{mode}"', text, count=1, flags=re.M)
    else:
        # insert near the top, after distribution_mode if present, else prepend
        if re.search(r"^distribution_mode:", text, re.M):
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
        print(f"settings permissions.defaultMode: {st['settings_default_mode']}")
        print("  guarded = prompt per allowlist · fullaccess = bypassPermissions (workflow gates + hooks unchanged)")
        return 0

    mode = "fullaccess" if args.set in ("full", "fullaccess") else "guarded"
    set_settings(MODE_TO_DEFAULTMODE[mode])
    set_state(mode)
    print(f"access_mode -> {mode} (settings permissions.defaultMode = {MODE_TO_DEFAULTMODE[mode]})")
    print("Workflow approval gates (R-011) and scope/secret/destructive hooks are UNCHANGED.")
    if mode == "fullaccess":
        print("Applies to new sessions; for the current session use the harness permission UI (Shift+Tab).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
