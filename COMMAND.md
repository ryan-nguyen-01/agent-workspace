# Commands

Canonical slash command index for `agent-workspace`.

Detailed command contracts live in `.claude/commands/*.md`. This file is the root entrypoint for humans and agents that need to know which command to use.

These are `agent-workspace` workflow commands, not guaranteed UI registrations for every AI tool. Claude Code may expose `.claude/commands/*.md` as slash commands; Codex currently treats `/` as its own built-in TUI menu and does not auto-list these project commands.

In Codex, invoke these as natural-language intents such as `coord: <request>` or `theo /coord: <request>`. Avoid bare leading `/coord` in Codex because unknown slash commands can be intercepted by the Codex TUI.

## Primary Rule

Every user request should enter through `/coord` unless the user intentionally calls a specific command.

## Commands

| Command | Owner | Use when |
| --- | --- | --- |
| `/coord` | Coordinator | Universal entrypoint; route natural-language requests and enforce workflow state. |
| `/onboard` | Onboarding | Build or refresh Project Brain, service catalog, test policy, and coder candidates. |
| `/create-coders` | Agent Factory | Generate scoped service coder agents after user approval. |
| `/analyze-task` | Task Analysis | Normalize HLD/LLD/ticket/text into `task-analysis.yaml`. |
| `/plan-dev` | Coder Leader | Build implementation plan and service assignments. |
| `/dev` | Coder Leader | Run implementation through assigned coders. |
| `/verify-dev` | Dev Verification | Evaluate Code Done, critical checks, scope, and test policy. |
| `/handoff-qc` | QC Handoff | Create Dev-to-QC handoff after DEV_DONE. |
| `/qc` | QC Runner | Run QC, record results, and classify blocker/non-blocker bugs. |
| `/bug` | Bug Router | Create or route blocker/non-blocker defects. |
| `/sync-memory` | Memory Update | Persist durable project/service/workflow learnings. |
| `/skills` | Coordinator | Maintain installed skills, `skills-lock.json`, and skill registry metadata. |
| `/resume-task` | Coordinator | Continue an interrupted task from current artifacts/state. |
| `/policy-check` | Workflow Policy | Validate transition, approval gate, or exception. |
| `/status` | Coordinator | Print workflow state, brain freshness, task, and agent registry summary. |

## Maintenance Commands

Use these intentionally; they are not part of normal feature implementation:

```text
/sync-memory --refresh-index
/sync-memory --scan --inputs
/sync-memory --scan --services <service-id>
/skills status
/skills audit
/skills update <skill-name>
/skills refresh-registry
/policy-check <transition-or-exception>
```

## Skill Updates

Skill updates must go through `/skills`; do not update installed skill folders from `/onboard`, `/create-coders`, or `/dev`.

```text
/skills status              Inspect installed folders, lock, registry
/skills audit               Review risk gates and overlapping scopes
/skills update <skill>      Propose and approve one skill update
/skills update --all        Maintenance-only batch update with approval
/skills refresh-registry    Reconcile registry/docs/lock metadata
```

## File Map

```text
COMMAND.md                    Root command index
.claude/commands/README.md    Internal command index
.claude/commands/*.md         Per-command contracts
.agent/workflow.md           Workflow states, transitions, gates
.agent/rules/                Mandatory command policies
```
