# Work System

Shared work is decomposed as:

```text
Initiative -> Epic -> Task -> Subtask
```

Use the smallest level that remains independently understandable and verifiable. A subtask that still
needs decomposition becomes a task. Store dependency graphs and progress beside the owning task.

Direct work may omit persistent artifacts. Assisted work records task, progress, and verification.
Governed work uses the complete analysis, planning, implementation, verification, and QC contract.

Runs are execution instances. A task describes intended work; a run records one attempt, including
checkpoints, traces, evals, approvals, and reports when the work is long-lived or multi-agent.
