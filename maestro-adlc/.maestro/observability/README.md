# Observability

This directory is the canonical domain for agent run evidence: traces, evals, activity summaries,
reports, and audit views.

Phase 1 keeps local runtime telemetry in `.maestro/runtime/` for compatibility with existing scripts.
Shared, reviewable evidence should be linked from this domain.

## Domains

```text
observability/
├── traces/    Agent run traces, tool-call summaries, and handoff evidence.
├── evals/     Eval definitions, eval runs, and regression evidence.
├── reports/   Human-readable status, verification, and quality reports.
└── audit/     Audit views derived from work, governance, and history artifacts.
```

Do not store raw secrets, raw transcripts, long logs, or private data here.
