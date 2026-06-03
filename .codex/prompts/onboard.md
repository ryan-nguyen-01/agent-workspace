---
description: "agent-workspace /onboard — Create or refresh Project Brain and service coding contracts."
argument-hint: "[request or args]"
---

You are running the agent-workspace `/onboard` workflow command inside Codex.

Follow `.codex/AGENTS.md` (or `AGENTS.md`) routing and the framework rules. Route every
request through the coordinator model; do not bypass approval gates, security/secret rules,
or the task-analysis source-edit gate. If the agent-workspace framework files
(`.agent/`, `.runtime/`, `.claude/commands/onboard.md`) are present, defer to them as the
authoritative contract — this prompt is a portable mirror.

User input for this command: $ARGUMENTS

---
## Command contract (mirrored from .claude/commands/onboard.md)

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
2. Run a signature scan first: tree shape, manifests, lockfiles, service roots, API/schema/test/CI/deploy config, and inputs-index.
3. Classify project_profile archetypes and source_layout with evidence/confidence.
4. Deep-read only the smallest source/doc set needed to detect services, modules, shared code, APIs, DB, CI, environments, and test policy.
5. Write .runtime/context/project-brain.yaml including context_economy.
6. Write .runtime/context/service-catalog.yaml.
7. Write .runtime/context/test-policy.yaml.
8. Write .runtime/context/services/<service>.yaml including profile.context_hints.
9. Refresh .runtime/context/index.yaml including context_economy routing rows.
10. Produce agent candidates requiring approval.
11. Return to Coordinator for create-coders approval.
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

1. Classify project/service archetypes and source layout.
2. Detect reusable assets and where they are used.
3. Detect coding conventions and flow patterns from repeated evidence.
4. Detect business and technical flows from entrypoints, service calls, events, jobs, and integrations.
5. Detect anti-patterns and existing safer alternatives.
6. Write structured data into .runtime/context/project-brain.yaml and service brain files.
7. Write context hints so later agents avoid broad reads.
8. Write human-readable indexes into .runtime/context/common/generics.md, .runtime/context/conventions.md, and .runtime/context/architecture.md.
9. Update .runtime/context/service-catalog.yaml with explicit service.path and allowed write boundary candidates.

Stop or mark partial when evidence is insufficient. Do not invent conventions.
