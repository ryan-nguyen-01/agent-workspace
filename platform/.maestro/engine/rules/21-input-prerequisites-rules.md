# R-021: Input Prerequisites & Refusal

## Applies to

Coordinator, Task Analysis, Solution Architect, Coder Leader, Service Coders, built-in coders, QC Runner.

## Purpose

Operationalize Four Karpathy principle 3 ("if critical data is missing, ask before coding"): each phase
and coder type declares the inputs it needs; when they are missing or insufficient, the agent refuses
and reports the gap instead of guessing, and the coordinator tells the user what to produce to advance.

Matrix and protocol: `.maestro/engine/docs/input-prerequisites.md`.

## Rules

```text
R-021-01: Before acting, an agent must verify its required inputs exist and are sufficient (per the
  prerequisites matrix). Required inputs differ by phase and by coder type (backend/frontend/data/
  database/infra) — see input-prerequisites.md.
R-021-02: "Sufficient" means present AND authoritative: a stale, draft, unapproved, empty, or
  contradictory document does NOT satisfy a prerequisite (doc precedence, R-018).
R-021-03: If a required input is missing or insufficient, the agent returns decision: blocked with
  reason: missing_prerequisites and a structured `missing[]` list (doc, why, produce_with), plus what is
  present and the next_action. It must NOT proceed, and must NOT invent the missing facts (contracts,
  acceptance criteria, schema, business rules, credentials).
R-021-04: Coders refuse at assignment time when their type's documents are missing (matrix in
  input-prerequisites.md):
    - Frontend: BA (stories + acceptance criteria) + approved UI/UX prototype + API contract + Error
      Code Catalog (ERR) + i18n keys when localized.
    - Backend/service: HLD + LLD + API contract + data model + business rules + ERR + NFR.
    - coder-data: data model/LLD + business rules + entities; coder-database: data model/entities +
      migration policy; coder-infra: HLD + NFR + deployment target.
  If any are missing/insufficient, return blocked: missing_prerequisites to Coder Leader (R-006). Do not
  write code and do not invent the contract, schema, error codes, or acceptance criteria.
R-021-05: The coordinator runs a readiness check on every request that implies a step. If prerequisites
  for the implied step are unmet, it replies with the gap (what is present, what is missing + how to
  produce each, the single next action) and does not silently route into that step. Surface this in the
  output contract (`missing_artifacts`, `block_reason`).
R-021-06: Exceptions — direct/trivial work the user explicitly scopes may proceed with the user as the
  source of a missing non-critical fact, recorded as an assumption; this never covers secrets, public
  contracts, acceptance criteria, or schema. Autopilot satisfies prerequisites via the blueprint gate and
  pipeline order; an unmet prerequisite it cannot produce alone becomes a hard-stop (R-019-05).
R-021-08: For cross-service integration, a missing counterpart API contract is a missing prerequisite
  that requires USER CONFIRMATION (not a silent guess): wait for the contract, or proceed on a
  user-approved stub interface recorded as assumption + draft contract (see R-006-22).
R-021-07: A "done"/"ready" claim is invalid if it skipped an unmet prerequisite. Prefer asking over
  guessing; a wrong assumption that breaks acceptance criteria, security, or scope must escalate (R-000).
```

## Violation handling

Stop and return the structured missing_prerequisites block; the coordinator requests the documents from
the user or routes to the agent/command that produces them. Never substitute invented data for a missing
prerequisite.
