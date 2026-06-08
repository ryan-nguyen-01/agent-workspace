# Commands

Canonical slash command index for `maestro`.

Detailed command contracts live in `.claude/commands/*.md`. This file is the root entrypoint for humans and agents that need to know which command to use.

These are `maestro` workflow commands, not guaranteed UI registrations for every AI tool. Claude Code may expose `.claude/commands/*.md` as slash commands; Codex currently treats `/` as its own built-in TUI menu and does not auto-list these project commands.

In Codex, invoke these as natural-language intents such as `coord: <request>` or `theo /coord: <request>`. Avoid bare leading `/coord` in Codex because unknown slash commands can be intercepted by the Codex TUI.

## Primary Rule

Every user request should enter through `/coord` unless the user intentionally calls a specific command.

Requests that maintain this repository's framework files still enter through `/coord`, but the coordinator should classify them as:

```yaml
target_scope: framework
requires_onboarding: false
```

Use natural-language intents such as `coord: framework <request>` when you want to make that scope explicit. Onboarding is required only when assisted/governed product work depends on missing component facts.

## Commands

| Command | Owner | Use when |
| --- | --- | --- |
| `/coord` | Coordinator | Universal entrypoint; route natural-language requests and enforce workflow state. |
| `/ship` | Coordinator | Autonomous build-to-done (Safe Autopilot): run the full pipeline under a one-time grant, self-heal build/test/runtime errors, stop only on hard-stops, deliver a finished product (R-019). |
| `/git` | Coordinator | Git-flow workflow: branch per task, milestone commits, sync, and PR. Outward git (push/PR/merge/tags) is user-gated (R-020). |
| `/onboard` | Onboarding | Build or refresh Project Knowledge, component registry, test policy, and coder candidates. |
| `/create-coders` | Agent Factory | Generate scoped component coder agents after user approval. |
| `/analyze-task` | Task Analysis | Normalize HLD/LLD/ticket/text into `task-analysis.yaml`. |
| `/plan-dev` | Coder Leader | Build implementation plan and service assignments. |
| `/dev` | Coder Leader | Run implementation through assigned coders. |
| `/verify-dev` | Dev Verification | Evaluate Code Done, critical checks, scope, and test policy. |
| `/handoff-qc` | QC Handoff | Create Dev-to-QC handoff after DEV_DONE. |
| `/qc` | QC Runner | Run QC, record results, and classify blocker/non-blocker bugs. |
| `/bug` | Bug Router | Create or route blocker/non-blocker defects. |
| `/sync-memory` | Memory Update | Persist durable project/component/workflow learnings. |
| `/skills` | Coordinator | Maintain installed skills, `skills-lock.json`, and skill registry metadata. |
| `/resume-task` | Coordinator | Continue an interrupted task from current artifacts/state. |
| `/maestro-init` | Coordinator | Install the `.maestro/` control plane, component/doc roots, local runtime seeds, and managed instruction block. |
| `/access` | Coordinator | Switch tool-permission posture: `full` (bypassPermissions) / `guarded`. Does not change workflow gates or hooks (R-011-14). |
| `/policy-check` | Workflow Policy | Validate transition, approval gate, exception, or workflow artifact snapshot. |
| `/status` | Coordinator | Print workflow state, project knowledge freshness, task, run, model routing, response UI mode, and agent activity dashboard. |

CLI mirror for tools that do not expose project slash commands:

```bash
python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json>
python3 scripts/status-dashboard.py --mode dashboard --write
python3 scripts/agent-activity.py start --agent-id <agent> --phase <phase> --current-action <summary>
python3 scripts/architecture-health-check.py --strict --write-report
```

## Fast Maintenance

Trivial framework maintenance may use the lightweight fast-track path from `.maestro/engine/workflow.md` §6.2. It can skip onboarding, generated coder selection, implementation-plan/service-assignments, and QC artifacts when the change does not affect approval gates, security rules, workflow state machine, generated coder scopes, destructive behavior, or application source under `services/`.

## Maintenance Commands

Use these intentionally; they are not part of normal feature implementation:

```text
/sync-memory --refresh-index
/sync-memory --scan --inputs
/sync-memory --scan --components <component-id>
/skills status
/skills audit
/skills update <skill-name>
/skills refresh-registry
/policy-check <transition-or-exception>
/policy-check snapshot --root <snapshot-root>
python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json>
python3 scripts/status-dashboard.py --mode dashboard --write
python3 scripts/agent-activity.py start --agent-id <agent> --phase <phase> --current-action <summary>
python3 scripts/agent-run.py create --summary <summary>
python3 scripts/agent-run.py checkpoint --run-id <run-id> --summary <summary> --next-action <next>
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
.maestro/engine/workflow.md           Workflow states, transitions, gates
.maestro/engine/rules/                Mandatory command policies
```
