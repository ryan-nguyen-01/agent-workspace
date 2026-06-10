# Runs

Runs are execution instances. A task describes intended work; a run records one attempt to perform it.

Use runs for long-lived or multi-agent work that needs durable execution, checkpointing, trace links,
eval evidence, human-in-the-loop pauses, or replay.

## Suggested Run Folder

```text
.maestro/work/runs/RUN-YYYYMMDD-NNN-slug/
├── run.yaml
├── checkpoints/
├── traces/
├── evals/
├── approvals/
└── report.md
```

Small `direct` work may omit run artifacts. Assisted and governed work should create a run when the
same task may have multiple attempts, pauses, or eval cycles.

## CLI

Use `python3 scripts/agent-run.py create|heartbeat|checkpoint|complete` to maintain run records and
keep `.maestro/runtime/workflow-state.yaml` aligned with the active execution.
