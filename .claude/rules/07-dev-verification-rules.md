# R-007: Dev Verification Rules

## Applies to

Dev Verification, Coder Leader, Coordinator, QC Handoff.

## Rules

```text
R-007-01: Code Done requires dev verification score >= 80%.
R-007-02: Code Done requires all critical checks to pass.
R-007-03: Code Done requires zero known blockers.
R-007-04: Code Done requires scope compliance.
R-007-05: Code Done requires test policy compliance.
R-007-06: If unit tests are required, test evidence must be recorded.
R-007-07: If unit tests are not required, manual verification evidence must be recorded.
R-007-08: Critical check failure overrides a score >= 80%.
R-007-09: Dev Verification must write dev-verification.yaml.
R-007-10: Dev Verification must not create missing tests when policy forbids tests.
```

## Required artifact

```text
.claude/tasks/<task-id>/dev-verification.yaml
```

## Violation handling

Return DEV_BLOCKED or NEEDS_FIX and route back to Coder Leader.
