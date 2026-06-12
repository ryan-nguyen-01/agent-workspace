# Variant Templates

Maestro ships **purpose-specific templates** as `maestro-*` folders at the repo root. Each template is a
self-contained framework folder (own `CLAUDE.md`, `.claude/`, `.codex/`, `.maestro/`) with a strict
behavior profile, a default methodology, a purpose-fit skill subset, and a **right-sized folder
structure** — no enterprise scaffolding in a small-tool template, no greenfield scaffolding in a
maintenance template.

## Templates

| Template | Purpose | Methodology | Skills | Structure |
|----------|---------|-------------|--------|-----------|
| `maestro-sdlc/` | Classic software delivery (web/mobile/API): BA → design → UI/UX → code → QC | spec-driven-development | 231 | full delivery scaffolding (no enterprise governance) |
| `maestro-adlc/` | AI products/agents with an eval gate before done | eval-driven-ai | 132 | delivery + observability/evals (no enterprise governance) |
| `maestro-enterprise/` | Agentic Enterprise: governance, compliance, audit, production agents | enterprise-agent-governance | 166 | full, including governance + audit + enterprise docs |
| `maestro-lite/` | Small tools/prototypes: direct mode, mini-brief instead of full blueprint | risk-based-routing | 39 | minimal core (no scaffolding) |
| `maestro-brownfield/` | EXISTING project maintenance: onboard deeply, execute precisely, **ask-don't-infer** | risk-based-routing | 231 | minimal core — never stamps structure onto an existing repo |

## How to use a template

```bash
# Option A — start a project FROM a template (greenfield):
cp -R maestro/maestro-sdlc my-app && cd my-app && claude     # or codex

# Option B (brownfield) — copy the template, then move the existing code INTO it:
cp -R maestro/maestro-brownfield ~/work/my-app-ws
#   move your project's code inside (services/, apps/ — or keep its layout and register paths in
#   .maestro/registry/components.yaml), then run claude + /onboard

# Option C — or apply the contract INTO your existing repo without moving code:
cd my-existing-app
cp -R /path/to/maestro/maestro-brownfield/.maestro .
cp -R /path/to/maestro/maestro-brownfield/.claude .            # skip if you keep your own .claude
cp    /path/to/maestro/maestro-brownfield/CLAUDE.md .          # have CLAUDE.md? add one line instead:
                                                               #   @.maestro/INSTRUCTIONS.md
claude   # then: /onboard
```

The AI identity and the variant's strict behavior contract live in both `CLAUDE.md` and
`.maestro/INSTRUCTIONS.md`, so either entry path loads them. Ask "who are you" — it must answer as
that Maestro variant operating your project.

## Build (regenerating templates)

```bash
python3 scripts/build-variant.py sdlc      # one template
python3 scripts/build-variant.py --all     # all templates
```

The build copies the platform, prunes skills (manifest `skills:` categories/include/exclude) and the
skill registry, prunes **structure groups** (manifest `structure:`; see `STRUCTURE_GROUPS` in
`scripts/build-variant.py`), patches identity/methodology/health-check, injects the variant profile
into `CLAUDE.md` + `.maestro/INSTRUCTIONS.md`, regenerates derived artifacts, and runs the template's
own `architecture-health-check.py --strict`.

## Rules

```text
- Templates are GENERATED (VARIANT.yaml marker). Never edit one by hand — change the platform or the
  manifest in variants/<name>.yaml, then rebuild. Engine changes propagate by rebuild (no drift).
- The platform root keeps the FULL structure; each template carries only the structure groups its
  manifest selects (right-sized: lite/brownfield = core only).
- The manifest's profile: block is the variant's behavioral identity (e.g. brownfield ask-don't-infer);
  it is enforced via CLAUDE.md + INSTRUCTIONS.md in the template.
```
