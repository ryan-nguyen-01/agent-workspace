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
Do not code before .runtime/tasks/<task_id>/task-analysis.yaml exists.
Use .runtime/context/workflow-state.yaml.active_task_id as the current task pointer.
If architecture_review.required is true, do not plan/code before architecture-review.yaml decision is approved.
Generated coders write only inside allowed_write_paths from .runtime/context/agent-registry.yaml.
Never copy .claude/ into service repos.
Never write secrets, tokens, raw cookies, private keys, or long logs into .runtime artifacts or tool adapter files.
```

## Codex Sandbox Boundary

`.codex/config.toml` is a project-level safety aid, not a hard per-service permission system. It is only loaded after the user trusts this project, and Codex may still allow writes under the trusted repository root depending on the active user config and CLI version.

Treat service write scope as a workflow contract:

```text
1. Read .runtime/context/workflow-state.yaml.active_task_id.
2. Read .runtime/tasks/<active_task_id>/task-analysis.yaml.
3. Read .runtime/context/agent-registry.yaml.
4. Write only inside the assigned coder's allowed_write_paths.
```

## Task Contract

Task IDs use:

```text
TASK-YYYYMMDD-NNN-slug
```

All task artifacts stay in:

```text
.runtime/tasks/<task_id>/
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

## Codex Slash Menu

Codex does not auto-register this repository's `.claude/commands/*.md` files in the Codex `/` popup. The Codex slash menu is owned by the Codex TUI and currently shows Codex built-ins such as `/model`, `/review`, `/plan`, `/status`, `/skills`, `/hooks`, `/mcp`, `/apps`, and `/plugins`.

Treat the commands below as `agent-workspace` workflow intents. If the user types one of them in natural language or asks for that phase, execute the matching contract from `.claude/commands/<name>.md`; do not expect Codex autocomplete to list them.

When instructing a human using Codex, prefer `coord: <request>` or `theo /coord: <request>` instead of a bare leading `/coord`, because Codex may intercept unknown leading slash commands before they reach the model.

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
/policy-check
/status
```

## Safe Default

When uncertain, mark facts as `unknown`, cite the missing evidence, and route to `/policy-check` or ask the user through Coordinator.
