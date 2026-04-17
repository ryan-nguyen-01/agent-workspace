# R-002: Onboarding Rules

## Applies to

Onboarding, Coordinator, Memory Update.

## Rules

```text
R-002-01: Onboarding scans and writes memory only.
R-002-02: Onboarding must not modify application source code.
R-002-03: Onboarding must not create active coder agents.
R-002-04: Onboarding must detect repository type, services/modules, stack, dependencies, APIs, DB, CI, environment hints, and test policy.
R-002-05: Onboarding must write Project Brain, Service Catalog, Test Policy, and Service Brain files.
R-002-06: Onboarding must produce agent candidates that require user approval.
R-002-07: Onboarding must not store secrets from env or config files.
R-002-08: If test policy evidence is unclear, mark unknown and require approval before creating tests.
```

## Required artifacts

```text
.claude/context/project-brain.yaml
.claude/context/service-catalog.yaml
.claude/context/test-policy.yaml
.claude/context/services/<service>.yaml
```

## Violation handling

Reject generated coder creation until onboarding artifacts exist and are coherent.

## Deep project intelligence rules

R-002-D01: Onboarding must scan reusable assets before proposing coder agents.
R-002-D02: Onboarding must identify project-specific coding conventions from repeated evidence, not generic assumptions.
R-002-D03: Onboarding must record business and technical flows when entrypoints and service interactions provide enough evidence.
R-002-D04: Every reusable asset, convention, flow, and anti-pattern must include evidence paths and confidence.
R-002-D05: Onboarding must write deep intelligence to project-brain.yaml, service brain files, common/generics.md, conventions.md, and architecture.md where relevant.
R-002-D06: Onboarding must not paste large source files, secrets, env values, tokens, or noisy logs into memory.
R-002-D07: If deep scan is incomplete, project-brain.yaml must mark deep_project_intelligence.status as partial, not complete.
