# Gemini Instructions — maestro

Use this file when Gemini works in this repository.

## Repository Role

`maestro` is a product-development workspace with an agent control plane.

```text
.maestro/                  Control plane, knowledge, work, memory, history, local runtime
docs/                 Official product and engineering documentation
apps|services|packages|infra|tests/  Product implementation
inputs/               External references awaiting curation
```

## Framework Maintenance Scope

Treat this repository as the `maestro` product-development control plane. `NEED_ONBOARDING`,
an empty component registry, and seed project knowledge are expected for framework-only maintenance.

For framework maintenance tasks that edit docs, workflow rules, templates, commands, tool adapters, workflow agents, or helper scripts:

```yaml
target_scope: framework
requires_onboarding: false
methodology:
  selected: risk-based-routing
  overlays: []
  industry_patterns: []
run_required: false
```

Do not require onboarding or component knowledge for framework-only tasks. Require onboarding only
when assisted/governed product work depends on missing component facts.

## Required Reading

```text
AGENTS.md
CLAUDE.md
COMMAND.md
.maestro/engine/workflow.md
.maestro/runtime/workflow-state.yaml
```

## Coordination Policy

```text
Every request starts at /coord for classification.
Classify target_scope before broad brain/service reads.
Select direct, assisted, or governed first, then add Spec-Driven Development, Eval-Driven AI
Development, or Enterprise Agent Governance overlays when traceability, eval-driven AI, or governed
autonomous operation is required.
Create a run under `.maestro/work/runs/` when work needs pause/resume, multiple attempts, trace/eval
evidence, or human approval.
Direct low-risk work may edit source without persistent artifacts and must disclose user verification.
Assisted work requires task.yaml. Governed work requires task-analysis.yaml and a medium/high-confidence context_plan.
No planning/coding before approved architecture-review.yaml when architecture_review.required is true.
No direct raw-user routing to coder-leader, qc-runner, generated coders, or built-in coders.
Specialist advisors live under .claude/agents/specialists/<category>/ (19 advisor-only experts). Invoke them in-pipeline per R-016 and task-analysis.yaml.advisory_required; they only write .maestro/work/tasks/<task_id>/advisories/<id>.yaml, never application code, never assign coders or mark gates, and are never a raw-user entrypoint.
Gemini has no hook runtime; enforce the selected execution mode manually, never write secrets, and
require explicit approval for destructive actions.
Generated coders must obey agents.yaml allowed_write_paths and forbidden_paths.
Use signature-first context loading: memory index, project/component profile summaries, service context hints, then specific evidence files. Do not broad-scan source or skills by default.
Use `.maestro/config/model-routing.yaml` for model profiles and `.maestro/runtime/agent-activity.yaml` for `/status` activity/ETA reporting.
Switch models through `.maestro/config/model-routing.yaml.model_overrides`; do not edit agent files or remove stable profiles to switch models.
Use `.maestro/config/response-ui.yaml` for markdown/text response structure.
Use `python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json>` as a terminal status mirror when project slash commands are not exposed. Add `--write` to generate `.maestro/runtime/reports/status.md` and `.maestro/runtime/reports/status.html`. Optional helpers: `python3 scripts/agent-activity.py` for telemetry updates and `python3 scripts/architecture-health-check.py --strict` for deterministic drift checks.
Framework maintenance may use workflow.md §6.2 lightweight fast-track evidence for trivial changes that do not alter approval gates, security rules, state machine, generated coder scope, destructive behavior, or services/<service-name>/ source.
Workflow behavior is controlled by current state, execution mode, target scope, and approval gates.
For migrated workspaces or artifact-only snapshots, run `/policy-check snapshot --root <workspace-or-snapshot>` before trusting DEV_DONE/QC_DONE state. This is an agent-native checklist, not a Python/Node/script dependency.
```

## Task Policy

Task IDs use:

```text
TASK-YYYYMMDD-NNN-slug
```

All artifacts for a task live in:

```text
.maestro/work/tasks/<task_id>/
```

Use `task-updates.yaml` as the append-only update log.

Do not create a separate handoff folder; `qc-handoff.md` inside the task folder is the single Dev-to-QC handoff.

## Safety

Never write secrets, private keys, tokens, raw cookies, or long logs into `.maestro/`, product docs, or tool adapter files.

If uncertain, mark the fact `unknown`, cite what evidence is missing, and ask the user through Coordinator or route to `/policy-check`.

Do not fabricate exact elapsed time or ETA. If Gemini does not expose reliable metrics, write `unknown` or clearly marked estimates in `agent-activity.yaml`.
