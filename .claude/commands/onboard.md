# /onboard

## Purpose

Create or refresh Project Brain.

## Responsible agent

onboarding

## Required rules

```text
00-core-rules.md
01-project-brain-rules.md
02-onboarding-rules.md
13-security-secret-rules.md
```

## Workflow

```text
1. Scan project structure.
2. Detect repository type, stack, services, modules, shared code, APIs, DB, CI, environments, and test policy.
3. Write project-brain.yaml.
4. Write service-catalog.yaml.
5. Write test-policy.yaml.
6. Write services/<service>.yaml.
7. Produce agent candidates requiring approval.
8. Return to Coordinator for create-coders approval.
```

## Must not

```text
Do not modify source code.
Do not create active coder agents.
Do not store secrets.
```

## Deep scan requirements

In addition to service and stack detection, /onboard must build deep project intelligence:

1. Detect reusable assets and where they are used.
2. Detect coding conventions and flow patterns from repeated evidence.
3. Detect business and technical flows from entrypoints, service calls, events, jobs, and integrations.
4. Detect anti-patterns and existing safer alternatives.
5. Write structured data into project-brain.yaml and service brain files.
6. Write human-readable indexes into common/generics.md, conventions.md, and architecture.md.

Stop or mark partial when evidence is insufficient. Do not invent conventions.
