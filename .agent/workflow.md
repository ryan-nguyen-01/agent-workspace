# End-to-End Workflow Policy

This is the mandatory source of truth for all `agent-workspace` adapters and workflow agents.

## 1. Required reading order

Every agent reads only the minimum files needed. Memory is the agent brain; services are coding targets; state is transient workflow position.

```text
1. .agent/workflow.md
2. .runtime/context/workflow-state.yaml
3. Its own .claude/agents/<agent>.agent.md
4. .runtime/context/index.yaml
5. .runtime/context/project-brain.yaml only when routing/planning needs project facts
6. .runtime/context/service-catalog.yaml when service discovery or impact analysis is needed
7. .runtime/context/agent-registry.yaml when routing or coding
8. .runtime/context/model-routing.yaml when selecting or reporting agent model profiles
9. .runtime/context/agent-activity.yaml when reporting status or updating activity telemetry
10. .runtime/context/response-ui.yaml when formatting status, reports, or final responses
11. .runtime/context/test-policy.yaml when coding, verifying, or QC testing
12. Relevant .runtime/context/services/<service>.yaml files only for impacted services
13. Relevant .runtime/tasks/<task-id> artifacts
```

If `.runtime/context/index.yaml` or `project-brain.yaml` is missing, empty, or stale for applied-service work, stop normal routing and run onboarding or `/sync-memory --refresh-index`. For framework maintenance, apply the framework-template exception below first.

### Framework-template exception

When `.runtime/context/workflow-state.yaml` has:

```yaml
distribution_mode: "framework-template"
instance_status: "not_applied"
```

the repository is the reusable `agent-workspace` distribution, not an onboarded application workspace. In this mode, `NEED_ONBOARDING`, empty service catalogs, and seed brain values are expected and must not block framework maintenance.

Framework maintenance includes changes to:

```text
AGENTS.md
CLAUDE.md
COMMAND.md
.agent/**
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

Onboarding, service catalog, generated service coders, and service brain freshness are required only before analyzing, planning, or coding application repositories under `services/<service-name>/`.

## 1.1. Folder semantics

```text
.runtime/context/           Durable brain + service control plane + workflow state
  project-brain.yaml         Project facts (architecture, policies, freshness)
  index.yaml                 Memory routing index
  service-catalog.yaml       Service paths and ownership
  agent-registry.yaml        Active generated coder agents
  test-policy.yaml           Test policy per service
  skill-registry.yaml        Skill selection registry
  workflow-state.yaml        Current workflow state, allowed transitions
  services/<service>.yaml    Per-service brain
  feedback/                  Patterns and anti-patterns
.runtime/tasks/             Per-task evidence and artifacts
.runtime/bugs/              Bug reports and blocker/non-blocker routing artifacts
inputs/                    User-provided reference docs (PRD, HLD, ADR, OpenAPI, glossary, runbooks)
  product/                   PRD, business specs, user stories
  architecture/              HLD, LLD, ADRs, system diagrams
  api/                       OpenAPI/Swagger specs, contracts
  domain/                    Domain models, glossary, business rules
  runbooks/                  Ops playbooks, incident response
  misc/                      Uncategorized
services/                  Ignored workspace for cloned application repositories (not memory, not inputs)
```

Agents must not treat `services/` (root-level workspace) as durable memory, and must not store source code under `.runtime/context/`. Onboarding reads `inputs/` (user knowledge) and `services/<repo>/` (source code) as the two scan sources; conflicts resolve per R-002-11.

## 1.2. Task classification for speed

The coordinator should classify every request before loading broad context:

```yaml
target_scope: framework | applied_service | unknown
task_size: trivial | normal | high_risk
requires_onboarding: true | false
requires_full_artifacts: true | false
```

Classification rules:

```text
target_scope=framework when the requested change is confined to framework instructions, rules, templates, tool adapters, scripts, or documentation in this repository.
target_scope=applied_service when the requested change reads or writes application source under services/<service-name>/.
requires_onboarding=false for target_scope=framework in framework-template/not_applied mode.
requires_full_artifacts=false for trivial framework maintenance with no approval-gate, security, state-machine, generated-coder scope, or service contract impact.
```

For `target_scope=framework`, agents should read only the entrypoint files and directly relevant framework files. Do not load project brain, service catalog, service brain files, agent registry, or test policy unless the requested change directly edits or validates those contracts.

## 1.3. Context economy and universal project support

The framework must work across project shapes without loading the whole repo. Agents use a signature-first read strategy and expand context only when task risk or evidence gaps require it.

### Universal project archetypes

Onboarding records one or more archetypes in `project-brain.yaml.project_profile.archetypes` and per-service `profile.archetypes`:

```text
backend-api, frontend-web, mobile-app, desktop-app, cli-tool, library-sdk,
data-pipeline, ml-model, infra-iac, embedded-firmware, docs-site,
docs-and-templates, plugin-extension, monorepo-platform, workflow-framework
```

Unknown or mixed projects are allowed, but must be marked with `confidence` and evidence. Do not force a project into a known archetype when evidence is weak.

### Signature-first reads

Before broad source reads, agents inspect only:

```text
file tree shape, service-catalog paths, package/build manifests, lockfiles,
route/API/schema definitions, test config, CI/deploy config, and inputs-index rows
```

Agents skip generated/vendor/heavy roots by default: `node_modules`, `vendor`, `dist`, `build`, `.next`, `coverage`, `.git`, and large generated files.

### Task context plan

Task Analysis writes `task-analysis.yaml.context_plan` for every applied-service task. Later phases must read that plan before opening source files. The plan records:

```text
context confidence, max memory/source/skill file budgets, required memory,
required source evidence, optional source evidence, excluded paths,
expansion triggers, unresolved context, and evidence confidence
```

If `context_plan.confidence` is low, or required service/test/contract evidence is missing, Coordinator must not advance into `IN_DEV` until the context is refreshed or the user explicitly accepts the risk.

### Expansion triggers

Agents may exceed the default context budget only when one of these is true:

```text
Impacted service cannot be resolved
Acceptance criteria cannot be mapped to files
Service boundary, test policy, or contract ownership is unknown
Security, schema, migration, data, infra, or cross-service risk appears
Implementation touches shared code or public contracts
Evidence is stale or contradicts inputs/
```

When expanding, record the reason in `task-analysis.yaml.context_plan` or the phase artifact that caused the expansion. This keeps recall high while making token use auditable.

## 1.4. Model routing and agent activity

Agent-to-model selection is controlled by `.runtime/context/model-routing.yaml`.

```text
Deep reasoning profile:
  Claude -> Opus
  Codex  -> GPT-5.5
  Use for task-analysis, solution-architect, workflow-policy, blocker routing, architecture/security/data/contract ambiguity.

Coding profile:
  Claude -> Sonnet
  Codex  -> Codex coding model (`gpt-5.3-codex` by default)
  Use for coder-leader implementation planning, generated service coders, coder-infra, coder-database, refactors, tests, and code review.
```

Provider model IDs are configurable aliases. If a tool does not support the configured model, use the closest available equivalent and record the fallback in `.runtime/context/agent-activity.yaml`.

`/status` renders the agent activity dashboard from `.runtime/context/agent-activity.yaml`:

```text
agent id, workflow phase, current action, status, model profile/model id,
started_at, elapsed time, ETA, token budget, token usage, and cost
```

Do not invent exact token usage or cost. If the active tool does not expose usage metrics, report `unknown` or a clearly marked estimate.

Adapters that can run local commands may update this file through:

```text
python3 scripts/agent-activity.py start --agent-id <agent> --phase <phase> --current-action <summary>
python3 scripts/agent-activity.py heartbeat --agent-id <agent> --current-action <summary>
python3 scripts/agent-activity.py block --agent-id <agent> --summary <summary>
python3 scripts/agent-activity.py complete --agent-id <agent> --summary <summary>
```

This helper is optional. It improves observability but does not weaken the rule that exact token/cost/ETA values require real adapter metrics.

## 1.5. Response UI contract

Response layout is controlled by `.runtime/context/response-ui.yaml`.

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

The terminal mirror supports `python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json>`. Add `--write` to generate `.runtime/status.md` and `.runtime/status.html` from the same source files.

User-requested output format wins for the current response unless it would hide required evidence, safety warnings, policy decisions, or unknown/estimated token/cost labels.

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

## 2.2. Distribution mode

`.runtime/context/workflow-state.yaml.distribution_mode` (`framework-template` | `workspace`) and
`instance_status` are set during onboarding, or by an explicit user-approved edit to
`workflow-state.yaml`. There is no dedicated switch command; the coordinator may change the mode only
under the approval-required action `switch_distribution_mode` (R-011-13).

```text
1. Do not infer a mode switch from unrelated task text; require explicit user intent.
2. Do not switch modes while active_task_id is set.
3. framework-template => distribution_mode=framework-template, instance_status=not_applied, current_state=NEED_ONBOARDING.
4. workspace          => distribution_mode=workspace, instance_status=applied, current_state=NEED_ONBOARDING.
5. Do not mutate project-brain.yaml, service-catalog.yaml, agent-registry.yaml, inputs/, or services/ as part of the switch.
6. After switching to workspace, the next applied-service command is /onboard.
```

## 3. Agent responsibilities

| Agent | Responsibility | Must not do |
|---|---|---|
| coordinator | Own routing, brain checks, approval gates, workflow state | Implement code |
| onboarding | Analyze project and write project/service brain | Create coder agents without user approval |
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
4. Onboarding writes .runtime/context/project-brain.yaml, .runtime/context/service-catalog.yaml, .runtime/context/test-policy.yaml, and .runtime/context/services/<service>.yaml.
5. Onboarding proposes coder agent candidates.
6. Coordinator asks the user whether to create coder agents.
7. Agent Factory runs only after approval.
```

Onboarding must not make application code changes.

## 5. Agent creation workflow

```text
1. Agent Factory reads project brain and .runtime/context/service-catalog.yaml.
2. It creates one coder contract per approved service/module.
3. It writes generated coder agent definitions from templates/agent-coder.template.md.
4. It writes or updates .runtime/context/agent-registry.yaml.
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
1. Coordinator assigns `TASK-YYYYMMDD-NNN-slug`, writes it to `.runtime/context/workflow-state.yaml.active_task_id`, and stores original input as `.runtime/tasks/<task-id>/task-input.md`.
2. Task Analysis creates task-analysis.yaml.
3. Task Analysis identifies intent, acceptance criteria, impacted services, risks, dependencies, critical checks, and whether architecture review is required.
4. If blocked by missing business or technical facts, Task Analysis asks through Coordinator and marks requires_user_clarification.
5. If architecture_review.required is true, Coordinator routes to Solution Architect before planning.
6. Coder Leader receives only analyzed tasks, and must read architecture-review.yaml when required.
```

No coder starts before `task-analysis.yaml` exists.

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

Some tasks are too small to justify the full pipeline. The applied-service fast-track lane skips the user-approval gate on `task-analysis.yaml` (R-011-10) and the full `implementation-plan.yaml`. It still requires `task-analysis.yaml.context_plan` and a lightweight `service-assignments.yaml` before any generated coder edits source. All other gates (scope, secrets, blocker stop, dev-verification, memory) still apply.

### Eligibility (ALL conditions must hold)

```text
intent in {typo, comment, format, rename-local, docs-only, dependency-version-bump, config-value-tweak}
impacted_services count <= 1
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

In framework-template/not_applied mode, trivial framework maintenance should use a lighter path:

```text
eligible: docs-only, typo, comment, format, rename-local, config-value-tweak, non-destructive helper script tweak
skip: onboarding, service catalog checks, generated coder selection, implementation-plan.yaml, service-assignments.yaml, qc-handoff.md, qc-test-results.yaml
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

Specialist advisors (the 4th agent class, see `.agent/docs/agent-taxonomy.md` and `R-016`) provide
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
2. The specialist writes .runtime/tasks/<task-id>/advisories/<id>.yaml and returns a summary.
3. The owning agent reads handoff.must_address, records disposition (addressed / deferred / rejected),
   and continues the state. Advisory output is advisory: the workflow agent still owns the decision.
4. Advisors that overlap a workflow mandate AUGMENT it (code-reviewer↔Coder Leader R-005-09,
   business-analyst↔Task Analysis, qa-strategist↔qc-runner/qc-handoff, security-auditor↔Dev Verification);
   the workflow agent remains the gate owner.
```

Advisors obey the same scope, security/secret (R-013), and tool limits (Read, Grep, Glob, Write own
advisory only). They never assign coders or mark gates.

## 7. Coder Leader workflow

This section applies to the standard applied-service implementation pipeline. Framework-maintenance fast-track skips Coder Leader unless the task changes high-risk framework behavior.

```text
1. Read task-analysis.yaml.
2. If architecture_review.required is true, read architecture-review.yaml and enforce its constraints.
3. Read agent-registry.yaml for applied-service coder selection.
4. Select impacted service coders.
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
1. Read task assignment and service brain.
2. Confirm task is within allowed write paths.
3. If outside scope, stop and ask Coder Leader.
4. Implement only assigned scope.
5. Reuse existing project patterns.
6. Follow service test policy.
7. Do not create test files if unit tests are not required by the service/project.
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
Required tests pass when service policy requires tests
Manual verification documented when tests are not required
QC handoff can be generated from available evidence
Coder Leader code-quality review completed and recorded in coder-results.yaml
```

If any critical check fails, state is `DEV_BLOCKED`, even if the score is >= 80%.

## 10. QC handoff workflow

```text
1. QC Handoff reads task analysis, implementation plan, coder outputs, and dev verification.
2. It writes .runtime/tasks/<task-id>/qc-handoff.md.
3. It includes scope, changed areas, acceptance criteria, dev verification result, QC test suggestions, known risks, test data, environment notes, and retest scope.
4. Coordinator marks QC_READY only after handoff exists.
```

QC Runner must not start without a QC handoff.

## 11. QC workflow

```text
1. QC Runner reads qc-handoff.md.
2. It creates QC test cases.
3. It executes or records tests by environment as allowed.
4. On blocker bug: stop immediately, create canonical blocker bug under `.runtime/bugs/blockers/`, update the task `bugs.yaml` index, route to dev.
5. On non-blocker bug: create canonical non-blocker bug under `.runtime/bugs/non-blockers/`, update the task `bugs.yaml` index, continue unaffected test cases.
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
1. Capture raw feedback in .runtime/context/feedback/inbox.md
2. For coding errors, include root_cause, prevention_rule, regression_check, and recurrence_key
3. During /sync-memory, triage each entry
4. Promote recurring mistakes -> feedback/anti-patterns.md
5. Promote validated fixes -> feedback/patterns.md
6. Feed relevant patterns/anti-patterns into the next task-analysis context_plan and service-assignment context_pack
7. Cite source artifact, canonical bug, and confidence in memory-updates.yaml
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

Rules live in `.agent/rules/` and are mandatory. Commands live in `.claude/commands/` and are the user-facing entrypoints.

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
/aw-init        Scaffold .agent/+.runtime/+CLAUDE.md into another project (post-plugin-install)
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
contextual_skills: selected from Project Brain, Service Brain, service stack, task risks, and artifact needs
```

Skill composition rules are defined in `.agent/rules/14-skill-composition-rules.md`.
Model routing, activity telemetry, and response UI rules are defined in `.agent/rules/15-model-routing-observability-rules.md`.
