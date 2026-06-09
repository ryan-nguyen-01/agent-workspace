# Maestro Folder Guide

> Folder layout is a text tree — see the workspace layout in `folder-guide.md` / `CLAUDE.md` (clearer than a diagram for directories).

This document explains `.maestro`, `.claude`, `docs`, `inputs`, and the product component roots.

## 1. What is Maestro?

`maestro` is a **product-development workspace**. It may contain a greenfield product directly
or coordinate existing repositories mounted under registered component roots.

This workspace separates four concerns:

```text
.maestro/          Product control plane, knowledge, work, memory, history, and local state
.claude/      Claude-native agents, commands, skills, hooks, and settings
docs/         Official product and engineering documentation
apps|services|packages|infra|tests/  Product implementation
```

Main goals:

```text
Avoid having to rescan the project from scratch on every new conversation
Do not create a generic coder agent before understanding the project
Match direct, assisted, or governed execution to task size and risk
Scope coder agents per service/module to avoid edits outside the intended scope
Standardize the dev -> QC handoff document
```

## 2. When to use maestro?

Use this workspace when you want to work through the end-to-end agent workflow.

Examples:

```text
Onboard a new project
Analyze the project structure
Create a Project Brain
Create coder agents per service/module
Receive a task from an HLD, LLD, ticket, or text
Split a task across multiple service coders
Check Code Done
Create a QC handoff
QC testing and classifying bugs as blocker/non-blocker
Resume a task in a new conversation
Update memory after finishing a task
```

Commonly used commands:

```text
/coord <request>       Main entry, auto-routes the workflow
/onboard               Scan the project and create the Project Brain
/create-coders         Create service coder agents after user approval
/analyze-task <input>  Analyze HLD/LLD/ticket/text
/plan-dev TASK-123     Create an implementation plan
/dev TASK-123          Run the dev flow
/verify-dev TASK-123   Check Code Done
/handoff-qc TASK-123   Create the QC handoff document
/qc TASK-123           Run the QC flow
/bug TASK-123          Route a blocker/non-blocker bug
/sync-memory TASK-123  Update the Project Brain
/resume-task TASK-123  Continue a task from the current state
/status                View workflow/brain/agents/model/activity status
/policy-check          Check gate/exception
```

## 3. When should you not use the full workflow?

You do not need the full workflow for things that are too small or outside the workflow.

Examples:

```text
Fix a small typo without the agent workflow
Ask for an explanation of a single code snippet
Write a temporary snippet
Local experiments that do not need memory saved
A task you do not yet want to send through QC/handoff
```

However, if the task can affect the real project, multiple services, auth, DB, API contract, QC, or needs to be resumed later, you should use the workflow in `maestro`.

## 4. Operating principles

`maestro` is designed around the model:

```text
Product request -> Control plane -> Tool adapter -> Product code and evidence
```

Meaning of each layer:

```text
.maestro/engine/workflow.md     Overall state machine and SOP
.maestro/engine/rules/          Mandatory rules, must not be skipped
.maestro/engine/templates/      Standard artifact file templates
.maestro/engine/docs/           Documentation and diagrams
.claude/commands/      Entry points the user calls in Claude Code
.claude/agents/        Role and responsibility of each Claude agent
.claude/skills/        Concrete how-to guidance for agents
.maestro/registry/       Component, agent, skill, input, and artifact addresses
.maestro/knowledge/      Durable project and component knowledge
.maestro/work/tasks/        Artifacts per task
.maestro/work/bugs/         Blocker/non-blocker bugs
.maestro/runtime/          Local-only active state and generated reports
docs/                 Official product and engineering documentation
```

Rule priority:

```text
.maestro/engine/workflow.md defines the state machine
.maestro/engine/rules/ defines mandatory policy
.claude/commands/ defines how the user invokes the workflow in Claude Code
.claude/agents/ defines role behavior
.claude/skills/ defines the detailed how-to
```

On conflict, prioritize:

```text
.maestro/engine/workflow.md + .maestro/engine/rules/
.claude/commands/
.claude/agents/
.claude/skills/
.maestro/engine/templates/
```

## 5. Folder structure overview

```text
.maestro/{engine,config,registry,knowledge,work,design,decision,memory,history,runtime}/
.claude/{agents,commands,skills}/
docs/{product,requirements,experience,architecture,quality,delivery,operations,governance}/
apps/
services/
packages/
infra/
tests/
```

## 6. Root-level files

### `CLAUDE.md`

The main guidance file for Claude/agents when entering the project.

Use it to learn:

```text
Default workflow
Bootstrap sequence
Basic aliases/commands
Approval gates
Rule priority
Visual flow reference
```

When to read:

```text
When an agent starts working in the project
When you need to understand how `maestro` orchestrates overall
When you need to know which entrypoint to use
```

### `README.md`

Documentation for users/dev leads.

Use it to learn:

```text
Overall architecture of `maestro`
How to run it for the first time
The standard task flow
Code Done rule
QC rule
Existing rules and commands
```

When to read:

```text
When onboarding a newcomer to the workflow
When you need to introduce the main folders of the workspace
When you need to view the standard command path
```

### `workflow.md`

The source of truth for the end-to-end state machine and SOP.

Use it to learn:

```text
The valid states
Which agent is responsible for which state
Onboarding flow
Coder-agent creation flow
Task intake flow
Dev flow
QC flow
Bug flow
Memory update flow
```

When to read:

```text
Every agent must read it before acting
When you need to validate a state transition
When you need to know which step a task is at
```

### `.maestro/runtime/workflow-state.yaml`

Tracks the current workflow state. This is the main state file of the workspace.

Use it to learn:

```text
Current state
Active task
Next required action
```

When to read:

```text
When you want to know where the system is
When resuming a task or resuming the workflow
```

### `changelog.md`

Records significant changes to the `maestro` workflow.

Use it to learn:

```text
What the architecture has changed
When rules/commands/agents were updated
How the workflow policy changed
```

When to read:

```text
When auditing workflow changes
When you need to understand why the current structure exists
```

## 7. `agents/`

This folder contains the core agent definitions and will later hold generated service coder agents.

```text
.claude/agents/
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
  coder-<service>.agent.md       generated later
```

### When to use?

Use it when you need to know which agent does what.

Examples:

```text
Coordinator routes tasks but does not code
Onboarding scans the project but does not create coders
Agent Factory creates coders after approval
Task Analysis normalizes HLD/LLD/text
Coder Leader splits work across multiple service coders
Service Coder only edits within its scope
Dev Verification decides Code Done
QC Runner tests and classifies bugs
Bug Router routes blocker/non-blocker
Memory Update updates Project Knowledge
Workflow Policy validates gate/transition
```

### Core agents

| Agent              | Role                                                          |
| ------------------ | ------------------------------------------------------------- |
| `coordinator`      | Orchestrate the workflow, check project knowledge, route commands, ask for approval |
| `onboarding`       | Scan project, create Project Knowledge, Component Registry, Test Policy |
| `agent-factory`    | Generate coder agents per component after approval            |
| `task-analysis`    | Analyze HLD/LLD/ticket/text into a task spec                  |
| `coder-leader`     | Lead multi-service implementation                             |
| `dev-verification` | Check Code Done, score >= 80%, critical pass                  |
| `qc-handoff`       | Create the dev -> QC handoff document                         |
| `qc-runner`        | Run QC, produce test results, detect bugs                     |
| `bug-router`       | Classify blocker/non-blocker, route back to dev              |
| `memory-update`    | Update durable memory                                         |
| `workflow-policy`  | Validate state transitions and approval gates                |

### Generated coder agents

Generated coder agents do not exist from the start.

They are only created after:

```text
/onboard
-> detect services/modules
-> user approve
-> /create-coders
```

Examples that may exist later:

```text
coder-auth-service.agent.md
coder-payment-service.agent.md
coder-admin-web.agent.md
coder-notification-worker.agent.md
```

Each coder agent must have:

```text
allowed_read_paths
allowed_write_paths
forbidden_paths
test_policy
critical_checks
handoff obligations
escalation rules
```

## 8. `commands/`

This folder contains the user-facing commands.

```text
.claude/commands/
  coord.md
  onboard.md
  create-coders.md
  status.md
  analyze-task.md
  plan-dev.md
  dev.md
  verify-dev.md
  handoff-qc.md
  qc.md
  bug.md
  sync-memory.md
  skills.md
  resume-task.md
  policy-check.md
```

### When to use?

Use it when you want to invoke the workflow via a clear entrypoint.

Examples:

```text
/coord add a reset password feature
/onboard
/create-coders
/qc TASK-123
/skills status
/status
```

### Why do we need commands?

Commands help:

```text
The user does not need to remember which agent to call
The agent knows which rules it must read
The workflow does not skip steps
Which artifacts to create are clearly defined
Clear stop conditions
Consistent output format
```

### Standard command path

```text
/coord
-> /onboard
-> /create-coders
-> /analyze-task
-> /plan-dev
-> /dev
-> /verify-dev
-> /handoff-qc
-> /qc
-> /bug if there is a defect
-> /sync-memory
```

## 9. `rules/`

This folder contains the mandatory policy.

```text
.maestro/engine/rules/
  00-core-rules.md
  01-project-brain-rules.md
  02-onboarding-rules.md
  03-agent-factory-rules.md
  04-task-analysis-rules.md
  05-coder-leader-rules.md
  06-service-coder-rules.md
  07-dev-verification-rules.md
  08-qc-rules.md
  09-bug-routing-rules.md
  10-memory-rules.md
  11-approval-gates.md
  12-artifact-contracts.md
  13-security-secret-rules.md
  14-skill-composition-rules.md
  15-model-routing-observability-rules.md
```

### When to use?

Use it when you need to check whether an agent is allowed to do something.

Examples:

```text
Is it allowed to create coder agents yet?
Is it allowed to code yet?
Is it allowed to create unit tests?
Is it allowed to move to QC?
Is QC allowed to continue when it hits a bug?
Is it allowed to save this information to memory?
Is user approval required?
```

### Some important rules

```text
Direct work may proceed without persistent workflow artifacts when scope and verification ownership are explicit
Assisted work requires task.yaml, progress.yaml, and verification.yaml
Governed work requires current Project Brain context and task-analysis.yaml before product code
No creating generated coders without onboarding and user approval
No QC without qc-handoff.md
Service coder only edits within allowed_write_paths
Unit tests are only created when the component policy requires them
If confidence is low or facts are missing: ask the user, do not guess, do not fabricate evidence
Code Done requires >= 80% and critical checks passing 100%
When QC hits a blocker, stop immediately
Do not store secrets/tokens/passwords/long logs in `.maestro/runtime` artifacts or tool adapter files
```

## 10. `skills/`

This folder contains concrete how-to guidance for agents.

```text
.claude/skills/
  skill-project-brain/
  skill-project-onboarding/
  skill-agent-factory/
  skill-task-analysis/
  skill-coder-leader/
  skill-service-coder/
  skill-dev-verification/
  skill-qc-handoff/
  skill-qc-runner/
  skill-bug-routing/
  skill-memory-update/
  skill-workflow-policy/
```

### When to use?

Use it when an agent needs to know **how to perform** a capability.

Examples:

```text
The Onboarding agent uses skill-project-onboarding
Agent Factory uses skill-agent-factory
Task Analysis uses skill-task-analysis
Coder Leader uses skill-coder-leader
QC Runner uses skill-qc-runner
Memory Update uses skill-memory-update
```

### How does it differ from `agents/`?

```text
agents/ = who is responsible
skills/ = by what method to do it
rules/  = which rules must not be violated
```

## 11. `templates/`

This folder contains the standard artifact templates.

```text
.maestro/engine/templates/
  agent-coder.template.md
  agents.template.yaml
  architecture-review.template.yaml
  bug.template.yaml
  dev-verification.template.yaml
  environment.template.yaml
  memory-update.template.yaml
  model-routing.template.yaml
  agent-activity.template.yaml
  response-ui.template.yaml
  project.template.yaml
  qc-handoff.template.md
  qc-test-result.template.yaml
  component.template.yaml
  task-analysis.template.yaml
  task-update.template.yaml
  task.template.yaml
  workflow-state.template.yaml
```

### When to use?

Use it when an agent needs to create a new artifact file.

Examples:

```text
Agent Factory creates a coder agent from agent-coder.template.md
Onboarding creates component knowledge from component.template.yaml
Task Analysis creates task-analysis.yaml from task-analysis.template.yaml
Dev Verification creates dev-verification.yaml
QC Runner creates qc-test-results.yaml
Bug Router creates a bug yaml
Memory Update creates memory-updates.yaml
```

### Why do we need templates?

Templates help:

```text
Consistent artifacts across tasks
QC reads handoffs easily
A new agent can resume a task from a file
Workflow Policy can easily validate which file is missing
```

## 12. `.maestro/`

`.maestro/` is the product-development control plane:

```text
Registry: canonical addresses for components, agents, skills, inputs, and artifacts
Knowledge: durable product and component facts
Work: initiative, epic, task, subtask, bug, and verification evidence
Memory: project patterns, task summaries, and local session context
Runtime: local active state, telemetry, cache, locks, and reports
```

Do not create parallel root `memory/`, `state/`, or `design/` control planes.

```text
.maestro/registry/{components,agents,skills,inputs,artifacts}.yaml
.maestro/knowledge/{index,project,test-policy}.yaml
.maestro/knowledge/components/<component>.yaml
.maestro/work/{index,initiatives,epics,tasks,bugs}/
.maestro/memory/{project,tasks,sessions}/
.maestro/runtime/{workflow-state,agent-activity,active-context}.yaml
```

Generated status artifacts:

```text
.maestro/runtime/reports/status.md
.maestro/runtime/reports/status.html
```

### When to use?

Use it when an agent needs to recall project information without rescanning from scratch.

Examples:

```text
What stack does this project use?
What services are there?
Which service has a coder agent?
Which service requires unit tests?
Which API/schema/event currently exists?
Which service does this task touch?
Is there a pattern/common util that should be reused?
```

### Important files

| File                      | Role                                                                                    |
| ------------------------- | --------------------------------------------------------------------------------------- |
| `.maestro/knowledge/index.yaml`       | Index read first to avoid opening the entire memory                                       |
| `.maestro/knowledge/project.yaml` | Overall memory of the project                                                          |
| `.maestro/registry/components.yaml`   | List of services/modules, source path, coding boundary                              |
| `.maestro/registry/agents.yaml` | List of coder agents and their scope                                              |
| `.maestro/knowledge/test-policy.yaml` | Unit/manual test rules per service                                                    |
| `.maestro/runtime/workflow-state.yaml` | Current state of the workflow                                                       |
| `.maestro/registry/skills.yaml` | Machine-readable registry for skill selection, risk gate, approval, installed/failed skills |
| `.maestro/config/model-routing.yaml` | Model profile routing for workflow agents                                            |
| `.maestro/runtime/agent-activity.yaml` | Activity dashboard and ETA telemetry                                        |
| `.maestro/config/response-ui.yaml` | Response layout modes for status/review/dev/final output                              |
| `.maestro/runtime/reports/status.md` / `.maestro/runtime/reports/status.html` | Generated status artifacts; regenerate with `scripts/status-dashboard.py --write` |
| `feedback/inbox.md`       | Where raw feedback lands when the AI does something wrong/incomplete                     |
| `feedback/patterns.md`    | Patterns confirmed through feedback for reuse                                            |
| `feedback/anti-patterns.md` | Recurring mistakes to avoid, drawn from feedback                                       |
| `.maestro/knowledge/components/<component-id>.yaml` | Detailed memory per component                                                            |
| `common/generics.md`      | Shared patterns/utils to avoid rewriting                                                 |

### Initial state

After setup, the state is usually:

```text
NEED_ONBOARDING
```

This means you need to run:

```text
/onboard
```

to fill in the real project information.

## 13. `docs/`

Folder of explanatory and visual documentation.

```text
.maestro/engine/docs/
  folder-guide.md
  visual-flow.md
  deep-onboarding.md
  skill-composition.md
  external-skills.md
```

Flow diagrams live inline in `visual-flow.md` as **Mermaid** (text), not as image files.

### When to use?

Use it when you need to understand the system through documentation or diagrams.

Examples:

```text
A newcomer wants to understand maestro
A dev lead wants to review the workflow
QC wants to understand the bug loop
An agent designer wants to adjust the architecture
```

### Important files

| File                   | Role                                             |
| ---------------------- | ------------------------------------------------ |
| `folder-guide.md`      | This document                                    |
| `visual-flow.md`       | Page to view all workflow diagrams               |
| `deep-onboarding.md`   | Deep onboarding standard                          |
| `skill-composition.md` | Skill composition standard                        |
| `external-skills.md`   | Registry of installed external skills             |
| `visual-flow.md`       | Mermaid flow diagrams (text, AI-readable; renders in Markdown) |

## 14. `.maestro/work/tasks/`

Folder that stores artifacts per task.

```text
.maestro/work/tasks/
  TASK-20260518-001-login/
    task-input.md
    task.yaml
    task-updates.yaml
    task-analysis.yaml
    architecture-review.yaml
    implementation-plan.yaml
    service-assignments.yaml
    coder-results.yaml
    dev-verification.yaml
    qc-handoff.md
    qc-test-results.yaml
    qc-delivery-report.md
    bugs.yaml
    memory-updates.yaml
```

### When to use?

Use it when there is a specific task that needs to go through the workflow.

Examples:

```text
Add a feature
Fix a bug
Refactor with a clear scope
Change an API
A task taken from an HLD/LLD/ticket
```

### Why is it important?

The task folder helps:

```text
Resume a task in a new conversation
Know which state the task is at
Know who did what
QC has a clear handoff
Bugs have clear reproduction
Memory update has a source artifact
```

The canonical QC handoff lives at `.maestro/work/tasks/<task_id>/qc-handoff.md`. Do not mirror it to a separate folder.

## 15. `.maestro/work/bugs/`

Folder that stores bugs found by QC or the workflow.

```text
.maestro/work/bugs/
  blockers/
    BUG-123.yaml
  non-blockers/
    BUG-456.yaml
```

### When to use?

Use it when QC finds a bug.

### Blocker bug

A blocker is a bug that prevents QC from continuing the main flow.

Examples:

```text
Happy path fails
App crash
Core API returns 500 entirely
Auth/permission is wrong
Data corruption
Unable to create baseline test data
A bug that blocks subsequent QC cases
```

Actions:

```text
Stop QC immediately
Create .maestro/work/bugs/blockers/<bug-id>.yaml
Route back to Coder Leader
Dev fixes
Verify again
QC retests
```

### Non-blocker bug

A non-blocker is a bug that does not stop QC from continuing.

Examples:

```text
Wrong UI copy
Minor layout
Warning that does not affect the flow
Secondary edge case
```

Actions:

```text
Create .maestro/work/bugs/non-blockers/<bug-id>.yaml
QC continues with the unaffected cases
Dev can fix in parallel
```

## 17. Real-world usage flows

### First-time project setup

```text
/coord
-> Project Brain Check
-> NEED_ONBOARDING
-> /onboard
-> Agent Candidate Report
-> User approve
-> /create-coders
-> AGENTS_READY
```

### Working on a new task

```text
/coord <task text or HLD/LLD>
-> /analyze-task
-> /plan-dev
-> /dev
-> /verify-dev
-> /handoff-qc
-> /qc
-> /sync-memory
```

### Hitting a blocker bug during QC

```text
/qc TASK-123
-> blocking bug found
-> /bug
-> create .maestro/work/bugs/blockers/BUG-xxx.yaml
-> stop QC
-> route to Coder Leader
-> /dev fix
-> /verify-dev
-> /handoff-qc
-> /qc retest
```

### Hitting a non-blocker bug during QC

```text
/qc TASK-123
-> non-blocking bug found
-> /bug
-> create .maestro/work/bugs/non-blockers/BUG-xxx.yaml
-> QC continues
-> dev fixes in parallel if needed
```

### Resuming a task in a new conversation

```text
/resume-task TASK-123
-> read task artifacts
-> detect current state
-> suggest next command
```

## 18. Who should read which file?

### Dev lead / user

```text
.claude/README.md
.maestro/engine/docs/folder-guide.md
.maestro/engine/docs/visual-flow.md
.claude/commands/README.md
```

### Coordinator agent

```text
.maestro/engine/workflow.md
.maestro/engine/rules/00-core-rules.md
.maestro/engine/rules/01-project-brain-rules.md
.maestro/engine/rules/11-approval-gates.md
.maestro/engine/rules/12-artifact-contracts.md
.claude/commands/coord.md
```

### Onboarding agent

```text
.maestro/engine/workflow.md
.claude/commands/onboard.md
.maestro/engine/rules/02-onboarding-rules.md
.maestro/engine/templates/project.template.yaml
.maestro/engine/templates/component.template.yaml
```

### Agent Factory

```text
.claude/commands/create-coders.md
.maestro/engine/rules/03-agent-factory-rules.md
.maestro/engine/templates/agent-coder.template.md
.maestro/registry/components.yaml
.maestro/knowledge/test-policy.yaml
```

### Service coder agent

```text
.maestro/engine/rules/06-service-coder-rules.md
.maestro/knowledge/components/<component-id>.yaml
.maestro/work/tasks/<task-id>/service-assignments.yaml
```

### QC agent

```text
.claude/commands/qc.md
.maestro/engine/rules/08-qc-rules.md
.maestro/engine/rules/09-bug-routing-rules.md
.maestro/work/tasks/<task-id>/qc-handoff.md
```

## 19. How to maintain this folder

When adding a new rule:

```text
Add a file or section in .maestro/engine/rules/
Update .maestro/engine/rules/README.md
Update the related commands
Update agent Rule bindings if needed
```

When adding a new command:

```text
Add .claude/commands/<command>.md
Declare the responsible agent
Declare the required rules
Declare the required artifacts
Update .claude/commands/README.md
Update README.md if it is an important user-facing command
```

When adding a new artifact:

```text
Add a template in .maestro/engine/templates/
Update .maestro/engine/rules/12-artifact-contracts.md
Update .maestro/engine/workflow.md if the artifact affects the state machine
Update .maestro/engine/docs/visual-flow.md if the flow changes
```

When changing the workflow:

```text
Update .maestro/engine/workflow.md first
Update the related rules
Update the related commands
Update the related agents
Update docs/visual-flow.md and the diagrams if needed
Update changelog.md
```

## 20. Quick checklist

Before coding:

```text
Is the Project Brain fresh?
Does the task already have task-analysis.yaml?
Do the impacted services have active coder agents?
Are the coder scopes correct?
Is the test policy clear?
```

Before moving to QC:

```text
Is the dev verification score >= 80%?
Do critical checks pass 100%?
Are there no blockers?
Has the QC handoff been created?
```

When QC hits a bug:

```text
Is the bug a blocker?
If a blocker: stop QC immediately
If a non-blocker: create a bug task and continue QC
Does the bug have reproduction, expected, actual?
```

When finishing a task:

```text
Is it QC_DONE?
What does the memory update need to record?
Did the component knowledge change?
Does the bug pattern need to be saved?
```

## 21. Skill composition standard

Skills are capabilities, not agent identities.

```text
One agent can use many skills.
One skill can be reused by many agents.
Generated service coders should combine workflow skills, technical skills, quality skills, and artifact skills.
```

Read [skill-composition.md](skill-composition.md) for the full standard.

## 22. Deep onboarding

Deep onboarding is the deep-scan layer that lets agents understand project-specific reusable assets, coding flow, business flow, conventions and anti-patterns before generating coder agents.

Use when:

- The project has many helpers/shared modules that are easy to duplicate.
- You need coder agents to follow the existing style/code flow.
- The task touches complex business flows such as auth, payment, notification, order, worker, event-driven, data sync.
- QC and Dev Verification need to know which flow is critical.

Related files:

- docs/deep-onboarding.md
- .maestro/memory/project/common/generics.md
- .maestro/knowledge/conventions.md
- .maestro/knowledge/architecture.md
- .maestro/knowledge/project.yaml deep_project_intelligence
- .maestro/knowledge/components/<component-id>.yaml component_deep_intelligence

Key principles:

- Onboarding must record path, purpose, when_to_reuse, evidence and confidence.
- Do not paste long source code into memory.
- Service coders must check reusable assets before creating a new helper.
- Dev Verification must check duplicate helper risk and convention compliance.
