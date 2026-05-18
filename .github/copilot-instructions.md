# GitHub Copilot — Agent Workspace Instructions

## Project type

This is **agent-workspace**: a coordinator-driven AI workflow workspace for software engineering.

It is not an application repository. Application/service repositories are cloned under `services/<service-name>/`, while this repository holds the agent engine, workflow rules, memory, task artifacts, and service coder scopes.

## How to use this workspace

Use `COMMAND.md` to choose a slash command. For natural-language requests, route through `/coord`.

The coordinator is the single entry point for all requests:

- Project setup / onboarding
- Task intake (HLD, LLD, tickets, bug reports, direct instructions)
- Optional architecture review for cross-service/API/data/event/security/infra risk
- Implementation planning and coding
- Dev verification and QC
- Memory updates
- Skill maintenance through `/skills`

Do **not** jump directly to sub-agents (onboarding, coder-leader, qc-runner, etc.) from raw user input. The coordinator handles routing.

## Copilot operating rules

- Open the `agent-workspace` root, not an individual service folder, when running workflow tasks.
- Do not copy `.claude/` into service repositories.
- Do not modify application source before `task-analysis.yaml` exists and the workflow has moved into implementation.
- If `task-analysis.yaml` requires architecture review, do not plan or code until `architecture-review.yaml` exists with `decision: approved`.
- Generated service coders may write only inside paths approved in `.runtime/context/agent-registry.yaml`.
- Treat `inputs/` as read-only user reference docs.
- Treat `.runtime/context/`, `.runtime/tasks/`, and `.runtime/bugs/` as workflow/runtime artifacts.
- Do not store secrets, tokens, raw cookies, private keys, or long logs in `.runtime/` artifacts or tool adapter files.
- If uncertain, mark the fact `unknown` and ask the user or route to `/policy-check`.

## Key files

| File | Purpose |
| --- | --- |
| `COMMAND.md` | Canonical slash command index |
| `CLAUDE.md` | Full system instructions and routing rules |
| `AGENTS.md` | Cross-agent entrypoint for non-Claude tools |
| `.agent/workflow.md` | End-to-end workflow policy |
| `.runtime/context/workflow-state.yaml` | Current workflow state |
| `.runtime/context/project-brain.yaml` | Durable workspace memory |
| `.runtime/context/service-catalog.yaml` | Service inventory and source paths |
| `.runtime/context/agent-registry.yaml` | Active coder agents and approved scopes |
| `.runtime/context/skill-registry.yaml` | Skill selection and approval metadata |
| `.claude/agents/coordinator.agent.md` | Coordinator agent definition |
| `.claude/agents/solution-architect.agent.md` | Optional architecture review definition |

## Commands

```text
/coord          Universal entrypoint
/onboard        Scan inputs/ and services/, build workspace brain
/create-coders  Generate service coders after approval
/analyze-task   Create task-analysis.yaml before coding
/plan-dev       Plan implementation
/dev            Implement through Coder Leader and scoped coders
/verify-dev     Evaluate Code Done
/handoff-qc     Create QC handoff
/qc             Run QC
/bug            Route defects
/sync-memory    Persist durable learnings
/skills         Maintain installed skills and registry metadata
/resume-task    Continue an interrupted task
/policy-check   Validate transitions and exceptions
/status         Print state banner
```

## Workflow states (summary)

```
NEW → NEED_ONBOARDING → ONBOARDED → NEED_AGENT_CREATION_APPROVAL → AGENTS_READY
→ READY_FOR_ANALYSIS → ANALYZED → ARCHITECTURE_REVIEWING → PLANNED
→ IN_DEV → DEV_VERIFYING → DEV_BLOCKED → IN_DEV (recovery)
→ DEV_DONE → QC_READY → QC_TESTING → BLOCKED_BY_BUG → FIXING → DEV_VERIFYING
→ DEV_DONE → QC_RETESTING → QC_DONE → MEMORY_SYNCING → DONE
```

## Coordinator startup behavior

On every new conversation, the coordinator will:

1. Read `.agent/workflow.md` and `.runtime/context/workflow-state.yaml`
2. Read `.runtime/context/index.yaml`, project brain, service catalog, and agent registry when present
3. Check brain freshness fields and registered coders
4. Report current state, then process your request

## Workspace layout

```text
agent-workspace/
  .agent/        Tool-neutral workflow source
  .runtime/      Memory, task artifacts, and bug records
  .claude/       Claude adapter
  inputs/        User-provided PRD/HLD/ADR/specs/runbooks
  services/      Local clones of application repositories
```

## Anti-guessing rules (Karpathy-aligned)

All agents in this system follow 4 principles:

1. State uncertainty explicitly — never guess silently
2. Ask clarification when missing facts affect scope, security, or correctness
3. Do not fabricate facts; use `unknown` + evidence-needed
4. Claim "done" only with concrete evidence (file, test, artifact)
