#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

DRY_RUN=false
ASSUME_YES=false

usage() {
  cat <<'EOF'
Usage: scripts/remove-workspace-git.sh [--dry-run] [--yes]

Detach the maestro root from Git by removing only the root .git entry.
This does not remove Git metadata inside services/<service-name>/ repositories.

Options:
  --dry-run   Show what would be removed without changing files.
  --yes       Skip the interactive confirmation.
  -h, --help  Show this help.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      ;;
    --yes)
      ASSUME_YES=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if [ ! -e ".git" ]; then
  echo "maestro root is already detached: .git does not exist."
  exit 0
fi

echo "Workspace root: $ROOT_DIR"
echo "Target to remove: $ROOT_DIR/.git"

if [ -d "services" ]; then
  SERVICE_GIT_COUNT=$(
    find services -mindepth 2 -maxdepth 2 -name .git -print 2>/dev/null | wc -l | tr -d ' '
  )
  echo "Service Git metadata found: $SERVICE_GIT_COUNT"
  echo "Service repositories under services/ will not be changed."
fi

if [ "$DRY_RUN" = true ]; then
  echo "Dry run only. No files were removed."
  exit 0
fi

if [ "$ASSUME_YES" != true ]; then
  echo
  echo "This removes Git metadata for maestro itself."
  echo "After this, run git commands from each services/<service-name>/ repo instead."
  printf "Type 'remove root .git' to continue: "
  read -r CONFIRM
  if [ "$CONFIRM" != "remove root .git" ]; then
    echo "Cancelled."
    exit 1
  fi
fi

rm -rf -- ".git"
echo "Removed root .git. maestro is now a plain coordination folder."
