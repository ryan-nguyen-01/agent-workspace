# agent-workspace — Claude Code Plugin

agent-workspace ships a Claude Code **plugin wrapper** so its agents, skills, commands, and
enforcement hooks can be installed into other projects via the `/plugin` system — without copying
`.claude/` by hand.

> **Codex users:** there is a separate Codex plugin (skills) + custom prompts (commands). See the
> "Codex Slash Menu" section of [`.codex/AGENTS.md`](.codex/AGENTS.md) and `scripts/build-codex-plugin.py`.
>
> The plugin is the **Claude tool layer**. The full stateful workflow (project brain, task
> artifacts, `CLAUDE.md` precedence, the tool-neutral `.agent/` source, and `services/` model) still
> lives in the workspace repo and cannot be delivered by a plugin. See [Scope & limits](#scope--limits).

## What the plugin provides

| Component | Source (single source of truth) |
|-----------|----------------------------------|
| 12 workflow agents + 2 built-in coders + 19 specialist advisors | `.claude/agents/**` |
| 231 skills | `.claude/skills/**` |
| 17 slash commands (incl. `/aw-init`, `/access`) | `.claude/commands/*.md` |
| scope / secret / destructive PreToolUse hooks | `scripts/hooks/*.py` via `.claude-plugin/hooks.json` |

The wrapper does **not** duplicate content: `.claude-plugin/plugin.json` points its component paths
directly at the existing `.claude/` directories. Hooks run from `${CLAUDE_PLUGIN_ROOT}/scripts/hooks/`.

## Install

```text
# 1. Register this repo as a plugin marketplace (git URL or local path)
/plugin marketplace add <git-url-or-local-path-to-agent-workspace>

# 2. Install the plugin
/plugin install agent-workspace@agent-workspace
```

`${CLAUDE_PLUGIN_ROOT}` resolves to the installed plugin directory; the hook scripts read the *target
project's* `.runtime/` state via the tool payload `cwd`, so enforcement applies to the project you are
working in.

## Regenerate the wrapper (maintainers)

The wrapper is generated from the repo — never hand-edit `.claude-plugin/*.json`:

```bash
python3 scripts/build-plugin.py          # regenerate plugin.json + hooks.json + marketplace.json
python3 scripts/build-plugin.py --check   # CI/drift: fail if wrapper is out of sync
```

`scripts/architecture-health-check.py` also fails if the wrapper drifts from source.

## Scope & limits

A plugin cannot ship a project-root `CLAUDE.md`, the `.agent/` workflow source, the `.runtime/` state
scaffold, or the non-Claude adapters (`.codex/`, `.cursor/`, `.gemini/`, `.github/copilot-instructions.md`).
So installing the plugin gives you the **tools**, not the full **workflow brain**:

- ✅ Use agent-workspace's agents, skills, commands, and hooks inside any Claude Code project.
- ⚠️ For the complete coordinator-driven workflow (task analysis → architecture → dev → QC → memory,
  with persistent project brain and task artifacts), clone and work inside the agent-workspace repo as
  described in [SETUP.md](SETUP.md).
- ⚠️ Other tools (Codex, Cursor, Gemini, Copilot) are served by their own adapter entrypoints in the
  repo, not by this Claude plugin.
