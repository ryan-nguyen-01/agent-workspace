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
1. Read .maestro/engine/workflow.md.
2. Classify target_scope and detect explicit command intents.
3. Check Project Knowledge and Agent Registry when needed for product-component work.
4. Validate current state transition and required artifacts.
5. If Project Knowledge is missing or stale for product-component work, route to /onboard.
6. If coder agents are needed but not active, ask user approval and route to /create-coders.
8. If input is a task, route to /analyze-task.
9. If task is analyzed but not planned, route to /plan-dev.
10. If task is planned, route to /dev.
11. If task is DEV_DONE, route to /handoff-qc. The canonical handoff stays inside .maestro/work/tasks/<task_id>/qc-handoff.md.
12. If task is QC_READY or QC_TESTING, route to /qc.
13. If bug exists, route to /bug.
14. If task is done, route to /sync-memory.
```

If any gate fails, coordinator must deny transition and return missing artifacts or approval requirements.

## Stop conditions

```text
Missing Project Knowledge for product-component work
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
