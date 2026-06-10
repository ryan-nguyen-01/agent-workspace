# Spec-Driven Development

Spec-Driven Development puts product and engineering specifications at the center of AI-assisted
software delivery. Use it when traceability from intent to implementation matters.

Legacy alias: `adlc`.

## Use When

- A new idea must become a real product capability.
- The work starts from PRD, HLD, LLD, ADR, ticket, incident, or regulatory requirement.
- Multiple components, roles, or verification stages are involved.
- Future readers need to understand why the implementation exists.

## Lifecycle

```text
Intent -> PRD -> Feature -> User Story / Use Case -> User Flow
       -> HLD -> LLD -> ADR -> Epic -> Task -> Subtask
       -> Implementation -> Dev Verification -> QC -> Release -> Memory Update
```

## Required Artifacts

| Stage | Artifact |
| --- | --- |
| Product intent | `docs/product/prds/` |
| Scope | `docs/requirements/features/`, `docs/requirements/user-stories/` |
| Experience | `docs/experience/user-flows/`, `docs/experience/ui-specifications/` |
| Architecture | `docs/architecture/high-level-design/`, `docs/architecture/low-level-design/` |
| Decisions | `docs/architecture/decisions/` |
| Delivery | `.maestro/work/initiatives/`, `.maestro/work/epics/`, `.maestro/work/tasks/` |
| Evidence | `verification.yaml`, `dev-verification.yaml`, QC results, runbooks when needed |

## Agent Rules

- Do not skip traceability when product intent, design, architecture, and delivery are all involved.
- Prefer stable IDs for PRDs, features, user stories, ADRs, epics, tasks, and components.
- Every accepted decision must have exactly one authoritative source.
- Use `governed` mode when specification artifacts drive code changes across components.
