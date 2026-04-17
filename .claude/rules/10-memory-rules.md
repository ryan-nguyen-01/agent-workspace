# R-010: Memory Rules

## Applies to

Memory Update, Coordinator, Onboarding, Coder Leader, QC Runner, Bug Router.

## Rules

```text
R-010-01: Update memory after DONE or meaningful workflow changes.
R-010-02: Update service memory after API, event, schema, dependency, or service responsibility changes.
R-010-03: Update bug pattern memory after reusable bug root causes.
R-010-04: Update test policy memory after user decisions or onboarding evidence changes.
R-010-05: Update agent registry memory after coder scope changes.
R-010-06: Memory entries must cite source artifact when possible.
R-010-07: Memory entries must include confidence when inferred.
R-010-08: Do not store secrets, passwords, raw tokens, long logs, or temporary noise.
```

## Required artifact

```text
.claude/tasks/<task-id>/memory-updates.yaml
```

## Violation handling

Reject memory update and redact sensitive/noisy content before writing.
