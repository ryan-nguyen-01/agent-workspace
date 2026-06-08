# Kiro Specs ↔ Maestro

Kiro's spec workflow (requirements → design → tasks) maps onto Maestro's existing artifacts. **Do not
create a parallel source of truth** — link to or generate the Maestro artifacts instead.

| Kiro spec file | Maestro source of truth |
|----------------|-------------------------|
| `requirements.md` | `docs/requirements/` (BA Documentation Standard: BRD/PRD/US/UC/BR/NFR/RTM) + `product-blueprint.yaml` (blueprint gate, R-019-0a) |
| `design.md` | `docs/architecture/` (HLD/LLD/ADR), `docs/experience/` (UI/UX prototype), `.maestro/engine/docs/code-layout.md` |
| `tasks.md` | `.maestro/work/tasks/<task-id>/` (task-analysis, implementation-plan, progress, verification) |

When Kiro generates a spec under `.kiro/specs/<feature>/`, treat it as a view; the approved, authoritative
requirement/design/task records live in the Maestro paths above and flow through `/coord` (or `/ship`).
