#!/usr/bin/env python3
"""PreToolUse(Write|Edit) hook: block writing secrets into files (R-013).

Inspects the content about to be written (Write.content, Edit.new_string,
MultiEdit.edits[].new_string) for secret-like material and blocks it.

Profiles:
  minimal  : disabled (no secret gating)
  standard : block high-confidence secret patterns (private keys, tokens, provider keys)
  strict   : also block generic `password:`/`secret:` style assignments with a value

Disable with MAESTRO_DISABLED_HOOKS=secret-guard.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lib  # noqa: E402

HOOK_ID = "secret-guard"

# High-confidence: blocked in standard + strict.
HIGH_CONFIDENCE = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}", re.I),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),                      # AWS access key id
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),            # Slack token
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}"),                 # Google API key
]

# Generic assignments: blocked only in strict (noisy; can match placeholders).
GENERIC = re.compile(
    r"\b(password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token)\s*[:=]\s*"
    r"['\"]?[^\s'\"#${}<>]{8,}",
    re.I,
)
# Allowlist obvious placeholders to reduce false positives in strict mode.
PLACEHOLDER = re.compile(r"(\{\{|\$\{|<[A-Z_]+>|example|placeholder|changeme|your[_-]?|xxxx|\*\*\*)", re.I)


def collect_content(payload: dict) -> str:
    ti = _lib.tool_input(payload)
    parts: list[str] = []
    if isinstance(ti.get("content"), str):
        parts.append(ti["content"])
    if isinstance(ti.get("new_string"), str):
        parts.append(ti["new_string"])
    edits = ti.get("edits")
    if isinstance(edits, list):
        for e in edits:
            if isinstance(e, dict) and isinstance(e.get("new_string"), str):
                parts.append(e["new_string"])
    return "\n".join(parts)


def main() -> int:
    if _lib.hook_disabled(HOOK_ID):
        return 0
    prof = _lib.profile()
    if prof == "minimal":
        return 0
    payload = _lib.read_payload()
    if _lib.tool_name(payload) not in {"Write", "Edit", "MultiEdit", "NotebookEdit"}:
        return 0
    content = collect_content(payload)
    if not content:
        return 0

    for pat in HIGH_CONFIDENCE:
        m = pat.search(content)
        if m:
            _lib.block(
                "Secret-like material blocked from being written (R-013).\n"
                f"⛔ Matched: {pat.pattern}\n"
                "⛔ Never commit secrets/tokens/keys. Use env vars / secret manager / .env (gitignored)."
            )

    if prof == "strict":
        m = GENERIC.search(content)
        if m and not PLACEHOLDER.search(m.group(0)):
            _lib.block(
                "Possible secret assignment blocked in strict profile (R-013).\n"
                f"⛔ Matched: {m.group(0)[:60]}...\n"
                "⛔ If this is a placeholder, use <PLACEHOLDER>/${ENV} form, or lower MAESTRO_HOOK_PROFILE to standard."
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
