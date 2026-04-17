# R-012: Artifact Contracts

## Applies to

All workflow agents and commands.

## Required task folder

Every implementation task should use:

```text
.claude/tasks/<task-id>/
  task-input.md
  task.yaml
  task-analysis.yaml
  implementation-plan.yaml
  service-assignments.yaml
  coder-handoff-<service>.yaml   (one per assigned coder)
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
Before coding: task-analysis.yaml with user approval
Before assigning coders: implementation-plan.yaml and service-assignments.yaml
Before coder-results.yaml: coder-handoff-<service>.yaml from each assigned coder
Before Code Done: coder-results.yaml and dev-verification.yaml
Before QC: qc-handoff.md
Before QC_DONE: qc-test-results.yaml with zero open blockers
Before user delivery: qc-delivery-report.md
Before DONE: memory-updates.yaml when durable facts changed
```

## Naming rules

```text
Task id: TASK-<number-or-slug>
Bug id: BUG-<number-or-slug>
Generated coder: coder-<service-slug>.agent.md
Service brain: .claude/context/services/<service-id>.yaml
```

## Violation handling

Stop transition and create or repair the missing artifact through the responsible agent.
