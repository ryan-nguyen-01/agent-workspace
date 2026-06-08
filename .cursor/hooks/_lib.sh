#!/usr/bin/env bash
# Shared helpers for Cursor hooks in maestro.
# Sourced by other .cursor/hooks/*.sh scripts.
#
# Provides: read_stdin, json_field <key>
# Strategy: use `jq` when available (robust on nested/escaped JSON); fall back
# to grep+sed for simple top-level keys when jq is missing.

# init_stdin — MUST be called once at the top of each hook script BEFORE any
# json_field call. Reads all of stdin into _HOOK_STDIN and exports it so child
# subshells (e.g. $(json_field foo)) inherit the cached payload. Without this,
# only the first json_field call would receive stdin and later calls would hang
# or return empty (stdin is a stream, drained on first read).
init_stdin() {
  _HOOK_STDIN=$(cat)
  export _HOOK_STDIN
}

# json_field <key> — print the string value of a top-level field from _HOOK_STDIN.
# Echoes empty string if not found. Handles top-level fields plus the common
# Cursor pattern of `tool_input.<key>` nesting (e.g. tool_input.file_path).
#
# Examples (with _HOOK_STDIN = '{"tool_name":"Edit","file_path":"src/a.ts"}'):
#   json_field tool_name  →  Edit
#   json_field file_path  →  src/a.ts
json_field() {
  local key="$1"
  : "${_HOOK_STDIN:?init_stdin must be called before json_field}"
  if command -v jq >/dev/null 2>&1; then
    # jq path: robust against nested objects, escaped quotes, whitespace.
    # We try top-level first, then `tool_input.<key>` (Cursor often nests there).
    local v
    v=$(printf '%s' "$_HOOK_STDIN" | jq -r --arg k "$key" '
      if has($k) then .[$k] // ""
      elif (.tool_input // null) and (.tool_input | type == "object") and (.tool_input | has($k))
        then .tool_input[$k] // ""
      else ""
      end
    ' 2>/dev/null)
    printf '%s' "$v"
  else
    # Fallback: grep + sed for top-level string fields only.
    # Limitations: does not handle escaped quotes inside values, unicode escapes,
    # or deeply nested keys. Sufficient for the basic Cursor hook payloads we use.
    printf '%s' "$_HOOK_STDIN" \
      | grep -oE "\"${key}\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" \
      | head -1 \
      | sed -E "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"([^\"]*)\".*/\1/"
  fi
}

# Truthy if `jq` is present on the system. Hooks can use this to log a warning
# (or to skip JSON-validation paths that depend on jq features).
have_jq() {
  command -v jq >/dev/null 2>&1
}
