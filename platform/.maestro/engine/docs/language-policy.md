# Language Policy

Goal: maximize how precisely an AI agent reads the framework, while letting the human user work in
their own language.

## Rule

```text
Framework documents (the AI contract)  → English.
User-facing conversation (chat replies) → match the user's language.
```

- **English for all framework artifacts**: rules (`.maestro/engine/rules/**`), `.maestro/engine/workflow.md`, agent and
  command definitions (`.claude/agents/**`, `.claude/commands/**`), templates (`.maestro/engine/templates/**`),
  `.maestro/engine/docs/**`, entry points (`CLAUDE.md`, `AGENTS.md`, adapters), playbooks, and config comments.
  These are read by the model as contracts; one consistent language removes ambiguity.
- **User's language for the conversation**: if the user writes in Vietnamese, reply in Vietnamese; if
  in English, reply in English. The reply language follows the user, not the docs.
- Identifiers stay English regardless: file paths, agent ids, rule ids (R-0xx), model/skill names,
  YAML keys, state names, command names, tool names — these are contract tokens.
- Task artifacts under `.maestro/work/tasks/**` may quote the user's own words verbatim (their language),
  but agent-authored analysis/decisions in those artifacts are English.

## Why

```text
- AI precision: mixed-language contracts create translation noise and edge-case misreads. English is
  the lowest-ambiguity option for current models reading instructions.
- Human accessibility: the user never has to read or write English to drive the workflow — the agent
  bridges. The docs being English does not change how the user talks to the agent.
```

## Migration status

The AI-contract layer is being converted to English (most of it already is). User-facing guides
(README, SETUP, QUICKSTART, GUIDELINES) are converted in a later pass; the conversation layer is
unaffected. New documents are authored in English from now on.
