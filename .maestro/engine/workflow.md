# End-to-End Workflow Policy

This is the mandatory source of truth for all `maestro` adapters and workflow agents.

## 1. Required reading order

Every agent reads only the minimum files needed. Memory is the agent brain; services are coding targets; state is transient workflow position.

```text
1. .maestro/engine/workflow.md
2. .maestro/runtime/workflow-state.yaml
3. Its own .claude/agents/<agent>.agent.md
4. .maestro/knowledge/index.yaml
5. .maestro/knowledge/project.yaml only when routing/planning needs project facts
6. .maestro/registry/components.yaml when service discovery or impact analysis is needed
7. .maestro/registry/agents.yaml when routing or coding
8. .maestro/config/model-routing.yaml when selecting or reporting agent model profiles
9. .maestro/runtime/agent-activity.yaml when reporting status or updating activity telemetry
10. .maestro/config/response-ui.yaml when formatting status, reports, or final responses
11. .maestro/knowledge/test-policy.yaml when coding, verifying, or QC testing
12. Relevant .maestro/knowledge/components/<component-id>.yaml files only for impacted components
13. Relevant .maestro/work/tasks/<task-id> artifacts
```

If `.maestro/knowledge/index.yaml` or `.maestro/knowledge/project.yaml` is missing, empty, or stale for product-component work, stop normal routing and run onboarding or `/sync-memory --refresh-index`. For framework maintenance, apply the scope exception below first.

### Framework maintenance scope exception

This repository is the `maestro` product-development control plane. `NEED_ONBOARDING`, an
empty component registry, and seed project knowledge are expected for framework-only maintenance and
must not block framework maintenance.

Framework maintenance includes changes to:

```text
AGENTS.md
CLAUDE.md
COMMAND.md
.maestro/engine/**
.claude/agents/**
.claude/commands/**
.codex/**
.cursor/**
.gemini/**
.github/copilot-instructions.md
scripts/**
SETUP.md
QUICKSTART.md
GUIDELINES.md
CHANGELOG.md
```

For framework maintenance, the coordinator must classify the request before brain checks:

```yaml
target_scope: framework
requires_onboarding: false
```

Onboarding and component knowledge are required only when assisted/governed work needs product facts
that are not already available from registered components and current evidence.

## 1.1. Folder semantics

```text
.maestro/engine/                  Workflow, rules, schemas, and templates
.maestro/registry/                Skills, agents, components, inputs, and artifact routing indexes
.maestro/knowledge/               Durable project facts and component profiles
.maestro/work/                    Initiative, epic, task, subtask, and bug artifacts
.maestro/design/                  Design metadata and links to official docs
.maestro/decision/                Decision index and lifecycle metadata
.maestro/memory/                  Project, task, and short-lived session memory
.maestro/history/                 Append-only workflow events and human timeline
.maestro/runtime/                 Current state, locks, cache, telemetry, and generated reports
docs/                        Official product, requirements, UX, architecture, quality, delivery, operations, governance docs
apps/                        Deployable user-facing applications
services/                    Deployable backend services, workers, and gateways
packages/                    Reusable libraries, contracts, shared types, and design system
infra/                       Infrastructure and delivery platform source
tests/                       Cross-component contract, integration, E2E, performance, and security suites
inputs/                      External or user-provided source material awaiting distillation
```

Agents must read `.maestro/registry/components.yaml` before scanning component roots. Source code never belongs under `.maestro/`. Official product documentation belongs under `docs/`; `.maestro/registry/artifacts.yaml` indexes it without duplicating the content.

## 1.2. Task classification for speed

The coordinator should classify every request before loading broad context:

```yaml
target_scope: framework | product_component | unknown
task_size: trivial | normal | high_risk
requires_onboarding: true | false
requires_full_artifacts: true | false
execution_mode: direct | assisted | governed
verification_owner: agent | user | shared
run_required: true | false
methodology:
  selected: risk-based-routing | spec-driven-development | enterprise-agent-governance | eval-driven-ai
  overlays: []
  industry_patterns: []
```

Classification rules:

```text
target_scope=framework when the requested change is confined to framework instructions, rules, templates, tool adapters, scripts, or documentation in this repository.
target_scope=product_component when the request reads or writes a component registered under apps,
services, packages, infra, or tests.
requires_onboarding=false for target_scope=framework unless product-component facts are required.
requires_full_artifacts=false for trivial framework maintenance with no approval-gate, security, state-machine, generated-coder scope, or service contract impact.
```

For `target_scope=framework`, agents should read only the entrypoint files and directly relevant framework files. Do not load project brain, component registry, component knowledge files, agent registry, or test policy unless the requested change directly edits or validates those contracts.

### Execution modes

```text
direct:
  Fast, low-risk implementation. Persistent task artifacts are optional.
  The response must still disclose unverified behavior and user-owned checks.

assisted:
  Bounded analysis and implementation. Persist task/progress/verification records when work crosses
  conversations or requires handoff.

governed:
  Full state machine, decomposition, approval, design, verification, QC, history, and memory contracts.
  Required for high-risk, cross-component, migration, production, security, or parallel multi-agent work.
```

Coordinator may automatically upgrade a task to a stricter mode and records the reason. It may not
automatically downgrade a user-selected or risk-required mode.

### Runs

A task describes intended work. A run records one execution attempt. Create a run when work may
pause/resume, has multiple agent attempts, needs eval cycles, needs trace evidence, or waits on human
approval. Small direct work may omit run artifacts.

Run artifacts live under `.maestro/work/runs/` and link to traces, evals, approvals, reports, and
checkpoints in `.maestro/observability/`, `.maestro/governance/`, and `.maestro/work/runs/<run-id>/`.
Agents can maintain the run lifecycle with
`python3 scripts/agent-run.py create|heartbeat|checkpoint|complete`.

### Methodology overlays

Risk-Based Workflow Routing is the default router. Spec-Driven Development, Eval-Driven AI
Development, and Enterprise Agent Governance are overlays that can be added when the task evidence
matches the selection matrix. Use
`docs/governance/methodologies/industry-alignment.md` to map local methodology names to production-agent
patterns such as durable workflows, human-in-the-loop, artifact management, eval-driven AI, trace
evidence, plugins, hooks, and enterprise governance.

### Verification ownership

```text
agent:
  Agent has sufficient environment, data, and tooling access to produce evidence.
user:
  User performs verification that requires protected environments, protected data, or business judgment.
shared:
  Agent runs available checks and the user completes the explicitly listed remaining checks.
```

Implementation may be complete while verification is `pending_user`; agents must never relabel unavailable
evidence as passed.

### Work decomposition

The hierarchy is `Initiative -> Epic -> Task -> Subtask`. Decomposition is required before implementation
when work spans multiple sessions, combines design and implementation, contains independent acceptance
criteria, affects multiple components, has parallel workstreams, includes migration/rollout, or requires
multiple specialists. Subtasks cannot contain nested subtasks.

Dependency graphs and progress live with the owning epic or task. Official design artifacts live under
`docs/` and are referenced by stable ids rather than copied into task folders.

## 1.3. Context economy and universal project support

The framework must work across project shapes without loading the whole repo. Agents use a signature-first read strategy and expand context only when task risk or evidence gaps require it.

### Universal project archetypes

Onboarding records one or more archetypes in `project.yaml.project_profile.archetypes` and per-service `profile.archetypes`:

```text
backend-api, frontend-web, mobile-app, desktop-app, cli-tool, library-sdk,
data-pipeline, ml-model, infra-iac, embedded-firmware, docs-site,
docs-and-templates, plugin-extension, monorepo-platform, workflow-framework
```

Unknown or mixed projects are allowed, but must be marked with `confidence` and evidence. Do not force a project into a known archetype when evidence is weak.

### Signature-first reads

Before broad source reads, agents inspect only:

```text
file tree shape, component-registry paths, package/build manifests, lockfiles,
route/API/schema definitions, test config, CI/deploy config, and inputs-index rows
```

Agents skip generated/vendor/heavy roots by default: `node_modules`, `vendor`, `dist`, `build`, `.next`, `coverage`, `.git`, and large generated files.

### Task context plan

Task Analysis writes `task-analysis.yaml.context_plan` for every product-component task. Later phases must read that plan before opening source files. The plan records:

```text
context confidence, max memory/source/skill file budgets, required memory,
required source evidence, optional source evidence, excluded paths,
expansion triggers, unresolved context, and evidence confidence
```

If `context_plan.confidence` is low, or required service/test/contract evidence is missing, Coordinator must not advance into `IN_DEV` until the context is refreshed or the user explicitly accepts the risk.

### Expansion triggers

Agents may exceed the default context budget only when one of these is true:

```text
Impacted component cannot be resolved
Acceptance criteria cannot be mapped to files
Service boundary, test policy, or contract ownership is unknown
Security, schema, migration, data, infra, or cross-service risk appears
Implementation touches shared code or public contracts
Evidence is stale or contradicts inputs/
```

When expanding, record the reason in `task-analysis.yaml.context_plan` or the phase artifact that caused the expansion. This keeps recall high while making token use auditable.

## 1.4. Model routing and agent activity

Agent-to-model selection is controlled by `.maestro/config/model-routing.yaml`.

```text
Deep reasoning profile:
  Claude -> Opus
  Codex  -> GPT-5.5
  Use for task-analysis, solution-architect, workflow-policy, blocker routing, architecture/security/data/contract ambiguity.

Coding profile:
  Claude -> Sonnet
  Codex  -> Codex coding model (`gpt-5.3-codex` by default)
  Use for coder-leader implementation planning, generated service coders, coder-infra, coder-database, coder-data, refactors, tests, and code review.
```

Provider model IDs are configurable aliases. If a tool does not support the configured model, use the closest available equivalent and record the fallback in `.maestro/runtime/agent-activity.yaml`.

`/status` renders the agent activity dashboard from `.maestro/runtime/agent-activity.yaml`:

```text
agent id, workflow phase, current action, status, model profile/model id,
started_at, elapsed time, and ETA
```

Do not invent exact ETA. If the active tool does not expose reliable metrics, report `unknown` or a clearly marked estimate.

Adapters that can run local commands may update this file through:

```text
python3 scripts/agent-activity.py start --agent-id <agent> --phase <phase> --current-action <summary>
python3 scripts/agent-activity.py heartbeat --agent-id <agent> --current-action <summary>
python3 scripts/agent-activity.py block --agent-id <agent> --summary <summary>
python3 scripts/agent-activity.py complete --agent-id <agent> --summary <summary>
```

This helper is optional. It improves observability but does not weaken the rule that exact ETA values require real adapter metrics.

## 1.5. Response UI contract

Response layout is controlled by `.maestro/config/response-ui.yaml`.

```text
compact    -> short status or simple completion update
concise    -> default final response
dashboard  -> /status and terminal dashboard
models     -> full model routing and provider profile report
dev        -> implementation completion report
review     -> review findings first, then questions/test gaps/summary
policy     -> workflow gate decision, evidence, violations, next action
```

The response UI contract controls markdown/text structure, section order, language preference, and line budgets. It does not control native Claude, Copilot, Cursor, or Gemini panel chrome, and it must not override workflow gates, approval requirements, write scopes, or evidence requirements.

The terminal mirror supports `python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json>`. Add `--write` to generate `.maestro/runtime/reports/status.md` and `.maestro/runtime/reports/status.html` from the same source files.

User-requested output format wins for the current response unless it would hide required evidence, safety warnings, or policy decisions.

## 1.6. Optional deterministic architecture health check

`/policy-check` remains agent-native and must not require Python, Node, jq, shell scripts, or local runtime dependencies. For CI/local maintenance, the framework also ships an optional deterministic drift checker:

```text
python3 scripts/architecture-health-check.py --strict
python3 scripts/architecture-health-check.py --strict --write-report
```

This helper catches mechanical drift in resource counts, required files, model routing, response UI, generated status artifacts, Cursor hook fail-closed gates, and cross-tool entrypoint references. It is a safety net, not a policy authority.

## 2. Workflow states

```text
NEW
NEED_ONBOARDING
ONBOARDED
NEED_AGENT_CREATION_APPROVAL
AGENTS_READY
READY_FOR_ANALYSIS
ANALYZED
ARCHITECTURE_REVIEWING
PLANNED
IN_DEV
DEV_VERIFYING
DEV_BLOCKED
DEV_DONE
QC_READY
QC_TESTING
BLOCKED_BY_BUG
FIXING
QC_RETESTING
QC_DONE
MEMORY_SYNCING
DONE
```

## 2.1. Single-entry coordinator gate

```text
Every user request enters through coordinator (/coord).
No direct routing from raw user input to onboarding, task-analysis, solution-architect, coder-leader, service coders, dev-verification, qc, or bug-router.
Coordinator must validate state transition legality, required artifacts, and approval gates before routing.
If validation fails, coordinator returns deny/needs_user_approval and does not advance state.
```

## 2.2. Workspace identity and state

Workspace identity belongs in `.maestro/project.yaml` and durable project knowledge belongs in
`.maestro/knowledge/project.yaml`. Runtime progress belongs in `.maestro/runtime/workflow-state.yaml`.
Workflow behavior is controlled by current state, execution mode, target scope, and approval gates.

```text
1. Do not infer identity or namespace changes from unrelated task text; require explicit user intent.
2. Do not change persistent workflow-state semantics while active_task_id is set unless the change is the task itself.
3. Framework maintenance is determined by target_scope=framework, not by a stored mode.
4. Product-component work uses `.maestro/project.yaml`, `.maestro/registry/components.yaml`, and Project Brain evidence.
5. After changing product identity or component roots, the next product-component command is /onboard or /sync-memory --refresh-index.
```

## 3. Agent responsibilities

| Agent | Responsibility | Must not do |
|---|---|---|
| coordinator | Own routing, brain checks, approval gates, workflow state | Implement code |
| onboarding | Analyze project and write project/component knowledge | Create coder agents without user approval |
| agent-factory | Generate service coder agents from project brain | Invent services not found by onboarding |
| task-analysis | Normalize HLD/LLD/text into actionable task spec | Modify source code |
| solution-architect | Review architecture risk before implementation planning when required | Write implementation code or assign coders |
| coder-leader | Plan and coordinate multi-service implementation | Directly bypass service coder scopes |
| generated service coder | Implement inside allowed paths only | Touch forbidden paths or create tests when policy forbids |
| dev-verification | Decide whether Code Done is valid | Pretend untested work is done |
| qc-handoff | Create QC handoff artifact | Test the feature |
| qc-runner | Execute QC flow, classify bugs | Fix code |
| bug-router | Route blocker/non-blocker bugs to dev flow | Continue QC after blocker |
| memory-update | Persist durable knowledge and decisions | Store secrets or noisy logs |
| workflow-policy | Validate transitions and gate violations | Override user approval gates |

## 4. Onboarding workflow

```text
1. Coordinator checks project brain.
2. If missing or stale, coordinator calls onboarding.
3. Onboarding scans project structure, stack, services, dependencies, APIs, DB, CI, environments, and test policy.
4. Onboarding writes .maestro/knowledge/project.yaml, .maestro/registry/components.yaml, .maestro/knowledge/test-policy.yaml, and .maestro/knowledge/components/<component-id>.yaml.
5. Onboarding proposes coder agent candidates.
6. Coordinator asks the user whether to create coder agents.
7. Agent Factory runs only after approval.
```

Onboarding must not make application code changes.

## 5. Agent creation workflow

```text
1. Agent Factory reads project brain and .maestro/registry/components.yaml.
2. It creates one coder contract per approved service/module.
3. It writes generated coder agent definitions from templates/agent-coder.template.md.
4. It writes or updates .maestro/registry/agents.yaml.
5. Coordinator marks AGENTS_READY.
```

Each generated coder requires:

```text
service id
allowed read paths
allowed write paths
forbidden paths
commands allowed by policy
test policy
critical checks
handoff requirements
escalation rules
```

## 6. Task intake workflow

Task sources may be HLD, LLD, ticket text, bug report, production incident, or direct user text.

```text
1. Coordinator classifies execution_mode, verification_owner, run_required, methodology, overlays, and
   industry_patterns.
2. Direct mode may implement immediately without a persistent task. It must disclose unverified
   behavior and the exact user-owned checks when the environment or data is inaccessible.
3. Assisted mode creates task.yaml, progress.yaml, and verification.yaml so work can resume. It creates
   a run when the task needs checkpoints, traces, evals, approvals, or multiple attempts.
4. Governed mode assigns `TASK-YYYYMMDD-NNN-slug`, writes local active state, stores task input, and
   runs Task Analysis before implementation.
5. Governed Task Analysis identifies acceptance criteria, impacted components, risks, dependencies,
   decomposition, critical checks, and architecture-review triggers.
6. If blocked by missing facts, ask through Coordinator and persist the unresolved question.
7. If architecture review is required, route to Solution Architect before planning.
```

Task analysis is mandatory for governed implementation. Assisted work needs a task manifest; direct
work does not create workflow ceremony unless the user requests persistence.

## 6.1. Architecture review lane

Architecture review is an optional gate for tasks that can change system shape or high-risk contracts.

### Required when any trigger exists

```text
Cross-service workflow, ownership, or dependency direction changes
Public API contract changes
Event contract, topic, queue, or async workflow changes
Database schema, migration, index, data backfill, or compatibility risk
New service, shared package, or runtime dependency boundary
Auth, permission, token, PII, payment, encryption, or other security-sensitive surface
Infrastructure, deployment, networking, CI/CD, or runtime topology change
Rollback, migration, data retention, or operational runbook risk
```

### Flow

```text
1. Task Analysis sets architecture_review.required, reason, and triggers.
2. Coordinator transitions ANALYZED -> ARCHITECTURE_REVIEWING.
3. Solution Architect writes architecture-review.yaml.
4. If decision is approved, Coordinator may transition to PLANNED.
5. If decision is changes_required, route back to Task Analysis or user clarification.
6. If decision is blocked, do not plan implementation until the blocker is resolved.
```

Coder Leader must include `constraints_for_coder_leader` from architecture-review.yaml in implementation-plan.yaml.

## 6.2. Fast-track lane (trivial tasks)

Some tasks are too small to justify the full pipeline. The product-component fast-track lane skips the user-approval gate on `task-analysis.yaml` (R-011-10) and the full `implementation-plan.yaml`. It still requires `task-analysis.yaml.context_plan` and a lightweight `service-assignments.yaml` before any generated coder edits source. All other gates (scope, secrets, blocker stop, dev-verification, memory) still apply.

### Eligibility (ALL conditions must hold)

```text
intent in {typo, comment, format, rename-local, docs-only, dependency-version-bump, config-value-tweak}
impacted_components count <= 1
no contract change (api, event, schema, ui, config that affects callers)
no security-sensitive surface (auth, permission, token, password, PII, payment, encryption — R-013-05)
no critical_checks beyond "lint passes" or "type-check passes"
diff size estimate <= 30 lines OR single file
no new dependency added
no test policy change
not a blocker-bug fix (blockers always use full pipeline — R-009-08)
```

If any condition fails, fall back to the standard pipeline.

### Framework-maintenance fast-track

Trivial framework maintenance should use a lighter path:

```text
eligible: docs-only, typo, comment, format, rename-local, config-value-tweak, non-destructive helper script tweak
skip: onboarding, component registry checks, generated coder selection, implementation-plan.yaml, service-assignments.yaml, qc-handoff.md, qc-test-results.yaml
required: concise task note or final response, changed_files[], and concrete verification evidence when a command or syntax check applies
```

Framework-maintenance fast-track is not allowed when the task changes:

```text
workflow state machine
approval gates
service coder write-scope rules
security/secret-handling rules
destructive command behavior
generated coder templates in a backward-incompatible way
```

Those changes remain framework maintenance, but require normal review rigor and cross-tool consistency updates.

### Fast-track flow

```text
1. Coordinator detects eligibility from user input or task-input.md.
2. task-analysis writes a minimal task-analysis.yaml with fast_track: true and skips user approval (R-011-10 exempted by R-011-10b).
3. Coder Leader skips the full implementation-plan.yaml, then writes a lightweight service-assignments.yaml with assignment_note, allowed write scope, critical checks, and context_pack.
4. Service coder implements within scope.
5. Dev verification still runs and still requires score >= 80% + critical_checks pass.
6. QC may be skipped only if test-policy.fast_track_skips_qc is true; otherwise qc-handoff + qc-runner still execute (a lightweight qc-handoff is acceptable).
7. Memory update runs only if a durable fact changed; otherwise record fast_track_completed: true in workflow-state.yaml.
```

### Required artifact deltas

```text
task-analysis.yaml: must include fast_track: true, fast_track_reason, and context_plan with medium/high confidence
service-assignments.yaml: must include assignment_note, assigned coder, allowed_write_paths, critical_checks, and context_pack
coder-results.yaml: must include changed_files[]
dev-verification.yaml: must include fast_track_acknowledged: true
```

### Audit and revocation

```text
- Coordinator records every fast-track use in workflow-state.yaml under fast_track_log[].
- If a fast-track task later causes a bug, memory-update writes the pattern to feedback/anti-patterns.md.
- User may revoke fast-track eligibility for a task at any time; Coordinator then upgrades to standard pipeline and records the upgrade reason.
```

## 6.3. Uncertainty and anti-guessing protocol (Karpathy-aligned)

All agents must follow these operating principles:

```text
1. State uncertainty explicitly (high/medium/low confidence).
2. Ask clarification when unknown facts can change behavior, scope, security, or acceptance criteria.
3. Do not fabricate facts or outputs; use unknown + evidence-needed instead.
4. Verify critical claims with concrete evidence before declaring completion.
```

When any principle is violated, stop execution and route back to Coordinator or Workflow Policy.

## 6.4. Specialist advisory lane

Specialist advisors (the 4th agent class, see `.maestro/engine/docs/agent-taxonomy.md` and `R-016`) provide
evidence-based domain advice **inside existing states** — they do not add new workflow states and are
never user entrypoints.

### When advisors are invoked

```text
1. Task Analysis lists advisory_required: [<specialist-id>, ...] in task-analysis.yaml, OR
2. A workflow agent detects a domain risk during its state:
   - Solution Architect (ARCHITECTURE_REVIEWING): api-designer, database-architect, cloud-architect,
     event-architect, ml-ai-architect, data-engineer.
   - Coder Leader (PLANNED/IMPLEMENTING): ui-ux-designer, migration-strategist, code-reviewer.
   - Dev Verification (DEV_VERIFYING): security-auditor, performance-engineer, accessibility-auditor,
     sre-observability, code-reviewer.
   - QC Handoff (QC): qa-strategist.
   - Coordinator (pre-pipeline / discovery): discovery-analyst, business-analyst, product-strategist.
   - Memory Update: technical-writer.
```

### Flow

```text
1. The owning workflow agent invokes the specialist as a sub-step of its current state.
2. The specialist writes .maestro/work/tasks/<task-id>/advisories/<id>.yaml and returns a summary.
3. The owning agent reads handoff.must_address, records disposition (addressed / deferred / rejected),
   and continues the state. Advisory output is advisory: the workflow agent still owns the decision.
4. Advisors that overlap a workflow mandate AUGMENT it (code-reviewer↔Coder Leader R-005-09,
   business-analyst↔Task Analysis, qa-strategist↔qc-runner/qc-handoff, security-auditor↔Dev Verification);
   the workflow agent remains the gate owner.
```

Advisors obey the same scope, security/secret (R-013), and tool limits (Read, Grep, Glob, Write own
advisory only). They never assign coders or mark gates.

## 6.5. Autonomous delivery lane (Autopilot)

Autopilot runs the pipeline to a finished, runnable product without stopping at soft gates. It is the
`autonomous` execution mode, started with `/ship` and governed by R-019. Full contract:
`.maestro/engine/rules/19-autonomous-delivery-rules.md`.

```text
0a. Blueprint gate (idea/greenfield): before building, produce product-blueprint.yaml (problem/goal/
   users, MVP vs production, monolith vs modular-monolith vs microservices with rationale, tech stack
   with rationale, features -> acceptance criteria, non-functional targets, assumptions/risks/tradeoffs,
   out-of-scope) and get EXPLICIT user approval (R-019-0a..0d). For UI products it MUST also include a
   UI/UX proposal delivered as a viewable static HTML/CSS prototype (docs/experience/wireframes/
   index.html + per-screen pages + styles.css tokens, plus Mermaid flows + specs) that the user opens
   in a browser and approves BEFORE coding the UI (R-019-0a-ui). Build only when status: approved. The approved blueprint is the build contract;
   acceptance criteria derive from it.
0b. Local-only: everything runs in the local dev environment — install, build, tests, and a local smoke
   run (R-019-00b). Autopilot never deploys or provisions infra; that is a separate phase after the user
   confirms the local result and requests it (R-019-00c).
1. Grant: record the one-time autonomy grant in workflow-state.yaml.autopilot (R-019-01). The grant is
   per-run and expires at DONE, cancel, or user revoke. Enable tool fullaccess for the run so calls do
   not prompt per command; the scope/secret/destructive hooks still run.
2. Soft gates auto-approve and record (R-019-04): create coders, run onboarding when knowledge is
   missing, create tests, governed analysis -> coder leader. Each writes an approval record with
   decided_by: autopilot.
3. Run the normal states (ANALYZED -> PLANNED -> IN_DEV -> DEV_VERIFYING -> QC -> ...). No new states.
4. Self-heal loop (R-019-07..10): after each step run real verification — build, lint when configured,
   tests, and a smoke run of the app when runnable. On failure, capture the error, route back through
   dev-verification -> coder-leader (or qc -> bug-router -> dev), fix, and re-verify. Bounded by
   max_attempts_per_stage (default 5). Never fabricate green; never skip/disable a failing test to pass.
5. Real-user QC (R-019-QC1..4): QC acts as a thorough end user — a full test plan across functional /
   UI / API / UX / edge / regression, logs every failure as a bug, and loops qc -> bug-router -> dev fix
   -> re-QC until every test case passes and ZERO bugs remain (blocker AND non-blocker), not just zero
   blockers.
6. Hard-stops (R-019-05) — always hand back to the user, never auto-approved: destructive/production/
   irreversible actions, a real secret/credential is required, scope expansion beyond acceptance
   criteria, workflow policy/state/identity changes, skipping QC or downgrading a blocker, or a stage
   that still fails after max attempts (escalate with diagnostics).
7. Done (R-019-11): transition to DONE only when, LOCALLY, build is clean, tests pass, the app
   smoke-runs, every acceptance criterion is met with evidence, the full QC suite is green with ZERO open
   bugs of any severity, and dev-verification passes. DONE = locally complete and user-verifiable, not
   deployed. Deliver the handover (R-019-12):
   what was built, the exact local run commands, and verification evidence; offer provisioning/deploy as
   the explicit next phase only after the user confirms locally.
```

## 7. Coder Leader workflow

This section applies to the standard product-component implementation pipeline. Framework-maintenance fast-track skips Coder Leader unless the task changes high-risk framework behavior.

```text
1. Read task-analysis.yaml.
2. If architecture_review.required is true, read architecture-review.yaml and enforce its constraints.
3. Read agents.yaml for product-component coder selection.
4. Select impacted component coders.
5. Create implementation-plan.yaml and service-assignments.yaml.
6. Sequence cross-service work.
7. Enforce API and event contracts.
8. Collect coder outputs.
9. Review code quality and architecture alignment.
10. Send to dev-verification.
```

For multi-service tasks, service coders communicate through Coder Leader, not directly.

## 8. Service coder workflow

```text
1. Read task assignment and component knowledge.
2. Confirm task is within allowed write paths.
3. If outside scope, stop and ask Coder Leader.
4. Implement only assigned scope.
5. Reuse existing project patterns.
6. Follow component test policy.
7. Do not create test files if unit tests are not required by the component/project.
8. If tests are required, add or update tests using existing conventions.
9. If tests are not required, perform manual verification and document evidence.
10. Return changed files, decisions, risks, and verification notes to Coder Leader.
```

## 9. Dev verification gate

Code Done requires all conditions:

```text
Implementation matches acceptance criteria
No known blocker remains
Allowed write scope respected
Critical checks pass 100%
Dev verification score >= 80%
Required tests pass when component policy requires tests
Manual verification documented when tests are not required
QC handoff can be generated from available evidence
Coder Leader code-quality review completed and recorded in coder-results.yaml
```

If any critical check fails, state is `DEV_BLOCKED`, even if the score is >= 80%.

## 10. QC handoff workflow

```text
1. QC Handoff reads task analysis, implementation plan, coder outputs, and dev verification.
2. It writes .maestro/work/tasks/<task-id>/qc-handoff.md.
3. It includes scope, changed areas, acceptance criteria, dev verification result, QC test suggestions, known risks, test data, environment notes, and retest scope.
4. Coordinator marks QC_READY only after handoff exists.
```

QC Runner must not start without a QC handoff.

## 11. QC workflow

```text
1. QC Runner reads qc-handoff.md.
2. It creates QC test cases.
3. It executes or records tests by environment as allowed.
4. On blocker bug: stop immediately, create canonical blocker bug under `.maestro/work/bugs/blockers/`, update the task `bugs.yaml` index, route to dev.
5. On non-blocker bug: create canonical non-blocker bug under `.maestro/work/bugs/non-blockers/`, update the task `bugs.yaml` index, continue unaffected test cases.
6. On fixes: retest bug scope and related regression scope.
7. QC_DONE requires zero open blockers.
```

## 12. Bug classification

Blocker if any condition is true:

```text
Main happy path cannot be tested
Application crashes or core API returns systemic failure
Authentication or authorization is broken
Data corruption or data loss risk exists
Required setup/data creation is blocked
Bug blocks downstream QC cases
Security vulnerability is severe
```

Non-blocker examples:

```text
Cosmetic issue
Copy or message issue
Minor layout issue
Rare edge case that does not block main flow
Non-critical warning
Performance concern below agreed blocker threshold
```

## 13. Memory update workflow

Update memory after:

```text
New service/module discovered
Agent scope changes
Architecture or API decision
Test policy decision
Bug root cause pattern
QC blocker/non-blocker classification insight
Reusable manual verification note
User workflow preference
User feedback on AI mistakes or missing cases
```

Never store:

```text
Secrets
Passwords
Raw access tokens
Long logs
Temporary noisy output
Speculative facts without confidence marker
```

Feedback triage flow:

```text
1. Capture raw feedback in .maestro/memory/project/feedback/inbox.md
2. For coding errors, include root_cause, prevention_rule, regression_check, and recurrence_key
3. During /sync-memory, triage each entry
4. Promote recurring mistakes -> feedback/anti-patterns.md
5. Promote validated fixes -> feedback/patterns.md
6. Feed relevant patterns/anti-patterns into the next task-analysis context_plan and service-assignment context_pack
7. Cite source artifact, canonical bug, and confidence in memory-updates.yaml
```

## 13.1. Git workflow (Git-flow)

Maestro uses Git-flow. Full contract: `.maestro/engine/rules/20-git-workflow-rules.md`; helper command
`/git`.

```text
1. Branches: main (production, tagged), develop (integration). Work happens on feature/<task-id>-<slug>
   off develop; release/<version> and hotfix/<id> follow Git-flow. Never commit directly to main/develop.
2. Commits: Conventional Commits (<type>(<scope>): summary), milestone-sized, each builds, body explains
   why. End every commit body with: Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>.
3. Never commit secrets/.env/raw tokens/large logs; respect .gitignore. Ask before git init on a
   non-repo; never commit pre-existing unrelated changes.
4. Outward-facing git is gated (explicit user approval, R-020-10): push, opening/merging a PR, merging
   to main/develop, tags/releases, force push, history rewrite. Destructive ones are also blocked by the
   destructive-guard hook.
5. PRs use pull-request.template.md; default squash-merge into develop unless the user chooses otherwise.
6. Autopilot git is local-only automatic (R-020-12/13): create the feature branch + milestone commits
   locally; push/PR/merge wait for the user. On DONE, propose the branch + ready PR for approval.
```

## 14. Allowed exceptions

Coordinator may ask user to approve exceptions for:

```text
Skipping generated coder creation
Running without complete onboarding
Skipping QC for urgent patch
Creating tests even though current policy does not require tests
Changing service scope
Skipping a blocker bug
```

Record every approved exception in the task history and memory update artifact.

## 15. Visual flow

The visual version of this workflow is maintained in [docs/visual-flow.md](docs/visual-flow.md). Keep the diagrams aligned with this policy whenever states, gates, or agent responsibilities change.

## 16. Rule and command layer

Rules live in `.maestro/engine/rules/` and are mandatory. Commands live in `.claude/commands/` and are the user-facing entrypoints.

```text
/coord          Main entrypoint
/onboard        Build or refresh Project Brain
/create-coders  Generate service coders after approval
/analyze-task   Normalize task input
/plan-dev       Plan implementation
/dev            Run implementation
/verify-dev     Evaluate Code Done
/handoff-qc     Create QC handoff
/qc             Run QC
/bug            Route defects
/sync-memory    Persist durable knowledge
/skills         Maintain installed skills and registry metadata
/resume-task    Continue from current state
/maestro-init        Install .maestro/ + component/doc roots + managed instruction block
/access         Switch tool-permission posture: full / guarded (R-011-14)
/policy-check   Validate transitions, exceptions, and artifact snapshots
/status         Print workflow status and agent activity dashboard using response-ui mode
```

Agents must load the rules required by the active command before acting.

## 17. Skill composition

Skills are composable capabilities. An agent may use many skills, and a skill may be reused by many agents.

```text
required_skills: always loaded for the agent's primary command
optional_skills: loaded only when the task needs that capability
contextual_skills: selected from Project Brain, Component Knowledge, component stack, task risks, and artifact needs
```

Skill composition rules are defined in `.maestro/engine/rules/14-skill-composition-rules.md`.
Model routing, activity telemetry, and response UI rules are defined in `.maestro/engine/rules/15-model-routing-observability-rules.md`.
