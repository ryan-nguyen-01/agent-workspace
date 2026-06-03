---
description: "agent-workspace /coord — Main entrypoint for any user request."
argument-hint: "[request or args]"
---

You are running the agent-workspace `/coord` workflow command inside Codex.

Follow `.codex/AGENTS.md` (or `AGENTS.md`) routing and the framework rules. Route every
request through the coordinator model; do not bypass approval gates, security/secret rules,
or the task-analysis source-edit gate. If the agent-workspace framework files
(`.agent/`, `.runtime/`, `.claude/commands/coord.md`) are present, defer to them as the
authoritative contract — this prompt is a portable mirror.

User input for this command: $ARGUMENTS

---
## Command contract (mirrored from .claude/commands/coord.md)

# /coord

## Purpose

Main entrypoint for any user request.

All requests must pass through this command before any other workflow command is executed.

## Responsible agent

coordinator

## Required rules

```text
00-core-rules.md
01-project-brain-rules.md
11-approval-gates.md
12-artifact-contracts.md
13-security-secret-rules.md
```

## Workflow

```text
1. Read .agent/workflow.md.
2. Classify target_scope and detect explicit command intents.
3. Check Project Brain and Agent Registry when needed for applied-service work.
4. Validate current state transition and required artifacts.
5. If Project Brain is missing or stale for applied-service work, route to /onboard.
6. If coder agents are needed but not active, ask user approval and route to /create-coders.
8. If input is a task, route to /analyze-task.
9. If task is analyzed but not planned, route to /plan-dev.
10. If task is planned, route to /dev.
11. If task is DEV_DONE, route to /handoff-qc. The canonical handoff stays inside .runtime/tasks/<task_id>/qc-handoff.md.
12. If task is QC_READY or QC_TESTING, route to /qc.
13. If bug exists, route to /bug.
14. If task is done, route to /sync-memory.
```

If any gate fails, coordinator must deny transition and return missing artifacts or approval requirements.

## Stop conditions

```text
Missing Project Brain for applied-service work
Missing user approval
Missing required artifact
Blocker bug
Security/secret risk
```

## Output format

```yaml
state: "<workflow-state>"
responsible_agent: "coordinator"
next_command: "<command>"
required_artifacts: []
blocked: false
reason: null
policy_decision: "allow|deny|needs_user_approval"
missing_artifacts: []
```
