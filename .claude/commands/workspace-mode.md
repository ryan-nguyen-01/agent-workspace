# /workspace-mode

## Purpose

Switch the workspace distribution mode recorded in `.runtime/context/workflow-state.yaml`.

Use this when turning the reusable framework distribution into an applied workspace, or when restoring a clean framework-template seed.

## Responsible agent

coordinator

## Required rules

```text
00-core-rules.md
01-project-brain-rules.md
11-approval-gates.md
12-artifact-contracts.md
13-security-secret-rules.md
```

## Usage

```text
/workspace-mode framework-template
/workspace-mode workspace
/workspace-mode status
/workspace-mode repair
```

Codex users should invoke this as natural language, for example:

```text
coord: workspace-mode workspace
coord: workspace-mode framework-template
coord: workspace-mode repair
```

## Allowed modes

```yaml
framework-template:
  distribution_mode: "framework-template"
  instance_status: "not_applied"
  current_state: "NEED_ONBOARDING"
  meaning: "Reusable agent-workspace distribution; onboarding is expected later."

workspace:
  distribution_mode: "workspace"
  instance_status: "applied"
  current_state: "NEED_ONBOARDING"
  meaning: "Applied coordination workspace; clone services/ and run onboarding next."
```

## Workflow

```text
1. Read .runtime/context/workflow-state.yaml.
2. If command is status, report distribution_mode, instance_status, current_state, and active_task_id.
3. If command is repair, route to workflow-policy and run the mode consistency checklist.
   - Read `.runtime/context/project-brain.yaml` and `.runtime/context/service-catalog.yaml`.
   - Repair is available only when Project Brain says `distribution.mode: workspace`, Project Brain says `instance_status: onboarded|applied`, and service catalog status is `onboarded|ready|generated|active`.
   - If repair is available, show the findings and ask for explicit confirmation before writing.
   - If user already explicitly requested repair/write, update `.runtime/context/workflow-state.yaml` directly through Coordinator.
   - Repair may update only `.runtime/context/workflow-state.yaml` and only when Project Brain + service catalog prove this is an older applied workspace.
4. Validate requested mode is framework-template or workspace.
5. If active_task_id is not null, deny the switch and ask the user to finish or clear the active task first.
6. Require explicit user intent for the requested mode; do not infer mode switches from unrelated tasks.
7. Update only these workflow-state fields:
   - distribution_mode
   - instance_status
   - current_state
   - updated_at
   - updated_by
   - reason
   - notes
8. Do not modify project-brain.yaml, service-catalog.yaml, agent-registry.yaml, services/, or inputs/.
9. Report the next recommended command.
```

## State write rules

```text
Switching to framework-template:
  distribution_mode: "framework-template"
  instance_status: "not_applied"
  current_state: "NEED_ONBOARDING"
  reason: "Workspace mode switched to reusable framework template."

Switching to workspace:
  distribution_mode: "workspace"
  instance_status: "applied"
  current_state: "NEED_ONBOARDING"
  reason: "Workspace mode switched to applied workspace; onboarding required."
```

## Stop conditions

```text
active_task_id is not null
requested mode is unknown
request would mutate files outside .runtime/context/workflow-state.yaml
request tries to skip onboarding for applied-service work
request would delete or rewrite services/, inputs/, project brain, or agent registry
repair cannot prove applied workspace mode from Project Brain + service catalog
```

## Output format

```yaml
mode_switch:
  status: "switched|unchanged|denied"
  from:
    distribution_mode: "<old>"
    instance_status: "<old>"
    current_state: "<old>"
  to:
    distribution_mode: "<new>"
    instance_status: "<new>"
    current_state: "<new>"
  next_command: "/onboard|/status|null"
  reason: "<reason>"
```
