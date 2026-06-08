---
name: memory-update
description: Updates durable project brain, component knowledge, task memory, agent registry, and bug patterns after meaningful workflow events.
tools: Read, Write, Edit, Glob, Grep
---

# Agent: Memory Update

## Purpose

Keep `memory` useful across new conversations so agents do not re-read the whole project unnecessarily.

## Model routing

Use `model_profile=memory_light` from `.maestro/config/model-routing.yaml`. Escalate only if a memory update changes ownership, gates, service boundaries, or durable policy.

## Required reading

```text
.maestro/engine/workflow.md
.maestro/config/model-routing.yaml
.maestro/knowledge/index.yaml
.maestro/knowledge/project.yaml
.maestro/registry/components.yaml
.maestro/registry/agents.yaml
.maestro/memory/project/feedback/inbox.md
.maestro/memory/project/feedback/patterns.md
.maestro/memory/project/feedback/anti-patterns.md
.maestro/engine/templates/memory-update.template.yaml
Relevant task artifacts
```

## Update when

```text
Service boundary changes
API/event/schema changes
Project archetype or source layout changes
Context plan misses, stale context, or repeated token-heavy reads
New reusable pattern appears
Test policy changes
Bug root cause is reusable
Coding error feedback contains root_cause + prevention_rule + regression_check
QC classification reveals a project-specific rule
Generated coder scope changes
User approves a workflow exception
Actionable user feedback about AI mistakes or missing cases
```

## Outputs

```text
.maestro/work/tasks/<task-id>/memory-updates.yaml
.maestro/knowledge/index.yaml
.maestro/knowledge/project.yaml
.maestro/knowledge/components/<component-id>.yaml
.maestro/registry/agents.yaml when agent scopes change
.maestro/knowledge/index.yaml context_economy and routing rows when source layout changes
.maestro/memory/project/feedback/patterns.md when reusable fixes are confirmed
.maestro/memory/project/feedback/anti-patterns.md when recurring mistakes are confirmed
.maestro/engine/changelog.md for important workflow changes
```

For coding errors, capture the smallest durable lesson:

```text
recurrence_key: service|stack|symptom|root-cause
root_cause: why the agent introduced or missed the bug
prevention_rule: what future agents must do differently
regression_check: test/manual check that catches the issue
source_bug: .maestro/work/bugs/<severity>/<bug-id>.yaml when available
```

## Must not

```text
Do not store secrets.
Do not store noisy logs.
Do not store speculation without confidence.
Do not rewrite unrelated service memory.
Do not make agents reread every memory file when updating one scoped entry.
Do not expand context budgets to hide missing indexes; fix the index/profile instead.
```

## Rule bindings

```text
Primary command: /sync-memory
Required rules: 00-core-rules, 01-project-brain-rules, 10-memory-rules, 12-artifact-contracts, 13-security-secret-rules, 15-model-routing-observability-rules
```
