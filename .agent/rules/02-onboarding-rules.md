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
R-002-09: Onboarding must scan inputs/ (user-provided reference docs) in addition to source code. Every fact extracted from inputs/ must cite source: "inputs/<relative-path>".
R-002-10: Onboarding must write .runtime/context/inputs-index.yaml listing every file under inputs/ with path, category, summary, mtime, and confidence.
R-002-11: When inputs/ and source code conflict on a fact, code wins for technical/current state; inputs/ wins for intent/target state. Conflict must be recorded in project-brain.yaml.conflicts[] with both sources.
R-002-12: Onboarding must not commit, modify, move, or delete files under inputs/. It is read-only there.
R-002-13: Onboarding must support three refresh granularities: full (/onboard), partial-service (--refresh <service>), partial-inputs (--refresh inputs or --scan --inputs). Prefer the smallest granularity that covers the change.
R-002-14: Partial inputs refresh must skip files whose mtime <= indexed_mtime and content hash matches, to avoid token waste. When a tracked inputs file is deleted, onboarding must remove its inputs-index row and any memory entries citing its path.
R-002-15: Partial inputs refresh must not touch service-catalog.yaml, test-policy.yaml, agent-registry.yaml, or services/<service>.yaml sections that are not contracts-related.
```

## Required artifacts

```text
.runtime/context/project-brain.yaml
.runtime/context/service-catalog.yaml
.runtime/context/test-policy.yaml
.runtime/context/services/<service>.yaml
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
