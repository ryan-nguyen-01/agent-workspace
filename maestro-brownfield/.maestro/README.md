# `.maestro` Product Control Plane

`.maestro/` contains the agent-readable control plane for one product workspace. Product code remains in
peer roots such as `apps/`, `services/`, `packages/`, `infra/`, and `tests/`.

## Domains

```text
.maestro/
├── INSTRUCTIONS.md       Stable harness entry point
├── project.yaml          Product identity, naming, and component roots
├── methodology.yaml      Methodology routing, overlays, and execution policy
├── manifest.yaml         Ownership and local/shared boundaries
├── config/               Shared model and response configuration
├── engine/               Canonical control plane: workflow, rules, templates, and docs
├── registry/             Components, agents, skills, inputs, and artifact addresses
├── knowledge/            Durable project facts and component knowledge
├── work/                 Initiative, epic, task, subtask, run, bug, and verification evidence
├── design/               Design artifact index and relationships
├── decision/             Decision index and ADR relationships
├── memory/
│   ├── project/          Durable reusable patterns and feedback
│   ├── tasks/            Task summaries for cross-session continuation
│   └── sessions/         Local short-term session memory
├── observability/        Traces, evals, reports, and audit views
├── governance/           Agent-readable governance, approvals, and risk indexes
├── history/              Compatibility event log and timeline
└── runtime/              Local-only active state, cache, locks, and reports
```

## Read Policy

Agents start with `INSTRUCTIONS.md`, then use registries and indexes to open only relevant files.
The skill registry is the canonical address book for capabilities. The component registry is the
canonical address book for product code.

Methodology names are local overlays mapped to current production-agent patterns in
`docs/governance/methodologies/industry-alignment.md`.

The architecture is run-centric: tasks describe work, runs record attempts, checkpoints preserve
progress, traces and evals support quality claims, and governance records ownership and approval
boundaries. `.maestro/engine/` is the single canonical control plane for workflow, rules, templates, and docs.

Shared product knowledge must not be written to `runtime/` or `memory/sessions/`. Those locations are
ignored by Git so parallel users do not conflict over active chat state or telemetry.

Do not store secrets, raw credentials, private data, or long logs anywhere under `.maestro/`.
