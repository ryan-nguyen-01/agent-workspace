# Gemini Instructions — agent-workspace

Use this file when Gemini works in this repository.

## Repository Role

`agent-workspace` is a coordination workspace for AI-driven software engineering workflows. It is not application source code.

```text
inputs/              User-provided PRD/HLD/ADR/OpenAPI/glossary/runbooks
services/            Local clones of application repositories
.runtime/context/     Durable brain, service catalog, agent registry, workflow state
.runtime/tasks/       Per-task artifacts
.runtime/bugs/        Bug routing artifacts
```

## Framework-template Mode

If `.runtime/context/workflow-state.yaml` has `distribution_mode: framework-template` and `instance_status: not_applied`, treat this repository as the reusable framework distribution. `NEED_ONBOARDING`, empty service catalogs, and seed brain values are expected.

For framework maintenance tasks that edit docs, workflow rules, templates, commands, tool adapters, workflow agents, or helper scripts:

```yaml
target_scope: framework
requires_onboarding: false
```

Do not require onboarding, service catalog, generated coders, or service brain freshness for those tasks. Require onboarding only before analyzing or coding application source under `services/<service-name>/`.

## Required Reading

```text
AGENTS.md
CLAUDE.md
COMMAND.md
.agent/workflow.md
.runtime/context/workflow-state.yaml
```

## Coordination Policy

```text
Every request starts at /coord.
Classify target_scope before broad brain/service reads.
No application coding under services/<service-name>/ before task-analysis.yaml.
No applied-service planning/coding before task-analysis.yaml.context_plan exists with medium/high confidence.
No planning/coding before approved architecture-review.yaml when architecture_review.required is true.
No direct raw-user routing to coder-leader, qc-runner, generated coders, or built-in coders.
Specialist advisors live under .claude/agents/specialists/<category>/ (19 advisor-only experts). Invoke them in-pipeline per R-016 and task-analysis.yaml.advisory_required; they only write .runtime/tasks/<task_id>/advisories/<id>.yaml, never application code, never assign coders or mark gates, and are never a raw-user entrypoint.
Gemini has no hook runtime; the scope/secret/destructive guardrails in scripts/hooks/ do not auto-enforce here. Follow R-000/R-006/R-013/R-011-07 and R-017 manually: no source edit without the task-analysis gate + coder scope, no secrets in writes, destructive commands need explicit user approval.
Generated coders must obey agent-registry.yaml allowed_write_paths and forbidden_paths.
Use signature-first context loading: memory index, project/service profile summaries, service context hints, then specific evidence files. Do not broad-scan source or skills by default.
Use `.runtime/context/model-routing.yaml` for model profiles and `.runtime/context/agent-activity.yaml` for `/status` activity/ETA/token/cost reporting.
Switch models through `.runtime/context/model-routing.yaml.model_overrides`; do not edit agent files or remove stable profiles to switch models.
Use `.runtime/context/response-ui.yaml` for markdown/text response structure.
Use `python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json>` as a terminal status mirror when project slash commands are not exposed. Add `--write` to generate `.runtime/status.md` and `.runtime/status.html`. Optional helpers: `python3 scripts/agent-activity.py` for telemetry updates and `python3 scripts/architecture-health-check.py --strict` for deterministic drift checks.
Framework-template maintenance may use workflow.md §6.2 lightweight fast-track evidence for trivial changes that do not alter approval gates, security rules, state machine, generated coder scope, destructive behavior, or services/<service-name>/ source.
Switch distribution_mode only via onboarding or an explicit user-approved edit to workflow-state.yaml (R-011-13); do not change mode fields ad hoc.
For migrated workspaces or artifact-only snapshots, run `/policy-check snapshot --root <workspace-or-snapshot>` before trusting DEV_DONE/QC_DONE state. This is an agent-native checklist, not a Python/Node/script dependency.
```

## Task Policy

Task IDs use:

```text
TASK-YYYYMMDD-NNN-slug
```

All artifacts for a task live in:

```text
.runtime/tasks/<task_id>/
```

Use `task-updates.yaml` as the append-only update log.

Do not create a separate handoff folder; `qc-handoff.md` inside the task folder is the single Dev-to-QC handoff.

## Safety

Never write secrets, private keys, tokens, raw cookies, or long logs into `.runtime/` artifacts or tool adapter files.

If uncertain, mark the fact `unknown`, cite what evidence is missing, and ask the user through Coordinator or route to `/policy-check`.

Do not fabricate exact token usage, model cost, elapsed time, or ETA. If Gemini does not expose reliable metrics, write `unknown` or clearly marked estimates in `agent-activity.yaml`.
