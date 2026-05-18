# Architecture Memory

Status: needs onboarding.

This file may contain human-readable architecture notes. Structured architecture memory belongs in `.runtime/context/project-brain.yaml` and `.runtime/context/services/<service>.yaml`.

## Business and technical flow memory

Onboarding should identify recurring project flows and keep them here in human-readable form.

```yaml
business_flows:
  - id: ""
    name: ""
    trigger: ""
    entrypoints: []
    services: []
    steps: []
    data_entities: []
    external_integrations: []
    events_emitted: []
    events_consumed: []
    reusable_assets: []
    critical_checks: []
    evidence: []
    confidence: "low|medium|high"
```
