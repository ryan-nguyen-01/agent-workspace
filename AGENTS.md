# AGENTS.md

> Entry point for AI coding agents (Codex, Cursor, Aider, Sourcegraph Cody, Continue, etc.).
> Project docs are primarily in Vietnamese, but this file is in English so any agent can parse it.
> Claude Code reads [CLAUDE.md](CLAUDE.md) first; other agents should read this file.

Tool-specific entrypoints:

- Codex: [.codex/AGENTS.md](.codex/AGENTS.md)
- Cursor: [.cursor/rules/agent-workspace.mdc](.cursor/rules/agent-workspace.mdc)
- Gemini: [.gemini/GEMINI.md](.gemini/GEMINI.md)
- GitHub Copilot: [.github/copilot-instructions.md](.github/copilot-instructions.md)

## What this repo is

`agent-workspace` is a **workflow-coordinator-driven multi-agent framework** for software engineering. It is not an application. It defines:

- 12 workflow agents (see [.claude/agents/workflow/](.claude/agents/workflow/))
- 19 specialist advisors (advisor-only, in-pipeline) at [.claude/agents/specialists/](.claude/agents/specialists/) — see [R-016](.agent/rules/16-specialist-advisory-rules.md)
- 231 skills (12 workflow + 219 technical) at [.claude/skills/](.claude/skills/); discovery layer: [.agent/docs/skill-catalog.md](.agent/docs/skill-catalog.md)
- 18 workflow rules at [.agent/rules/](.agent/rules/)
- 22 templates at [.agent/templates/](.agent/templates/)
- 17 slash commands at [.claude/commands/](.claude/commands/)
- 2 built-in cross-cutting coders: `coder-infra` and `coder-database` at [.claude/agents/coders/](.claude/agents/coders/)
- Deterministic hook guardrails (scope/secret/destructive) at [scripts/hooks/](scripts/hooks/) — see [R-017](.agent/rules/17-hook-enforcement-rules.md)
- Durable memory at [.runtime/context/](.runtime/context/)
- User-provided reference docs (PRD, HLD, ADR, OpenAPI, glossary, runbooks) at [inputs/](inputs/) — onboarding scans these to seed the brain

The authoritative spec is [.agent/workflow.md](.agent/workflow.md). Read it before acting on non-trivial work.

This repository is the coordination workspace. Do not copy `.claude/` into each service repository. Users clone service repositories under `services/`, add reference docs under `inputs/`, then run onboarding from this repository. Do not treat `NEED_ONBOARDING`, empty `service-catalog.yaml`, or stale seed brain values as defects before services have been cloned and onboarding has run.

## Framework-template mode

This repository can be used in two modes:

- **Framework template:** `distribution_mode: "framework-template"` and `instance_status: "not_applied"` in [.runtime/context/workflow-state.yaml](.runtime/context/workflow-state.yaml). This is the reusable distribution. `NEED_ONBOARDING` is expected and must not block maintenance of framework files.
- **Applied workspace:** service repositories have been cloned under `services/`, reference docs have been added under `inputs/`, and onboarding has created the project brain/service contracts.

For framework-template maintenance, classify the request before brain checks:

```yaml
target_scope: framework
requires_onboarding: false
```

Framework maintenance includes docs, scripts, workflow rules, templates, command contracts, workflow agent definitions, and tool entrypoints in this repository. Do not require onboarding, service catalog, generated service coders, or service brain freshness unless the request reads or writes application source under `services/<service-name>/`.

## Rules you MUST follow

1. **Single entrypoint.** Every user request enters through `coordinator` (the `/coord` command). Do not jump straight to `coder-leader`, `qc-runner`, etc. from raw user input.
2. **No application coding without `task-analysis.yaml`.** The `task-analysis` agent normalizes applied-service intent/AC/risks first. R-000-06. Trivial framework-template maintenance may use the lightweight fast-track path.
3. **Scoped writes.** Generated service coders write only inside `allowed_write_paths` and never inside `forbidden_paths`. R-006-01..03.
4. **Approval gates.** User approval is required for: creating coder agents, expanding scope, skipping QC, downgrading a blocker bug, proceeding from task-analysis to coder-leader. Full list: [.agent/rules/11-approval-gates.md](.agent/rules/11-approval-gates.md).
5. **Anti-guessing.** If a fact is uncertain, mark `unknown` and ask. Do not fabricate. Critical claims need evidence (file/test/command/artifact). R-000-11..14.
6. **No secrets in artifacts.** Never write passwords, tokens, private keys, raw cookies, or long logs into `.runtime/` artifacts or tool adapter files. R-013-01..04.
7. **Project CLAUDE.md beats global CLAUDE.md.** Agents/aliases defined in `~/.claude/CLAUDE.md` that are not in this project's 12-agent list (below) must route through `coordinator` instead.
8. **Context economy.** For applied-service work, use `.runtime/context/index.yaml`, `project_profile`, service `profile.context_hints`, and `task-analysis.yaml.context_plan` before opening broad source context. Expand reads only when a recorded trigger requires it. R-001-18..24.
9. **Model routing, observability, and response UI.** Select agent model profiles from `.runtime/context/model-routing.yaml`, surface live activity/token/cost telemetry through `.runtime/context/agent-activity.yaml` and `/status`, and format status/reports/final answers through `.runtime/context/response-ui.yaml`. Never fabricate exact token/cost values. R-015-01..22.

## The 12 workflow agents

| Agent | Model profile | Role | Activates when |
|---|---|---|---|
| `coordinator` | `fast_router` | Routes, gates, holds workflow state | Every request enters here |
| `onboarding` | `deep_reasoning` | Builds Project Brain (scan-only) | Brain missing or stale |
| `agent-factory` | `coding_planner` | Generates service-specific coders | After onboarding + user approval |
| `task-analysis` | `deep_reasoning` | Normalizes input into task spec | Before any implementation |
| `solution-architect` | `deep_reasoning` | Reviews architecture risk and constraints | When task-analysis requires architecture review |
| `coder-leader` | `coding_planner` | Plans + coordinates service coders | Implementation phase |
| `dev-verification` | `verification` | Decides Code Done (≥80% + critical checks) | After implementation |
| `qc-handoff` | `fast_router` | Writes Dev→QC handoff doc | After Code Done |
| `qc-runner` | `verification` | Executes QC, classifies bugs | After handoff |
| `bug-router` | `deep_reasoning` | Routes blocker/non-blocker bugs | QC found a defect |
| `memory-update` | `memory_light` | Persists durable learnings | After meaningful workflow events |
| `workflow-policy` | `deep_reasoning` | Validates transitions and gates | State dispute |

Provider defaults live in `.runtime/context/model-routing.yaml`: Claude deep reasoning uses Opus, Claude coding uses Sonnet; Codex deep reasoning uses GPT-5.5, Codex coding uses the configured Codex coding model (`gpt-5.3-codex` by default).

## Built-in cross-cutting coders

`coder-infra` and `coder-database` are shipped with the framework as built-in cross-cutting coders. They are not generated from workspace onboarding, and they do not replace service-specific coders. Coder Leader may assign them only when the task scope matches their permission contract:

- `coder-infra`: Terraform/IaC, Kubernetes, Docker, CI/CD.
- `coder-database`: schema, migrations, queries, indexes.

## Workflow phases

```text
NEW
  → NEED_ONBOARDING / ONBOARDED
  → NEED_AGENT_CREATION_APPROVAL → AGENTS_READY
  → READY_FOR_ANALYSIS → ANALYZED → ARCHITECTURE_REVIEWING / PLANNED
  → IN_DEV → DEV_VERIFYING → DEV_DONE
  → QC_READY → QC_TESTING → QC_DONE
  → MEMORY_SYNCING → DONE
```

Current state lives in [.runtime/context/workflow-state.yaml](.runtime/context/workflow-state.yaml). Model routing lives in [.runtime/context/model-routing.yaml](.runtime/context/model-routing.yaml). Live activity/status telemetry lives in [.runtime/context/agent-activity.yaml](.runtime/context/agent-activity.yaml). Response layout modes live in [.runtime/context/response-ui.yaml](.runtime/context/response-ui.yaml). The `coordinator` writes every transition and activity update.

## Slash commands

These are `agent-workspace` workflow commands. Tool support differs by client: Claude Code can use `.claude/commands/*.md` directly, while Codex does not auto-register these files in its `/` popup. In Codex, treat them as workflow intents backed by `COMMAND.md` and `.claude/commands/*.md`.

Run any of these via the Claude Code CLI or by directly invoking the matching agent:

```text
/coord            Universal entrypoint — start here
/onboard          Build or refresh Project Brain
/create-coders    Generate service coders after approval
/analyze-task     Normalize a task into task-analysis.yaml
/plan-dev         Plan implementation
/dev              Implement code
/verify-dev       Evaluate Code Done
/handoff-qc       Create QC handoff
/qc               Run QC
/bug              Route defects
/sync-memory      Persist durable knowledge
/skills           Maintain installed skills and registry metadata
/resume-task      Continue an interrupted task
/access           Switch tool-permission posture: full / guarded (R-011-14)
/policy-check     Validate transitions, exceptions, and artifact snapshots
/status           Print state banner and agent activity dashboard using response UI mode
```

For tools that do not expose project slash commands, `python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json>` renders the status/model dashboard from `.runtime/context/`. Add `--write` to generate `.runtime/status.md` and `.runtime/status.html`. Tool adapters may update telemetry through `python3 scripts/agent-activity.py`; maintainers may run `python3 scripts/architecture-health-check.py --strict` as an optional deterministic drift check. Switch default models through `model-routing.yaml.model_overrides`, not by editing agent files.

## Fast-track lane (small tasks)

A trivial applied-service task may skip the user-approval gate on `task-analysis.yaml` and the full `implementation-plan.yaml`. It still requires `task-analysis.yaml.context_plan` and a lightweight `service-assignments.yaml` before source edits. Eligibility is strict — see workflow.md §6.2. All other gates still apply (scope, secrets, dev-verification, QC).

Eligible intents: `typo`, `comment`, `format`, `rename-local`, `docs-only`, `dependency-version-bump`, `config-value-tweak`. Disqualifiers: any contract change, security surface, >30 LOC diff, new dependency, blocker-bug fix.

For framework-template maintenance, use the lighter fast-track path in workflow.md §6.2 when the change is trivial and does not alter approval gates, security/secret rules, workflow state machine, service coder write scopes, destructive behavior, or application code under `services/`.

## Drift detection

The coordinator reads `project-brain.yaml.freshness` at session startup and compares `last_indexed_at`, `stale_after_days`, and `tracked_paths` against the workspace state when needed. It surfaces `Brain: fresh|stale|missing|template-seed` in its state banner. When stale for applied-service work, do not advance into `IN_DEV` without `/sync-memory --refresh-index` or explicit user acceptance. In framework-template/not_applied mode, seed or stale brain values do not block framework maintenance.

## Context economy

Onboarding classifies each workspace/service with project archetypes such as `backend-api`, `frontend-web`, `mobile-app`, `cli-tool`, `library-sdk`, `data-pipeline`, `ml-model`, `infra-iac`, `embedded-firmware`, `docs-site`, `docs-and-templates`, and `monorepo-platform`. Agents start with a signature scan and indexed summaries, not a full repo read.

For applied-service tasks, `task-analysis.yaml` must include `context_plan` with bounded memory/source/skill budgets, required evidence, excluded paths, expansion triggers, unresolved context, and confidence. Do not advance to implementation when context confidence is low or service/test/contract ownership is unknown.

## Policy consistency

Run `/policy-check snapshot --root .` before trusting migrated workspace state or `/policy-check snapshot --root <snapshot-root>` for shared artifact-only snapshots without `services/`. This is handled by the `workflow-policy` agent and must not depend on Python, Node, jq, or shell helpers. Missing `services/` is reported as `services_available: false`, not as a project defect. `DEV_DONE` requires `dev-verification.yaml` result/verdict `DEV_DONE`; `QC_DONE`/`PASS` is invalid while required cases remain blocked/pending/not_run/failed or manual/retest evidence is still required.

## Where to find more

| Need | File |
|---|---|
| Full workflow spec | [.agent/workflow.md](.agent/workflow.md) |
| Slash commands | [COMMAND.md](COMMAND.md) |
| All workflow rules | [.agent/rules/](.agent/rules/) |
| Agent taxonomy | [.agent/docs/agent-taxonomy.md](.agent/docs/agent-taxonomy.md) |
| Coordinator behavior | [.claude/agents/workflow/coordinator.agent.md](.claude/agents/workflow/coordinator.agent.md) |
| Template for new artifacts | [.agent/templates/](.agent/templates/) |
| Claude Code-specific instructions | [CLAUDE.md](CLAUDE.md) |
| Setup and install | [SETUP.md](SETUP.md) |
| Quickstart | [QUICKSTART.md](QUICKSTART.md) |
| Quick semantics | [GUIDELINES.md](GUIDELINES.md) |
| Visual flow diagrams | [.agent/docs/visual-flow.md](.agent/docs/visual-flow.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |

## Folder semantics

```text
.runtime/context/   Durable brain + service contracts + workflow state (agent-generated)
.runtime/tasks/     Per-task evidence and artifacts
.runtime/bugs/      Bug reports and routing
inputs/            USER drops reference docs (PRD, HLD, ADR, OpenAPI, glossary, runbooks)
                   Onboarding scans recursively. Subdirs: product, architecture, api, domain, runbooks, misc.
services/          Ignored workspace for cloned application repositories (source code, not memory)
```

Conflict rule: when `inputs/` and source code disagree, **code wins for technical facts**, **inputs/ wins for intent/target state**. R-002-11.

## Per-tool enforcement boundary

Different AI tools enforce the same workflow policy through different mechanisms. Know which one applies before relying on automated gates.

| Tool | Auto-discovers | Lifecycle hooks | Enforcement path |
| --- | --- | --- | --- |
| Claude Code | `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `CLAUDE.md` | No | Coordinator routing + agent contracts |
| Codex CLI | `.codex/AGENTS.md`; `.codex/config.toml` (when project trusted) | No | AGENTS.md instructions + sandbox as policy aid; service write scope still comes from `workflow-state.yaml.active_task_id` + `agent-registry.yaml` |
| Cursor | `.cursor/rules/*.mdc` (glob-targeted), `.cursor/hooks.json` | **Yes** — `preToolUse`, `beforeShellExecution`, `afterFileEdit`, etc. | Rules + hooks (real runtime enforcement) |
| Gemini Code Assist | `.gemini/GEMINI.md` | No | GEMINI.md instructions |
| GitHub Copilot | `.github/copilot-instructions.md` | No | Instructions file |

**Important:** `.cursor/hooks.json` and the scripts in `.cursor/hooks/` are **Cursor-only**. They do not fire under Claude Code, Codex, Gemini, or Copilot. When you add a workflow gate, mirror the rule into the other tools' entrypoint files if it should apply universally.

## What this repo is NOT

- Not an SDK. Do not `pip install` or `npm install` it as a library.
- Not a runtime. It is a set of instructions + memory + artifact contracts the AI agent follows.
- Not a sandbox. Application source code lives in `services/<cloned-repo>/`, which is gitignored.

## If you are confused

Default to: **route the request through `coordinator`, do not modify code, ask for clarification.** This is always a safe action under this framework's rules.
