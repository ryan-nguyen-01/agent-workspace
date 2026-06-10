# R-003: Agent Factory Rules

## Applies to

Agent Factory, Coordinator, Workflow Policy.

## Rules

```text
R-003-01: Create generated coder agents only after explicit user approval.
R-003-02: Create agents only for services discovered by onboarding or explicitly approved by the user.
R-003-03: Every generated coder must have allowed_read_paths.
R-003-04: Every generated coder must have allowed_write_paths.
R-003-05: Every generated coder must have forbidden_paths.
R-003-06: Every generated coder must have test_policy.
R-003-07: Every generated coder must have escalation rules.
R-003-08: Do not create full-repo coder agents.
R-003-09: Do not expand write scope without user approval.
R-003-10: Update agents.yaml after creating or changing coder agents.
```

## Required artifacts

```text
.claude/agents/coders/coder-<service>.agent.md
.maestro/registry/agents.yaml
.maestro/knowledge/components/<component-id>.yaml
```

## Violation handling

Deny agent activation and return to Coordinator for approval or onboarding refresh.
