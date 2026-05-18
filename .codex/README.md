# Codex Adapter

This folder adapts `agent-workspace` for OpenAI Codex.

## How Codex Reads This Repo

Codex reads `AGENTS.md` instruction files. It does not treat `.claude/commands/*.md` as Codex-native slash commands, and project-local custom slash commands are not currently auto-registered in the Codex `/` menu.

When working in Codex:

- Read `.codex/AGENTS.md`, root `AGENTS.md`, `CLAUDE.md`, `COMMAND.md`, and `.agent/workflow.md`.
- Route natural-language work through the Coordinator semantics from `/coord`.
- Use `.claude/commands/*.md` as workflow contracts, not as Codex TUI command registrations.
- Use Codex built-in slash commands only for Codex controls such as `/model`, `/review`, `/plan`, `/status`, `/skills`, `/hooks`, `/mcp`, `/apps`, and `/plugins`.
- Invoke workspace phases in Codex with natural language, for example `coord: onboard services` or `theo /coord: implement task X`; avoid bare leading `/coord` because the Codex TUI may intercept it.

## Sandbox Boundary

`.codex/config.toml` can tighten the default Codex session after the project is trusted, but it is not the source of truth for service-level permissions. The hard workflow contract remains `.runtime/context/workflow-state.yaml.active_task_id` plus `.runtime/context/agent-registry.yaml.allowed_write_paths`.

## Why `/coord` Does Not Appear

`/coord`, `/onboard`, `/dev`, `/qc`, and the other workspace commands are framework-level workflow intents. They are understood through repository instructions and `COMMAND.md`.

They will not appear when typing `/` in Codex unless Codex adds native support for project-defined slash commands in a future release.
