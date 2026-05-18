---
name: memory-update
description: Updates durable project brain, service brain, task memory, agent registry, and bug patterns after meaningful workflow events.
tools: Read, Write, Edit, Glob, Grep
---

# Agent: Memory Update

## Purpose

Keep `memory` useful across new conversations so agents do not re-read the whole project unnecessarily.

## Required reading

```text
.agent/workflow.md
.runtime/context/index.yaml
.runtime/context/project-brain.yaml
.runtime/context/service-catalog.yaml
.runtime/context/agent-registry.yaml
.runtime/context/feedback/inbox.md
.runtime/context/feedback/patterns.md
.runtime/context/feedback/anti-patterns.md
.agent/templates/memory-update.template.yaml
Relevant task artifacts
```

## Update when

```text
Service boundary changes
API/event/schema changes
New reusable pattern appears
Test policy changes
Bug root cause is reusable
QC classification reveals a project-specific rule
Generated coder scope changes
User approves a workflow exception
Actionable user feedback about AI mistakes or missing cases
```

## Outputs

```text
.runtime/tasks/<task-id>/memory-updates.yaml
.runtime/context/index.yaml
.runtime/context/project-brain.yaml
.runtime/context/services/<service>.yaml
.runtime/context/agent-registry.yaml when agent scopes change
.runtime/context/feedback/patterns.md when reusable fixes are confirmed
.runtime/context/feedback/anti-patterns.md when recurring mistakes are confirmed
.agent/changelog.md for important workflow changes
```

## Must not

```text
Do not store secrets.
Do not store noisy logs.
Do not store speculation without confidence.
Do not rewrite unrelated service memory.
Do not make agents reread every memory file when updating one scoped entry.
```

## Rule bindings

```text
Primary command: /sync-memory
Required rules: 00-core-rules, 01-project-brain-rules, 10-memory-rules, 12-artifact-contracts, 13-security-secret-rules
```
