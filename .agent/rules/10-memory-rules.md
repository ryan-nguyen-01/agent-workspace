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
R-010-09: Actionable user feedback must be recorded in .runtime/context/feedback/inbox.md.
R-010-10: Durable or recurring feedback must be promoted to .runtime/context/feedback/patterns.md or .runtime/context/feedback/anti-patterns.md.
R-010-11: Every memory update must refresh .runtime/context/index.yaml or explicitly record why the index did not change.
R-010-12: Agents must read .runtime/context/index.yaml before opening multiple memory files.
R-010-13: Coding-error feedback must include `root_cause`, `prevention_rule`, `regression_check`, and `recurrence_key` before promotion.
R-010-14: Bugs with `prevention.promote_to_feedback: true` must create or update feedback inbox/pattern/anti-pattern entries during `/sync-memory`.
R-010-15: Memory Update must avoid storing raw logs; summarize evidence and cite source artifacts or canonical bug files.
```

## Required artifact

```text
.runtime/tasks/<task-id>/memory-updates.yaml
```

## Violation handling

Reject memory update and redact sensitive/noisy content before writing.
