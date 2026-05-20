# R-009: Bug Routing Rules

## Applies to

Bug Router, QC Runner, Coordinator, Coder Leader.

## Rules

```text
R-009-01: Classify every QC defect as blocker or non-blocker.
R-009-02: Blocking bugs stop QC immediately.
R-009-03: Non-blocking bugs allow QC to continue on unaffected cases.
R-009-04: Every bug must include reproduction steps.
R-009-05: Every bug must include expected result and actual result.
R-009-06: Every bug must include impacted services when known.
R-009-07: Every bug must include assigned leader and target coder when known.
R-009-08: Blocker bug fixes return through Coder Leader and Dev Verification before QC retest.
R-009-09: Do not downgrade blocker severity just to keep QC moving.
R-009-10: Every defect must have one canonical bug artifact under `.runtime/bugs/blockers/` or `.runtime/bugs/non-blockers/`.
R-009-11: `.runtime/tasks/<task-id>/bugs.yaml` is only a task-local index and must reference each canonical bug with `bug_id`, `severity`, `status`, `canonical_path`, and `retest_scope`.
R-009-12: User/manual defects found after an agent reports done still route through `/bug`; if the original task is not accepted yet, attach the bug index to that task, otherwise create a new bug-report task linked by `source_task`.
R-009-13: Confirmed coding defects must include prevention fields when known: `root_cause`, `recurrence_key`, `prevention_rule`, and `regression_check`.
R-009-14: Bugs with reusable prevention must set `prevention.promote_to_feedback: true` so Memory Update can create or promote feedback entries.
```

## Required artifacts

```text
.runtime/bugs/blockers/<bug-id>.yaml
.runtime/bugs/non-blockers/<bug-id>.yaml
.runtime/tasks/<task-id>/bugs.yaml          (index/link, not canonical detail)
```

## Violation handling

Stop QC if severity is ambiguous and the defect may block main flow.
