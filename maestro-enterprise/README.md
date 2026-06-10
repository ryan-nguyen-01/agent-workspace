# maestro

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/Agents-33-blue)](#agents)
[![Skills](https://img.shields.io/badge/Skills-231-green)](#skills)
[![Stars](https://img.shields.io/github/stars/ryan-nguyen-01/maestro?style=social)](https://github.com/ryan-nguyen-01/maestro)

> **Language policy** ([.maestro/engine/docs/language-policy.md](.maestro/engine/docs/language-policy.md)):
> framework documents, workflow rules, agent definitions, command definitions, templates, entry points,
> and methodology playbooks are written in English so AI agents read them with minimal ambiguity. The
> conversation follows the user. Identifiers such as paths, agent ids, rule ids, YAML keys, command
> names, and tool names remain English contract tokens.

`maestro` is a product-development control plane for building and operating real software with
AI agents. It keeps product code, official documentation, design decisions, work history, runtime state,
and agent memory in separate, auditable domains.

The root name stays stable as `maestro`. The actual product identity and namespace live in
`.maestro/project.yaml`.

## Documentation Entry Points

| Need | File |
| --- | --- |
| Fast workspace startup | [QUICKSTART.md](QUICKSTART.md) |
| Slash command index | [COMMAND.md](COMMAND.md) |
| Framework overview | [README.md](README.md) |
| Install, upgrade, and validation guide | [SETUP.md](SETUP.md) |
| Entry point for non-Claude AI agents | [AGENTS.md](AGENTS.md) |
| Entry point for Claude Code | [CLAUDE.md](CLAUDE.md) |
| Entry point for Codex | [.codex/AGENTS.md](.codex/AGENTS.md) |
| Workflow source of truth | [.maestro/engine/workflow.md](.maestro/engine/workflow.md) |
| Agent taxonomy | [.maestro/engine/docs/agent-taxonomy.md](.maestro/engine/docs/agent-taxonomy.md) |

## Templates (copy one and go)

Open this repo and the **`maestro-*` folders at the root are the products** — each a self-contained
workspace (own `CLAUDE.md` + `.claude/` + `.codex/` + `.maestro/` + skill subset + folders for your
source code). Copy one anywhere, drop your service code inside, run `claude` (or `codex`) in it:

| Folder | Purpose | Skills |
| --- | --- | --- |
| [`maestro-sdlc/`](maestro-sdlc/) | Software delivery end-to-end: BA → design → UI/UX → code → QC | 231 |
| [`maestro-adlc/`](maestro-adlc/) | AI products/agents with an eval gate | 132 |
| [`maestro-enterprise/`](maestro-enterprise/) | Governed/production agents: compliance, audit | 166 |
| [`maestro-lite/`](maestro-lite/) | Small tools/prototypes, minimal ceremony | 39 |
| [`maestro-brownfield/`](maestro-brownfield/) | Existing project maintenance — ask-don't-infer | 231 |

```bash
cp -R maestro/maestro-adlc ~/work/my-ai-app   # copy the template anywhere
cd ~/work/my-ai-app                            # move your service code into services/ or apps/
claude                                         # the agent follows this template's contract
```

Details + build system: [variants/README.md](variants/README.md). Rebuild after platform changes:
`python3 scripts/build-variant.py --all`.

## Why This Workspace Exists

AI coding tools are powerful, but in a real codebase the same problems repeat:

- Each conversation can start as a fresh context, so decisions, conventions, and known mistakes are easy to lose.
- Agents may jump into code before analyzing requirements, impact, ownership, or test policy.
- Without explicit write scope, agents may edit files outside the task boundary.
- Completion claims can happen without verification evidence.
- Review feedback and bug root causes are often not recorded for future work.

`maestro` adds a control plane before source edits happen.

| Problem | Workspace mechanism |
| --- | --- |
| Agents forget durable context | `.maestro/knowledge/` and `.maestro/memory/` preserve reusable project knowledge |
| Every task is treated the same | `direct`, `assisted`, and `governed` modes scale process to task risk |
| Agents do not know write boundaries | Component registry and scoped coder agents define read/write scope |
| Quality gates are inconsistent | Dev Verification and QC Runner require evidence before handoff |
| Mistakes repeat | Memory Update promotes root causes, patterns, and anti-patterns |
| Context grows too large | Indexes, context hints, and task `context_plan` limit what agents read |
| Large tasks are not decomposed | Initiative -> Epic -> Task -> Subtask contracts create bounded work |
| Product documentation is missing | `docs/` stores PRD, feature, user story, flow, HLD, LLD, ADR, quality, and runbook artifacts |

## Execution Modes

| Mode | Use When | Verification |
| --- | --- | --- |
| `direct` | Small, fast work where the user can verify quickly | User or shared |
| `assisted` | Bounded work that may need resume, progress, or lightweight evidence | Agent or shared |
| `governed` | High-risk, cross-component, security, migration, production, or compliance work | Agent evidence plus required gates |

The methodology router can select `risk-based-routing`, `spec-driven-development`,
`enterprise-agent-governance`, or `eval-driven-ai` based on the task and the artifact requirements.
These names are workspace overlays mapped to current
production-agent patterns in
[industry-alignment.md](docs/governance/methodologies/industry-alignment.md): durable workflows,
human-in-the-loop, artifact management, eval-driven AI, trace evidence, plugins, hooks, and governed
enterprise autonomy.

The operating model is run-centric: a task describes intended work; a run records one execution
attempt with checkpoints, trace links, eval evidence, approvals, and reports when needed.
Agents can use `python3 scripts/agent-run.py create|heartbeat|checkpoint|complete` to maintain
`.maestro/work/runs/` without depending on a specific coding harness.

## System Architecture

> Diagram: see **[System overview](.maestro/engine/docs/visual-flow.md#1-system-overview)** in visual-flow.md (Mermaid).

See [visual-flow.md](.maestro/engine/docs/visual-flow.md) for all workflow diagrams.

## Current Counts

| Area | Count |
| --- | --- |
| Framework agents | 34: 12 workflow agents, 3 built-in coders, 19 specialist advisors |
| Skills | 231: 12 workflow skills plus 154 technical skills |
| Rules | 19 |
| Templates | 51 |
| Commands | 17 |

The deterministic guard for these counts is `python3 scripts/architecture-health-check.py --strict`.

## Folder Structure

```text
maestro/
├── .maestro/                         Product-development control plane
│   ├── INSTRUCTIONS.md          Stable harness entry
│   ├── project.yaml             Product identity and naming standard
│   ├── methodology.yaml         Risk routing, spec-driven, eval-driven, governance routing
│   ├── engine/                  Canonical control plane: workflow, rules, templates, docs
│   ├── registry/                Components, agents, skills, inputs, artifacts
│   ├── knowledge/               Durable project and component knowledge
│   ├── work/                    Initiative, epic, task, subtask, run, bug evidence
│   ├── design/                  Design artifact index
│   ├── decision/                ADR and decision index
│   ├── memory/                  Project, task, and local session memory
│   ├── observability/           Traces, evals, reports, audit views
│   ├── governance/              Agent governance, approvals, risk indexes
│   ├── history/                 Compatibility timeline and event log
│   └── runtime/                 Local-only active state, cache, reports
├── .claude/                     Native Claude agents, skills, commands, hooks
├── .codex/                      Codex adapter
├── docs/                        Official product documentation
├── apps/                        Product applications, for example `<project>-web-app`
├── services/                    Deployable services, for example `<project>-auth-service`
├── packages/                    Shared libraries and design systems
├── infra/                       Deployable infrastructure and environments
├── tests/                       System, contract, performance, and E2E suites
└── inputs/                      User-provided references pending curation
```

## Product Documentation Roots

| Root | Purpose |
| --- | --- |
| `docs/product/prds/` | Product requirements and outcomes |
| `docs/requirements/features/` | Feature scope, business rules, acceptance criteria |
| `docs/requirements/user-stories/` | User value and testable acceptance criteria |
| `docs/requirements/use-cases/` | Actor-system behavior |
| `docs/requirements/non-functional/` | Performance, reliability, security, compliance |
| `docs/experience/` | User journeys, flows, wireframes, UI specifications |
| `docs/architecture/high-level-design/` | System boundaries and major decisions |
| `docs/architecture/low-level-design/` | Implementation-level design |
| `docs/architecture/decisions/` | ADRs |
| `docs/governance/methodologies/` | Risk-Based Workflow Routing, Spec-Driven Development, Eval-Driven AI Development, Enterprise Agent Governance |
| `docs/governance/methodologies/industry-alignment.md` | Mapping from workspace methods to production-agent patterns |
| `docs/governance/enterprise-agent-governance/` | Governance Policy, Mission, Behavior Contract, Autonomy Policy, Agent Definition, Eval Suite, Audit Log, Interaction Protocol |
| `docs/operations/runbooks/` | Operational procedures and recovery |

## Agents

| Agent | Profile | Role |
| --- | --- | --- |
| Coordinator | `fast_router` | Routes tasks, checks project state, and enforces workflow gates |
| Onboarding | `deep_reasoning` | Scans project structure and creates durable project knowledge |
| Agent Factory | `coding_planner` | Creates scoped coder agents after user approval |
| Task Analysis | `deep_reasoning` | Converts tickets, HLDs, LLDs, bugs, and text into structured task specs |
| Solution Architect | `deep_reasoning` | Reviews cross-service, API, data, event, security, or infra risks |
| Coder Leader | `coding_planner` | Plans, assigns, integrates, and reviews coder work |
| Dev Verification | `verification` | Checks Code Done evidence, critical checks, and test policy |
| QC Handoff | `fast_router` | Creates Dev-to-QC handoff documents |
| QC Runner | `verification` | Runs QC from handoff and stops on blocker bugs |
| Bug Router | `deep_reasoning` | Classifies defects and routes fixes |
| Memory Update | `memory_light` | Persists reusable learnings after meaningful workflow events |
| Workflow Policy | `deep_reasoning` | Validates state transitions, artifacts, and approval gates |

Two built-in cross-cutting coders are available before generated service coders:

- `coder-infra`: Terraform/IaC, Kubernetes, Docker, CI/CD.
- `coder-database`: schemas, migrations, queries, indexes.

Nineteen specialist advisors live under `.claude/agents/specialists/`. They are advisor-only and do
not write application code, assign coder work, or mark Code Done.

## Workflow

### Onboarding

```text
User opens workspace and requests analysis
  -> coordinator detects missing or stale project knowledge
  -> onboarding scans docs, inputs, components, stack, and conventions
  -> agent-factory proposes scoped coder agents when needed
  -> coordinator can route the next task
```

### Governed Feature Delivery

```text
User request
  -> coordinator selects methodology and execution mode
  -> task-analysis writes task-analysis.yaml
  -> solution-architect reviews risky architecture when required
  -> coder-leader creates the implementation plan and assignments
  -> scoped coders edit only allowed paths
  -> coder-leader integrates and reviews work
  -> dev-verification checks evidence and test policy
  -> qc-handoff creates handoff
  -> qc-runner executes QC
  -> bug-router routes defects if needed
  -> memory-update records durable learnings
  -> DONE
```

### Bug Loop

```text
QC Runner finds a defect
  -> bug-router classifies blocker or non-blocker
  -> coder-leader assigns the fix
  -> dev-verification verifies the fix
  -> qc-runner retests
  -> memory-update stores root cause and prevention when useful
```

## Generated Service Coders

`agent-factory` creates component-specific coder agents after onboarding and user approval.

Naming convention:

```text
coder-<component-slug>.agent.md
```

Example:

```text
Detected stack: NestJS + React + PostgreSQL + Redis

Generated:
  coder-api.agent.md          Backend API service
  coder-web.agent.md          Frontend React app
  coder-shared.agent.md       Shared packages
```

Each coder has `allowed_read_paths`, `allowed_write_paths`, `forbidden_paths`, `test_policy`, and
escalation rules. Scope expansion requires user approval.

## Rules

Rules under `.maestro/engine/rules/` define workflow constraints and governance:

| Rule | Purpose |
| --- | --- |
| R-000 | Read workflow first; do not code before required analysis |
| R-001 | Project Knowledge is the durable memory source |
| R-002 | Onboarding scans and records; it does not edit product code |
| R-003 | Agent creation requires user approval |
| R-004 | Tasks must be normalized before governed coding |
| R-005 | Coder Leader owns planning and cross-coder coordination |
| R-006 | Service coders write only inside approved scope |
| R-007 | Code Done requires evidence, score, and critical checks |
| R-008 | QC runs after handoff and stops on blockers |
| R-009 | Bugs are classified as blocker or non-blocker |
| R-010 | Memory updates happen only for reusable learnings |
| R-011 | Approval gates protect risky actions |
| R-012 | Required artifacts depend on workflow state |
| R-013 | Secrets and credentials must not be written to artifacts |
| R-014 | Skills are capabilities, not agent identity |
| R-015 | Model routing, activity, status, and response UI must not fabricate metrics |
| R-016 | Specialist advisors are advisory only |
| R-017 | Hooks enforce scope, secret, and destructive-command guardrails |
| R-018 | Document precedence defines which source wins conflicts |

## Skills

Workflow skills with the `skill-*` prefix:

| Skill | Purpose |
| --- | --- |
| `skill-project-brain` | Manage reusable Project Knowledge memory (legacy skill ID) |
| `skill-project-onboarding` | Create Project Knowledge from the initial scan |
| `skill-agent-factory` | Generate component coder agents |
| `skill-task-analysis` | Normalize requests into task specs |
| `skill-coder-leader` | Coordinate service coders |
| `skill-service-coder` | Implement code inside approved scope |
| `skill-dev-verification` | Assess Code Done readiness |
| `skill-qc-handoff` | Create QC handoff |
| `skill-qc-runner` | Run QC and record results |
| `skill-bug-routing` | Classify and route defects |
| `skill-memory-update` | Persist reusable learnings |
| `skill-workflow-policy` | Validate transitions and gates |

Technical skills cover frontend, backend, database, mobile, cloud, testing, security, payments,
knowledge patches, and language-specific engineering practices.

## Commands

| Command | Purpose |
| --- | --- |
| `/coord` | Route a request through the coordinator |
| `/onboard` | Build or refresh project knowledge |
| `/analyze-task` | Normalize a request into a task spec |
| `/create-coders` | Create service coder agents |
| `/plan-dev` | Create an implementation plan |
| `/dev` | Implement code |
| `/verify-dev` | Check Code Done readiness |
| `/handoff-qc` | Create QC handoff |
| `/qc` | Run QC tests |
| `/bug` | Route a bug report |
| `/sync-memory` | Update durable memory |
| `/skills` | Maintain installed skills |
| `/policy-check` | Validate workflow policy |
| `/status` | Show workflow and agent activity status |
| `/resume-task` | Resume an interrupted task |
| `/access` | Adjust Claude Code tool-permission posture |

## Memory And Registry

The control plane separates data by lifecycle:

```text
.maestro/registry/          Addresses and capabilities for components, agents, skills, inputs, artifacts
.maestro/knowledge/         Durable project facts, conventions, architecture, component knowledge
.maestro/work/              Initiative, epic, task, subtask, bug, and evidence
.maestro/memory/tasks/      Continuation handoffs and summaries for long tasks
.maestro/memory/sessions/   Local short-term memory, not committed
.maestro/runtime/           Local active state, telemetry, cache, reports, not committed
docs/                  Official product documentation
```

Agents do not read all memory every time. They read `.maestro/knowledge/index.yaml` first, use project and
component context hints, then open only the files needed for the active task.

## Task Artifacts

Each task has a folder under `.maestro/work/tasks/`:

```text
.maestro/work/tasks/<task_id>/        TASK-YYYYMMDD-NNN-slug
├── task-input.md                Original user input
├── task.yaml                    Task manifest and artifact paths
├── task-updates.yaml            Append-only updates
├── task-analysis.yaml           Normalized task spec
├── architecture-review.yaml     Architecture gate when required
├── implementation-plan.yaml     Coder Leader plan
├── service-assignments.yaml     Coder assignments
├── coder-results.yaml           Coder outputs
├── dev-verification.yaml        Code Done evidence
├── qc-handoff.md                Dev-to-QC handoff
├── qc-test-results.yaml         QC results
├── bugs.yaml                    Task-local bug index
└── memory-updates.yaml          Learnings to persist
```

## Tool Support

| Tool | Integration |
| --- | --- |
| Claude Code | Reads `CLAUDE.md` and `.claude/` |
| Codex | Reads `.codex/AGENTS.md` and `AGENTS.md` |
| Other agents | Read `AGENTS.md` |

No package or server is required. The framework is a set of Markdown, YAML, and script contracts that
AI tools read and follow.

## Quick Start

Detailed setup: [SETUP.md](SETUP.md)

Fast usage guide: [GUIDELINES.md](GUIDELINES.md)

Workspace startup: [QUICKSTART.md](QUICKSTART.md)

```bash
git clone <repo-url> ~/Downloads/maestro
cd ~/Downloads/maestro
```

Then:

```text
1. Configure product key, display name, and component namespace in `.maestro/project.yaml`.
2. Create or mount components such as `apps/nova-web-app`, `services/nova-auth-service`, and `packages/nova-design-system`.
3. Register components in `.maestro/registry/components.yaml`.
4. Put official product documents in `docs/`; put external references in `inputs/`.
5. Run `/onboard` when durable component knowledge is needed.
6. Start work through `/coord`.
```

Example requests:

```text
"Analyze this project"          -> onboarding
"Implement API /orders"         -> coordinator -> task-analysis -> coder-leader
"Check if the code is ready"    -> dev-verification
```

## File Reference

| File | Meaning |
| --- | --- |
| `CLAUDE.md` | Claude Code entry point |
| `AGENTS.md` | General AI-agent entry point |
| `COMMAND.md` | Canonical slash command index |
| `.maestro/INSTRUCTIONS.md` | Stable `.maestro/` entry |
| `.maestro/engine/workflow.md` | Workflow source of truth |
| `.maestro/engine/rules/*.md` | Workflow constraints |
| `.maestro/engine/templates/*.template.*` | Artifact templates |
| `.maestro/registry/*.yaml` | Component, agent, skill, input, and artifact routing |
| `.maestro/knowledge/index.yaml` | Memory routing index |
| `.maestro/config/model-routing.yaml` | Model profile and override contract |
| `.maestro/config/response-ui.yaml` | Response layout contract |
| `.claude/commands/*.md` | Claude slash commands |
| `.claude/skills/*/SKILL.md` | Skill definitions |

## License

MIT License. See [LICENSE](LICENSE).

This is an open framework. You may use it in commercial projects, fork it for a team, add private
skills or agents, and contribute improvements through pull requests.
