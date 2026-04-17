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
1. Read task.yaml or available task artifacts.
2. Determine current state.
3. Check required artifact for the next transition.
4. Route to the next command.
5. If artifacts are missing, route to the responsible command to recreate them.
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
