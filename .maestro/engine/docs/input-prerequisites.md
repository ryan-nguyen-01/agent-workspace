# Input Prerequisites & Refusal

Every phase and every coder type needs specific inputs (documents/artifacts) before it can act. When a
required input is missing or insufficient, the agent **refuses and reports the gap** instead of guessing
(Four Karpathy principle 3). The coordinator surfaces the gap to the user during normal chat so they
know exactly what to produce to advance.

Contract: `.maestro/engine/rules/21-input-prerequisites-rules.md` (R-021).

## Prerequisites by phase

| Phase / agent | Required inputs | Produced by |
|---------------|-----------------|-------------|
| task-analysis | the request; for a product feature: requirements (user stories / acceptance criteria or a clear spec) | business-analyst (BA docs) / blueprint / user |
| solution-architect | task-analysis.yaml; requirements + NFR for architecture decisions | task-analysis, business-analyst |
| coder-leader / coders | task-analysis.yaml with acceptance_criteria; architecture/contracts per coder type (below); test-policy | task-analysis, solution-architect, BA |
| qc-runner | acceptance criteria; qc-handoff.md | task-analysis (AC), qc-handoff |

## Prerequisites by coder type

| Coder type | Required documents | Missing → produce with |
|------------|--------------------|------------------------|
| **Backend / service coder** | task-analysis acceptance criteria; **API contract** (endpoints/DTOs); **data model / schema (LLD)**; business rules (when logic depends on them); test policy | api-designer / HLD-LLD in `docs/architecture/`, `inputs/api/`; coder-database; business-analyst (business-rules) |
| **Frontend coder** | **approved UI/UX prototype + design tokens** (`docs/experience/wireframes/`); **API contract** to call; acceptance criteria | ui-ux-designer (blueprint UI/UX gate); api-designer / HLD |
| **coder-data** | **schema (LLD)**; business rules; entity definitions | coder-database; business-analyst; `inputs/domain/` |
| **coder-database** | **data model / entities** (domain glossary, LLD/HLD); migration policy | solution-architect / database-architect; `docs/architecture/`, `inputs/domain/` |
| **coder-infra** | deployment target; **NFR** (availability/scale/security); architecture (HLD) | solution-architect / cloud-architect; nfr doc; `docs/architecture/` |

> HLD = High-Level Design (`docs/architecture/high-level-design/`); LLD = Low-Level Design
> (`docs/architecture/low-level-design/`). BA docs follow the BA Documentation Standard
> (`.maestro/engine/docs/ba-documentation-standard.md`).

## Refusal protocol (structured "blocked: missing_prerequisites")

When a required input is missing, the agent must NOT proceed or invent it. It returns:

```yaml
decision: blocked
reason: missing_prerequisites
missing:
  - doc: "API contract"
    why: "the backend endpoints/DTOs for this feature are not specified"
    produce_with: "api-designer / solution-architect, or provide docs/architecture/low-level-design or inputs/api"
  - doc: "data model (LLD)"
    why: "entities/relationships needed to write the repository layer are undefined"
    produce_with: "coder-database / database-architect, or docs/architecture/low-level-design"
present: ["task-analysis.yaml (acceptance_criteria)", "test-policy.yaml"]
next_action: "produce the missing docs (run the listed agents/commands), then resume"
```

"Insufficient" counts as missing: a stale, draft, unapproved, or contradictory document does not satisfy
a prerequisite. Approved/authoritative only (doc precedence, R-018).

## Coordinator readiness (normal chat)

On any request that implies a step, the coordinator computes required-vs-present inputs for that step and,
if anything is missing, replies with: what the user wants → which step, what is present, what is MISSING
(with how to produce each), and the single next action. It does not silently route into a step whose
prerequisites are unmet.

## Exceptions

```text
- direct/trivial work the user explicitly scopes may proceed with the user as the source of missing facts,
  recorded as an assumption (still never invent secrets, contracts, or acceptance criteria).
- autopilot (/ship) satisfies prerequisites in order via the blueprint gate and the pipeline; if it cannot
  produce a prerequisite without the user (real credential, business decision), it hits a hard-stop (R-019-05).
```
