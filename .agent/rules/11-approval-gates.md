# R-011: Approval Gates

## Applies to

Coordinator, Agent Factory, Coder Leader, Service Coders, QC Runner, Workflow Policy.

## User approval required before

```text
R-011-01: Creating generated service coder agents.
R-011-02: Expanding a generated coder's allowed_write_paths.
R-011-03: Skipping onboarding when Project Brain is missing or stale.
R-011-04: Skipping QC.
R-011-05: Skipping or downgrading a blocker bug.
R-011-06: Creating tests when service policy says tests are not required.
R-011-07: Running destructive environment, database, deployment, or data actions.
R-011-08: Changing workflow policy or state machine rules.
R-011-09: Touching files outside a coder agent's approved scope.
R-011-10: Proceeding from Task Analysis to Coder Leader (user must review and approve task-analysis.yaml).
R-011-10b: Exception to R-011-10 — Fast-track tasks (workflow.md §6.2) skip the user approval gate when ALL eligibility conditions hold. Coordinator must record fast_track: true in task-analysis.yaml and add an entry to workflow-state.yaml.fast_track_log[]. User may revoke fast-track at any time.
R-011-11: USER may explicitly disable fast-track for the project by setting fast_track_enabled: false in test-policy.yaml. When disabled, R-011-10b does not apply.
R-011-12: Updating installed skill content, skills-lock.json, or skill risk/approval metadata requires explicit user approval. High/critical risk skill updates require separate per-skill approval.
R-011-13: Switching distribution_mode (via onboarding or an explicit user-approved edit to workflow-state.yaml) requires explicit user intent and must be denied when workflow-state.yaml.active_task_id is not null.
```

## Approval record

Every approval must be recorded in one of:

```text
.runtime/tasks/<task-id>/memory-updates.yaml
.runtime/context/agent-registry.yaml
.runtime/context/workflow-state.yaml
.claude/changelog.md
CHANGELOG.md
```

## Violation handling

Stop and ask Coordinator to request user approval.
