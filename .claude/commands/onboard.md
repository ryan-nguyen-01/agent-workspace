# /onboard

## Purpose

Create or refresh Project Brain and service coding contracts.

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
1. Read .runtime/context/index.yaml if it exists.
2. Scan project structure.
3. Detect repository type, stack, services, modules, shared code, APIs, DB, CI, environments, and test policy.
4. Write .runtime/context/project-brain.yaml.
5. Write .runtime/context/service-catalog.yaml.
6. Write .runtime/context/test-policy.yaml.
7. Write .runtime/context/services/<service>.yaml.
8. Refresh .runtime/context/index.yaml.
9. Produce agent candidates requiring approval.
10. Return to Coordinator for create-coders approval.
```

## Usage

```text
/onboard
  Initial fetch for the current repository. Scans inputs/ AND source code.

/onboard ../service-a
  Initial fetch for a sibling service project.

/onboard --refresh <service-id-or-path>
  Partial refresh after service structure, stack, API, schema, or test policy changes.
  Does not rescan inputs/.

/onboard --refresh inputs
  Partial refresh of user-provided reference docs only.
  Equivalent to /sync-memory --scan --inputs. Does not touch services/.

/onboard --files <paths> [--services <service-ids>]
  Targeted onboarding refresh. Read only specified files/folders and update matching memory/service docs.
  --services optional when all paths are under inputs/.
```

### Picking the right command after a change

```text
What changed                          | Command
--------------------------------------|---------------------------------------------
First time setup                      | /onboard
Added a PRD/HLD/spec file in inputs/  | /sync-memory --files inputs/<path>
Added many files / new inputs subdir  | /onboard --refresh inputs
                                      |   (alias: /sync-memory --scan --inputs)
One service's code/API changed        | /onboard --refresh <service>
Stack / boundaries / multi-service    | /onboard         (full)
Manual edits to memory yaml           | /sync-memory --refresh-index
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
5. Write structured data into .runtime/context/project-brain.yaml and service brain files.
6. Write human-readable indexes into .runtime/context/common/generics.md, .runtime/context/conventions.md, and .runtime/context/architecture.md.
7. Update .runtime/context/service-catalog.yaml with explicit service.path and allowed write boundary candidates.

Stop or mark partial when evidence is insufficient. Do not invent conventions.
