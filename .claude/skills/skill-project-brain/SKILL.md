---
name: skill-project-brain
description: Manage reusable project brain files so agents can resume work across conversations without rescanning the whole repository.
---

# Skill: Project Brain

Use when checking, creating, refreshing, or querying `.claude/context` memory.

## Core files

```text
.claude/context/project-brain.yaml
.claude/context/service-catalog.yaml
.claude/context/agent-registry.yaml
.claude/context/test-policy.yaml
.claude/context/workflow-state.yaml
.claude/context/services/<service>.yaml
```

## Rules

```text
Read project brain before scanning source.
Prefer partial refresh over full rescan when stale areas are known.
Record confidence for inferred facts.
Never store secrets, raw tokens, passwords, or long logs.
Link durable facts to source task or onboarding evidence.
```

## Staleness triggers

```text
Workspace/package config changed
Service folder added, removed, or moved
Framework or package manager changed
API/event/schema contract changed
Test policy changed
Generated coder scope changed
```
