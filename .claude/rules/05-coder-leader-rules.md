# R-005: Coder Leader Rules

## Applies to

Coder Leader, Coordinator, generated service coders.

## Rules

```text
R-005-01: Coder Leader owns all multi-service implementation coordination.
R-005-02: Service coders must not coordinate cross-service changes directly.
R-005-03: Coder Leader must create implementation-plan.yaml before assigning coders.
R-005-04: Coder Leader must create service-assignments.yaml before coder work starts.
R-005-05: Coder Leader must select coders from agent-registry.yaml.
R-005-06: Coder Leader must reject tasks when no active coder exists for an impacted service.
R-005-07: Coder Leader must protect API, event, schema, and shared package contracts.
R-005-08: Coder Leader must not claim Code Done; Dev Verification owns that decision.
```

## Required artifacts

```text
.claude/tasks/<task-id>/implementation-plan.yaml
.claude/tasks/<task-id>/service-assignments.yaml
.claude/tasks/<task-id>/coder-results.yaml
```

## Violation handling

Stop implementation and route to Coordinator for missing coder creation, scope approval, or task clarification.
