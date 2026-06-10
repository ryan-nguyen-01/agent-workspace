# Product Documentation

`docs/` contains the official product artifacts read by users and agents. `.maestro/registry/artifacts.yaml`
is the routing index; `.maestro/` must not duplicate the authoritative document body.

Traceability flows from product intent to operations:

```text
Methodology -> Vision -> PRD -> Feature -> User Story / Use Case -> User Flow
       -> HLD / LLD / ADR -> Epic -> Task -> Code -> Test Evidence
       -> Release -> Runbook / Observability
```

Methodology playbooks live under `docs/governance/methodologies/`. They define when the workspace
should run fast, when it should become document-led, and when enterprise governance is required.
`docs/governance/methodologies/industry-alignment.md` maps those local playbooks to current
production-agent patterns such as durable workflows, human-in-the-loop, eval-driven AI, artifacts,
plugins, hooks, and enterprise autonomy.
