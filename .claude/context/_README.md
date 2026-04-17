# Project Brain

This directory is the reusable memory for `.claude` agents.

## Required files

```text
project-brain.yaml       Project-level summary, policies, freshness
service-catalog.yaml     Services/modules detected by onboarding
agent-registry.yaml      Generated coder agents and scopes
test-policy.yaml         Unit/manual verification policy per service
workflow-state.yaml      State machine and approval gates
skill-registry.yaml      Machine-readable skill selection registry
services/<service>.yaml  Per-service brain
```

Do not store secrets, passwords, raw tokens, or long logs here.
