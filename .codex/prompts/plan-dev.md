---
description: "agent-workspace /plan-dev — Create implementation plan and service assignments for an analyzed task."
argument-hint: "[request or args]"
---

You are running the agent-workspace `/plan-dev` workflow command inside Codex.

Follow `.codex/AGENTS.md` (or `AGENTS.md`) routing and the framework rules. Route every
request through the coordinator model; do not bypass approval gates, security/secret rules,
or the task-analysis source-edit gate. If the agent-workspace framework files
(`.agent/`, `.runtime/`, `.claude/commands/plan-dev.md`) are present, defer to them as the
authoritative contract — this prompt is a portable mirror.

User input for this command: $ARGUMENTS

---
## Command contract (mirrored from .claude/commands/plan-dev.md)

# /plan-dev

## Purpose

Create implementation plan and service assignments for an analyzed task.

This command creates the standard applied-service plan. Applied-service fast-track may use it only to create a lightweight service-assignments.yaml; framework-maintenance fast-track skips it entirely.

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
task-analysis.yaml.context_plan exists for applied-service tasks
context_plan.confidence is medium or high
agent-registry.yaml has active coder agents for impacted services
```

## Workflow

```text
1. Read task-analysis.yaml.
2. Read and apply context_plan before opening source files.
3. Match impacted services to active coders.
4. Define implementation sequence.
5. Define contract and integration checkpoints.
6. For standard tasks, write implementation-plan.yaml, including any approved context expansion.
7. Write service-assignments.yaml with only the context each coder needs. For fast-track, this may be a lightweight assignment_note + context_pack.
```

## Stop conditions

```text
No active coder for impacted service
context_plan missing, low confidence, or unresolved service/test/contract gaps
Task requires forbidden scope
Cross-service contract is ambiguous
```
