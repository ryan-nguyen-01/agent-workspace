---
description: "maestro /overview — One command that prints the **whole project picture and current status**: identity, methodology and execution mode, w..."
argument-hint: "[request or args]"
---

You are running the maestro `/overview` workflow command inside Codex.

Follow `.codex/AGENTS.md` (or `AGENTS.md`) routing and the framework rules. Route every
request through the coordinator model; do not bypass approval gates, security/secret rules,
or the task-analysis source-edit gate. If the maestro framework files
(`.maestro/engine/`, `.maestro/registry/`, `.maestro/knowledge/`, `.maestro/work/`, `.maestro/runtime/`, `.claude/commands/overview.md`) are present, defer to them as the
authoritative contract — this prompt is a portable mirror.

User input for this command: $ARGUMENTS

---
## Command contract (mirrored from .claude/commands/overview.md)

# /overview

## Purpose

One command that prints the **whole project picture and current status**: identity, methodology and
execution mode, workflow state, active task/run, autopilot, knowledge, requirements/design artifacts,
framework structure (agents/skills/rules/templates/commands), and git state — plus the suggested next
action. Use it to get oriented at the start of a session or to check where the project stands.

`/status` is the quick runtime status; `/overview` is the full project briefing.

## Responsible agent

coordinator

## Behavior

```text
1. Run: python3 scripts/status-dashboard.py --mode overview
2. Present the output. Do not fabricate values; fields that are unknown print as unknown/none.
3. If the project brain is stale/missing for product work, point to /onboard. End with the next action.
```

CLI mirror:

```bash
python3 scripts/status-dashboard.py --mode overview
python3 scripts/status-dashboard.py --mode overview --write   # also writes the status artifacts
```

## Output (sections)

```text
Project              workspace/product identity, component roots
Methodology & mode   methodology, execution mode, verification owner, access mode
Workflow status      state, active task/run, autopilot, activity, next action
Knowledge            project-brain freshness, components, active coder agents
Requirements & design  BA docs (BRD/PRD/US/UC/BR/NFR/RTM) and UI prototype presence
Framework structure  agents (workflow/coders/specialists), skills, rules, templates, commands
Git                  branch, ahead/behind, uncommitted files, last commit
```

## Required rules

```text
00-core-rules.md
15-model-routing-observability-rules.md
```
