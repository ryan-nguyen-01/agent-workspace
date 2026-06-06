# R-018: Document Precedence Rules

## Applies to

All agents and commands that read or write framework/runtime documents. The tier map lives in
`.agent/docs/doc-precedence.md`; this file is its enforceable form. Adapted from the ADLC tier model.

## Core principle

```text
Exactly one official source per decision. When two documents conflict, the higher tier wins.
Lower tiers never override higher tiers; they re-derive from them.
```

Tiers (full map in `.agent/docs/doc-precedence.md`):

```text
T0  CLAUDE.md, .agent/workflow.md, .agent/rules/**, agent-taxonomy.md   (framework contract)
T1  project-brain.yaml, model-routing.yaml, response-ui.yaml, workflow-state.yaml   (project SSOT)
T2  service-catalog.yaml, agent-registry.yaml, test-policy.yaml, skill-registry.yaml, service brains
T3  task-analysis.yaml + task artifacts + advisories   (per-task, regenerated)
```

## Rules

```text
R-018-01: Every decision has exactly one authoritative document — the highest tier that owns it.
          Other docs reference it; they must not restate-and-diverge.
R-018-02: On conflict, the higher tier wins. A T3 artifact must never silently contradict a T1/T2
          source; if it must differ, that is an error to surface, not a value to use.
R-018-03: Upward correction only. If a lower tier reveals a higher-tier source is wrong, surface it
          (raise to user / record in CHANGELOG as a decision) and fix the higher-tier source. Do not
          patch the lower tier to mask the conflict, and do not fork the truth.
R-018-04: Generated documents are never authoritative. Anything produced by scripts/build-*.py mirrors
          a source; the source's tier wins. A manual edit to a generated file is drift and must be
          reverted or promoted into the source, then regenerated (see R-018-06).
R-018-05: Specialist advisories (T3, R-016) recommend; the owning workflow agent decides. An advisory
          never overrides a T0–T2 contract.
R-018-06: Generators must detect manual edits to their generated outputs (hash conflict) and refuse to
          silently overwrite without --force. scripts/architecture-health-check.py + each generator's
          --check enforce that generated outputs match their source.
R-018-07: Coder scope contracts in agent-registry.yaml (T2) are authoritative for write scope. A T3
          plan/assignment that needs scope beyond the contract must go through R-011-02 approval, not
          edit the contract inline.
```

## Conflict resolution procedure

```text
1. Identify the decision and which tier owns it (doc-precedence.md).
2. If a lower-tier doc disagrees with the owner: the owner wins for execution.
3. If the owner looks wrong: stop, surface to user or record a decision, fix the owner, re-derive.
4. Never resolve a conflict by editing the lower tier to match a stale higher tier — fix the source.
```

## Violation handling

If an agent finds two documents in conflict, it must not pick arbitrarily. Apply the tier rule; if the
authoritative source itself is wrong or ambiguous, route to Coordinator / Workflow Policy rather than
guessing (Karpathy rule 3).
