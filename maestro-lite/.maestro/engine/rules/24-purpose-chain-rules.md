# R-024: Purpose Chain & Intent Ledger

## Applies to

Every agent. Coordinator and Workflow Policy enforce; Task Analysis assigns purpose; coders/QC carry it.

## Purpose

Nothing is built "because the agent felt like it". Every piece of work traces to an approved purpose,
and every step is journaled as intent -> action -> evidence. This turns "work with a specific goal, do
not invent work" into a machine-checkable gate instead of a hope.

## The chain

```text
Goal (blueprint/BRD) -> Feature -> User Story -> Acceptance Criterion -> Task -> Handoff -> Change/Deliverable -> Test
```

## Rules

```text
R-024-01: Every task, subtask, and handoff carries purpose_ref — the AC/story/feature id it serves
  (task.yaml.purpose_ref, handoff.purpose_ref). Task Analysis assigns it when decomposing (R-022).
R-024-02: ORPHAN-WORK GATE. Work without a resolvable purpose_ref is refused: the coordinator does not
  route it, a coder does not code it, QC does not test it. If the user asks for something with no
  parent purpose, the coordinator first creates/extends the requirement (story/AC) or records an
  explicit user decision — THEN work proceeds. "While I'm here" improvements with no purpose_ref are
  scope expansion (hard-stop under autopilot, R-019-05).
R-024-03: INTENT LEDGER. Each non-trivial task keeps a journal at
  .maestro/work/tasks/<task-id>/journal.md (template: journal.template.md). Before each significant
  step the agent records: WHAT it is about to do, WHY (purpose_ref), and the EVIDENCE it expects.
  After: the outcome, the actual evidence, and any deviation from intent. Entries are append-only.
R-024-04: CLAIMS CITE SOURCES. Any factual claim in any artifact (not only advisories) cites its
  source: file:line, document id, command output, or test run. A claim with no source is marked
  assumption with confidence, or removed. Inventing requirements, contracts, schema, error codes,
  test results, or "the user wants X" is fabrication (R-019-10 applies everywhere).
R-024-05: DEVIATION HONESTY. Discovering necessary work outside the current purpose_ref does not allow
  silently doing it: journal it, raise it (new task proposal or cross_service_request), and continue
  only after it has its own purpose.
R-024-06: The traceability matrix (RTM, R-022) is the index of the chain: requirement -> tasks ->
  tests. The orphan check runs forward (before work) — the RTM audits backward (after work). Both
  directions must be clean for DONE.
R-024-07: Trivial direct-mode work may keep the ledger as a single journal note (intent + evidence),
  but the orphan rule still applies: even a one-line fix answers "which purpose does this serve?" —
  the user's explicit ask counts as the purpose and is recorded.
```

## Violation handling

Orphan work is stopped and routed back through requirements. Unsourced claims are downgraded to
assumptions or removed before the artifact is accepted. Repeated fabrication attempts escalate to the
user via the coordinator.
