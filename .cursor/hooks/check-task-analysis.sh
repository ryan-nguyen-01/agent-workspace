#!/usr/bin/env bash
# preToolUse hook: enforce direct/assisted/governed source-edit contracts.
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

block() {
  cat >&2 <<EOF
⛔ [maestro] $1
⛔ Blocked file: $FILE_PATH
EOF
  exit 2
}

yaml_value_from_line() {
  printf '%s' "$1" \
    | sed -E 's/^[^:]+:[[:space:]]*//; s/[[:space:]]+#.*$//; s/^[[:space:]]+|[[:space:]]+$//g; s/^"//; s/"$//'
}

yaml_list_value_from_line() {
  printf '%s' "$1" \
    | sed -E 's/^[[:space:]]*-[[:space:]]*//; s/[[:space:]]+#.*$//; s/^[[:space:]]+|[[:space:]]+$//g; s/^"//; s/"$//'
}

path_matches_pattern() {
  local path="$1"
  local pattern="$2"
  pattern=${pattern#./}
  [ -n "$pattern" ] || return 1

  case "$path" in
    $pattern) return 0 ;;
  esac

  # Treat literal **/foo as also matching foo at repository root.
  case "$pattern" in
    \*\*/*)
      local root_pattern="${pattern#\*\*/}"
      case "$path" in
        $root_pattern) return 0 ;;
      esac
      ;;
  esac

  return 1
}

scope_allows_file() {
  local rel_path="$1"
  local registry_file="$2"
  [ -f "$registry_file" ] || return 1

  local scope_allowed=false
  local agent_seen=false
  local agent_status=""
  local agent_allowed=false
  local agent_forbidden=false
  local section=""
  local line pattern

  finalize_agent_scope() {
    [ "$agent_seen" = true ] || return 0
    if [ "$agent_status" = "active" ] && \
       [ "$agent_allowed" = true ] && \
       [ "$agent_forbidden" != true ]; then
      scope_allowed=true
    fi
  }

  while IFS= read -r line; do
    if printf '%s\n' "$line" | grep -Eq '^  - id:'; then
      finalize_agent_scope
      agent_seen=true
      agent_status=""
      agent_allowed=false
      agent_forbidden=false
      section=""
      continue
    fi

    [ "$agent_seen" = true ] || continue

    if printf '%s\n' "$line" | grep -Eq '^    status:'; then
      agent_status=$(yaml_value_from_line "$line")
      continue
    fi

    if printf '%s\n' "$line" | grep -Eq '^      allowed_write_paths:'; then
      section="allow"
      continue
    fi

    if printf '%s\n' "$line" | grep -Eq '^      forbidden_paths:'; then
      section="forbid"
      continue
    fi

    if printf '%s\n' "$line" | grep -Eq '^      [A-Za-z0-9_]+:'; then
      section=""
      continue
    fi

    if [ -n "$section" ] && printf '%s\n' "$line" | grep -Eq '^        - '; then
      pattern=$(yaml_list_value_from_line "$line")
      if path_matches_pattern "$rel_path" "$pattern"; then
        case "$section" in
          allow) agent_allowed=true ;;
          forbid) agent_forbidden=true ;;
        esac
      fi
    fi
  done < "$registry_file"

  finalize_agent_scope
  [ "$scope_allowed" = true ]
}

# Edit-class tools only (Read/Bash/Grep should not be gated).
TOOL_NAME=$(json_field tool_name)
case "$TOOL_NAME" in
  Edit|Write|MultiEdit|NotebookEdit) ;;
  *) exit 0 ;;
esac

FILE_PATH=$(json_field file_path)
[ -z "$FILE_PATH" ] && exit 0

REL_PATH="$FILE_PATH"
case "$REL_PATH" in
  "$PWD"/*) REL_PATH=${REL_PATH#"$PWD"/} ;;
esac
REL_PATH=${REL_PATH#./}

# Only gate likely application source code. Keep this broader than services/**
# because applied workspaces may be single-repo apps, CLIs, libraries, data jobs,
# or Go/Rust-style layouts at the workspace root.
case "$FILE_PATH" in
  */services/*|services/*|*/src/*|src/*|*/app/*|app/*|*/packages/*|packages/*|*/apps/*|apps/*|*/cmd/*|cmd/*|*/internal/*|internal/*|*/pkg/*|pkg/*|*/lib/*|lib/*|*/libs/*|libs/*|*/crates/*|crates/*|*/notebooks/*|notebooks/*|*/dags/*|dags/*|*/jobs/*|jobs/*|*/pipelines/*|pipelines/*|*/tests/*|tests/*) ;;
  *) exit 0 ;;
esac

# Skip generated/vendored artifacts.
case "$FILE_PATH" in
  */node_modules/*|node_modules/*|*/.git/*|.git/*|*/dist/*|dist/*|*/build/*|build/*|*/.next/*|.next/*|*/__pycache__/*|__pycache__/*) exit 0 ;;
esac

cd "${CURSOR_PROJECT_DIR:-.}" || exit 0

REL_PATH="$FILE_PATH"
case "$REL_PATH" in
  "$PWD"/*) REL_PATH=${REL_PATH#"$PWD"/} ;;
esac
REL_PATH=${REL_PATH#./}

STATE_FILE=".maestro/runtime/workflow-state.yaml"
ACTIVE_TASK_ID=""
EXECUTION_MODE=""

if [ -f "$STATE_FILE" ]; then
  EXECUTION_MODE=$(
    sed -nE 's/^[[:space:]]*active_execution_mode:[[:space:]]*"?([^"#]+)"?[[:space:]]*(#.*)?$/\1/p' "$STATE_FILE" \
      | head -1 \
      | sed -E 's/^[[:space:]]+|[[:space:]]+$//g'
  )
  case "$EXECUTION_MODE" in
    ""|"null"|"~")
      EXECUTION_MODE=$(
        sed -nE 's/^[[:space:]]*default_execution_mode:[[:space:]]*"?([^"#]+)"?[[:space:]]*(#.*)?$/\1/p' "$STATE_FILE" \
          | head -1 \
          | sed -E 's/^[[:space:]]+|[[:space:]]+$//g'
      )
      ;;
  esac
  ACTIVE_TASK_ID=$(
    sed -nE 's/^[[:space:]]*active_task_id:[[:space:]]*"?([^"#]+)"?[[:space:]]*(#.*)?$/\1/p' "$STATE_FILE" \
      | head -1 \
      | sed -E 's/^[[:space:]]+|[[:space:]]+$//g'
  )
fi

[ -n "$EXECUTION_MODE" ] || EXECUTION_MODE="assisted"

case "$EXECUTION_MODE" in
  direct) exit 0 ;;
  assisted|governed) ;;
  *) block "Unknown execution mode '$EXECUTION_MODE'. Expected direct, assisted, or governed." ;;
esac

case "$ACTIVE_TASK_ID" in
  ""|"null"|"~")
    block "No active_task_id in $STATE_FILE. Run /coord then /analyze-task before editing source."
    ;;
esac

case "$ACTIVE_TASK_ID" in
  TASK-*) ;;
  *)
    block "Invalid active_task_id in $STATE_FILE: $ACTIVE_TASK_ID. Expected TASK-YYYYMMDD-NNN-slug."
    ;;
esac

ACTIVE_TASK=".maestro/work/tasks/$ACTIVE_TASK_ID"

if [ ! -d "$ACTIVE_TASK" ]; then
  block "Active task folder does not exist: $ACTIVE_TASK. Run /coord then /analyze-task before editing source."
fi

if [ "$EXECUTION_MODE" = "assisted" ]; then
  [ -f "$ACTIVE_TASK/task.yaml" ] || \
    block "Assisted source edits require $ACTIVE_TASK/task.yaml for cross-conversation continuity."
  exit 0
fi

TASK_ANALYSIS="$ACTIVE_TASK/task-analysis.yaml"

if [ ! -f "$TASK_ANALYSIS" ]; then
  block "Active task $ACTIVE_TASK has no task-analysis.yaml. Run /analyze-task first (R-000-06)."
fi

if grep -Eq '^[[:space:]]*requires_user_clarification:[[:space:]]*true' "$TASK_ANALYSIS"; then
  block "Active task requires user clarification; source edits are blocked until clarification is resolved."
fi

IS_FAST_TRACK=false
if grep -Eq '^[[:space:]]*fast_track:[[:space:]]*true' "$TASK_ANALYSIS"; then
  IS_FAST_TRACK=true
fi

# Every product-component source edit needs a context plan, including fast-track.
# Fast-track may skip the full implementation plan, not the context/evidence gate.
grep -Eq '^[[:space:]]*context_plan:' "$TASK_ANALYSIS" || \
  block "product-component source edits require task-analysis.yaml.context_plan before editing."

CONTEXT_CONFIDENCE=$(
  awk '
    /^[[:space:]]*context_plan:/ { in_context=1; next }
    in_context && /^[^[:space:]]/ { in_context=0 }
    in_context && /^[[:space:]]*confidence:/ {
      gsub(/"/, "", $0)
      sub(/^[^:]+:[[:space:]]*/, "", $0)
      sub(/[[:space:]]+#.*$/, "", $0)
      print $0
      exit
    }
  ' "$TASK_ANALYSIS" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g'
)

case "$CONTEXT_CONFIDENCE" in
  high|medium) ;;
  "") block "task-analysis.yaml.context_plan.confidence is missing." ;;
  *) block "task-analysis.yaml.context_plan.confidence is $CONTEXT_CONFIDENCE; require medium or high before source edits." ;;
esac

if awk '
    /^[[:space:]]*context_plan:/ { in_context=1; next }
    in_context && /^[^[:space:]]/ { in_context=0 }
    in_context && /^[[:space:]]*unresolved_context:[[:space:]]*\[\][[:space:]]*$/ { empty=1; next }
    in_context && /^[[:space:]]*unresolved_context:/ { in_unresolved=1; next }
    in_unresolved && /^[[:space:]]*[A-Za-z0-9_]+:/ { in_unresolved=0 }
    in_unresolved && /^[[:space:]]*-[[:space:]]+/ { found=1 }
    END { exit found ? 0 : 1 }
  ' "$TASK_ANALYSIS"; then
  block "task-analysis.yaml.context_plan.unresolved_context is not empty."
fi

if [ "$IS_FAST_TRACK" = true ]; then
  TASK_INTENT=$(
    sed -nE 's/^[[:space:]]*intent:[[:space:]]*"?([^"#]+)"?[[:space:]]*(#.*)?$/\1/p' "$TASK_ANALYSIS" \
      | head -1 \
      | sed -E 's/^[[:space:]]+|[[:space:]]+$//g'
  )
  case "$TASK_INTENT" in
    typo|comment|format|rename-local|docs-only|dependency-version-bump|config-value-tweak) ;;
    *) block "fast_track: true is only allowed for trivial intents; found intent: ${TASK_INTENT:-missing}." ;;
  esac
  grep -Eq '^[[:space:]]*fast_track_reason:[[:space:]]*"?[^"#]+' "$TASK_ANALYSIS" || \
    block "fast_track: true requires non-empty fast_track_reason."
fi

ARCH_REQUIRED=$(
  awk '
    /^[[:space:]]*architecture_review:/ { in_arch=1; next }
    in_arch && /^[^[:space:]]/ { in_arch=0 }
    in_arch && /^[[:space:]]*required:[[:space:]]*true/ { print "true"; exit }
  ' "$TASK_ANALYSIS"
)

if [ "$ARCH_REQUIRED" = "true" ]; then
  [ "$IS_FAST_TRACK" != true ] || \
    block "fast_track: true is not allowed when architecture_review.required is true."
  ARCH_REVIEW="$ACTIVE_TASK/architecture-review.yaml"
  [ -f "$ARCH_REVIEW" ] || block "task-analysis.yaml requires architecture review, but $ARCH_REVIEW is missing."
  grep -Eq '^[[:space:]]*decision:[[:space:]]*"?approved"?[[:space:]]*($|#)' "$ARCH_REVIEW" || \
    block "architecture-review.yaml must have decision: approved before source edits."
fi

if [ "$IS_FAST_TRACK" != true ]; then
  [ -f "$ACTIVE_TASK/implementation-plan.yaml" ] || \
    block "Standard implementation requires implementation-plan.yaml before source edits."
  [ -f "$ACTIVE_TASK/service-assignments.yaml" ] || \
    block "Standard implementation requires service-assignments.yaml before source edits."
else
  [ -f "$ACTIVE_TASK/service-assignments.yaml" ] || \
    block "Fast-track product-component edits require lightweight service-assignments.yaml before source edits."
fi

REGISTRY_FILE=".maestro/registry/agents.yaml"
if ! scope_allows_file "$REL_PATH" "$REGISTRY_FILE"; then
  block "No active coder in $REGISTRY_FILE allows writes to $REL_PATH, or the path is forbidden by that coder scope."
fi

exit 0
