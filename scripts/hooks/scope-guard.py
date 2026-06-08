#!/usr/bin/env python3
"""PreToolUse(Write|Edit) hook: enforce the source-edit workflow gate + coder scope.

Ports .cursor/hooks/check-task-analysis.sh to the Claude Code adapter. Turns the
prompt-based scope rule (R-006) into a hard guardrail:

  - Only gates likely APPLICATION source (services/**, src/**, app/**, tests/**, ...).
    Framework files (.maestro/engine/**, .claude/**, scripts/**, docs) are NOT gated, so
    framework maintenance is unaffected.
  - direct mode allows fast user-driven development without workflow artifacts.
  - assisted mode requires a task manifest but not the governed artifact pipeline.
  - governed mode requires task-analysis.yaml + context_plan (R-000-06),
    architecture-review approval when required, and implementation/service-assignment artifacts.
  - Requires that some ACTIVE coder in agents.yaml allows the path and does
    not forbid it (R-006).

Profiles:
  minimal  : disabled (no scope gating).
  standard : full gating, fail-closed on violation (default; mirrors Cursor failClosed:true).
  strict   : same as standard.

Disable with MAESTRO_DISABLED_HOOKS=scope-guard.
"""

from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lib  # noqa: E402

HOOK_ID = "scope-guard"

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

# Gate only likely application source. Broader than services/** because applied
# workspaces may be single-repo apps, CLIs, libs, data jobs, or Go/Rust layouts.
SOURCE_DIR_TOKENS = (
    "services", "src", "app", "packages", "apps", "cmd", "internal", "pkg",
    "lib", "libs", "crates", "notebooks", "dags", "jobs", "pipelines", "tests",
)
VENDOR_TOKENS = ("node_modules", ".git", "dist", "build", ".next", "__pycache__")

FAST_TRACK_INTENTS = {
    "typo", "comment", "format", "rename-local", "docs-only",
    "dependency-version-bump", "config-value-tweak",
}


def is_source_path(file_path: str) -> bool:
    parts = file_path.replace("\\", "/").split("/")
    if any(tok in parts for tok in VENDOR_TOKENS):
        return False
    return any(tok in parts for tok in SOURCE_DIR_TOKENS)


def path_matches(path: str, pattern: str) -> bool:
    pattern = pattern[2:] if pattern.startswith("./") else pattern
    if not pattern:
        return False
    if fnmatch.fnmatch(path, pattern):
        return True
    # Treat literal **/foo as also matching foo at repository root.
    if pattern.startswith("**/"):
        root_pattern = pattern[3:]
        if fnmatch.fnmatch(path, root_pattern):
            return True
    return False


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def yaml_scalar(text: str, key: str) -> str:
    m = re.search(rf'^[ \t]*{re.escape(key)}:[ \t]*"?([^"#\n]+)"?', text, re.M)
    return m.group(1).strip() if m else ""


def block_section_has_items(text: str, key: str) -> bool:
    """True if a `key:` mapping/list under context_plan has at least one `- item`."""
    # context_plan.unresolved_context: [] (empty inline) -> no items
    if re.search(rf'^[ \t]*{re.escape(key)}:[ \t]*\[\][ \t]*$', text, re.M):
        return False
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.match(rf'^[ \t]*{re.escape(key)}:[ \t]*$', line):
            base_indent = len(line) - len(line.lstrip())
            for nxt in lines[i + 1:]:
                if not nxt.strip():
                    continue
                indent = len(nxt) - len(nxt.lstrip())
                if indent <= base_indent:
                    break
                if nxt.lstrip().startswith("- "):
                    return True
            return False
    return False


def scope_allows_file(rel_path: str, registry_text: str) -> bool:
    """Replicate the indent-based scan of agents.yaml active coders.

    Layout:
      agents:
        - id: "coder-x"
          status: "active"
          permissions:
            allowed_write_paths:
              - "services/x/**"
            forbidden_paths:
              - "..."
    """
    scope_allowed = False
    agent_seen = False
    status = ""
    allowed = False
    forbidden = False
    section = ""

    def finalize():
        nonlocal scope_allowed
        if agent_seen and status == "active" and allowed and not forbidden:
            scope_allowed = True

    for raw in registry_text.splitlines():
        if re.match(r"^  - id:", raw):
            finalize()
            agent_seen = True
            status = ""
            allowed = False
            forbidden = False
            section = ""
            continue
        if not agent_seen:
            continue
        if re.match(r"^    status:", raw):
            status = re.sub(r'^[^:]+:[ \t]*"?([^"#]*)"?.*$', r"\1", raw).strip()
            continue
        if re.match(r"^      allowed_write_paths:", raw):
            section = "allow"
            continue
        if re.match(r"^      forbidden_paths:", raw):
            section = "forbid"
            continue
        if re.match(r"^      [A-Za-z0-9_]+:", raw):
            section = ""
            continue
        if section and re.match(r"^        - ", raw):
            pattern = raw.strip()[2:].strip().strip('"').strip("'")
            if path_matches(rel_path, pattern):
                if section == "allow":
                    allowed = True
                elif section == "forbid":
                    forbidden = True
    finalize()
    return scope_allowed


def main() -> int:
    if _lib.hook_disabled(HOOK_ID) or _lib.profile() == "minimal":
        return 0
    payload = _lib.read_payload()
    if _lib.tool_name(payload) not in EDIT_TOOLS:
        return 0
    file_path = _lib.field(payload, "file_path")
    if not file_path:
        return 0
    if not is_source_path(file_path):
        return 0  # framework / non-app files are not gated

    root = _lib.project_dir(payload)
    rel = _lib.rel_path(file_path, root)

    state = read_text(root / ".maestro/runtime/workflow-state.yaml")
    execution_mode = yaml_scalar(state, "active_execution_mode")
    if execution_mode in ("", "null", "~"):
        execution_mode = yaml_scalar(state, "default_execution_mode") or "assisted"
    if execution_mode == "direct":
        return 0

    task_id = yaml_scalar(state, "active_task_id")
    if task_id in ("", "null", "~"):
        _lib.block("No active_task_id in workflow-state.yaml. Run /coord then /analyze-task before editing source.")
    if not task_id.startswith("TASK-"):
        _lib.block(f"Invalid active_task_id: {task_id}. Expected TASK-YYYYMMDD-NNN-slug.")

    task_dir = root / ".maestro/work/tasks" / task_id
    if not task_dir.is_dir():
        _lib.block(f"Active task folder missing: .maestro/work/tasks/{task_id}. Run /analyze-task first.")

    if execution_mode == "assisted":
        if not (task_dir / "task.yaml").is_file():
            _lib.block("Assisted source edits require task.yaml so work can continue across conversations.")
        return 0

    if execution_mode != "governed":
        _lib.block(f"Unknown execution mode '{execution_mode}'. Expected direct, assisted, or governed.")

    ta_path = task_dir / "task-analysis.yaml"
    if not ta_path.is_file():
        _lib.block(f"Active task {task_id} has no task-analysis.yaml. Run /analyze-task first (R-000-06).")
    ta = read_text(ta_path)

    if re.search(r"^[ \t]*requires_user_clarification:[ \t]*true", ta, re.M):
        _lib.block("Active task requires user clarification; source edits blocked until resolved.")

    if not re.search(r"^[ \t]*context_plan:", ta, re.M):
        _lib.block("product-component source edits require task-analysis.yaml.context_plan before editing.")

    confidence = yaml_scalar(ta, "confidence")
    if confidence not in ("high", "medium"):
        _lib.block(f"context_plan.confidence is '{confidence or 'missing'}'; require medium or high before source edits.")

    if block_section_has_items(ta, "unresolved_context"):
        _lib.block("task-analysis.yaml.context_plan.unresolved_context is not empty.")

    is_fast_track = bool(re.search(r"^[ \t]*fast_track:[ \t]*true", ta, re.M))
    if is_fast_track:
        intent = yaml_scalar(ta, "intent")
        if intent not in FAST_TRACK_INTENTS:
            _lib.block(f"fast_track: true only allowed for trivial intents; found intent: {intent or 'missing'}.")
        if not re.search(r'^[ \t]*fast_track_reason:[ \t]*"?[^"#\n]+', ta, re.M):
            _lib.block("fast_track: true requires non-empty fast_track_reason.")

    arch_required = bool(re.search(
        r"architecture_review:\s*(?:#.*)?\n(?:[ \t].*\n)*?[ \t]*required:[ \t]*true", ta))
    if arch_required:
        if is_fast_track:
            _lib.block("fast_track: true is not allowed when architecture_review.required is true.")
        ar = read_text(task_dir / "architecture-review.yaml")
        if not ar:
            _lib.block("task-analysis requires architecture review, but architecture-review.yaml is missing.")
        if not re.search(r'^[ \t]*decision:[ \t]*"?approved"?[ \t]*(?:$|#)', ar, re.M):
            _lib.block("architecture-review.yaml must have decision: approved before source edits.")

    if not is_fast_track:
        if not (task_dir / "implementation-plan.yaml").is_file():
            _lib.block("Standard implementation requires implementation-plan.yaml before source edits.")
        if not (task_dir / "service-assignments.yaml").is_file():
            _lib.block("Standard implementation requires service-assignments.yaml before source edits.")
    else:
        if not (task_dir / "service-assignments.yaml").is_file():
            _lib.block("Fast-track product-component edits require lightweight service-assignments.yaml before source edits.")

    registry = read_text(root / ".maestro/registry/agents.yaml")
    if not scope_allows_file(rel, registry):
        _lib.block(f"No active coder in .maestro/registry/agents.yaml allows writes to {rel}, or it is forbidden by that coder scope (R-006).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
