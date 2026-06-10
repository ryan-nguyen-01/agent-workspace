# Variant Bundles

This folder defines the **purpose-specific template bundles** generated from the maestro platform.
Each bundle is a standalone framework folder (own `CLAUDE.md`, `.claude/`, `.maestro/`) with a tighter
behavior profile, a default methodology, and a purpose-fit skill subset — so opening a harness inside
a bundle gives a focused context instead of one mega-config serving every purpose.

## Bundles

| Manifest | Output | Purpose | Methodology default | Skills |
|----------|--------|---------|---------------------|--------|
| `sdlc.yaml` | `../maestro-sdlc` | Classic software delivery (web/mobile/API), full BA → design → UI/UX → code → QC | spec-driven-development | all |
| `adlc.yaml` | `../maestro-adlc` | AI development lifecycle: AI products/agents with an eval gate | eval-driven-ai | workflow + data-ai + backend + database + testing + meta + patches |
| `enterprise.yaml` | `../maestro-enterprise` | Agentic Enterprise: governance, compliance, audit, production agents | enterprise-agent-governance | + security + devops-cloud |
| `lite.yaml` | `../maestro-lite` | Small tools/prototypes: direct mode, mini-brief instead of full blueprint | risk-based-routing | minimal (~39) |
| `brownfield.yaml` | `../maestro-brownfield` | EXISTING project maintenance: onboard deeply, execute tasks precisely, **ask-don't-infer** | risk-based-routing | all (stack unknown upfront) |

## Build

```bash
python3 scripts/build-variant.py sdlc      # one bundle
python3 scripts/build-variant.py --all     # all bundles
```

The build copies the platform, prunes skills to the manifest's category/include/exclude selection,
prunes the skill registry to match, patches identity (project.yaml), default methodology, and the
variant profile into `CLAUDE.md`, regenerates derived artifacts (skill taxonomy/catalog, plugin
wrappers, codex plugin + prompts), patches health-check counts, and runs the bundle's
`architecture-health-check.py --strict`.

## Rules

```text
- Bundles are GENERATED. Never edit a bundle by hand — change the platform or the manifest, rebuild.
- Engine changes happen once in the platform; rebuild propagates them to every bundle (no drift).
- A bundle is self-contained: open the harness in its folder, or run its scripts/maestro-init.py to
  install that variant into a project.
- The manifest's `profile:` block is inserted near the top of the bundle's CLAUDE.md — it is the
  behavioral identity of the variant (e.g. brownfield's ask-don't-infer contract).
```
