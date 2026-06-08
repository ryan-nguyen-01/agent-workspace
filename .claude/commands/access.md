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
/access status     Report current access_mode + the fullaccess allowlist state
/access full       fullaccess — run terminal + read/edit files without a per-call permission prompt
/access guarded    guarded (default) — remove the fullaccess allowlist; tools prompt as normal
```

fullaccess uses a permission **allowlist** (`permissions.allow`), NOT `bypassPermissions` /
`--dangerously-skip-permissions`. The bypass mode is refused by Claude Code under root/sudo; the
allowlist works for all users (including root) and keeps the hooks active.

## Behavior

```text
1. Run: python3 scripts/access-mode.py --status | --set full | --set guarded
2. The script writes:
   - .claude/settings.json  permissions.allow  (grants Bash + file tools for full, removed for guarded;
     also strips any unsafe legacy permissions.defaultMode=bypassPermissions)
   - .maestro/runtime/workflow-state.yaml  access_mode  (for /status visibility)
3. A permission-mode change applies to NEW sessions; for the current session use the harness
   permission UI (Shift+Tab) if immediate effect is needed.
```

## What fullaccess does NOT change

```text
- Workflow approval gates (R-011): create coders, Task Analysis -> Coder Leader, skip QC,
  downgrade blocker, expand scope, workflow policy/state-machine changes — the agent still ASKS for each.
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
