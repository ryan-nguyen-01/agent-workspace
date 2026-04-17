# /plan-dev

## Purpose

Create implementation plan and service assignments for an analyzed task.

## Responsible agent

coder-leader

## Required rules

```text
00-core-rules.md
05-coder-leader-rules.md
06-service-coder-rules.md
12-artifact-contracts.md
14-skill-composition-rules.md
```

## Preconditions

```text
task-analysis.yaml exists
agent-registry.yaml has active coder agents for impacted services
```

## Workflow

```text
1. Read task-analysis.yaml.
2. Match impacted services to active coders.
3. Define implementation sequence.
4. Define contract and integration checkpoints.
5. Write implementation-plan.yaml.
6. Write service-assignments.yaml.
```

## Stop conditions

```text
No active coder for impacted service
Task requires forbidden scope
Cross-service contract is ambiguous
```
