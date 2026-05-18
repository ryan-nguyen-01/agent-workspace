#!/usr/bin/env bash
# afterFileEdit hook: when .runtime/context/ files change, mark project brain
# freshness as stale so Coordinator surfaces it at next session.
# Schema per https://cursor.com/docs/agent/hooks.
#
# Scope: Cursor IDE only.
# Input  : JSON on stdin with "file_path" + "edits"
# Output : exit 0 (informational, never blocks)

set -u

# shellcheck source=./_lib.sh
. "$(dirname "$0")/_lib.sh"
init_stdin

FILE_PATH=$(json_field file_path)
[ -z "$FILE_PATH" ] && exit 0

case "$FILE_PATH" in
  *".runtime/context/"*) ;;
  *) exit 0 ;;
esac

cd "${CURSOR_PROJECT_DIR:-.}" || exit 0
BRAIN=".runtime/context/project-brain.yaml"
[ ! -f "$BRAIN" ] && exit 0

grep -q '^[[:space:]]*last_drift_check_result:[[:space:]]*"stale"' "$BRAIN" && exit 0

# BSD/GNU portable sed. Use [[:space:]] instead of \s.
if [ "$(uname)" = "Darwin" ]; then
  sed -i '' -E 's/^([[:space:]]*last_drift_check_result:[[:space:]]*)"(fresh|unknown)"$/\1"stale"/' "$BRAIN"
else
  sed -i -E 's/^([[:space:]]*last_drift_check_result:[[:space:]]*)"(fresh|unknown)"$/\1"stale"/' "$BRAIN"
fi

if grep -q '^[[:space:]]*last_drift_check_result:[[:space:]]*"stale"' "$BRAIN"; then
  echo "ℹ️  [agent-workspace] Brain marked stale after edit to $FILE_PATH. Coordinator will surface this at next session." >&2
fi
exit 0
