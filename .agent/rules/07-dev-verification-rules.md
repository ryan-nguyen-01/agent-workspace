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
R-007-11: Dev Verification is the output-readiness gate and must not replace Coder Leader code-quality/architecture review ownership.
```

## Required artifact

```text
.runtime/tasks/<task-id>/dev-verification.yaml
```

## Violation handling

Return DEV_BLOCKED or NEEDS_FIX and route back to Coder Leader.

## Boundary with Coder Leader

The authoritative ownership matrix and worked examples live in `.agent/rules/05-coder-leader-rules.md` → "Boundary with Dev Verification". Dev Verification must read that matrix before flagging a Leader-owned concern.

Quick reference (binary gates only):

```text
Dev Verification owns:
  artifact-exists, scope-compliance, test-evidence, manual-verification,
  critical-checks pass/fail, score computation, secret/PII scan

Dev Verification does NOT own:
  architecture review, layer boundaries, naming, duplicate-helper detection,
  contract-drift judgment, refactoring suggestions
```

If Dev Verification observes a Leader-owned issue that escaped review, return NEEDS_FIX with `missed_by_leader_review: true` in dev-verification.yaml so the audit trail records the gap.
