# `.agent` Workflow Source

This folder is the tool-neutral source layer for `agent-workspace`. It contains the workflow spec, rules, templates, and documentation shared by Claude, Codex, Cursor, Gemini, Copilot, and other coding agents.

Runtime memory and task artifacts do not live here. They live under `.runtime/`.

Claude-specific executable adapters live under `.claude/`.

## Architecture

```text
User
  -> Coordinator Agent
  -> Project Brain Check
  -> Onboarding Agent when brain is missing or stale
  -> Agent Factory after user approval
  -> Task Analysis Agent for HLD, LLD, ticket text, or free-form task
  -> Coder Leader Agent
  -> Built-in Cross-cutting Coders and/or Generated Service Coder Agents
  -> Dev Verification Gate
  -> QC Handoff Agent
  -> QC Runner Agent
  -> Bug Router when defects appear
  -> Memory Update Agent
```

## Folder layout

```text
.agent/
  workflow.md
  rules/
    00-core-rules.md
    ...
  templates/
    agent-coder.template.md
    ...
  docs/
    folder-guide.md
    visual-flow.md
    ...

.runtime/context/
  index.yaml
  project-brain.yaml
  service-catalog.yaml
  agent-registry.yaml
  test-policy.yaml
  skill-registry.yaml
  workflow-state.yaml
  services/
    <service>.yaml
  feedback/
.runtime/tasks/
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
1. Clone application repositories under `services/` and put reference docs under `inputs/`.
2. Ask coordinator to onboard the workspace.
3. Onboarding scans `inputs/` and `services/`, then writes the project brain.
4. Coordinator asks whether to create service coder agents.
5. Agent Factory creates coder agents using templates/agent-coder.template.md.
6. New development tasks can now enter the full workflow.
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

Do not make agents rediscover the whole repository every session. Store durable facts, service coding contracts, and workflow state in `.runtime/context`, and per-task facts in `.runtime/tasks/<task-id>`.

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
.agent/rules/      Mandatory policies that agents must follow
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
-> /skills for explicit skill maintenance
```

## Folder guide

For a detailed explanation of what this folder is for, when to use it, and what each subfolder contains, read [docs/folder-guide.md](docs/folder-guide.md).

## Deep onboarding

Onboarding also extracts reusable project assets, coding conventions, business flows, and anti-patterns so generated coder agents can follow the existing project style. See [docs/deep-onboarding.md](docs/deep-onboarding.md).

## Skill composition

Agents are not limited to one skill. Skills are composable capabilities. See [docs/skill-composition.md](docs/skill-composition.md).

## Skill registry and external skills

Agent Factory uses [.runtime/context/skill-registry.yaml](.runtime/context/skill-registry.yaml) as the machine-readable source of truth for skill selection, risk gates, unavailable skills, and approval requirements.

[docs/external-skills.md](docs/external-skills.md) is the human-readable install log and reference notes for skills from skills.sh.
