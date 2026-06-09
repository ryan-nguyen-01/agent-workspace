# BA Documentation Standard

The standard set of business-analysis documents, their templates, IDs, and when each is required, so
requirements are captured consistently and everything built traces back to an approved requirement.

business-analyst produces these as requirement artifacts under `docs/requirements/` (and `docs/product/`
for the PRD/BRD). They are documents, not application code — the advisor-only boundary (R-016) holds.
task-analysis references them to build the official `task-analysis.yaml`.

## Document set

| Document | Template | Lives in | Purpose | ID |
|----------|----------|----------|---------|----|
| BRD — Business Requirements | `brd.template.md` | `docs/product/` | Business goals, stakeholders, scope, as-is/to-be, high-level requirements | `<KEY>-BRD-NNN` |
| PRD — Product Requirements | `prd.template.md` | `docs/product/prds/` | Product scope, functional + NFR summary, success metrics | `<KEY>-PRD-NNN` |
| Use Case | `use-case.template.md` | `docs/requirements/use-cases/` | Actor goal, main/alternate/exception flows, postconditions | `<KEY>-UC-NNN` |
| User Story | `user-story.template.md` | `docs/requirements/user-stories/` | INVEST story + Given/When/Then acceptance criteria | `<KEY>-US-NNN` |
| Business Rules | `business-rules.template.md` | `docs/requirements/features/` | Constraints/validations independent of implementation | `<KEY>-BR-NNN` |
| Non-Functional Requirements | `nfr.template.md` | `docs/requirements/non-functional/` | Measurable performance/security/availability/usability targets | `<KEY>-NFR-NNN` |
| Traceability Matrix (RTM) | `requirements-traceability.template.md` | `docs/requirements/` | Requirement → story → AC → code → test coverage | `<KEY>-RTM-NNN` |

## When each is required (right-sized to scope_target)

```text
MVP:        PRD (light) + User Stories with acceptance criteria + key Business Rules + a short NFR.
            BRD optional; RTM kept lightweight.
Production: BRD + PRD + Use Cases + User Stories + Business Rules + full NFR + RTM (full coverage).
Always:     every implementation task must trace to an approved requirement (RTM), or record why none.
```

## Granularity & completeness (R-022)

```text
- SPLIT PER FEATURE — one unit per file, never crammed together:
    one User Story per file   docs/requirements/user-stories/<KEY>-US-NNN-<slug>.md
    one Use Case per file     docs/requirements/use-cases/<KEY>-UC-NNN-<slug>.md
    Business Rules per area   docs/requirements/features/<KEY>-BR-NNN-<area>.md
- COMPLETE, TESTABLE ACs — every story has multiple specific Given/When/Then ACs covering happy path +
  at least one alternate/negative + at least one boundary/edge (>= 3 typical). Each AC has id
  AC-<story>.<n>, concrete inputs/outputs, error codes from the Error Catalog. No vague ACs.
- Write like a team: detailed and reviewable, not a one-paragraph summary for a multi-feature scope.
  A thin/placeholder doc is insufficient (R-022-11) and is treated as a missing prerequisite (R-021).
```

## ID & lifecycle conventions

```text
- IDs: <PROJECT_KEY>-<TYPE>-<NNN> (zero-padded), stable once assigned; never reuse a retired id.
- status: draft -> in-review -> approved. Build governed work only from approved requirements.
- Acceptance criteria use Given/When/Then; they become QC test cases (R-019-QC) and feed the RTM.
- Keep one authoritative source per requirement (doc precedence, R-018); link instead of duplicating.
```

## How it fits the workflow

```text
1. Blueprint gate (R-019): features in product-blueprint.yaml come from / become these requirement docs.
2. business-analyst writes/refines the BA docs in docs/; updates the RTM.
3. task-analysis references the approved requirements to produce task-analysis.yaml (acceptance_criteria).
4. Coders implement; QC derives test cases from the acceptance criteria; RTM status moves open -> done.
5. No requirement with no test = a gap; no test/feature with no requirement = scope creep (RTM flags both).
```
