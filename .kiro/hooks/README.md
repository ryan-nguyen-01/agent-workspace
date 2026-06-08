# Kiro Agent Hooks

**SCOPE: Kiro IDE only.** These hooks fire only inside Kiro's Agent runtime. Claude Code, Codex,
Cursor, Gemini, and Copilot do NOT respect them — each enforces the same policy through its own
entrypoint doc. When you change a hook here, mirror the policy into the other entrypoints if the gate
should apply across all tools.

**SCHEMA: verified against the Kiro docs ([kiro.dev/docs/hooks](https://kiro.dev/docs/hooks/), June 2026).**
Hooks live in `.kiro/hooks/` with the `.kiro.hook` extension and this shape:

```json
{
  "enabled": true,
  "name": "...",
  "description": "...",
  "version": "1",
  "when": { "type": "<trigger>", "patterns": ["glob", "..."] },
  "then": { "type": "askAgent", "prompt": "..." }
}
```

Valid `when.type` (per [kiro.dev/docs/hooks/types](https://kiro.dev/docs/hooks/types/)): `fileCreate`,
`fileSave`, `fileDelete`, `manualTrigger`, `promptSubmit`, `agentStop`, `preToolUse`, `postToolUse`,
`preTaskExecution`, `postTaskExecution`. `then.type` is `askAgent` (needs `prompt`) or `runCommand`
(needs `command`).

Kiro supports `preToolUse`/`postToolUse` hooks (so it can gate around tool calls, unlike a plain
event-only model). Still, the deterministic hard blocks for this framework live in `scripts/hooks/`
(scope/secret/destructive guards) and the steering policy — the Kiro hooks here are agent-assist
automations that complement them. Follow the ECC profile convention:
`MAESTRO_HOOK_PROFILE=minimal|standard|strict` (default `standard`).

## Hooks here

- `maestro-drift-check.kiro.hook` — on save under `.maestro/engine/**`, `.claude/agents/**`,
  `.claude/commands/**`, `scripts/**`: ask the agent to run the architecture health check and report drift.
- `maestro-secret-scan.kiro.hook` — on save: ask the agent to ensure no secrets/keys/.env values were
  introduced (R-013) and to keep them out of commits.
