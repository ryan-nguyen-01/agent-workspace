"""Shared helpers for Claude Code hooks in maestro.

Claude Code hook contract (PreToolUse):
  - Hook receives a JSON object on stdin:
      {session_id, transcript_path, cwd, hook_event_name, tool_name, tool_input: {...}}
  - Exit 0  = allow.
  - Exit 2  = block; stderr is fed back to the model as the block reason.
  - Other   = non-blocking error (fail-open); stderr is surfaced as a warning.

Execution profiles (learned from ECC hook runtime controls):
  MAESTRO_HOOK_PROFILE = minimal | standard (default) | strict
  MAESTRO_DISABLED_HOOKS = comma-separated hook ids to disable (e.g. "scope-guard,secret-guard")

These scripts have NO third-party dependencies (no jq, no PyYAML) so they run
anywhere Python 3.8+ is available.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

VALID_PROFILES = {"minimal", "standard", "strict"}


def read_payload() -> dict:
    """Read and parse the hook JSON payload from stdin. Fail-open on parse error."""
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def profile() -> str:
    p = (os.environ.get("MAESTRO_HOOK_PROFILE") or "standard").strip().lower()
    return p if p in VALID_PROFILES else "standard"


def hook_disabled(hook_id: str) -> bool:
    disabled = os.environ.get("MAESTRO_DISABLED_HOOKS", "")
    ids = {x.strip() for x in disabled.split(",") if x.strip()}
    return hook_id in ids


def tool_name(payload: dict) -> str:
    return str(payload.get("tool_name") or "")


def tool_input(payload: dict) -> dict:
    ti = payload.get("tool_input")
    return ti if isinstance(ti, dict) else {}


def field(payload: dict, key: str) -> str:
    """Return tool_input.<key> (then top-level <key>) as a string, else ''."""
    ti = tool_input(payload)
    if key in ti and ti[key] is not None:
        return str(ti[key])
    if key in payload and payload[key] is not None:
        return str(payload[key])
    return ""


def project_dir(payload: dict) -> Path:
    cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return Path(cwd)


def rel_path(file_path: str, root: Path) -> str:
    p = file_path
    try:
        rp = Path(p)
        if rp.is_absolute():
            return str(rp.relative_to(root))
    except Exception:
        pass
    p = p[2:] if p.startswith("./") else p
    return p


def allow() -> None:
    sys.exit(0)


def block(reason: str) -> None:
    sys.stderr.write(f"⛔ [maestro] {reason}\n")
    sys.exit(2)


def warn_fail_open(reason: str) -> None:
    """Non-blocking: surface a warning but let the tool proceed (exit 1)."""
    sys.stderr.write(f"⚠️ [maestro] {reason}\n")
    sys.exit(1)
