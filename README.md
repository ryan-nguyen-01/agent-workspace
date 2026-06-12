# Maestro

**Maestro** is a coordinator-driven multi-agent delivery framework. The `maestro-*` folders below are
**ready-to-copy workspaces**: copy one anywhere, put your source code inside, run `claude` (or `codex`)
in it — the agent follows that template's workflow, gates, and identity.

## Pick a template

| Folder | Use it when you want to… | Methodology | Skills |
| --- | --- | --- | --- |
| [`maestro-sdlc/`](maestro-sdlc/) | Build software end-to-end: BA → design → UI/UX prototype → code → real-user QC | spec-driven-development | 231 |
| [`maestro-adlc/`](maestro-adlc/) | Build AI products/agents with an **eval gate** before done | eval-driven-ai | 132 |
| [`maestro-enterprise/`](maestro-enterprise/) | Operate governed/production agents: compliance, audit, accountability | enterprise-agent-governance | 166 |
| [`maestro-lite/`](maestro-lite/) | Ship a small tool/prototype fast, minimal ceremony (no specialist advisors) | risk-based-routing | 39 |
| [`maestro-brownfield/`](maestro-brownfield/) | Maintain an EXISTING project: deep onboarding, precise tasks, **ask-don't-infer** | risk-based-routing | 231 |

## Use it

```bash
cp -R maestro/maestro-adlc ~/work/my-ai-app    # copy the template anywhere
cd ~/work/my-ai-app                             # move your service code into services/ or apps/
claude                                          # /coord to start · /ship for autonomous build-to-done
```

Each template is self-contained and standardized: entry points (`CLAUDE.md`, `AGENTS.md`,
`COMMAND.md`), the `.maestro/` workflow brain, a purpose-fit agent/skill set, and folders for your
code and working artifacts. Ask the agent "who are you" — it answers as that Maestro variant
operating your project.

## Platform (framework source)

[`platform/`](platform/) holds the framework source and the generator. Maintain Maestro there:

```bash
cd platform && python3 scripts/build-variant.py --all   # rebuild all maestro-* templates
```

Template manifests and the build contract: [platform/variants/README.md](platform/variants/README.md).

## License

MIT — see [LICENSE](LICENSE).
