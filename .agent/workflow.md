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
8. .runtime/context/test-policy.yaml when coding, verifying, or QC testing
9. Relevant .runtime/context/services/<service>.yaml files only for impacted services
10. Relevant .runtime/tasks/<task-id> artifacts
```

If `.runtime/context/index.yaml` or `project-brain.yaml` is missing, empty, or stale, stop normal routing and run onboarding or `/sync-memory --refresh-index`.

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

Some tasks are too small to justify the full pipeline. The fast-track lane skips the user-approval gate on `task-analysis.yaml` (R-011-10) and the implementation-plan/service-assignments artifacts. All other gates (scope, secrets, blocker stop, dev-verification, memory) still apply.

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

### Fast-track flow

```text
1. Coordinator detects eligibility from user input or task-input.md.
2. task-analysis writes a minimal task-analysis.yaml with fast_track: true and skips user approval (R-011-10 exempted by R-011-10b).
3. Coder Leader skips implementation-plan.yaml and service-assignments.yaml; writes a single-line assignment in coder-results.yaml.assignment_note instead.
4. Service coder implements within scope.
5. Dev verification still runs and still requires score >= 80% + critical_checks pass.
6. QC may be skipped only if test-policy.fast_track_skips_qc is true; otherwise qc-handoff + qc-runner still execute (a lightweight qc-handoff is acceptable).
7. Memory update runs only if a durable fact changed; otherwise record fast_track_completed: true in workflow-state.yaml.
```

### Required artifact deltas

```text
task-analysis.yaml: must include fast_track: true and fast_track_reason
coder-results.yaml: must include assignment_note and changed_files[]
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

## 7. Coder Leader workflow

```text
1. Read task-analysis.yaml.
2. If architecture_review.required is true, read architecture-review.yaml and enforce its constraints.
3. Read agent-registry.yaml.
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
4. On blocker bug: stop immediately, create blocker bug, route to dev.
5. On non-blocker bug: create non-blocker bug, continue unaffected test cases.
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
2. During /sync-memory, triage each entry
3. Promote recurring mistakes -> feedback/anti-patterns.md
4. Promote validated fixes -> feedback/patterns.md
5. Cite source artifact and confidence in memory-updates.yaml
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
/policy-check   Validate transitions and exceptions
/status         Print workflow status
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
