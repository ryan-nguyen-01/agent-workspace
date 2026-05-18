# R-012: Artifact Contracts

## Applies to

All workflow agents and commands.

## Required task folder

Every implementation task should use:

```text
.runtime/tasks/<task_id>/
  task-input.md
  task.yaml
  task-updates.yaml
  task-analysis.yaml
  architecture-review.yaml       (when architecture_review.required is true)
  implementation-plan.yaml
  service-assignments.yaml
  coder-results.yaml
  dev-verification.yaml
  qc-handoff.md
  qc-test-results.yaml
  qc-delivery-report.md
  bugs.yaml
  memory-updates.yaml
```

## Required state artifacts

```text
On task creation: task.yaml manifest with unique task_id and task folder
On every state/artifact change: append task-updates.yaml
Before coding: task-analysis.yaml with user approval
Before planning high-impact changes: architecture-review.yaml with decision approved
Before assigning coders: implementation-plan.yaml and service-assignments.yaml
Before Dev Verification: coder-results.yaml with coder_outputs[] consolidated by Coder Leader
Before Code Done: dev-verification.yaml with DEV_DONE result
Before QC: qc-handoff.md
Before QC_DONE: qc-test-results.yaml with zero open blockers
Before user delivery: qc-delivery-report.md
Before DONE: memory-updates.yaml when durable facts changed
```

## Naming rules

```text
Task id: TASK-YYYYMMDD-NNN-slug
Task folder: .runtime/tasks/<task_id>/
Bug id: BUG-<number-or-slug>
Generated coder: coder-<service-slug>.agent.md
Service brain: .runtime/context/services/<service-id>.yaml
```

Task IDs must be assigned by Coordinator before Task Analysis writes task-analysis.yaml.
The `NNN` sequence is per day and should use the next unused number under `.runtime/tasks/`.
Do not create task artifacts outside the task folder.
Do not mirror QC handoff outside the task folder; the canonical Dev-to-QC artifact is `.runtime/tasks/<task_id>/qc-handoff.md`.

## Violation handling

Stop transition and create or repair the missing artifact through the responsible agent.
