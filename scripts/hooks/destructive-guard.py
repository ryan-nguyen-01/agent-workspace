#!/usr/bin/env python3
"""PreToolUse(Bash) hook: block destructive shell commands (R-011-07).

Mirrors .cursor/hooks/block-destructive.sh for the Claude Code adapter.
Destructive environment/data actions require explicit user approval through
Coordinator; this hook is a guardrail, not the place to decide if cleanup is safe.

Profiles: active in all profiles (minimal/standard/strict). Disable with
AW_DISABLED_HOOKS=destructive-guard.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lib  # noqa: E402

HOOK_ID = "destructive-guard"

DENIED_PATTERNS = [
    r"(^|[;&|\s])rm\s+-[^\s;&|]*r[^\s;&|]*f",
    r"(^|[;&|\s])rm\s+-[^\s;&|]*f[^\s;&|]*r",
    r"(^|[;&|\s])rm\s+(-r\s+-f|-f\s+-r)",
    r"git\s+push\s+.*--force.*(main|master)",
    r"git\s+push\s+-f\s+.*(main|master)",
    r"git\s+reset\s+--hard(\s|$)",
    r"git\s+clean\s+-[^\s]*[dfx]",
    r"find\s+.*\s-delete(\s|$)",
    r"kubectl\s+(apply|delete)",
    r"terraform\s+(apply|destroy)",
    r"docker\s+push",
    r"DROP\s+(TABLE|DATABASE|SCHEMA)",
    r":\(\)\s*\{\s*:\|:&\s*\};:",  # fork bomb
]


def main() -> int:
    if _lib.hook_disabled(HOOK_ID):
        return 0
    payload = _lib.read_payload()
    if _lib.tool_name(payload) != "Bash":
        return 0
    cmd = _lib.field(payload, "command")
    if not cmd:
        return 0
    for pattern in DENIED_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            _lib.block(
                "Destructive command blocked.\n"
                f"⛔ Command : {cmd}\n"
                f"⛔ Pattern : {pattern}\n"
                "⛔ Per R-011-07, destructive environment/data actions need explicit user approval.\n"
                "⛔ If intentional, get approval through Coordinator and run it manually."
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
