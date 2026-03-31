#!/bin/bash
# Enable versioned git hooks for this repo (team-safe)
# Usage: bash hooks/enable-githooks.sh

set -euo pipefail

if [ ! -d ".git" ]; then
  echo "Error: must run at a git repo root (no .git found)."
  exit 1
fi

git config core.hooksPath .githooks
chmod +x .githooks/post-commit .githooks/post-merge || true

echo "Done. Enabled versioned hooks via core.hooksPath=.githooks"
echo "Verify: git config core.hooksPath"

