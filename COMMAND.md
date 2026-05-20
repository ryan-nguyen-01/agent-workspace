# Commands

Canonical slash command index for `agent-workspace`.

Detailed command contracts live in `.claude/commands/*.md`. This file is the root entrypoint for humans and agents that need to know which command to use.

These are `agent-workspace` workflow commands, not guaranteed UI registrations for every AI tool. Claude Code may expose `.claude/commands/*.md` as slash commands; Codex currently treats `/` as its own built-in TUI menu and does not auto-list these project commands.

In Codex, invoke these as natural-language intents such as `coord: <request>` or `theo /coord: <request>`. Avoid bare leading `/coord` in Codex because unknown slash commands can be intercepted by the Codex TUI.

## Primary Rule

Every user request should enter through `/coord` unless the user intentionally calls a specific command.

In framework-template/not_applied mode, requests that maintain this repository's framework files still enter through `/coord`, but the coordinator should classify them as:

```yaml
target_scope: framework
requires_onboarding: false
```

Use natural-language intents such as `coord: framework <request>` when you want to make that scope explicit. Onboarding is required only before applied-service work under `services/<service-name>/`.

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
| `/workspace-mode` | Coordinator | Switch or repair `distribution_mode` between `framework-template` and `workspace`. |
| `/policy-check` | Workflow Policy | Validate transition, approval gate, exception, or workflow artifact snapshot. |
| `/status` | Coordinator | Print workflow state, brain freshness, task, model routing, response UI mode, and agent activity/token dashboard. |

CLI mirror for tools that do not expose project slash commands:

```bash
python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json>
python3 scripts/status-dashboard.py --mode dashboard --write
python3 scripts/agent-activity.py start --agent-id <agent> --phase <phase> --current-action <summary>
python3 scripts/architecture-health-check.py --strict --write-report
```

## Fast Maintenance

Trivial framework maintenance may use the lightweight fast-track path from `.agent/workflow.md` §6.2. It can skip onboarding, generated coder selection, implementation-plan/service-assignments, and QC artifacts when the change does not affect approval gates, security rules, workflow state machine, generated coder scopes, destructive behavior, or application source under `services/`.

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
/workspace-mode status
/workspace-mode framework-template
/workspace-mode workspace
/workspace-mode repair
/policy-check <transition-or-exception>
/policy-check snapshot --root <snapshot-root>
python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json>
python3 scripts/status-dashboard.py --mode dashboard --write
python3 scripts/agent-activity.py start --agent-id <agent> --phase <phase> --current-action <summary>
python3 scripts/architecture-health-check.py --strict --write-report
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
