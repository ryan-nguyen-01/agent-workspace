---
description: "agent-workspace /policy-check — Validate workflow transitions, approval gates, exception requests, and recorded artifact snapshots without requiring ..."
argument-hint: "[request or args]"
---

You are running the agent-workspace `/policy-check` workflow command inside Codex.

Follow `.codex/AGENTS.md` (or `AGENTS.md`) routing and the framework rules. Route every
request through the coordinator model; do not bypass approval gates, security/secret rules,
or the task-analysis source-edit gate. If the agent-workspace framework files
(`.agent/`, `.runtime/`, `.claude/commands/policy-check.md`) are present, defer to them as the
authoritative contract — this prompt is a portable mirror.

User input for this command: $ARGUMENTS

---
## Command contract (mirrored from .claude/commands/policy-check.md)

# /policy-check

## Purpose

Validate workflow transitions, approval gates, exception requests, and recorded artifact snapshots without requiring external scripts or runtimes.

## Responsible agent

workflow-policy

## Required rules

```text
00-core-rules.md
11-approval-gates.md
12-artifact-contracts.md
13-security-secret-rules.md
```

## Workflow

```text
1. Read current state.
2. Read requested transition or exception.
3. Check required artifacts.
4. Check responsible agent permissions.
5. Check approval gates.
6. For whole-workspace consistency or migration checks, run the Workflow Policy invariant checklist below.
7. For shared artifact-only snapshots, set services_available=false when services/ is absent and validate recorded artifacts only.
8. Return allow, deny, or needs_user_approval.
```

## Snapshot consistency check

Use this when validating a workspace migrated from an older framework version or a shared `.runtime/` evidence snapshot without `services/`.

```text
/policy-check snapshot --root .
/policy-check snapshot --root DATA
/policy-check snapshot --root DATA --write-report
```

The checker is the `workflow-policy` agent itself. It must not require Python, Node, jq, shell scripts, or any other local runtime. It must not treat missing or empty `services/` as a project defect. It reports `services_available: false` and validates recorded workflow/artifact evidence only.

Optional deterministic CI/local helper:

```text
python3 scripts/architecture-health-check.py --strict
python3 scripts/architecture-health-check.py --strict --write-report
```

This helper catches mechanical drift in counts, model routing, response UI, status artifacts, and cross-tool entrypoints. It is a safety net only; it does not replace this command's agent-native policy decision.

It fails when it finds any of these invariants broken:

```text
workflow-state distribution_mode disagrees with Project Brain distribution.mode
workflow-state instance_status is seed/not_applied while Project Brain says onboarded/applied
DEV_DONE or later exists without dev-verification.yaml verdict/result DEV_DONE
QC_DONE/PASS exists while required cases are blocked/pending/not_run/failed
QC_DONE/PASS exists while notes still require manual/retest evidence
task.yaml artifact manifest disagrees with files in the task folder
agent-registry top-level status conflicts with active/approved coder entries
applied-service task advances to PLANNED/IN_DEV without usable task-analysis.yaml.context_plan
model-routing.yaml is missing when an agent claims a specific model profile
agent-activity.yaml claims exact token/cost/ETA values without evidence or marks estimates as actual
response-ui.yaml is missing when a tool entrypoint claims configurable response layout
```

## Required reads by check type

```text
transition:
  - .runtime/context/workflow-state.yaml
  - requested transition/actor
  - relevant rule files only

workspace:
  - .runtime/context/workflow-state.yaml
  - .runtime/context/project-brain.yaml
  - .runtime/context/service-catalog.yaml
  - .runtime/context/agent-registry.yaml
  - .runtime/context/model-routing.yaml
  - .runtime/context/agent-activity.yaml
  - .runtime/context/response-ui.yaml

snapshot:
  - <root>/.runtime/context/workflow-state.yaml
  - <root>/.runtime/context/project-brain.yaml
  - <root>/.runtime/context/service-catalog.yaml
  - <root>/.runtime/context/agent-registry.yaml
  - <root>/.runtime/context/model-routing.yaml
  - <root>/.runtime/context/agent-activity.yaml
  - <root>/.runtime/context/response-ui.yaml
  - active task folder and workflow-state.parallel_tasks folders

task:
  - .runtime/tasks/<task-id>/task.yaml
  - task-updates.yaml
  - task-analysis.yaml
  - artifact files named by task.yaml or required by current state
```

## Report artifact

When the user asks for a saved report, write YAML using:

```text
.agent/templates/policy-check-report.template.yaml
```

Default report paths:

```text
.runtime/policy-check-report.yaml
.runtime/tasks/<task-id>/policy-check-report.yaml
```

## Output format

```yaml
policy_decision: "allow|deny|needs_user_approval"
reason: "<reason>"
missing_artifacts: []
required_next_action: "<action>"
policy_check_report: "optional path or inline summary"
```
