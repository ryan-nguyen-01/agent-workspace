# Maestro

**Maestro** is a coordinator-driven multi-agent delivery framework — a "software company of agents"
you apply to a project by **copying a template**. Open this repo and you see exactly three things:

```text
maestro/
├── templates/    ← pick one, copy it, build (the products)
├── platform/     ← the framework source (read & maintain here)
└── workspace/    ← your local working area (gitignored)
```

## Pick a template

| Template | Use it when you want to… | Methodology | Skills |
|----------|--------------------------|-------------|--------|
| [`templates/sdlc`](templates/sdlc/) | Build software end-to-end (web/mobile/API): BA → design → UI/UX prototype → code → real-user QC | spec-driven-development | 231 |
| [`templates/adlc`](templates/adlc/) | Build AI products/agents with an **eval gate** before done | eval-driven-ai | 132 |
| [`templates/enterprise`](templates/enterprise/) | Operate governed/production agents: compliance, audit, accountability | enterprise-agent-governance | 166 |
| [`templates/lite`](templates/lite/) | Ship a small tool/prototype fast with minimal ceremony | risk-based-routing | 39 |
| [`templates/brownfield`](templates/brownfield/) | Maintain an EXISTING project: onboard deeply, execute precisely, **ask-don't-infer** | risk-based-routing | 231 |

Each template is **self-contained** (own `CLAUDE.md`, `.claude/`, `.codex/`, `.maestro/`) with a strict
behavior profile and a right-sized folder structure. Ask it "who are you" — it answers as that Maestro
variant operating your project.

## Apply a template

```bash
# Greenfield — start a project FROM a template:
cp -R maestro/templates/sdlc my-app && cd my-app && claude     # or codex

# Existing project — apply brownfield INTO your repo:
cd my-existing-app
cp -R /path/to/maestro/templates/brownfield/.maestro .
cp -R /path/to/maestro/templates/brownfield/.claude .          # skip if you keep your own .claude
cp    /path/to/maestro/templates/brownfield/CLAUDE.md .        # already have CLAUDE.md? add one line:
                                                               #   @.maestro/INSTRUCTIONS.md
claude   # then: /onboard
```

Details and the template build system: [platform/variants/README.md](platform/variants/README.md).

## The platform (framework source)

[`platform/`](platform/) is the full framework workspace: engine (workflow, 23 rules, 59 templates),
34 agents, 231 skills, commands, hooks, and the generator that builds `templates/`. Maintain the
framework by opening a harness inside `platform/` — see [platform/README.md](platform/README.md).

```bash
cd platform && python3 scripts/build-variant.py --all   # rebuild all templates after platform changes
```

## License

MIT — see [LICENSE](LICENSE).
