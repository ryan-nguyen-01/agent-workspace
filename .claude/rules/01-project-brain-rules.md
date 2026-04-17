# R-001: Project Brain Rules

## Applies to

Coordinator, Onboarding, Agent Factory, Task Analysis, Coder Leader, Memory Update, Workflow Policy.

## Rules

```text
R-001-01: .claude/context/project-brain.yaml is the first project memory source.
R-001-02: Do not rescan the full repository when Project Brain is fresh enough for the task.
R-001-03: If Project Brain is missing, empty, or stale, route to Onboarding.
R-001-04: Prefer partial rescan when stale areas are known.
R-001-05: Service-specific facts belong in .claude/context/services/<service>.yaml.
R-001-06: Generated coder facts belong in .claude/context/agent-registry.yaml.
R-001-07: Test policy belongs in .claude/context/test-policy.yaml.
R-001-08: Inferred facts must carry confidence or be marked unknown.
```

## Required artifacts

```text
.claude/context/project-brain.yaml
.claude/context/service-catalog.yaml
.claude/context/test-policy.yaml
.claude/context/agent-registry.yaml
```

## Violation handling

If memory is stale or insufficient, stop normal routing and run `/onboard` or partial onboarding.
