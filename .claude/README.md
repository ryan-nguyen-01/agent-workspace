# `.claude` Dynamic Agent Architecture

This folder defines a project-aware agent workflow for development teams. Coder agents are not prebuilt. They are generated from project onboarding so each coder has the correct service scope, permissions, test policy, and handoff obligations.

## Architecture

```text
User
  -> Coordinator Agent
  -> Project Brain Check
  -> Onboarding Agent when brain is missing or stale
  -> Agent Factory after user approval
  -> Task Analysis Agent for HLD, LLD, ticket text, or free-form task
  -> Coder Leader Agent
  -> Generated Service Coder Agents
  -> Dev Verification Gate
  -> QC Handoff Agent
  -> QC Runner Agent
  -> Bug Router when defects appear
  -> Memory Update Agent
```

## Folder layout

```text
.claude/
  CLAUDE.md
  README.md
  workflow.md
  agents/
    coordinator.agent.md
    onboarding.agent.md
    agent-factory.agent.md
    task-analysis.agent.md
    coder-leader.agent.md
    dev-verification.agent.md
    qc-handoff.agent.md
    qc-runner.agent.md
    bug-router.agent.md
    memory-update.agent.md
    workflow-policy.agent.md
  skills/
    skill-project-brain/SKILL.md
    skill-project-onboarding/SKILL.md
    skill-agent-factory/SKILL.md
    skill-task-analysis/SKILL.md
    skill-coder-leader/SKILL.md
    skill-service-coder/SKILL.md
    skill-dev-verification/SKILL.md
    skill-qc-handoff/SKILL.md
    skill-qc-runner/SKILL.md
    skill-bug-routing/SKILL.md
    skill-memory-update/SKILL.md
    skill-workflow-policy/SKILL.md
  templates/
    agent-coder.template.md
    agent-registry.template.yaml
    bug.template.yaml
    dev-verification.template.yaml
    environment.template.yaml
    handover.template.md
    memory-update.template.yaml
    project-brain.template.yaml
    qc-test-result.template.yaml
    service-brain.template.yaml
    task-analysis.template.yaml
    task.template.yaml
    workflow-state.template.yaml
  context/
    project-brain.yaml
    service-catalog.yaml
    agent-registry.yaml
    test-policy.yaml
    workflow-state.yaml
    services/
      <service>.yaml
  tasks/
    <task-id>/
      task-input.md
      task-analysis.yaml
      implementation-plan.yaml
      service-assignments.yaml
      dev-verification.yaml
      qc-handoff.md
      qc-test-results.yaml
      bugs.yaml
```

## First run

```text
1. Ask coordinator to onboard the project.
2. Onboarding scans the repository and writes the project brain.
3. Coordinator asks whether to create service coder agents.
4. Agent Factory creates coder agents using templates/agent-coder.template.md.
5. New development tasks can now enter the full workflow.
```

## Task run

```text
1. Coordinator receives HLD, LLD, ticket text, or direct text.
2. Task Analysis normalizes it into task-analysis.yaml.
3. Coder Leader creates a multi-service implementation plan.
4. Service coders implement only inside their allowed write scopes.
5. Dev Verification checks Code Done.
6. QC Handoff creates a handoff document.
7. QC Runner executes test cases and classifies bugs.
8. Bug Router sends blockers back to dev and non-blockers into parallel fix tasks.
9. Memory Update persists reusable knowledge.
```

## Code Done rule

A task can move to QC only when:

```text
Dev verification score is at least 80%
All critical checks pass
No known blocker remains
Scope policy is respected
Required tests are created only when service policy requires them
Manual verification is documented when tests are not required
QC handoff document exists
```

## QC rule

```text
Blocking bug: stop QC immediately, create blocker bug, return to Coder Leader.
Non-blocking bug: create bug task, continue QC, let dev fix in parallel.
```

## Memory rule

Do not make agents rediscover the whole repository every session. Store durable facts in `.claude/context` and per-task facts in `.claude/tasks/<task-id>`.

## Visual flow

See [docs/visual-flow.md](docs/visual-flow.md) for the full Mermaid diagrams:

```text
End-to-end flow
Onboarding and coder generation
Development and QC loop
State machine
```

## Rules and commands

The workflow has two extra control layers:

```text
.claude/rules/      Mandatory policies that agents must follow
.claude/commands/   User-facing entrypoints for running the workflow
```

Recommended command path:

```text
/coord
-> /onboard when brain is missing or stale
-> /create-coders after user approval
-> /analyze-task for HLD, LLD, ticket, or text
-> /plan-dev
-> /dev
-> /verify-dev
-> /handoff-qc
-> /qc
-> /bug if defects appear
-> /sync-memory when done
```

## Folder guide

For a detailed explanation of what this folder is for, when to use it, and what each subfolder contains, read [docs/folder-guide.md](docs/folder-guide.md).

## Deep onboarding

Onboarding also extracts reusable project assets, coding conventions, business flows, and anti-patterns so generated coder agents can follow the existing project style. See [docs/deep-onboarding.md](docs/deep-onboarding.md).

## Skill composition

Agents are not limited to one skill. Skills are composable capabilities. See [docs/skill-composition.md](docs/skill-composition.md).

## Skill registry and external skills

Agent Factory uses [context/skill-registry.yaml](context/skill-registry.yaml) as the machine-readable source of truth for skill selection, risk gates, unavailable skills, and approval requirements.

[docs/external-skills.md](docs/external-skills.md) is the human-readable install log and reference notes for skills from skills.sh.
