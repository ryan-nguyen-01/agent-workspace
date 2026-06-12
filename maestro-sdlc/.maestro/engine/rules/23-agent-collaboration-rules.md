# R-023: Agent Collaboration Contracts (A2A)

## Applies to

Every agent that delegates work or receives delegated work: Coordinator, Task Analysis, Solution
Architect, Coder Leader, Service/Built-in Coders, Dev Verification, QC Handoff, QC Runner, Bug Router.

## Purpose

Agent-to-agent links are **contracts, not conventions**. Every delegation travels in one standardized
handoff envelope and returns in one result envelope (`.maestro/engine/contracts/`). A receiver
validates before working — like a person refusing an incomplete brief — and a result without evidence
is invalid by schema.

## Rules

```text
R-023-01: Every delegation between agents uses the handoff envelope (contracts/handoff.schema.yaml),
  instantiated from engine/templates/handoff.template.yaml and stored at
  .maestro/work/tasks/<task-id>/handoffs/<seq>-<from>-to-<to>.yaml. Side-channel delegation
  ("just go do X" with no envelope) is not a valid handoff for governed/assisted work.
R-023-02: The RECEIVER validates the envelope BEFORE doing any work: intent is one actionable
  sentence; purpose_ref resolves (R-024); inputs satisfy the R-021 matrix for the receiver's role and
  are authoritative; acceptance items are testable; schema_version matches. Any failure ->
  status: blocked, block_reason: invalid_handoff, with the exact missing fields/docs. Never fill the
  gaps by guessing.
R-023-03: The reply uses the result envelope (contracts/result.schema.yaml): done REQUIRES evidence
  per acceptance item; deviations from the handoff MUST be listed (empty list = none); blocked carries
  missing[]/block_reason; the journal entry is referenced (R-024).
R-023-04: The SENDER verifies the result against its own acceptance list before passing work
  downstream; unaccepted deviations bounce back to the receiver, not silently absorbed.
R-023-05: Existing pipeline artifacts (task-analysis.yaml, implementation-plan.yaml,
  service-assignments.yaml, coder-results.yaml, qc-handoff.md, advisories) remain the CONTENT of work;
  the envelopes are the LINKS between agents. Assignments inside service-assignments.yaml count as
  envelopes when they carry the same required fields (intent, purpose_ref, inputs, acceptance).
R-023-06: Schemas are versioned. A version mismatch is a refusal (schema_mismatch), not a best-effort
  parse. Changing envelope semantics is a workflow-policy change (R-011-08).
R-023-07: Direct-mode trivial work may skip persisted envelopes, but the verbal contract still applies:
  state intent + acceptance before acting, report evidence after (R-024 journal note suffices).
```

## Violation handling

An invalid handoff is refused back to the sender with specifics. A result lacking evidence or hiding
deviations is rejected by the sender and re-done. Repeated contract violations are recorded in
feedback (R-010) for pattern review.
