# /access

## Purpose

Switch the **harness tool-execution permission posture** (`access_mode`) — whether ordinary tool
calls (terminal commands, file reads/edits) prompt for permission each time.

`access_mode` is ONLY about per-tool permission prompts. It does **not** change the workflow: every
R-011 approval gate still asks, and the scope/secret/destructive hooks still block (R-011-14).

## Responsible agent

coordinator

## Usage

```text
/access status     Report current access_mode + settings permissions.defaultMode
/access full       fullaccess — run terminal + read/edit files without a per-call permission prompt
/access guarded    guarded (default) — tool calls follow .claude/settings.json allowlist
```

## Behavior

```text
1. Run: python3 scripts/access-mode.py --status | --set full | --set guarded
2. The script writes:
   - .claude/settings.json  permissions.defaultMode  (bypassPermissions for full, removed for guarded)
   - .runtime/context/workflow-state.yaml  access_mode  (for /status visibility)
3. A permission-mode change applies to NEW sessions; for the current session use the harness
   permission UI (Shift+Tab) if immediate effect is needed.
```

## What fullaccess does NOT change

```text
- Workflow approval gates (R-011): create coders, Task Analysis -> Coder Leader, skip QC,
  downgrade blocker, expand scope, switch distribution_mode — the agent still ASKS for each.
- scope-guard / secret-guard / destructive-guard hooks — still block (R-006, R-013, R-011-07).
- Production deployment and irreversible data actions — still require explicit user approval.
```

## Must not

```text
Do not treat fullaccess as permission to bypass workflow gates, hooks, or destructive/production approval.
Do not switch access_mode without explicit user intent (R-011-14).
```

## Required rules

```text
00-core-rules.md
11-approval-gates.md
13-security-secret-rules.md
```
