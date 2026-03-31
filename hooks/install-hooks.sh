#!/bin/bash
# Install agent-platform git hooks into a project
# Usage: bash install-hooks.sh [/path/to/project]

PROJECT_DIR="${1:-$(pwd)}"
HOOKS_SRC="$(cd "$(dirname "$0")" && pwd)"
GIT_HOOKS_DIR="$PROJECT_DIR/.git/hooks"

if [ ! -d "$PROJECT_DIR/.git" ]; then
  echo "Error: $PROJECT_DIR is not a git repository."
  exit 1
fi

echo "Installing agent-platform hooks into: $PROJECT_DIR"

for hook in post-commit post-merge; do
  SRC="$HOOKS_SRC/$hook"
  DEST="$GIT_HOOKS_DIR/$hook"

  if [ -f "$DEST" ]; then
    # Append to existing hook instead of overwriting
    echo "" >> "$DEST"
    echo "# --- agent-platform ---" >> "$DEST"
    cat "$SRC" | tail -n +3 >> "$DEST"
    echo "  Updated existing $hook hook (appended)"
  else
    cp "$SRC" "$DEST"
    chmod +x "$DEST"
    echo "  Installed $hook hook"
  fi
done

echo ""
echo "Done. Hooks installed at: $GIT_HOOKS_DIR"
echo "Verify: ls -la $GIT_HOOKS_DIR"
