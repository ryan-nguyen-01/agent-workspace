# R-008: QC Rules

## Applies to

QC Runner, Bug Router, Coordinator, QC Handoff.

## Rules

```text
R-008-01: In the standard pipeline, QC starts only after qc-handoff.md exists.
R-008-02: QC Runner must not modify application source code.
R-008-03: QC Runner creates or records test cases from acceptance criteria and risks.
R-008-04: QC Runner stops immediately on blocker bugs.
R-008-05: QC Runner continues unaffected cases for non-blocking bugs.
R-008-06: QC_DONE requires zero open blocker bugs.
R-008-07: In the standard pipeline, QC results must be recorded in qc-test-results.yaml.
R-008-08: Real secrets must not be written to QC artifacts.
R-008-09: After QC_DONE, QC Runner must write qc-delivery-report.md summarizing results, completed features, verification steps, and next steps for the user.
R-008-10: Framework-maintenance fast-track skips QC Runner unless the task explicitly changes QC policy, test behavior, or a runnable helper script with user-facing risk.
R-008-11: QC_DONE/PASS is invalid when any required QC test case is blocked, pending, not_run, failed, or still marked as requiring manual/retest evidence.
R-008-12: If interactive/manual verification cannot run, QC must return CONTINUE_TESTING or NEEDS_USER_DECISION unless the user explicitly approves deferring that check.
```

## Required artifacts

```text
.runtime/tasks/<task-id>/qc-handoff.md          (standard pipeline)
.runtime/tasks/<task-id>/qc-test-results.yaml   (standard pipeline)
.runtime/tasks/<task-id>/qc-delivery-report.md  (standard pipeline)
```

## Violation handling

If blocker appears, stop QC and route through Bug Router.
