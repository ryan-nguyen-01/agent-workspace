# R-022: Artifact Granularity & Completeness

## Applies to

Business Analyst, Solution Architect, Task Analysis, QC Runner, QA Strategist, Coordinator.

## Purpose

Documents must be produced as if a team wrote them: **split per feature, detailed, with complete
acceptance criteria and a full QC test suite** — not one sketchy file that crams everything together.
A thin/placeholder artifact is "insufficient" and does not satisfy a prerequisite (R-021-02).

## Granularity — one unit per file (do NOT cram)

```text
R-022-01: Split requirements per feature, one unit per file with a stable id:
  - one User Story per file        docs/requirements/user-stories/<KEY>-US-NNN-<slug>.md
  - one Use Case per file          docs/requirements/use-cases/<KEY>-UC-NNN-<slug>.md
  - Business Rules grouped per feature area  docs/requirements/features/<KEY>-BR-NNN-<area>.md
  Never put multiple features/stories in a single document.
R-022-02: Design is split by level and scope:
  - HLD: one system-level document (boundaries, components, main flows, contracts, NFR, security).
  - LLD: ONE PER feature/module/service (interfaces, data structures, control flow, error handling) —
    not a single mega-LLD for the whole system. Each LLD links its parent HLD and the stories it implements.
R-022-03: Group large doc sets in per-area subfolders; keep the RTM as the index linking everything.
```

## Acceptance criteria — complete and testable

```text
R-022-04: Every user story has MULTIPLE specific, testable acceptance criteria in Given/When/Then form.
  Minimum per story: cover the happy path + at least one alternate/negative + at least one boundary/edge
  (>= 3 ACs typical). Each AC is verifiable and measurable.
R-022-05: No vague ACs ("works correctly", "is fast", "good UX"). Use concrete inputs, states, and
  expected outputs (numbers, error codes from the Error Catalog, specific UI states).
R-022-06: Each AC carries a stable id (AC-<story>.<n>) so QC test cases and the RTM trace to it.
```

## Design completeness

```text
R-022-07: HLD and LLD fill every template section with real content (no empty headings, "TBD", or a
  single paragraph for a multi-feature scope). LLD interfaces show concrete signatures/DTOs; error
  handling references Error Catalog codes (ERR); test design lists what to test.
```

## QC test-case completeness (no "a few cases")

```text
R-022-08: QC derives test cases SYSTEMATICALLY from acceptance criteria and contracts; the count scales
  with the work, it is never a token handful. Minimum coverage:
  - every AC -> at least one positive AND one negative/edge test case
  - every API endpoint -> success + validation error + auth/authz + not-found/error (per Error Catalog)
  - every screen -> each state (empty/loading/error/success) + primary interactions + responsive
  - cross-feature flows -> end-to-end; plus regression for changed areas
R-022-09: Each test case records: id, linked AC/endpoint/screen, preconditions, steps, expected result,
  status, evidence. Vague cases ("test the page works") are invalid.
R-022-10: A QC pass with obviously low coverage relative to the ACs/endpoints/screens is rejected — it
  is not Done (R-019-QC3). Do not shrink the suite to pass faster.
```

## Task decomposition & self-containment

```text
R-022-12: Decompose, do NOT cram a task. When a user story / feature needs more than one unit of work,
  split it into multiple tasks (or a parent task with subtasks). The PARENT (the user story doc, or a
  parent task) holds only its own summary + links to its child tasks — not the full content of every child.
R-022-13: Each TASK/SUBTASK is small and self-contained and attaches its full document bundle, so the
  executing agent works from the attached references (not from a giant blob). A task carries a
  `context_bundle` with the exact docs its coder type needs (R-021): requirement (US id + the specific AC
  ids), design (HLD/LLD ids), API contract, Error Catalog codes used, UI/UX screens (frontend), business
  rules, data model (backend/data), test policy, and the target code paths it may write.
R-022-14: Link, do not duplicate (R-018): the task references docs by id/path; it does not copy their
  full body. Children link back to the parent (US) and the parent lists its children; the RTM ties
  requirement -> tasks -> tests.
R-022-15: A task with no context_bundle, or one that bundles unrelated features together, is invalid —
  task-analysis/coder-leader must decompose and attach the proper documents before assigning a coder.
```

## Insufficiency

```text
R-022-11: An artifact that is monolithic-when-it-should-be-split, has empty/placeholder sections, lacks
  complete ACs, or ships a thin test suite is INSUFFICIENT: downstream agents treat it as a missing
  prerequisite (R-021) and request the proper version before proceeding.
```

## Violation handling

Return the artifact for completion (or, downstream, return blocked: missing_prerequisites). Do not
proceed on a sketchy artifact and do not pad with invented detail — fill it from real requirements/design.
