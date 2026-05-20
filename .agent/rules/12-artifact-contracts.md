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

Framework maintenance in framework-template/not_applied mode may use lightweight evidence instead of the full task folder when all of these are true:

```text
target_scope: framework
task_size: trivial
no approval-gate, security, state-machine, generated-coder scope, service contract, or destructive-command impact
no application source under services/<service-name>/ is modified
```

Lightweight evidence must still include:

```text
changed files
verification command or reason no command applies
cross-tool entrypoint updates when the user-facing contract changed
```

## Required state artifacts

```text
Model routing/status/response UI: model-routing.yaml, agent-activity.yaml, and response-ui.yaml under .runtime/context/
On task creation: task.yaml manifest with unique task_id and task folder
On every state/artifact change: append task-updates.yaml
Before application coding under services/<service-name>: task-analysis.yaml with user approval unless fast-track R-011-10b applies, plus context_plan for all applied-service tasks
Before planning high-impact changes: architecture-review.yaml with decision approved
Before assigning coders in standard pipeline: implementation-plan.yaml and service-assignments.yaml
Before assigning coders in applied-service fast-track: lightweight service-assignments.yaml with assignment_note, allowed_write_paths, critical_checks, and context_pack
Before Dev Verification in standard pipeline: coder-results.yaml with coder_outputs[] consolidated by Coder Leader
Before Code Done in standard pipeline: dev-verification.yaml with DEV_DONE result
Before QC in standard pipeline: qc-handoff.md
Before QC_DONE in standard pipeline: qc-test-results.yaml with zero open blockers
Before user delivery in standard pipeline: qc-delivery-report.md
Before routing a defect: canonical .runtime/bugs/<severity>/<bug-id>.yaml plus .runtime/tasks/<task-id>/bugs.yaml index entry
Before DONE: memory-updates.yaml when durable facts changed
```

## Consistency validator

Run Workflow Policy before trusting a migrated workspace, resuming a task after manual edits, or validating a shared artifact-only snapshot:

```text
/policy-check snapshot --root .
/policy-check snapshot --root <snapshot-root>
```

The validator is agent-native and must not require Python, Node, jq, shell scripts, or any local runtime. It is allowed to pass with `services_available: false`; this means `services/` is absent or empty and the check used recorded artifacts only. Missing `services/` is not itself a defect for shared evidence snapshots.

The validator must fail on:

```text
distribution_mode / instance_status drift between workflow-state.yaml and Project Brain
DEV_DONE or later without dev-verification.yaml result/verdict DEV_DONE
QC_DONE/PASS with blocked, pending, not_run, or failed required checks
QC_DONE/PASS while notes still require manual or retest evidence
task.yaml artifact manifest entries that disagree with files in the task folder
agent-registry status that conflicts with active/approved coder entries
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
Do not store the only copy of a defect inside `.runtime/tasks/<task_id>/bugs.yaml`; it is an index that must point to the canonical `.runtime/bugs/.../<bug-id>.yaml` artifact.

## Violation handling

Stop transition and create or repair the missing artifact through the responsible agent.
