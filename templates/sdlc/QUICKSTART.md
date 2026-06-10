# Quickstart

Use `maestro` as the stable root for one product. The root name does not change; product
identity and component naming come from `.maestro/project.yaml`.

## 1. Create The Workspace


```bash
git clone <repo-url> maestro
cd maestro

# Existing project alternative:
  --project-key nova --project-name "Nova"
```

Initialization preserves existing `CLAUDE.md`, `AGENTS.md`, `.claude/`, and source files. It appends a
managed instruction block and keeps runtime/session state local.

## 2. Configure Product Identity

Set `.maestro/project.yaml`:

```yaml
product:
  id: "nova"
  key: "nova"
  display_name: "Nova"
  status: "configured"

naming:
  component_namespace: "nova"
```

## 3. Add Product Components

Create or mount components under the appropriate root:

```text
apps/nova-web-app/
services/nova-auth-service/
services/nova-billing-service/
packages/nova-design-system/
infra/nova-platform/
tests/nova-system-tests/
```

Register every component in `.maestro/registry/components.yaml`. Components may be folders in one
monorepo or independent repositories.

## 4. Add Product Documentation

Official artifacts live under `docs/`:

```text
docs/product/prds/
docs/requirements/features/
docs/requirements/user-stories/
docs/experience/user-flows/
docs/experience/ui-specifications/
docs/architecture/high-level-design/
docs/architecture/low-level-design/
docs/architecture/decisions/
docs/quality/
docs/operations/runbooks/
```

Put external or uncurated references under `inputs/`; onboarding distills relevant facts into
`.maestro/knowledge/`.

## 5. Choose Execution Depth

Start through Coordinator:

```text
/coord <request>
```

- `direct`: fast, low-risk work; user may own verification when agent access is limited.
- `assisted`: resumable work with task, progress, verification, and continuation memory.
- `governed`: high-risk or cross-component work with decomposition, analysis, approvals, and QC.

Large work is decomposed as `Initiative -> Epic -> Task -> Subtask`. When a conversation becomes too
long, the agent writes a checkpoint and continuation handoff before starting a new session.

## 6. Verify The Workspace

```bash
python3 scripts/build-skill-catalog.py --check
python3 scripts/status-dashboard.py --mode dashboard
python3 scripts/architecture-health-check.py --strict
```
