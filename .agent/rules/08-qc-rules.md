# R-008: QC Rules

## Applies to

QC Runner, Bug Router, Coordinator, QC Handoff.

## Rules

```text
R-008-01: QC starts only after qc-handoff.md exists.
R-008-02: QC Runner must not modify application source code.
R-008-03: QC Runner creates or records test cases from acceptance criteria and risks.
R-008-04: QC Runner stops immediately on blocker bugs.
R-008-05: QC Runner continues unaffected cases for non-blocking bugs.
R-008-06: QC_DONE requires zero open blocker bugs.
R-008-07: QC results must be recorded in qc-test-results.yaml.
R-008-08: Real secrets must not be written to QC artifacts.
R-008-09: After QC_DONE, QC Runner must write qc-delivery-report.md summarizing results, completed features, verification steps, and next steps for the user.
```

## Required artifacts

```text
.runtime/tasks/<task-id>/qc-handoff.md
.runtime/tasks/<task-id>/qc-test-results.yaml
.runtime/tasks/<task-id>/qc-delivery-report.md
```

## Violation handling

If blocker appears, stop QC and route through Bug Router.
