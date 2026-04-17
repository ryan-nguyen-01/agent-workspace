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
```

## Approval record

Every approval must be recorded in one of:

```text
.claude/tasks/<task-id>/memory-updates.yaml
.claude/context/agent-registry.yaml
.claude/context/workflow-state.yaml
.claude/changelog.md
```

## Violation handling

Stop and ask Coordinator to request user approval.
