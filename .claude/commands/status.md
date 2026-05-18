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
1. Read .runtime/context/workflow-state.yaml.
2. Read .runtime/context/index.yaml freshness.
3. Read .runtime/context/project-brain.yaml freshness only if needed.
4. Read .runtime/context/service-catalog.yaml summary.
5. Read .runtime/context/agent-registry.yaml summary.
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
