---
inclusion: always
---

# Tech

This repository is a **tool-neutral control plane**, not an application stack. Its "tech" is the
framework substrate and the per-tool adapters.

## Substrate

- Control plane: Markdown + YAML under `.maestro/` (engine workflow, rules, templates, registries,
  knowledge, work, runtime). No application source lives under `.maestro/`.
- Helper scripts: **Python 3** in `scripts/` (status dashboard, agent activity/runs, init, plugin/prompt
  builders, architecture health check). No third-party Python deps required (custom minimal YAML reader).
- Skills: flat `.claude/skills/<name>/SKILL.md` for harness discovery.

## Tool adapters

`.claude/` (native: agents, skills, commands, hooks) · `.codex/` · `.cursor/` (rules + hooks) ·
`.gemini/` · `.github/copilot-instructions.md` · `.kiro/`. Each adapter points its tool at the same
`.maestro/` control plane; policy is mirrored across entrypoints (validated by the architecture health
check).

## Deterministic guards (ECC-style hook profiles)

`scripts/hooks/{scope,secret,destructive}-guard.py` enforce scope/secret/destructive rules as hard
blocks. Runtime profiles (from the ECC pattern): `MAESTRO_HOOK_PROFILE=minimal|standard|strict`
(default `standard`) and `MAESTRO_DISABLED_HOOKS=ids`. Claude wires them in `.claude/settings.json`;
Cursor mirrors them in `.cursor/hooks/`. Kiro agent hooks (`.kiro/hooks/*.kiro.hook`) support
file save/create/delete and pre/post-tool-use triggers; here they run agent-assist automations
(drift check, secret scan). Deterministic hard blocks remain in the Python guards + steering policy.

## When generating an app

Pick the actual app stack from the approved blueprint (it is not fixed by this repo). Follow the Code
Layout Standard (`.maestro/engine/docs/code-layout.md`): feature modules + layers.

## Common commands

```bash
python3 scripts/status-dashboard.py --mode overview         # full project briefing
python3 scripts/architecture-health-check.py --strict       # deterministic drift check
python3 scripts/maestro-init.py --from <framework> --to .   # install into a project
```
