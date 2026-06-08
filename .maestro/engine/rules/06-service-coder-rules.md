# R-006: Service Coder Rules

## Applies to

Generated service coder agents, built-in cross-cutting coders, Coder Leader, Dev Verification.

## Rules

```text
R-006-01: Generated coders may write only inside allowed_write_paths.
R-006-02: Generated coders may read only allowed project memory and assigned service memory/task context.
R-006-03: Generated coders must not write forbidden_paths.
R-006-04: Generated coders must stop when a task requires another service change.
R-006-05: Generated coders must raise cross_service_requests to Coder Leader.
R-006-06: Generated coders must not modify shared packages unless their contract allows it or the user approves scope expansion.
R-006-07: Generated coders must follow service test_policy.
R-006-08: If unit_tests_required is false, do not create new test files.
R-006-09: If unit_tests_required is true, add or update tests using existing project conventions.
R-006-10: If test policy is unknown, ask Coder Leader before creating tests.
R-006-11: Manual verification must be documented when tests are not required.
R-006-12: Built-in cross-cutting coders (`coder-infra`, `coder-database`, `coder-data`) may be assigned only by Coder Leader after task-analysis identifies matching infra/database/data-generation scope.
R-006-13: Built-in cross-cutting coders must have `origin: "built-in"`, `scope_class: "cross-cutting"`, and `requires_project_onboarding: false` in agents.yaml.
R-006-14: Built-in cross-cutting coders do not replace generated service coders. If application code changes are required, Coder Leader must assign the owning generated service coder or raise a scope/approval request.
R-006-15: Service coders return structured results to Coder Leader; they must not create separate coder-handoff files. Coder Leader consolidates outputs in coder-results.yaml.coder_outputs[].
R-006-16: Before coding, service coders must check feedback patterns/anti-patterns assigned in the context_pack and record `feedback_preflight`.
R-006-17: If a coder hits or introduces a coding error, it must return `coding_error_feedback` with root_cause, prevention_rule, and regression_check.
R-006-18: A coder must not knowingly repeat a known feedback anti-pattern; if the task appears to require it, stop and ask Coder Leader.
R-006-19: New code follows the Code Layout Standard (.maestro/engine/docs/code-layout.md): place feature code in its module folder with layered files (controller/service/repository/dto/types/test for backend; features/<feature> with components/hooks/api for frontend); put cross-cutting code in core/ or shared/. Match the existing repo layout when it already differs; do not scatter a feature across unrelated layers.
```

## Required artifacts

```text
.maestro/registry/agents.yaml
.maestro/knowledge/components/<component-id>.yaml
.maestro/work/tasks/<task-id>/service-assignments.yaml
.maestro/work/tasks/<task-id>/coder-results.yaml
```

## Violation handling

Return `blocked` or `needs_leader` to Coder Leader for consolidation in coder-results.yaml and stop file changes.

## Reuse and convention rules

R-006-D01: Service coders must check component_deep_intelligence before implementation.
R-006-D02: Service coders must check common/generics.md and conventions.md before creating new reusable code.
R-006-D03: Existing reusable assets must be preferred over newly written helpers when they satisfy the task.
R-006-D04: New reusable assets require Coder Leader visibility and ownership notes.
R-006-D05: Coder results must list reusable assets used, conventions followed, and anti-patterns avoided.
R-006-D06: A coder must stop and ask Coder Leader if the task requires changing a shared reusable asset outside its allowed_write_paths.
R-006-D07: Coder results must list feedback patterns applied and known error patterns avoided.
