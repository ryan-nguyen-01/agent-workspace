# /maestro-init

## Purpose

Scaffold the maestro **full flow** into the current project. A plugin install only delivers
the tool layer (agents, skills, commands, hooks); this command adds the `.maestro/` product control plane,
official documentation roots, product component roots, and a managed `CLAUDE.md` import so the
coordinator-driven workflow actually runs here.

Use this once, right after installing the maestro plugin into a project that is NOT the
framework repo itself.

## Responsible agent

coordinator

## Behavior

```text
1. Resolve the framework root:
   - plugin install  -> ${CLAUDE_PLUGIN_ROOT}
   - inside the repo  -> repo root (already scaffolded; this command is a no-op there)
2. Run: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/maestro-init.py --from ${CLAUDE_PLUGIN_ROOT} --to .
3. The script creates the `.maestro/` domains, seeds local runtime from templates, and appends one
   idempotent `@.maestro/INSTRUCTIONS.md` import block to CLAUDE.md.
4. It preserves existing CLAUDE.md and AGENTS.md content and appends managed, idempotent entrypoint
   blocks to both files.
5. Shared project files are not overwritten unless --force. `--sync` refreshes framework-owned
   engine files only and uses `.maestro/runtime/cache/sync.json` SHA-256 hashes to stop before replacing
   a locally edited framework file.
6. After scaffolding, route to /onboard (or /coord) to build the project brain.
```

Run a dry run first when unsure:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/maestro-init.py" --from "${CLAUDE_PLUGIN_ROOT}" --to . --dry-run
```

## Must not

```text
Do not initialize the framework repo into itself; use --attach or --sync there.
Do not replace user-owned CLAUDE.md or AGENTS.md content.
Do not mutate user source under apps/, services/, packages/, infra/, or tests/.
```

## Required rules

```text
00-core-rules.md
11-approval-gates.md
13-security-secret-rules.md
```

## Next

After `/maestro-init`, the project has `.maestro/INSTRUCTIONS.md`, the full `.maestro/` control plane, component and
documentation roots, local runtime state, and a managed instruction block in `CLAUDE.md`. Run
`/onboard` to scan inputs and registered product components, then drive work through `/coord`.
