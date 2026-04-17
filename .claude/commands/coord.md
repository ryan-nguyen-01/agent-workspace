# /coord

## Purpose

Main entrypoint for any user request.

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
1. Read .claude/workflow.md.
2. Check Project Brain and Agent Registry.
3. If Project Brain is missing or stale, route to /onboard.
4. If coder agents are needed but not active, ask user approval and route to /create-coders.
5. If input is a task, route to /analyze-task.
6. If task is analyzed but not planned, route to /plan-dev.
7. If task is planned, route to /dev.
8. If task is DEV_DONE, route to /handoff-qc.
9. If task is QC_READY or QC_TESTING, route to /qc.
10. If bug exists, route to /bug.
11. If task is done, route to /sync-memory.
```

## Stop conditions

```text
Missing Project Brain
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
```
