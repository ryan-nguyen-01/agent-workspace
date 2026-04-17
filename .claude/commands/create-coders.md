# /create-coders

## Purpose

Generate scoped service coder agents after user approval.

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
Project Brain exists
Service Catalog exists
Test Policy exists
User approved coder creation
```

## Workflow

```text
1. Read approved service list.
2. Read service brain for each service.
3. Create coder-<service>.agent.md from template.
4. Set allowed_read_paths, allowed_write_paths, forbidden_paths, test policy, and escalation rules.
5. Update agent-registry.yaml.
6. Return AGENTS_READY to Coordinator.
```

## Stop conditions

```text
No user approval
Missing service brain
Unknown test policy with no approved default
Overbroad write scope
```

---

## Stack skill loading

`/create-coders` must ask Agent Factory to load `.claude/context/skill-registry.yaml` and map detected service stacks to active coder skills. `.claude/docs/external-skills.md` is supporting documentation, not the machine-readable source of truth. Do not create a generic coder with all skills attached. Each generated coder must include a compact selected-skill list and an explicit skipped-skill list.

Skills marked `requires_user_approval: true` must not be attached automatically.
