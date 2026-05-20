#!/usr/bin/env bash
# beforeShellExecution hook: block destructive shell commands.
# Schema per https://cursor.com/docs/agent/hooks.
#
# Scope: Cursor IDE only. Other AI tools enforce the same policy via their own
# entrypoint files (.codex/AGENTS.md, .gemini/GEMINI.md, CLAUDE.md).
#
# Input  : JSON on stdin with "command" + "cwd"
# Output : exit 0 = allow, exit 2 = block

set -u

# shellcheck source=./_lib.sh
. "$(dirname "$0")/_lib.sh"
init_stdin

CMD=$(json_field command)
[ -z "$CMD" ] && exit 0

# Patterns Cursor must never auto-run (R-011-07: destructive ops require
# explicit user approval). Keep these broad: hooks are a guardrail, not the
# place to decide whether destructive cleanup is safe.
DENIED_PATTERNS=(
  '(^|[;&|[:space:]])rm[[:space:]]+-[^;&|[:space:]]*r[^;&|[:space:]]*f'
  '(^|[;&|[:space:]])rm[[:space:]]+-[^;&|[:space:]]*f[^;&|[:space:]]*r'
  '(^|[;&|[:space:]])rm[[:space:]]+(-r[[:space:]]+-f|-f[[:space:]]+-r)'
  'git[[:space:]]+push[[:space:]]+.*--force.*(main|master)'
  'git[[:space:]]+push[[:space:]]+-f[[:space:]]+.*(main|master)'
  'git[[:space:]]+reset[[:space:]]+--hard([[:space:]]|$)'
  'git[[:space:]]+clean[[:space:]]+-[^[:space:]]*[dfx]'
  'git[[:space:]]+checkout[[:space:]]+--[[:space:]]'
  'find[[:space:]].*[[:space:]]-delete([[:space:]]|$)'
  'kubectl[[:space:]]+apply'
  'kubectl[[:space:]]+delete'
  'terraform[[:space:]]+apply'
  'terraform[[:space:]]+destroy'
  'docker[[:space:]]+push'
  'DROP[[:space:]]+(TABLE|DATABASE|SCHEMA)'
  ':\(\)[[:space:]]*\{[[:space:]]*:[|]:&[[:space:]]*\};:' # fork bomb
)

for pattern in "${DENIED_PATTERNS[@]}"; do
  if printf '%s' "$CMD" | grep -Eiq "$pattern"; then
    cat >&2 <<EOF
⛔ [agent-workspace] Destructive command blocked.
⛔ Command : $CMD
⛔ Pattern : $pattern
⛔ Per R-011-07, destructive environment/data actions need explicit user approval.
⛔ If intentional, get explicit approval through Coordinator and run it manually.
EOF
    exit 2
  fi
done

exit 0
