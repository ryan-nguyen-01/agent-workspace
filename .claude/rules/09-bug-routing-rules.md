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
```

## Required artifacts

```text
.claude/bugs/blockers/<bug-id>.yaml
.claude/bugs/non-blockers/<bug-id>.yaml
.claude/tasks/<task-id>/bugs.yaml
```

## Violation handling

Stop QC if severity is ambiguous and the defect may block main flow.
