# /status

## Purpose

Report current workflow state, brain freshness, generated coders, and task status.

## Responsible agent

coordinator

## Required rules

```text
00-core-rules.md
01-project-brain-rules.md
12-artifact-contracts.md
```

## Workflow

```text
1. Read workflow-state.yaml.
2. Read project-brain.yaml freshness.
3. Read service-catalog.yaml summary.
4. Read agent-registry.yaml summary.
5. If task id is provided, read task artifacts status.
6. Report next recommended command.
```

## Output format

```yaml
workflow_state: "<state>"
project_brain: "fresh|stale|missing"
services_detected: 0
active_coder_agents: 0
task_state: null
next_command: "/onboard|/create-coders|/analyze-task|..."
```
