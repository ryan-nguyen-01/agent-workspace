# Workflow Reference

![State machine](diagrams/05-state-machine.svg)

This document is the reference for workflow states, transitions, commands, approval gates, and artifact requirements.

## Workflow states

These are the canonical state names from `.runtime/context/workflow-state.yaml`.

| State | Owner | Description |
| --- | --- | --- |
| NEW | Coordinator | Fresh workspace state before classification |
| NEED_ONBOARDING | Coordinator / Onboarding | Services and inputs still need scanning |
| ONBOARDED | Onboarding | Project brain and service catalog exist |
| NEED_AGENT_CREATION_APPROVAL | Coordinator | Generated service coder creation needs user approval |
| AGENTS_READY | Agent Factory | Approved generated coders are available |
| READY_FOR_ANALYSIS | Coordinator | Task intake may start |
| ANALYZED | Task Analysis | `task-analysis.yaml` exists |
| ARCHITECTURE_REVIEWING | Solution Architect | Architecture review is required and in progress |
| PLANNED | Coder Leader | Implementation plan and assignments are ready |
| IN_DEV | Coder Leader / Coders | Scoped implementation is running |
| DEV_VERIFYING | Dev Verification | Code Done gate is running |
| DEV_BLOCKED | Coder Leader | Development output failed or is blocked |
| DEV_DONE | Dev Verification | Code Done criteria passed |
| QC_READY | QC Handoff | Handoff exists and QC may start |
| QC_TESTING | QC Runner | QC is executing |
| BLOCKED_BY_BUG | Bug Router | QC found a blocker |
| FIXING | Coder Leader | Blocker fix is in progress |
| QC_RETESTING | QC Runner | Fix retest is running |
| QC_DONE | QC Runner | QC passed with zero open blockers |
| MEMORY_SYNCING | Memory Update | Durable learnings are being persisted |
| DONE | Coordinator | Workflow is complete |

## State transitions

```text
NEW ──→ NEED_ONBOARDING | READY_FOR_ANALYSIS

NEED_ONBOARDING ──→ ONBOARDED
  Requires: project-brain.yaml, service-catalog.yaml, test-policy.yaml

ONBOARDED ──→ NEED_AGENT_CREATION_APPROVAL ──→ AGENTS_READY
  Requires: user approval before generated coder creation

AGENTS_READY ──→ READY_FOR_ANALYSIS

READY_FOR_ANALYSIS ──→ ANALYZED
  Requires: task-input.md, task-analysis.yaml
  For applied-service tasks: task-analysis.yaml.context_plan with medium/high confidence

ANALYZED ──→ ARCHITECTURE_REVIEWING
  Requires: task-analysis.yaml with architecture_review.required: true

ARCHITECTURE_REVIEWING ──→ PLANNED
  Requires: architecture-review.yaml with decision approved

ANALYZED ──→ PLANNED
  Requires: task-analysis.yaml with user approval (R-011-10 unless fast-track applies), context_plan present and actionable for applied-service tasks

PLANNED ──→ IN_DEV
  Requires: implementation-plan.yaml, service-assignments.yaml
  Applied-service fast-track may skip implementation-plan.yaml but still requires lightweight service-assignments.yaml

IN_DEV ──→ DEV_VERIFYING
  Requires: coder-results.yaml

DEV_VERIFYING ──→ DEV_DONE
  Requires: dev-verification.yaml (score ≥80%, critical checks pass)

DEV_VERIFYING ──→ DEV_BLOCKED | IN_DEV
  Requires: dev-verification.yaml (score <80% or critical check failed)

DEV_BLOCKED ──→ IN_DEV
  Requires: updated service-assignments.yaml

DEV_DONE ──→ QC_READY
  Requires: dev-verification.yaml with DEV_DONE

QC_READY ──→ QC_TESTING
  Requires: qc-handoff.md

QC_TESTING ──→ QC_DONE
  Requires: qc-test-results.yaml (zero open blockers)

QC_TESTING ──→ BLOCKED_BY_BUG
  Requires: blocker bug detected

BLOCKED_BY_BUG ──→ FIXING ──→ DEV_VERIFYING
  Requires: bugs.yaml, blocker bug file

DEV_DONE ──→ QC_RETESTING ──→ QC_DONE
  Requires: retest after blocker fix

QC_DONE ──→ MEMORY_SYNCING ──→ DONE
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
| `/skills`       | Coordinator     | Maintain installed skills and registry metadata |
| `/policy-check` | Workflow Policy | Validate transition, gate, or artifact snapshot |
| `/status`       | Coordinator     | Show workflow state, brain, agents, model routing, response UI, and activity dashboard |
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
| Fast-track exemption from Task Analysis approval  | R-011-10b |
| Disabling fast-track through test policy          | R-011-11 |
| Updating installed skill content/lock/risk metadata | R-011-12 |
| Switching distribution_mode (onboarding or manual edit) | R-011-13 |

## Required artifacts per state

```text
Before coding:
  .runtime/tasks/<task-id>/task-input.md
  .runtime/tasks/<task-id>/task-analysis.yaml (with user approval)
  .runtime/tasks/<task-id>/task-analysis.yaml.context_plan (all applied-service tasks)

Before planning architecture-sensitive tasks:
  .runtime/tasks/<task-id>/architecture-review.yaml (when required)

Before assigning coders:
  .runtime/tasks/<task-id>/implementation-plan.yaml
  .runtime/tasks/<task-id>/service-assignments.yaml
  Applied-service fast-track may omit implementation-plan.yaml but not service-assignments.yaml.

Before Code Done:
  .runtime/tasks/<task-id>/coder-results.yaml
  .runtime/tasks/<task-id>/dev-verification.yaml

Before QC:
  .runtime/tasks/<task-id>/qc-handoff.md

Before QC_DONE:
  .runtime/tasks/<task-id>/qc-test-results.yaml (zero open blockers)

Before user delivery:
  .runtime/tasks/<task-id>/qc-delivery-report.md

Before DONE:
  .runtime/tasks/<task-id>/memory-updates.yaml (when durable facts changed)
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
| R-015 | Model/Observability/UI | Model profiles, activity dashboard, response UI, token/cost reporting |

## Related documents

- [architecture-guide.md](architecture-guide.md) — System architecture
- [agent-catalog.md](agent-catalog.md) — Detailed agent descriptions
- [visual-flow.md](visual-flow.md) — All 8 SVG workflow diagrams
- [folder-guide.md](folder-guide.md) — Folder structure reference
