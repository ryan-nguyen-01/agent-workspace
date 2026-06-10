---
description: "maestro /create-coders — Generate scoped component coder agents after user approval."
argument-hint: "[request or args]"
---

You are running the maestro `/create-coders` workflow command inside Codex.

Follow `.codex/AGENTS.md` (or `AGENTS.md`) routing and the framework rules. Route every
request through the coordinator model; do not bypass approval gates, security/secret rules,
or the task-analysis source-edit gate. If the maestro framework files
(`.maestro/engine/`, `.maestro/registry/`, `.maestro/knowledge/`, `.maestro/work/`, `.maestro/runtime/`, `.claude/commands/create-coders.md`) are present, defer to them as the
authoritative contract — this prompt is a portable mirror.

User input for this command: $ARGUMENTS

---
## Command contract (mirrored from .claude/commands/create-coders.md)

# /create-coders

## Purpose

Generate scoped component coder agents after user approval.

## Responsible agent

agent-factory

## Required rules

```text
00-core-rules.md
03-agent-factory-rules.md
11-approval-gates.md
12-artifact-contracts.md
14-skill-composition-rules.md
```

## Preconditions

```text
Project Knowledge exists
Component Registry exists
Test Policy exists
User approved coder creation
```

## Workflow

```text
1. Read approved component list.
2. Read component knowledge for each component.
3. Create coder-<component>.agent.md from template.
4. Set allowed_read_paths, allowed_write_paths, forbidden_paths, test policy, and escalation rules.
5. Update .maestro/registry/agents.yaml.
6. Return AGENTS_READY to Coordinator.
```

## Stop conditions

```text
No user approval
Missing component knowledge
Unknown test policy with no approved default
Overbroad write scope
```

---

## Stack skill loading

`/create-coders` must ask Agent Factory to load `.maestro/registry/skills.yaml` and map detected component stacks to active coder skills. `.maestro/engine/docs/external-skills.md` is supporting documentation, not the machine-readable source of truth. Do not create a generic coder with all skills attached. Each generated coder must include a compact selected-skill list and an explicit skipped-skill list.

Skills marked `requires_user_approval: true` must not be attached automatically.
