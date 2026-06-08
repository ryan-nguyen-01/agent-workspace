# GitHub Copilot — Maestro Instructions

## Project type

This is **maestro**: a product-development workspace with a coordinator-driven agent control plane.

Product code lives in registered roots (`apps/`, `services/`, `packages/`, `infra/`, `tests/`).
Official product documentation lives in `docs/`; `.maestro/` holds the development control plane.

## Framework Maintenance Scope

This repository is the `maestro` product-development control plane. Do not use a distribution
mode to decide routing. `NEED_ONBOARDING`, an empty component registry, and seed project knowledge are
expected for framework-only maintenance and must not block maintenance of framework files.

For framework maintenance, classify first:

```yaml
target_scope: framework
requires_onboarding: false
methodology:
  selected: risk-based-routing
  overlays: []
  industry_patterns: []
run_required: false
```

Framework maintenance covers docs, scripts, workflow rules, templates, slash commands, workflow agent
definitions, and tool entrypoints. Require onboarding only when assisted/governed product work depends
on missing component facts.

## How to use this workspace

Use `COMMAND.md` to choose a slash command. For natural-language requests, route through `/coord`.

The coordinator is the single entry point for all requests:

- Project setup / onboarding
- Task intake (HLD, LLD, tickets, bug reports, direct instructions)
- Optional architecture review for cross-service/API/data/event/security/infra risk
- Implementation planning and coding
- Dev verification and QC
- Memory updates
- Skill maintenance through `/skills`

Do **not** jump directly to sub-agents (onboarding, coder-leader, qc-runner, etc.) from raw user input. The coordinator handles routing.

## Copilot operating rules

- Open the `maestro` root, not an individual service folder, when running workflow tasks.
- Classify `target_scope` before broad project-knowledge or component-registry reads.
- Do not copy `.claude/` into service repositories.
- Select `direct`, `assisted`, or `governed` before editing source.
- Add Spec-Driven Development, Eval-Driven AI Development, or Enterprise Agent Governance overlays
  when traceability, eval-driven AI, or governed autonomous operation is required.
- Create a run under `.maestro/work/runs/` when work needs pause/resume, multiple attempts, trace/eval
  evidence, or human approval.
- Direct low-risk work may omit persistent artifacts and must disclose user-owned verification.
- Assisted work requires task.yaml; governed work requires task-analysis.yaml and context_plan.
- Use signature-first context loading: Memory Index, project/component profile summaries, service context hints, then specific evidence files. Do not broad-scan source or skills by default.
- Use `.maestro/config/model-routing.yaml` for model profiles and `.maestro/runtime/agent-activity.yaml` for `/status` activity/ETA reporting.
- Switch models through `.maestro/config/model-routing.yaml.model_overrides`; do not edit agent files or remove stable profiles to switch models.
- Use `.maestro/config/response-ui.yaml` for markdown/text response structure and generated status artifacts. Copilot support is best-effort; do not claim native Copilot panel customization.
- Framework maintenance may use workflow.md §6.2 lightweight fast-track evidence for trivial changes that do not affect approval gates, security rules, workflow state machine, generated coder scopes, destructive behavior, or application source under `services/`.
- If `task-analysis.yaml` requires architecture review, do not plan or code until `architecture-review.yaml` exists with `decision: approved`.
- Generated service coders may write only inside paths approved in `.maestro/registry/agents.yaml`.
- Specialist advisors live under `.claude/agents/specialists/<category>/` (19 advisor-only experts). Invoke them in-pipeline per `R-016` and `task-analysis.yaml.advisory_required`; they only write `.maestro/work/tasks/<task_id>/advisories/<id>.yaml`, never application code, never assign coders or mark gates, and are never a raw-user entrypoint.
- Copilot has no hook runtime, so enforce the selected execution mode manually, never write secrets,
  and require explicit approval for destructive actions.
- Treat `inputs/` as read-only user reference docs.
- Treat `.maestro/knowledge/` and `.maestro/work/` as shared control-plane artifacts; `.maestro/runtime/` is local-only.
- Do not store secrets, tokens, raw cookies, private keys, or long logs in `.maestro/`, product docs, or tool adapter files.
- Do not fabricate exact elapsed time or ETA. If Copilot does not expose reliable metrics, write `unknown` or clearly marked estimates.
- If uncertain, mark the fact `unknown` and ask the user or route to `/policy-check`.

## Key files

| File | Purpose |
| --- | --- |
| `COMMAND.md` | Canonical slash command index |
| `CLAUDE.md` | Full system instructions and routing rules |
| `AGENTS.md` | Cross-agent entrypoint for non-Claude tools |
| `.maestro/engine/workflow.md` | End-to-end workflow policy |
| `.maestro/runtime/workflow-state.yaml` | Current workflow state |
| `.maestro/knowledge/project.yaml` | Durable workspace memory |
| `.maestro/registry/components.yaml` | Service inventory and source paths |
| `.maestro/registry/agents.yaml` | Active coder agents and approved scopes |
| `.maestro/registry/skills.yaml` | Skill selection and approval metadata |
| `.maestro/config/model-routing.yaml` | Agent model profile routing |
| `.maestro/runtime/agent-activity.yaml` | Agent activity dashboard and ETA telemetry |
| `.maestro/config/response-ui.yaml` | Response layout modes for chat/status/report outputs |
| `.maestro/runtime/reports/status.md` | Generated readable status artifact |
| `.maestro/runtime/reports/status.html` | Generated browser status dashboard |
| `.claude/agents/workflow/coordinator.agent.md` | Coordinator agent definition |
| `.claude/agents/workflow/solution-architect.agent.md` | Optional architecture review definition |
| `.claude/agents/specialists/README.md` | Specialist advisor catalog (19 advisors, quick-selection) |
| `scripts/hooks/` | Deterministic scope/secret/destructive guardrails (Claude adapter) |
| `.maestro/engine/docs/skill-catalog.md` | Skill discovery catalog (231 skills by domain) |

## Commands

```text
/coord          Universal entrypoint
/onboard        Scan inputs/ and services/, build workspace brain
/create-coders  Generate service coders after approval
/analyze-task   Create task-analysis.yaml before coding
/plan-dev       Plan implementation
/dev            Implement through Coder Leader and scoped coders
/verify-dev     Evaluate Code Done
/handoff-qc     Create QC handoff
/qc             Run QC
/bug            Route defects
/sync-memory    Persist durable learnings
/skills         Maintain installed skills and registry metadata
/resume-task    Continue an interrupted task
/policy-check   Validate transitions, exceptions, and artifact snapshots
/status         Print state banner and agent activity dashboard using response UI mode
```

Terminal status mirror: `python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json>`; add `--write` to generate `.maestro/runtime/reports/status.md` and `.maestro/runtime/reports/status.html`. Optional helpers: `python3 scripts/agent-activity.py` for telemetry updates and `python3 scripts/architecture-health-check.py --strict` for deterministic drift checks.

## Workflow states (summary)

```
NEW → NEED_ONBOARDING → ONBOARDED → NEED_AGENT_CREATION_APPROVAL → AGENTS_READY
→ READY_FOR_ANALYSIS → ANALYZED → ARCHITECTURE_REVIEWING → PLANNED
→ IN_DEV → DEV_VERIFYING → DEV_BLOCKED → IN_DEV (recovery)
→ DEV_DONE → QC_READY → QC_TESTING → BLOCKED_BY_BUG → FIXING → DEV_VERIFYING
→ DEV_DONE → QC_RETESTING → QC_DONE → MEMORY_SYNCING → DONE
```

## Coordinator startup behavior

On every new conversation, the coordinator will:

1. Read `.maestro/engine/workflow.md` and `.maestro/runtime/workflow-state.yaml`
2. Read `.maestro/knowledge/index.yaml`, project knowledge, component registry, and agent registry when present
3. Check brain freshness fields and registered coders
4. Report current state, then process your request

## Workspace layout

```text
maestro/
  .maestro/engine/        Tool-neutral workflow source
  .maestro/runtime/      Memory, task artifacts, and bug records
  .claude/       Claude adapter
  inputs/        User-provided PRD/HLD/ADR/specs/runbooks
  services/      Registered deployable services, workers, and gateways
```

## Anti-guessing rules (Karpathy-aligned)

All agents in this system follow 4 principles:

1. State uncertainty explicitly — never guess silently
2. Ask clarification when missing facts affect scope, security, or correctness
3. Do not fabricate facts; use `unknown` + evidence-needed
4. Claim "done" only with concrete evidence (file, test, artifact)
