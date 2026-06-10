# maestro — Claude Code Plugin

maestro ships a Claude Code **plugin wrapper** so its agents, skills, commands, and
enforcement hooks can be installed into other projects via the `/plugin` system — without copying
`.claude/` by hand.

> **Codex users:** there is a separate Codex plugin (skills) + custom prompts (commands). See the
> "Codex Slash Menu" section of [`.codex/AGENTS.md`](.codex/AGENTS.md) and `scripts/build-codex-plugin.py`.
>
> The plugin is the shared **Claude tool layer**. Run `/maestro-init` in a target project to install its
> project-local `.maestro/` control plane and managed instruction entrypoint.

## What the plugin provides

| Component | Source (single source of truth) |
|-----------|----------------------------------|
| 12 workflow agents + 3 built-in coders + 19 specialist advisors | `.claude/agents/**` |
| 231 skills | `.claude/skills/**` |
| 20 slash commands (incl. `/ship`, `/maestro-init`, `/access`) | `.claude/commands/*.md` |
| scope / secret / destructive PreToolUse hooks | `scripts/hooks/*.py` via `.claude-plugin/hooks.json` |

The wrapper does **not** duplicate content: `.claude-plugin/plugin.json` points its component paths
directly at the existing `.claude/` directories. Hooks run from `${CLAUDE_PLUGIN_ROOT}/scripts/hooks/`.

## Install

```text
# 1. Register this repo as a plugin marketplace (git URL or local path)
/plugin marketplace add <git-url-or-local-path-to-maestro>

# 2. Install the plugin
/plugin install maestro@maestro
```

`${CLAUDE_PLUGIN_ROOT}` resolves to the installed plugin directory; the hook scripts read the *target
project's* `.maestro/runtime/` state via the tool payload `cwd`, so enforcement applies to the project you are
working in.

## Regenerate the wrapper (maintainers)

The wrapper is generated from the repo — never hand-edit `.claude-plugin/*.json`:

```bash
python3 scripts/build-plugin.py          # regenerate plugin.json + hooks.json + marketplace.json
python3 scripts/build-plugin.py --check   # CI/drift: fail if wrapper is out of sync
```

`scripts/architecture-health-check.py` also fails if the wrapper drifts from source.

## Scope & limits

A plugin does not directly own project-root instruction or state files. `/maestro-init` bridges that boundary
by copying framework-owned `.maestro/engine/` files, creating project-owned workspace domains, seeding
ignored local runtime, and appending one managed import block:

- ✅ Use maestro's agents, skills, commands, and hooks inside any Claude Code project.
- ✅ Run `/maestro-init` for the complete risk-based workflow in an existing or greenfield project.
- ✅ Existing `CLAUDE.md`, `AGENTS.md`, `.claude/`, and source roots are preserved.
- ⚠️ Codex is served by its own adapter entrypoints in the
  repo, not by this Claude plugin.
