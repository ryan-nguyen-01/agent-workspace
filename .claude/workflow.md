# End-to-End Workflow Policy

This is the mandatory source of truth for `.claude` agents.

## 1. Required reading order

Every agent reads only the minimum files needed, in this order:

```text
1. .claude/workflow.md
2. Its own .claude/agents/<agent>.agent.md
3. .claude/context/project-brain.yaml
4. .claude/context/agent-registry.yaml when routing or coding
5. .claude/context/test-policy.yaml when coding, verifying, or QC testing
6. Relevant .claude/context/services/<service>.yaml files
7. Relevant .claude/tasks/<task-id> artifacts
```

If the project brain is missing, empty, or stale, stop normal routing and run onboarding.

## 2. Workflow states

```text
NEW
NEED_ONBOARDING
ONBOARDED
NEED_AGENT_CREATION_APPROVAL
AGENTS_READY
READY_FOR_ANALYSIS
ANALYZED
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
No direct routing from raw user input to onboarding, task-analysis, coder-leader, service coders, dev-verification, qc, or bug-router.
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
4. Onboarding writes project-brain.yaml, service-catalog.yaml, test-policy.yaml, and services/<service>.yaml.
5. Onboarding proposes coder agent candidates.
6. Coordinator asks the user whether to create coder agents.
7. Agent Factory runs only after approval.
```

Onboarding must not make application code changes.

## 5. Agent creation workflow

```text
1. Agent Factory reads project brain and service catalog.
2. It creates one coder contract per approved service/module.
3. It writes generated coder agent definitions from templates/agent-coder.template.md.
4. It writes or updates context/agent-registry.yaml.
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
1. Coordinator stores original input as tasks/<task-id>/task-input.md.
2. Task Analysis creates task-analysis.yaml.
3. Task Analysis identifies intent, acceptance criteria, impacted services, risks, dependencies, and critical checks.
4. If blocked by missing business or technical facts, Task Analysis asks through Coordinator and marks requires_user_clarification.
5. Coder Leader receives only analyzed tasks.
```

No coder starts before `task-analysis.yaml` exists.

## 6.1. Uncertainty and anti-guessing protocol (Karpathy-aligned)

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
2. Read agent-registry.yaml.
3. Select impacted service coders.
4. Create implementation-plan.yaml and service-assignments.yaml.
5. Sequence cross-service work.
6. Enforce API and event contracts.
7. Collect coder outputs.
8. Send to dev-verification.
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
```

If any critical check fails, state is `DEV_BLOCKED`, even if the score is >= 80%.

## 10. QC handoff workflow

```text
1. QC Handoff reads task analysis, implementation plan, coder outputs, and dev verification.
2. It writes tasks/<task-id>/qc-handoff.md.
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

Rules live in `.claude/rules/` and are mandatory. Commands live in `.claude/commands/` and are the user-facing entrypoints.

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
/resume-task    Continue from current state
/policy-check   Validate transitions and exceptions
```

Agents must load the rules required by the active command before acting.

## 17. Skill composition

Skills are composable capabilities. An agent may use many skills, and a skill may be reused by many agents.

```text
required_skills: always loaded for the agent's primary command
optional_skills: loaded only when the task needs that capability
contextual_skills: selected from Project Brain, Service Brain, service stack, task risks, and artifact needs
```

Skill composition rules are defined in `.claude/rules/14-skill-composition-rules.md`.
