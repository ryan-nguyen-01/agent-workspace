# GitHub Copilot — Workspace Instructions

## Project type

This is the **agent-platform** — a multi-agent workflow system for running software development pipelines inside VS Code Copilot.

## How to use this workspace

**Always select the `coordinator` agent** in the Copilot agent selector before starting any task.

The coordinator is the single entry point for all requests:

- Project setup / onboarding
- Task intake (HLD, LLD, tickets, bug reports, direct instructions)
- Implementation planning and coding
- Dev verification and QC
- Memory updates

Do **not** jump directly to sub-agents (onboarding, coder-leader, qc-runner, etc.) from raw user input. The coordinator handles routing.

## Key files

| File                                  | Purpose                                      |
| ------------------------------------- | -------------------------------------------- |
| `.claude/workflow.md`                 | End-to-end workflow policy (source of truth) |
| `.claude/context/workflow-state.yaml` | Current workflow state                       |
| `.claude/context/project-brain.yaml`  | Project memory                               |
| `.claude/context/agent-registry.yaml` | Active service coder agents                  |
| `.claude/agents/coordinator.agent.md` | Coordinator agent definition                 |
| `CLAUDE.md`                           | Full system instructions and routing rules   |

## Workflow states (summary)

```
NEW → NEED_ONBOARDING → ONBOARDED → NEED_AGENT_CREATION_APPROVAL → AGENTS_READY
→ READY_FOR_ANALYSIS → ANALYZED → PLANNED
→ IN_DEV → DEV_VERIFYING → DEV_BLOCKED → IN_DEV (recovery)
→ DEV_DONE → QC_READY → QC_TESTING → BLOCKED_BY_BUG → FIXING → DEV_VERIFYING
→ DEV_DONE → QC_RETESTING → QC_DONE → MEMORY_SYNCING → DONE
```

## Coordinator startup behavior

On every new conversation, the coordinator will:

1. Read `workflow.md` and `workflow-state.yaml`
2. Check project brain and agent registry
3. Report current state, then process your request

## Anti-guessing rules (Karpathy-aligned)

All agents in this system follow 4 principles:

1. State uncertainty explicitly — never guess silently
2. Ask clarification when missing facts affect scope, security, or correctness
3. Do not fabricate facts; use `unknown` + evidence-needed
4. Claim "done" only with concrete evidence (file, test, artifact)
