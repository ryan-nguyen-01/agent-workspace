# /aw-init

## Purpose

Scaffold the agent-workspace **full flow** into the current project. A plugin install only delivers
the tool layer (agents, skills, commands, hooks); this command adds the tool-neutral source
(`.agent/`), the runtime state tree (`.runtime/`), and `CLAUDE.md` precedence so the
coordinator-driven workflow actually runs here.

Use this once, right after installing the agent-workspace plugin into a project that is NOT the
framework repo itself.

## Responsible agent

coordinator

## Behavior

```text
1. Resolve the framework root:
   - plugin install  -> ${CLAUDE_PLUGIN_ROOT}
   - inside the repo  -> repo root (already scaffolded; this command is a no-op there)
2. Run: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/aw-init.py --from ${CLAUDE_PLUGIN_ROOT} --to .
3. The script copies .agent/, seeds .runtime/ from templates, copies CLAUDE.md.
4. It NEVER overwrites existing files unless --force; it reports what it skipped.
5. After scaffolding, route to /onboard (or /coord) to build the project brain.
```

Run a dry run first when unsure:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/aw-init.py" --from "${CLAUDE_PLUGIN_ROOT}" --to . --dry-run
```

## Must not

```text
Do not scaffold into the framework repo itself (the script refuses when --from == --to).
Do not overwrite an existing .agent/ or CLAUDE.md without explicit user approval (--force).
Do not mutate the user's application source under services/<service-name>/.
```

## Required rules

```text
00-core-rules.md
11-approval-gates.md
13-security-secret-rules.md
```

## Next

After `/aw-init`, the project has `.agent/workflow.md`, `.runtime/` state, and `CLAUDE.md`. Run
`/onboard` to scan inputs/services and build the brain, then drive work through `/coord`.
