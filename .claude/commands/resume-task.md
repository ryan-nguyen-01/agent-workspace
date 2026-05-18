# /resume-task

## Purpose

Resume a task from its current state without rediscovering context from scratch.

## Responsible agent

coordinator

## Required rules

```text
00-core-rules.md
01-project-brain-rules.md
11-approval-gates.md
12-artifact-contracts.md
```

## Workflow

```text
1. Resolve task_id and task folder under .runtime/tasks/<task_id>/.
2. Read task.yaml first; if missing, reconstruct only from artifacts in that same folder.
3. Read task-updates.yaml when present for state/artifact history.
4. Determine current state.
5. Check required artifact for the next transition.
6. Route to the next command.
7. If artifacts are missing, route to the responsible command to recreate them.
```

## Output format

```yaml
task_id: "<task-id>"
current_state: "<state>"
next_command: "<command>"
missing_artifacts: []
blocked: false
reason: null
```
