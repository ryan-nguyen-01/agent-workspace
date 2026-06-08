# Agent Catalog

![System overview](diagrams/01-system-overview.svg)

This document is the detailed reference for all 12 workflow agents and the generated service coder pattern. For the 19 specialist advisors (4th agent class, advisor-only) see [`.claude/agents/specialists/README.md`](../../.claude/agents/specialists/README.md) and [agent-taxonomy.md](agent-taxonomy.md); for class definitions see [agent-taxonomy.md](agent-taxonomy.md).

## Agent overview

| #   | Agent            | Phase     | Writes code? | Key rule |
| --- | ---------------- | --------- | ------------ | -------- |
| 1   | Coordinator      | Routing   | No           | R-000    |
| 2   | Onboarding       | Knowledge | No           | R-002    |
| 3   | Agent Factory    | Knowledge | No           | R-003    |
| 4   | Task Analysis    | Execution | No           | R-004    |
| 5   | Solution Architect | Execution | No         | R-004/R-005 |
| 6   | Coder Leader     | Execution | No           | R-005    |
| 7   | Dev Verification | Execution | No           | R-007    |
| 8   | QC Handoff       | QC        | No           | R-008    |
| 9   | QC Runner        | QC        | No           | R-008    |
| 10  | Bug Router       | QC        | No           | R-009    |
| 11  | Memory Update    | Knowledge | No           | R-010    |
| 12  | Workflow Policy  | Routing   | No           | R-011    |
| —   | Service Coders   | Execution | **Yes**      | R-006    |

Only generated service coders write application code. All 12 fixed agents are read-only with respect to application source.

---

## 1. Coordinator

**File:** `coordinator.agent.md`

**Role:** Central workflow router. Checks project brain, routes tasks to the correct agent, enforces approval gates, and manages the state machine. Does not write application code.

**Inputs:** User request, project brain state, agent registry, workflow state

**Outputs:** State transitions, routing decisions, approval requests

**Required skills:** skill-project-brain, skill-workflow-policy

**Key behaviors:**

```text
Check project brain freshness before routing
Enforce bootstrap guard (onboarding if brain missing)
Ask user approval for gated actions (R-011)
Route to correct agent based on task state
Never write application code
```

---

## 2. Onboarding

**File:** `onboarding.agent.md`

**Role:** Scans the project repository to build the project brain, component registry, test policy, and component knowledge files. Proposes coder agent candidates but does not create them.

**Inputs:** Repository filesystem

**Outputs:**

```text
.maestro/knowledge/project.yaml
.maestro/registry/components.yaml
.maestro/knowledge/test-policy.yaml
.maestro/knowledge/components/<component-id>.yaml
Coder agent candidates (requires user approval)
```

**Required skills:** skill-project-onboarding, skill-project-brain

**Key behaviors:**

```text
Detect: repo type, languages, services, entry points, DB, CI/CD, test frameworks
Build deep project intelligence (reusable assets, conventions, flows)
Mark incomplete scans as partial, not complete
Never modify application code
Never create coder agents without user approval
Never store secrets
```

See also: [deep-onboarding.md](deep-onboarding.md)

---

## 3. Agent Factory

**File:** `agent-factory.agent.md`

**Role:** Creates component-specific coder agents from onboarding output and the user-approved component list. Writes agent contracts and updates the agent registry.

**Inputs:** Approved component list, project brain, component registry, test policy

**Outputs:**

```text
.claude/agents/coders/coder-<service-slug>.agent.md
.maestro/registry/agents.yaml (updated)
```

**Required skills:** skill-agent-factory

**Key behaviors:**

```text
Create agents only for explicitly approved services
Each coder must have: allowed_read_paths, allowed_write_paths,
  forbidden_paths, test_policy, escalation rules
Never create full-repo coder agents
Never expand scope without user approval
```

---

## 4. Task Analysis

**File:** `task-analysis.agent.md`

**Role:** Normalizes HLD, LLD, tickets, bug reports, or user text into a structured task specification before implementation.

**Inputs:** Task source (any format), project brain, component registry

**Outputs:**

```text
.maestro/work/tasks/<task-id>/task-input.md
.maestro/work/tasks/<task-id>/task-analysis.yaml
```

**Required skills:** skill-task-analysis

**Key behaviors:**

```text
Extract: intent, business goal, acceptance criteria, impacted services,
  risks, blockers, critical checks, dev verification checklist, QC focus
Identify reusable assets and conventions relevant to the task
Present task-analysis.yaml to user for review and approval before routing
Mark requires_user_clarification when blocked by missing facts
Never write application code
```

---

## 5. Solution Architect

**File:** `solution-architect.agent.md`

**Role:** Reviews architecture risk after Task Analysis and before implementation planning when a task changes cross-component flows, public APIs, events, schemas, security-sensitive surfaces, infrastructure, or rollout strategy.

**Inputs:** Task analysis, project brain, architecture memory, component registry, agent registry

**Outputs:**

```text
.maestro/work/tasks/<task-id>/architecture-review.yaml
Decision: approved | changes_required | blocked
```

**Required skills:** none fixed; reads architecture memory and applicable technical skills selected by task context

**Key behaviors:**

```text
Validate service boundaries, contracts, data flow, migration, rollout, and rollback constraints
Identify ADR needs, open questions, and approval gates
Write constraints_for_coder_leader for implementation planning
Never write application code or assign coders
```

---

## 6. Coder Leader

**File:** `coder-leader.agent.md`

**Role:** Coordinates generated service coders for implementation. Owns planning, assignment, cross-service integration, and dev readiness.

**Inputs:** Task analysis, project brain, agent registry, test policy

**Outputs:**

```text
.maestro/work/tasks/<task-id>/implementation-plan.yaml
.maestro/work/tasks/<task-id>/service-assignments.yaml
.maestro/work/tasks/<task-id>/coder-results.yaml
```

**Required skills:** skill-coder-leader

**Key behaviors:**

```text
Create implementation plan before assigning coders
Select coders from agent registry
Protect API, event, schema, and shared package contracts
Route cross-service requests between coders
Cannot claim Code Done (dev verification owns that)
```

---

## 7. Dev Verification

**File:** `dev-verification.agent.md`

**Role:** Evaluates whether implementation qualifies as Code Done using critical checks, test policy compliance, and a verification score.

**Inputs:** Task analysis, coder results, test policy

**Outputs:**

```text
.maestro/work/tasks/<task-id>/dev-verification.yaml
Decision: DEV_DONE | DEV_BLOCKED | NEEDS_FIX | NEEDS_USER_DECISION
```

**Required skills:** skill-dev-verification

**Key behaviors:**

```text
Code Done requires: score ≥80% + all critical checks pass + zero blockers
Critical check failure overrides passing score
Do not create tests when component policy forbids them
Do not lower requirements to reach the threshold
```

---

## 8. QC Handoff

**File:** `qc-handoff.agent.md`

**Role:** Creates the mandatory Dev-to-QC handoff document after Code Done. Does not run QC tests.

**Inputs:** Task analysis, coder results, dev verification

**Outputs:**

```text
.maestro/work/tasks/<task-id>/qc-handoff.md
```

**Required skills:** skill-qc-handoff

**Key behaviors:**

```text
Cannot create handoff if dev verification is not DEV_DONE
Include: summary, scope, changed services, acceptance criteria,
  dev evidence, critical checks evidence, suggested QC test cases,
  known risks, retest scope
```

---

## 9. QC Runner

**File:** `qc-runner.agent.md`

**Role:** Executes QC test cases from the handoff document. Records results and stops immediately on blocker bugs.

**Inputs:** QC handoff document

**Outputs:**

```text
.maestro/work/tasks/<task-id>/qc-test-results.yaml
.maestro/work/tasks/<task-id>/qc-delivery-report.md
.maestro/work/bugs/blockers/<bug-id>.yaml (on blocker)
.maestro/work/bugs/non-blockers/<bug-id>.yaml (on non-blocker)
```

**Required skills:** skill-qc-runner, skill-bug-routing

**Key behaviors:**

```text
Build test cases from handoff → execute → record results
Stop immediately on blocker bugs
Continue on non-blocker bugs for unaffected test cases
QC_DONE requires zero open blockers
After QC_DONE, write qc-delivery-report.md summarizing results for user
Never fix code directly
Never write secrets to artifacts
```

---

## 10. Bug Router

**File:** `bug-router.agent.md`

**Role:** Classifies QC defects as blocker or non-blocker and routes fixes through Coder Leader.

**Inputs:** QC test results, defect details

**Outputs:**

```text
.maestro/work/bugs/blockers/<bug-id>.yaml
.maestro/work/bugs/non-blockers/<bug-id>.yaml
.maestro/work/tasks/<task-id>/bugs.yaml
```

**Required skills:** skill-bug-routing

**Key behaviors:**

```text
Blocker: main flow broken, crash, auth/security broken, data corruption
Non-blocker: cosmetic, copy, layout, warning, rare edge case
Every bug includes: reproduction steps, expected/actual result, impacted services
Blocker fixes go through: Coder Leader → Dev Verification → QC retest
Never downgrade blocker severity to keep QC moving
```

---

## 11. Memory Update

**File:** `memory-update.agent.md`

**Role:** Persists durable project, service, and task learnings after meaningful workflow events.

**Inputs:** Task artifacts, workflow events, existing project brain

**Outputs:**

```text
.maestro/work/tasks/<task-id>/memory-updates.yaml
.maestro/knowledge/project.yaml (updated)
.maestro/knowledge/components/<component-id>.yaml (updated)
.maestro/registry/agents.yaml (when scopes change)
```

**Required skills:** skill-memory-update, skill-project-brain

**Key behaviors:**

```text
Update when: service boundaries change, API/event/schema changes,
  new reusable patterns, test policy changes, bug root cause is reusable
Cite source artifacts for every update
Include confidence levels for inferred facts
Never store secrets, noisy logs, or speculation
```

---

## 12. Workflow Policy

**File:** `workflow-policy.agent.md`

**Role:** Validates workflow state transitions, approval gates, and policy compliance.

**Inputs:** Workflow state, agent registry, task artifacts

**Outputs:** Decision (allow | deny | needs_user_approval), reason, missing artifacts

**Required skills:** skill-workflow-policy

**Key behaviors:**

```text
Validate: state allows transition, artifacts exist, agent is allowed,
  user approval exists for gated actions, coder scopes respected
Cannot change source code
Cannot approve missing evidence
Cannot bypass user approval gates
```

---

## Generated service coders

Generated by Agent Factory after onboarding and user approval. These are the **only agents that write application code**.

### Contract structure

Every generated coder agent file includes:

```yaml
agent_id: coder-<service-slug>
service: <service-name>
allowed_read_paths: [...]
allowed_write_paths: [...]
forbidden_paths: [...]
test_policy:
  unit_tests_required: true|false
  test_framework: <framework>
escalation_rules:
  cross_service_change: stop_and_ask_leader
  shared_package_change: stop_and_ask_leader
  auth_security_change: stop_and_ask_leader
```

### Naming convention

```text
coder-<service-slug>.agent.md
```

### Constraints (R-006)

```text
Write only inside allowed_write_paths
Read only allowed context and assigned service context
Stop when a task requires another service change
Raise cross_service_requests to Coder Leader
Follow service test_policy
Check reusable assets and conventions before implementation
```

### Coder results format

Every coder reports in `coder-results.yaml`:

```text
status: done | blocked | needs_leader
files_changed: [...]
reusable_assets_used: [...]
conventions_followed: [...]
anti_patterns_avoided: [...]
cross_service_requests: [...]
```

## Related documents

- [architecture-guide.md](architecture-guide.md) — System architecture
- [workflow-reference.md](workflow-reference.md) — Workflow states and commands
- [skill-guide.md](skill-guide.md) — Skill system and composition
- [skill-composition.md](skill-composition.md) — Skill composition standard
