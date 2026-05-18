#!/usr/bin/env bash
# preToolUse hook: block edits to application source unless an active
# task-analysis.yaml exists. Schema per https://cursor.com/docs/agent/hooks.
#
# Scope: Cursor IDE only. Other AI tools (Claude Code, Codex, Gemini, Copilot)
# enforce the same gate via their own AGENTS.md / CLAUDE.md instructions.
#
# Input  : JSON on stdin (hook_event_name = "preToolUse")
# Output : exit 0 = allow, exit 2 = block

set -u

# shellcheck source=./_lib.sh
. "$(dirname "$0")/_lib.sh"
init_stdin

# Edit-class tools only (Read/Bash/Grep should not be gated).
TOOL_NAME=$(json_field tool_name)
case "$TOOL_NAME" in
  Edit|Write|MultiEdit|NotebookEdit) ;;
  *) exit 0 ;;
esac

FILE_PATH=$(json_field file_path)
[ -z "$FILE_PATH" ] && exit 0

# Only gate application source code.
case "$FILE_PATH" in
  */services/*|*/src/*|*/app/*|*/packages/*|*/apps/*) ;;
  *) exit 0 ;;
esac

# Skip generated/vendored artifacts.
case "$FILE_PATH" in
  */node_modules/*|*/.git/*|*/dist/*|*/build/*|*/.next/*|*/__pycache__/*) exit 0 ;;
esac

cd "${CURSOR_PROJECT_DIR:-.}" || exit 0

STATE_FILE=".runtime/context/workflow-state.yaml"
ACTIVE_TASK_ID=""

if [ -f "$STATE_FILE" ]; then
  ACTIVE_TASK_ID=$(
    sed -nE 's/^[[:space:]]*active_task_id:[[:space:]]*"?([^"#]+)"?[[:space:]]*(#.*)?$/\1/p' "$STATE_FILE" \
      | head -1 \
      | sed -E 's/^[[:space:]]+|[[:space:]]+$//g'
  )
fi

case "$ACTIVE_TASK_ID" in
  ""|"null"|"~")
    cat >&2 <<EOF
⛔ [agent-workspace] No active_task_id in $STATE_FILE.
⛔ Run /coord then /analyze-task so Coordinator creates an active task before editing source.
⛔ Blocked file: $FILE_PATH
EOF
    exit 2
    ;;
esac

case "$ACTIVE_TASK_ID" in
  TASK-*) ;;
  *)
    cat >&2 <<EOF
⛔ [agent-workspace] Invalid active_task_id in $STATE_FILE: $ACTIVE_TASK_ID
⛔ Expected format: TASK-YYYYMMDD-NNN-slug.
⛔ Blocked file: $FILE_PATH
EOF
    exit 2
    ;;
esac

ACTIVE_TASK=".runtime/tasks/$ACTIVE_TASK_ID"

if [ ! -d "$ACTIVE_TASK" ]; then
  cat >&2 <<EOF
⛔ [agent-workspace] Active task folder does not exist: $ACTIVE_TASK
⛔ Run /coord then /analyze-task to create the task folder before editing source.
⛔ Blocked file: $FILE_PATH
EOF
  exit 2
fi

if [ ! -f "$ACTIVE_TASK/task-analysis.yaml" ]; then
  cat >&2 <<EOF
⛔ [agent-workspace] Active task $ACTIVE_TASK has no task-analysis.yaml.
⛔ Run /analyze-task to normalize the task before editing source (R-000-06).
⛔ Blocked file: $FILE_PATH
EOF
  exit 2
fi

exit 0
