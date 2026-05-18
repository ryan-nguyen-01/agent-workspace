#!/usr/bin/env bash
# preToolUse hook: warn (do not block) when editing framework workflow agents.
# Schema per https://cursor.com/docs/agent/hooks.
#
# Scope: Cursor IDE only.
# Input  : JSON on stdin
# Output : exit 0 (informational only)

set -u

# shellcheck source=./_lib.sh
. "$(dirname "$0")/_lib.sh"
init_stdin

TOOL_NAME=$(json_field tool_name)
case "$TOOL_NAME" in
  Edit|Write|MultiEdit) ;;
  *) exit 0 ;;
esac

FILE_PATH=$(json_field file_path)
[ -z "$FILE_PATH" ] && exit 0

WORKFLOW_AGENTS=(
  ".claude/agents/coordinator.agent.md"
  ".claude/agents/onboarding.agent.md"
  ".claude/agents/agent-factory.agent.md"
  ".claude/agents/task-analysis.agent.md"
  ".claude/agents/solution-architect.agent.md"
  ".claude/agents/coder-leader.agent.md"
  ".claude/agents/dev-verification.agent.md"
  ".claude/agents/qc-handoff.agent.md"
  ".claude/agents/qc-runner.agent.md"
  ".claude/agents/bug-router.agent.md"
  ".claude/agents/memory-update.agent.md"
  ".claude/agents/workflow-policy.agent.md"
)

for agent in "${WORKFLOW_AGENTS[@]}"; do
  case "$FILE_PATH" in
    *"$agent"|"$agent")
      cat >&2 <<EOF
⚠️  [agent-workspace] Editing framework workflow agent:
    $FILE_PATH

This file defines the AI workflow contract. Edits cascade to every project using
this framework. If intentional (improving the framework), proceed. Otherwise:
  - For per-project agent scopes  → /create-coders or agent-factory
  - For per-project policy tweaks → /policy-check first
  - For documentation only        → consider AGENTS.md / CLAUDE.md instead
EOF
      break
      ;;
  esac
done

exit 0
