# GitHub Copilot — Agent Workspace Instructions

## Project type

This is **agent-workspace**: a coordinator-driven AI workflow workspace for software engineering.

It is not an application repository. Application/service repositories are cloned under `services/<service-name>/`, while this repository holds the agent engine, workflow rules, memory, task artifacts, and service coder scopes.

## Framework-template mode

When `.runtime/context/workflow-state.yaml` has `distribution_mode: framework-template` and `instance_status: not_applied`, this repository is the reusable framework distribution. `NEED_ONBOARDING`, empty service catalogs, and seed Project Brain values are expected and must not block maintenance of framework files.

For framework maintenance, classify first:

```yaml
target_scope: framework
requires_onboarding: false
```

Framework maintenance covers docs, scripts, workflow rules, templates, slash commands, workflow agent definitions, and tool entrypoints in this repository. Do not require onboarding, service catalog, generated coders, or service brain freshness unless the task reads or writes application source under `services/<service-name>/`.

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

- Open the `agent-workspace` root, not an individual service folder, when running workflow tasks.
- Classify `target_scope` before broad Project Brain or service catalog reads.
- Do not copy `.claude/` into service repositories.
- Do not modify application source before `task-analysis.yaml` exists and the workflow has moved into implementation.
- For applied-service tasks, do not plan or code until `task-analysis.yaml.context_plan` exists with medium/high confidence.
- Use signature-first context loading: Memory Index, project/service profile summaries, service context hints, then specific evidence files. Do not broad-scan source or skills by default.
- Use `.runtime/context/model-routing.yaml` for model profiles and `.runtime/context/agent-activity.yaml` for `/status` activity/ETA/token/cost reporting.
- Switch models through `.runtime/context/model-routing.yaml.model_overrides`; do not edit agent files or remove stable profiles to switch models.
- Use `.runtime/context/response-ui.yaml` for markdown/text response structure and generated status artifacts. Copilot support is best-effort; do not claim native Copilot panel customization.
- Framework-template maintenance may use workflow.md §6.2 lightweight fast-track evidence for trivial changes that do not affect approval gates, security rules, workflow state machine, generated coder scopes, destructive behavior, or application source under `services/`.
- If `task-analysis.yaml` requires architecture review, do not plan or code until `architecture-review.yaml` exists with `decision: approved`.
- Generated service coders may write only inside paths approved in `.runtime/context/agent-registry.yaml`.
- Specialist advisors live under `.claude/agents/specialists/<category>/` (19 advisor-only experts). Invoke them in-pipeline per `R-016` and `task-analysis.yaml.advisory_required`; they only write `.runtime/tasks/<task_id>/advisories/<id>.yaml`, never application code, never assign coders or mark gates, and are never a raw-user entrypoint.
- Copilot has no hook runtime, so the scope/secret/destructive guardrails in `.claude/settings.json` + `scripts/hooks/` do not auto-enforce here. Follow `R-000`/`R-006`/`R-013`/`R-011-07` and `R-017` manually: no source edit without the task-analysis gate + coder scope, no secrets in writes, destructive commands need explicit user approval.
- Treat `inputs/` as read-only user reference docs.
- Treat `.runtime/context/`, `.runtime/tasks/`, and `.runtime/bugs/` as workflow/runtime artifacts.
- Do not store secrets, tokens, raw cookies, private keys, or long logs in `.runtime/` artifacts or tool adapter files.
- Do not fabricate exact token usage, model cost, elapsed time, or ETA. If Copilot does not expose reliable metrics, write `unknown` or clearly marked estimates.
- If uncertain, mark the fact `unknown` and ask the user or route to `/policy-check`.

## Key files

| File | Purpose |
| --- | --- |
| `COMMAND.md` | Canonical slash command index |
| `CLAUDE.md` | Full system instructions and routing rules |
| `AGENTS.md` | Cross-agent entrypoint for non-Claude tools |
| `.agent/workflow.md` | End-to-end workflow policy |
| `.runtime/context/workflow-state.yaml` | Current workflow state |
| `.runtime/context/project-brain.yaml` | Durable workspace memory |
| `.runtime/context/service-catalog.yaml` | Service inventory and source paths |
| `.runtime/context/agent-registry.yaml` | Active coder agents and approved scopes |
| `.runtime/context/skill-registry.yaml` | Skill selection and approval metadata |
| `.runtime/context/model-routing.yaml` | Agent model profile routing |
| `.runtime/context/agent-activity.yaml` | Agent activity dashboard, ETA, token/cost telemetry |
| `.runtime/context/response-ui.yaml` | Response layout modes for chat/status/report outputs |
| `.runtime/status.md` | Generated readable status artifact |
| `.runtime/status.html` | Generated browser status dashboard |
| `.claude/agents/workflow/coordinator.agent.md` | Coordinator agent definition |
| `.claude/agents/workflow/solution-architect.agent.md` | Optional architecture review definition |
| `.claude/agents/specialists/README.md` | Specialist advisor catalog (19 advisors, quick-selection) |
| `scripts/hooks/` | Deterministic scope/secret/destructive guardrails (Claude adapter) |
| `.agent/docs/skill-catalog.md` | Skill discovery catalog (231 skills by domain) |

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

Terminal status mirror: `python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json>`; add `--write` to generate `.runtime/status.md` and `.runtime/status.html`. Optional helpers: `python3 scripts/agent-activity.py` for telemetry updates and `python3 scripts/architecture-health-check.py --strict` for deterministic drift checks.

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

1. Read `.agent/workflow.md` and `.runtime/context/workflow-state.yaml`
2. Read `.runtime/context/index.yaml`, project brain, service catalog, and agent registry when present
3. Check brain freshness fields and registered coders
4. Report current state, then process your request

## Workspace layout

```text
agent-workspace/
  .agent/        Tool-neutral workflow source
  .runtime/      Memory, task artifacts, and bug records
  .claude/       Claude adapter
  inputs/        User-provided PRD/HLD/ADR/specs/runbooks
  services/      Local clones of application repositories
```

## Anti-guessing rules (Karpathy-aligned)

All agents in this system follow 4 principles:

1. State uncertainty explicitly — never guess silently
2. Ask clarification when missing facts affect scope, security, or correctness
3. Do not fabricate facts; use `unknown` + evidence-needed
4. Claim "done" only with concrete evidence (file, test, artifact)
