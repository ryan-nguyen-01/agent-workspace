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
