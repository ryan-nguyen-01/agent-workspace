# Guidelines

## Core Model

```text
.maestro/        Product-development control plane
.claude/    Native Claude tool layer
docs/       Official product and engineering documentation
apps/       User-facing applications
services/   Deployable services, workers, and gateways
packages/   Shared libraries, contracts, and design system
infra/      Infrastructure and delivery platform
tests/      Cross-component and system test suites
inputs/     External references awaiting curation
```

The root remains `maestro`. Configure product identity and namespace in `.maestro/project.yaml`.

## `.maestro` Domains

| Domain | Purpose | Git policy |
| --- | --- | --- |
| `engine/` | Workflow, rules, templates, internal framework docs | Shared |
| `config/` | Model routing and response behavior | Shared |
| `registry/` | Component, agent, skill, input, and artifact addresses | Shared |
| `knowledge/` | Durable product and component facts | Shared |
| `work/` | Initiative, epic, task, subtask, bug, verification evidence | Shared |
| `design/` | Design artifact index and relationships | Shared |
| `decision/` | ADR index and lifecycle | Shared |
| `memory/project/` | Reusable patterns and feedback | Shared |
| `memory/tasks/` | Task summaries and continuation handoffs | Shared |
| `memory/sessions/` | Short-term conversation memory | Local |
| `history/` | Timeline and auditable events | Shared |
| `runtime/` | Active state, telemetry, cache, locks, reports | Local |

Agents read `.maestro/INSTRUCTIONS.md`, then the relevant registry/index. They do not scan every skill,
component, document, or memory file.

## Execution Modes

### Direct

Use for low-risk, fast development. Persistent task artifacts are optional. The response must state
what was not verified and list exact user checks when the agent cannot access the environment or data.

### Assisted

Use when work may span conversations or needs lightweight traceability. Required baseline:

```text
task.yaml
progress.yaml
verification.yaml
.maestro/memory/tasks/<task-id>/handoff.md when the conversation is split
```

### Governed

Use for security, privacy, data migration, public contracts, infrastructure/production changes,
cross-component work, or parallel workstreams. It uses the full analysis, planning, implementation,
verification, QC, and memory pipeline.

## Work Decomposition

```text
Initiative -> Epic -> Task -> Subtask
```

Decompose before implementation when work spans sessions, has independent acceptance criteria,
combines design and implementation, affects multiple components, requires rollout/migration, or can
run in parallel. Do not nest subtasks; promote a complex subtask to a task.

## Documentation And Design

Official content belongs in `docs/`; `.maestro/registry/artifacts.yaml` indexes it.

- PRD: `docs/product/prds/`
- Features and user stories: `docs/requirements/`
- User journeys, flows, wireframes, UI specs: `docs/experience/`
- HLD, LLD, ADR: `docs/architecture/`
- Quality, delivery, operations, governance: matching `docs/` domains
- Methodology playbooks: `docs/governance/methodologies/`
- Shared design tokens/components: `packages/<project>-design-system/`

Do not duplicate authoritative document bodies under `.maestro/`.

## Naming

Use kebab-case and business capabilities:

```text
<project>-<channel>-app
<project>-<capability>-service
<project>-<capability>-worker
<project>-<scope>-gateway
<project>-<capability>
<project>-design-system
```

Avoid generic names such as `backend`, `common`, `utils`, `core-service`, or `service-1`.

## Skills

`.maestro/registry/skills.yaml` is the canonical address book for all installed skills. Each catalog entry
contains its `path`, `category`, and `capability`; hand-maintained policy overrides add risk and
approval metadata. Agents select candidates there before opening any `SKILL.md`.

Regenerate and verify:

```bash
python3 scripts/build-skill-catalog.py --no-inject
python3 scripts/build-skill-catalog.py --check
```

## Memory Continuity

Before splitting a long conversation, write:

```text
.maestro/work/tasks/<task-id>/checkpoints/<checkpoint-id>.yaml
.maestro/memory/tasks/<task-id>/handoff.md
```

The next session resumes from task manifest, handoff, checkpoint, and bounded references. Accepted
decisions and resolved questions are not asked again unless new contradictory evidence appears.

## Verification

Verification ownership is `agent`, `user`, or `shared`. Missing agent access must be recorded, never
invented. Keep environment-specific pending checks in `verification.yaml`.

## Maintenance

After changing commands, skills, plugin wrappers, paths, or counts:

```bash
python3 scripts/build-plugin.py
python3 scripts/build-codex-prompts.py
python3 scripts/build-codex-plugin.py
python3 scripts/build-skill-catalog.py --check
python3 scripts/architecture-health-check.py --strict
```

Current distribution: 12 workflow agents, 19 specialist advisors, 3 built-in coders, 166 skills,
23 rules, 59 templates, and 19 commands.
