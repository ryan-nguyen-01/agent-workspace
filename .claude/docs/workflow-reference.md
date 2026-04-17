# Workflow Reference

![State machine](diagrams/05-state-machine.svg)

This document is the reference for workflow states, transitions, commands, approval gates, and artifact requirements.

## Task states

| State         | Owner            | Description                                   |
| ------------- | ---------------- | --------------------------------------------- |
| TASK_RECEIVED | Coordinator      | Task input received, not yet analyzed         |
| ANALYZING     | Task Analysis    | Normalizing task into structured spec         |
| PLANNING      | Coder Leader     | Creating implementation plan and assignments  |
| IMPLEMENTING  | Service Coders   | Writing code within scoped boundaries         |
| DEV_VERIFYING | Dev Verification | Evaluating Code Done criteria                 |
| CODE_DONE     | Coordinator      | Dev verification passed, ready for QC handoff |
| NEEDS_FIX     | Coder Leader     | Dev verification failed, returning to dev     |
| QC_HANDOFF    | QC Handoff       | Creating handoff document for QC              |
| QC_RUNNING    | QC Runner        | Executing QC test cases                       |
| QC_DONE       | QC Runner        | All test cases recorded, zero open blockers   |
| QC_BLOCKED    | Bug Router       | Blocker bug found, QC stopped                 |
| BUG_ROUTING   | Bug Router       | Classifying and routing bug to Coder Leader   |
| MEMORY_UPDATE | Memory Update    | Persisting durable learnings                  |
| DONE          | Coordinator      | Task complete                                 |

## State transitions

```text
TASK_RECEIVED ──→ ANALYZING
  Requires: task-input.md

ANALYZING ──→ PLANNING
  Requires: task-analysis.yaml with user approval (R-011-10)

PLANNING ──→ IMPLEMENTING
  Requires: implementation-plan.yaml, service-assignments.yaml

IMPLEMENTING ──→ DEV_VERIFYING
  Requires: coder-results.yaml

DEV_VERIFYING ──→ CODE_DONE
  Requires: dev-verification.yaml (score ≥80%, critical checks pass)

DEV_VERIFYING ──→ NEEDS_FIX
  Requires: dev-verification.yaml (score <80% or critical check failed)

NEEDS_FIX ──→ IMPLEMENTING
  Requires: updated service-assignments.yaml

CODE_DONE ──→ QC_HANDOFF
  Requires: dev-verification.yaml with DEV_DONE

QC_HANDOFF ──→ QC_RUNNING
  Requires: qc-handoff.md

QC_RUNNING ──→ QC_DONE
  Requires: qc-test-results.yaml (zero open blockers)

QC_RUNNING ──→ QC_BLOCKED
  Requires: blocker bug detected

QC_BLOCKED ──→ BUG_ROUTING ──→ IMPLEMENTING
  Requires: bugs.yaml, blocker bug file

QC_DONE ──→ DELIVERY_REPORT ──→ MEMORY_UPDATE ──→ DONE
  Requires: qc-delivery-report.md, memory-updates.yaml (when durable facts changed)
```

## Commands

### Core workflow commands

| Command          | Agent triggered  | Description                            |
| ---------------- | ---------------- | -------------------------------------- |
| `/coord`         | Coordinator      | Main entry point, auto-routes workflow |
| `/onboard`       | Onboarding       | Scan project, build project brain      |
| `/create-coders` | Agent Factory    | Create service coder agents            |
| `/analyze-task`  | Task Analysis    | Normalize task into structured spec    |
| `/plan-dev`      | Coder Leader     | Create implementation plan             |
| `/dev`           | Coder Leader     | Execute implementation                 |
| `/verify-dev`    | Dev Verification | Check Code Done criteria               |

### QC commands

| Command       | Agent triggered | Description                       |
| ------------- | --------------- | --------------------------------- |
| `/handoff-qc` | QC Handoff      | Create Dev-to-QC handoff document |
| `/qc`         | QC Runner       | Run QC test cases                 |
| `/bug`        | Bug Router      | Classify and route a bug          |

### Utility commands

| Command         | Agent triggered | Description                             |
| --------------- | --------------- | --------------------------------------- |
| `/sync-memory`  | Memory Update   | Update project brain and service brains |
| `/policy-check` | Workflow Policy | Validate transition or gate             |
| `/status`       | Coordinator     | Show workflow state, brain, agents      |
| `/resume-task`  | Coordinator     | Resume interrupted task from last state |

## Approval gates (R-011)

User approval is required before:

| Action                                           | Rule     |
| ------------------------------------------------ | -------- |
| Creating generated service coder agents          | R-011-01 |
| Expanding a coder's allowed_write_paths          | R-011-02 |
| Skipping onboarding when brain is missing/stale  | R-011-03 |
| Skipping QC                                      | R-011-04 |
| Skipping or downgrading a blocker bug            | R-011-05 |
| Creating tests when service policy says no tests | R-011-06 |
| Destructive environment/database/deploy actions  | R-011-07 |
| Changing workflow policy or state machine rules  | R-011-08 |
| Touching files outside a coder's approved scope  | R-011-09 |
| Proceeding from Task Analysis to Coder Leader    | R-011-10 |

## Required artifacts per state

```text
Before coding:
  .claude/tasks/<task-id>/task-input.md
  .claude/tasks/<task-id>/task-analysis.yaml (with user approval)

Before assigning coders:
  .claude/tasks/<task-id>/implementation-plan.yaml
  .claude/tasks/<task-id>/service-assignments.yaml

Before Code Done:
  .claude/tasks/<task-id>/coder-results.yaml
  .claude/tasks/<task-id>/dev-verification.yaml

Before QC:
  .claude/tasks/<task-id>/qc-handoff.md

Before QC_DONE:
  .claude/tasks/<task-id>/qc-test-results.yaml (zero open blockers)

Before user delivery:
  .claude/tasks/<task-id>/qc-delivery-report.md

Before DONE:
  .claude/tasks/<task-id>/memory-updates.yaml (when durable facts changed)
```

## Code Done criteria (R-007)

Code Done requires all of:

```text
1. Dev verification score ≥80%
2. All critical checks pass
3. Zero known blockers
4. Scope compliance (coders stayed within allowed paths)
5. Test policy compliance:
   - If tests required → test evidence recorded
   - If tests not required → manual verification evidence recorded
```

Critical check failure overrides a score ≥80%.

## QC Done criteria (R-008)

```text
1. qc-handoff.md exists
2. All test cases from handoff are recorded in qc-test-results.yaml
3. Zero open blocker bugs
4. Non-blocker bugs documented (do not block QC_DONE)
```

## Bug severity classification (R-009)

### Blocker

```text
Main flow blocked or broken
Application crash
Auth or security broken
Data corruption risk
Downstream QC test cases blocked
```

### Non-blocker

```text
Does not block main flow
Cosmetic, copy, or layout issue
Warning without functional impact
Rare edge case behavior
```

Blocker bugs stop QC immediately. Do not downgrade severity to keep QC moving.

## Workflow rules summary

| Rule  | Scope              | Key constraint                                               |
| ----- | ------------------ | ------------------------------------------------------------ |
| R-000 | Core               | Read workflow before acting, no coding without task-analysis |
| R-001 | Project Brain      | First memory source, prefer partial rescan                   |
| R-002 | Onboarding         | Scan only, no code changes                                   |
| R-003 | Agent Factory      | User approval required to create coders                      |
| R-004 | Task Analysis      | Normalize before coding, explicit acceptance criteria        |
| R-005 | Coder Leader       | Multi-service coordination, protect contracts                |
| R-006 | Service Coders     | Scoped writes only, escalate cross-service                   |
| R-007 | Dev Verification   | ≥80% score + critical checks for Code Done                   |
| R-008 | QC                 | Stop on blockers, zero blockers for QC_DONE                  |
| R-009 | Bug Routing        | Classify blocker vs non-blocker, no downgrading              |
| R-010 | Memory             | Update after DONE or meaningful changes                      |
| R-011 | Approval Gates     | User consent for destructive/scope-changing actions          |
| R-012 | Artifact Contracts | Required artifacts per state transition                      |
| R-013 | Security           | No secrets in artifacts, critical checks for auth            |
| R-014 | Skill Composition  | Skills are capabilities, not agent identities                |

## Related documents

- [architecture-guide.md](architecture-guide.md) — System architecture
- [agent-catalog.md](agent-catalog.md) — Detailed agent descriptions
- [visual-flow.md](visual-flow.md) — All 8 SVG workflow diagrams
- [folder-guide.md](folder-guide.md) — Folder structure reference
