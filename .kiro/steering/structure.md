---
inclusion: always
---

# Structure

```text
.maestro/             Control plane (framework-owned brain + project-shared data)
├── engine/           workflow.md, rules/ (21), templates/ (58), docs/ (standards)
├── registry/         components, agents, skills, inputs, artifacts indexes
├── knowledge/        durable project + component knowledge
├── work/             initiatives, epics, tasks, subtasks, runs, bugs (evidence)
├── design/ decision/ design + ADR indexes
├── memory/ history/  continuation memory + auditable timeline
├── governance/ observability/  governance + traces/evals/reports/audit
└── runtime/          local-only state, telemetry, cache, reports (gitignored)

.claude/              Native Claude adapter: agents/, skills/, commands/, hooks via settings.json
.codex/ .cursor/ .gemini/ .github/ .kiro/   Other tool adapters
docs/                 Official docs: product, requirements (BA), experience (UX), architecture, etc.
apps/ services/ packages/ infra/ tests/     Product implementation roots
inputs/               External references awaiting curation
scripts/              Python helpers + scripts/hooks/ deterministic guards
```

## Agents (34 framework-owned)

`.claude/agents/workflow/` (12 control-plane) · `.claude/agents/coders/` (3 built-in: coder-infra,
coder-database, coder-data; + generated service coders) · `.claude/agents/specialists/<category>/`
(19 advisor-only). Everything routes through `coordinator`.

## Code layout for generated services/apps

Feature-based + layered (`.maestro/engine/docs/code-layout.md`):
`services/<svc>/src/modules/<feature>/{controller,service,repository,dto,types,spec}` + `core/`,
`shared/`; `apps/<app>/src/features/<feature>/{components,hooks,api}` + `shared/`.

## Conventions

- kebab-case folders; one feature = one module; dependencies point inward (controller→service→repository).
- No source under `.maestro/`; official docs under `docs/`; secrets never committed (R-013).
- Tasks: `TASK-YYYYMMDD-NNN-slug`; all artifacts in `.maestro/work/tasks/<task-id>/`.
