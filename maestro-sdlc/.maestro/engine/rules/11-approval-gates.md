# R-011: Approval Gates

## Applies to

Coordinator, Agent Factory, Coder Leader, Service Coders, QC Runner, Workflow Policy.

## User approval required before

```text
R-011-00: Gates apply when the selected execution mode, risk escalation, or explicit user policy
requires them. Direct mode does not bypass secret, destructive-action, production, or scope safety.
R-011-01: Creating generated service coder agents.
R-011-02: Expanding a generated coder's allowed_write_paths.
R-011-03: Skipping onboarding when Project Brain is missing or stale.
R-011-04: Skipping QC.
R-011-05: Skipping or downgrading a blocker bug.
R-011-06: Creating tests when component policy says tests are not required.
R-011-07: Running destructive environment, database, deployment, or data actions.
R-011-08: Changing workflow policy or state machine rules.
R-011-09: Touching files outside a coder agent's approved scope.
R-011-10: Proceeding from governed Task Analysis to Coder Leader when user review is configured as required.
R-011-10b: Exception to R-011-10 — Fast-track tasks (workflow.md §6.2) skip the user approval gate when ALL eligibility conditions hold. Coordinator must record fast_track: true in task-analysis.yaml and add an entry to workflow-state.yaml.fast_track_log[]. User may revoke fast-track at any time.
R-011-11: USER may explicitly disable fast-track for the project by setting fast_track_enabled: false in test-policy.yaml. When disabled, R-011-10b does not apply.
R-011-12: Updating installed skill content, skills-lock.json, or skill risk/approval metadata requires explicit user approval. High/critical risk skill updates require separate per-skill approval.
R-011-13: Changing workflow policy, state-machine semantics, or persistent workflow-state fields requires explicit user intent and must be denied when the change would invalidate workflow-state.yaml.active_task_id.
R-011-14: workflow-state.yaml.access_mode (guarded | fullaccess, default guarded) is a HARNESS
TOOL-EXECUTION posture only. It controls whether ordinary tool calls (terminal commands, file
reads/edits) prompt the user for permission — it does NOT touch the workflow approval gates
(R-011-01..13) or any hook. Switch with the /access command; record the change.
```

## Access mode

`workflow-state.yaml.access_mode` is purely about **harness permission prompts**, not the workflow.
The pipeline still runs the same, and every gate above still asks. Default `guarded`.
Switch with `/access full | guarded | status`.

```text
guarded   (default): the fullaccess allowlist is removed; tool calls prompt as normal.
fullaccess          : .claude/settings.json permissions.allow grants Bash + file tools so they run
                      without a per-call prompt.
```

fullaccess uses a permission **allowlist**, NOT `bypassPermissions` / `--dangerously-skip-permissions`.
The bypass mode is refused by Claude Code under root/sudo, so it must not be used. The allowlist works
for every user (including root), each tool is explicitly allowed, and the PreToolUse hooks still run
(destructive/secret/scope guards keep blocking).

`access_mode` ONLY removes the per-tool permission prompt. It does NOT change any of the following —
they apply identically in both modes:

```text
- All R-011 gates activated by execution mode or risk (create coders, governed analysis review,
  skip QC, downgrade blocker, expand scope, workflow policy/state changes, and destructive actions).
- The scope-guard / secret-guard / destructive-guard hooks — they still block (R-006, R-013, R-011-07).
- Production deployment and irreversible data actions still require explicit user approval.
```

So `fullaccess` = "you have terminal + file access without being asked each time", while the workflow
keeps asking for everything it must ask. Implemented by `scripts/access-mode.py` (writes
settings.json + workflow-state.yaml); takes effect for new sessions or via the harness permission UI.

## Approval record

Every approval must be recorded in one of:

```text
.maestro/work/tasks/<task-id>/memory-updates.yaml
.maestro/registry/agents.yaml
.maestro/runtime/workflow-state.yaml
.claude/changelog.md
CHANGELOG.md
```

## Violation handling

Stop and ask Coordinator to request user approval.
