# Kiro Agent Hooks

> **SCOPE: Kiro IDE only.** These hooks fire only inside Kiro's Agent runtime. Claude Code, Codex,
> Cursor, Gemini, and Copilot do NOT respect them — each enforces the same policy through its own
> entrypoint doc. When you change a hook here, mirror the policy into the other entrypoints if the gate
> should apply across all tools.

> **Kiro hooks are event-triggered agent prompts, not deterministic exit-code blockers.** They assist
> (e.g., run a drift check, remind about scope) but cannot hard-block a tool call the way Cursor/Claude
> `preToolUse` hooks can. Hard enforcement comes from the steering policy (`.kiro/steering/`) and the
> Python guards in `scripts/hooks/` (scope/secret/destructive). Follow the ECC profile convention:
> `MAESTRO_HOOK_PROFILE=minimal|standard|strict` (default `standard`).

> **SCHEMA caveat:** `*.kiro.hook` files use Kiro's agent-hook JSON. Verify the exact schema against the
> current Kiro docs before relying on these in CI; field names may evolve.

## Hooks here

- `maestro-drift-check.kiro.hook` — on edits under `.maestro/engine/**`, ask the agent to run the
  architecture health check and report drift.
- `maestro-secret-scan.kiro.hook` — on file save, remind the agent to ensure no secrets/keys/.env values
  were introduced (R-013), and to keep them out of commits.

These complement, and do not replace, `scripts/hooks/` and the steering policy.
