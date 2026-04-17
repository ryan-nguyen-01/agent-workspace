# R-006: Service Coder Rules

## Applies to

Generated service coder agents, Coder Leader, Dev Verification.

## Rules

```text
R-006-01: Generated coders may write only inside allowed_write_paths.
R-006-02: Generated coders may read only allowed project context and assigned service context.
R-006-03: Generated coders must not write forbidden_paths.
R-006-04: Generated coders must stop when a task requires another service change.
R-006-05: Generated coders must raise cross_service_requests to Coder Leader.
R-006-06: Generated coders must not modify shared packages unless their contract allows it or the user approves scope expansion.
R-006-07: Generated coders must follow service test_policy.
R-006-08: If unit_tests_required is false, do not create new test files.
R-006-09: If unit_tests_required is true, add or update tests using existing project conventions.
R-006-10: If test policy is unknown, ask Coder Leader before creating tests.
R-006-11: Manual verification must be documented when tests are not required.
```

## Required artifacts

```text
.claude/context/agent-registry.yaml
.claude/context/services/<service>.yaml
.claude/tasks/<task-id>/service-assignments.yaml
.claude/tasks/<task-id>/coder-results.yaml
```

## Violation handling

Return `blocked` or `needs_leader` in coder-results.yaml and stop file changes.

## Reuse and convention rules

R-006-D01: Service coders must check service_deep_intelligence before implementation.
R-006-D02: Service coders must check common/generics.md and conventions.md before creating new reusable code.
R-006-D03: Existing reusable assets must be preferred over newly written helpers when they satisfy the task.
R-006-D04: New reusable assets require Coder Leader visibility and ownership notes.
R-006-D05: Coder results must list reusable assets used, conventions followed, and anti-patterns avoided.
R-006-D06: A coder must stop and ask Coder Leader if the task requires changing a shared reusable asset outside its allowed_write_paths.
