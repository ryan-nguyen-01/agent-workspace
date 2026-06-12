# Specialist Advisors

16 domain experts operating as **in-pipeline advisors**: invoked by a workflow agent,
producing an evidence-backed advisory artifact at `.maestro/work/tasks/<task-id>/advisories/<id>.yaml`, they do **not**
write application code, do **not** assign coders, and do **not** mark Code Done/QC Done.

Contract & limits: [`.maestro/engine/rules/16-specialist-advisory-rules.md`](../../../.maestro/engine/rules/16-specialist-advisory-rules.md).
Template: [`.maestro/engine/templates/agent-specialist.template.md`](../../../.maestro/engine/templates/agent-specialist.template.md).

## Quick-selection

| When you need advice on… | Specialist | Category | Model | Invoked by |
|--------------------|-----------|----------|-------|---------------|
| REST/GraphQL API design, versioning, contract | `api-designer` | architecture | sonnet | task-analysis, solution-architect |
| Schema, migration, SQL/NoSQL choice, indexing | `database-architect` | architecture | opus | task-analysis, solution-architect |
| Cloud topology, IAM, networking, DR, WAF | `cloud-architect` | architecture | opus | solution-architect |
| Event contract, messaging, saga, ordering | `event-architect` | architecture | opus | solution-architect |
| Wireframe, component, design tokens, layout | `ui-ux-designer` | architecture | sonnet | task-analysis, coder-leader |
| OWASP, authn/authz, secrets, injection, threat model | `security-auditor` | quality-security | opus | dev-verification, coder-leader |
| Latency, N+1, caching, bundle size, load test | `performance-engineer` | quality-security | opus | dev-verification, coder-leader |
| WCAG, ARIA, keyboard nav, contrast | `accessibility-auditor` | quality-security | sonnet | dev-verification, coder-leader |
| Deep code review (augments coder-leader) | `code-reviewer` | quality-security | opus | coder-leader, dev-verification |
| User stories, acceptance criteria (augments task-analysis) | `business-analyst` | product | sonnet | coordinator, task-analysis |
| Data pipeline, ETL, streaming, analytics schema | `data-engineer` | data-ai | sonnet | task-analysis, solution-architect |
| Monitoring, SLO, tracing, incident runbook | `sre-observability` | ops-devex | sonnet | dev-verification, coder-leader |
| Docs, API docs, README, changelog, ADR | `technical-writer` | ops-devex | haiku | memory-update, coder-leader |
| Migration/upgrade/refactor planning, tech-debt | `migration-strategist` | ops-devex | opus | task-analysis, coder-leader |
| Technology evaluation, library comparison, spike | `tech-researcher` | research-qa | opus | task-analysis, solution-architect |
| Test strategy, test-case design, coverage (advises qc) | `qa-strategist` | research-qa | sonnet | task-analysis, qc-handoff |

## How activation works

1. `task-analysis` flags it in `task-analysis.yaml`:
   ```yaml
   advisory_required: [security-auditor, api-designer]
   ```
2. Or a workflow agent (coordinator/solution-architect/coder-leader/dev-verification/qc-handoff) detects a domain risk and invokes it.
3. The specialist writes the advisory → the downstream workflow agent reads it and resolves `handoff.must_address`.

Advisories **create no new state machine** — they run as a sub-step inside existing states (ANALYZED, ARCHITECTURE_REVIEWING, DEV_VERIFYING, QC). See [`.maestro/engine/workflow.md`](../../../.maestro/engine/workflow.md).
