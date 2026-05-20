# Codex Instructions — agent-workspace

Use this file when Codex opens this repository.

## Project Type

This repository is `agent-workspace`, a coordinator-driven AI workflow workspace. It is not an application repo and not an SDK.

Application repositories live under:

```text
services/<service-name>/
```

Reference docs live under:

```text
inputs/
```

## Framework-template Mode

When `.runtime/context/workflow-state.yaml` contains:

```yaml
distribution_mode: "framework-template"
instance_status: "not_applied"
```

Codex is maintaining the reusable framework distribution. In this mode, `NEED_ONBOARDING`, empty service catalogs, and seed Project Brain values are expected and must not block changes to framework files.

Classify early:

```yaml
target_scope: framework | applied_service | unknown
requires_onboarding: false   # for framework maintenance
```

Framework maintenance includes `AGENTS.md`, `CLAUDE.md`, `COMMAND.md`, `.agent/**`, `.claude/agents/**`, `.claude/commands/**`, `.codex/**`, `.cursor/**`, `.gemini/**`, `.github/copilot-instructions.md`, `scripts/**`, and root docs such as `SETUP.md`, `QUICKSTART.md`, `GUIDELINES.md`, and `CHANGELOG.md`.

Do not read project brain, service catalog, service brain files, agent registry, or test policy for framework maintenance unless the requested change directly touches those contracts. Require onboarding only before analyzing or coding application repositories under `services/<service-name>/`.

## Required Entry Points

Read these first:

```text
AGENTS.md
.agent/workflow.md
.runtime/context/workflow-state.yaml
COMMAND.md
```

Use `CLAUDE.md` as the most complete project policy reference, even when not running Claude Code.

## Operating Rules

```text
Every user request enters through /coord.
Do not jump directly to coder-leader, qc-runner, or generated coders from raw user input.
Do not code application source under services/<service-name>/ before .runtime/tasks/<task_id>/task-analysis.yaml exists.
For applied-service work, task-analysis.yaml must include context_plan before planning/coding; context_plan defines the bounded read set and expansion triggers.
Use .runtime/context/workflow-state.yaml.active_task_id as the current task pointer.
If architecture_review.required is true, do not plan/code before architecture-review.yaml decision is approved.
Generated coders write only inside allowed_write_paths from .runtime/context/agent-registry.yaml.
Use signature-first context loading: .runtime/context/index.yaml -> project_profile/service catalog summaries -> relevant service profile.context_hints -> specific evidence files. Do not broad-scan services/ or .claude/skills/** by default.
Use .runtime/context/model-routing.yaml for model profiles. In Codex, deep reasoning defaults to GPT-5.5 and coding defaults to the configured Codex coding model (`gpt-5.3-codex` by default). Switch defaults through model-routing.yaml.model_overrides; do not edit agent files or remove stable profiles to switch models.
Use .runtime/context/agent-activity.yaml for /status activity, elapsed/ETA, token budget, token usage, and cost reporting. If exact usage is unavailable, mark unknown or estimated; do not invent token/cost numbers.
Use .runtime/context/response-ui.yaml for status, model report, review, dev, policy, and final response layout. User-requested format wins unless it hides required evidence or unknown/estimated metric labels.
Framework-template maintenance may use workflow.md §6.2 lightweight fast-track instead of full task artifacts when the change is trivial and does not affect approval gates, security rules, state machine, generated coder scope, destructive commands, or services/<service-name>/ source.
For migrated workspaces or artifact-only snapshots, run `/policy-check snapshot --root <workspace-or-snapshot>` before trusting DEV_DONE/QC_DONE state. This is an agent-native checklist, not a Python/Node/script dependency.
Never copy .claude/ into service repos.
Never write secrets, tokens, raw cookies, private keys, or long logs into .runtime artifacts or tool adapter files.
```

## Codex Sandbox Boundary

`.codex/config.toml` is a project-level safety aid, not a hard per-service permission system. It is only loaded after the user trusts this project, and Codex may still allow writes under the trusted repository root depending on the active user config and CLI version.

For application source under `services/<service-name>/`, treat service write scope as a workflow contract:

```text
1. Read .runtime/context/workflow-state.yaml.active_task_id.
2. Read .runtime/tasks/<active_task_id>/task-analysis.yaml.
3. Confirm task-analysis.yaml.context_plan exists and has medium/high confidence for applied-service work.
4. Read .runtime/context/agent-registry.yaml.
5. Write only inside the assigned coder's allowed_write_paths.
```

For framework maintenance, do not read active_task task artifacts or agent-registry.yaml unless the requested change directly concerns those contracts.

## Task Contract

Task IDs use:

```text
TASK-YYYYMMDD-NNN-slug
```

All task artifacts stay in:

```text
.runtime/tasks/<task_id>/
```

Model/status artifacts:

```text
.runtime/context/model-routing.yaml
.runtime/context/agent-activity.yaml
.runtime/context/response-ui.yaml
.runtime/status.md
.runtime/status.html
```

Canonical task artifacts:

```text
task-input.md
task.yaml
task-updates.yaml
task-analysis.yaml
architecture-review.yaml       optional
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

Do not create a separate handoff folder. The Dev-to-QC handoff is `.runtime/tasks/<task_id>/qc-handoff.md`.

## Policy Consistency Check

Use the Workflow Policy agent for state/artifact drift:

```text
/policy-check snapshot --root .
/policy-check snapshot --root DATA
/policy-check snapshot --root DATA --write-report
```

The checker supports artifact-only snapshots and must not require Python, Node, jq, or shell helpers. If `services/` is absent, it reports `services_available: false` and validates recorded `.runtime/` evidence only.

Do not trust `DEV_DONE` unless `dev-verification.yaml` exists and has `result` or `verdict` equal to `DEV_DONE`. Do not trust `QC_DONE`/`PASS` while required QC cases are blocked/pending/not_run/failed or notes still require manual/retest evidence.

## Codex Slash Menu

Codex does not auto-register this repository's `.claude/commands/*.md` files in the Codex `/` popup. The Codex slash menu is owned by the Codex TUI and currently shows Codex built-ins such as `/model`, `/review`, `/plan`, `/status`, `/skills`, `/hooks`, `/mcp`, `/apps`, and `/plugins`.

Treat the commands below as `agent-workspace` workflow intents. If the user types one of them in natural language or asks for that phase, execute the matching contract from `.claude/commands/<name>.md`; do not expect Codex autocomplete to list them.

When instructing a human using Codex, prefer `coord: <request>` or `theo /coord: <request>` instead of a bare leading `/coord`, because Codex may intercept unknown leading slash commands before they reach the model.

For status in Codex or any terminal, `python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json>` renders the workflow state, activity dashboard, and model-profile map from `.runtime/context/`. Add `--write` to generate `.runtime/status.md` and `.runtime/status.html`. Use `python3 scripts/agent-activity.py` for adapter telemetry updates and `python3 scripts/architecture-health-check.py --strict` for optional deterministic drift checks; neither replaces agent-native `/policy-check`.

## Agent Workspace Commands

```text
/coord
/onboard
/create-coders
/analyze-task
/plan-dev
/dev
/verify-dev
/handoff-qc
/qc
/bug
/sync-memory
/skills
/resume-task
/workspace-mode
/policy-check
/status
```

## Safe Default

When uncertain, mark facts as `unknown`, cite the missing evidence, and route to `/policy-check` or ask the user through Coordinator.
