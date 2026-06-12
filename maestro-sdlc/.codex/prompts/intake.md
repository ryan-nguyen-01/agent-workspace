---
description: "maestro /intake — Triage whatever the user dropped into the intake folders (`docs/`, `inputs/` where present) so messy input never sile..."
argument-hint: "[request or args]"
---

You are running the maestro `/intake` workflow command inside Codex.

Follow `.codex/AGENTS.md` (or `AGENTS.md`) routing and the framework rules. Route every
request through the coordinator model; do not bypass approval gates, security/secret rules,
or the task-analysis source-edit gate. If the maestro framework files
(`.maestro/engine/`, `.maestro/registry/`, `.maestro/knowledge/`, `.maestro/work/`, `.maestro/runtime/`, `.claude/commands/intake.md`) are present, defer to them as the
authoritative contract — this prompt is a portable mirror.

User input for this command: $ARGUMENTS

---
## Command contract (mirrored from .claude/commands/intake.md)

# /intake

## Purpose

Triage whatever the user dropped into the intake folders (`docs/`, `inputs/` where present) so messy
input never silently poisons the workspace. Users WILL dump anything there — specs, screenshots, bug
reports, error logs, SQL dumps, archives, `.env` files, even whole source trees. Intake classifies
everything, flags risks, and proposes placement — **without moving or editing a single user file
until the user confirms**.

## Responsible agent

onboarding (invoked by coordinator; also runs automatically as the first step of /onboard)

## Behavior

```text
1. Scan intake folders (docs/, inputs/) recursively. For each item classify:
   type: spec | requirement | bug-report | error-log | design | data-dump | source-code | archive | secret-risk | unknown
2. Write the index (non-destructive — files are NEVER moved/renamed/edited without approval):
   docs/INDEX.md           human view: file -> type -> related component -> status -> flags
   .maestro/registry/inputs.yaml   machine view for onboarding/task-analysis to consume
3. FLAGS (each requires a user decision, never silent handling):
   - secret-risk: file matches secret/credential/PII patterns (.env, dumps with passwords/tokens).
     -> WARN immediately, do not quote contents into any artifact, recommend removal/redaction (R-013).
   - misplaced-source: looks like application source dropped into docs/.
     -> ask: "this looks like code for <X> — should it live in services/<X>? move or keep?"
   - conflicting-doc: contradicts the CODE or a newer doc -> mark stale-candidate; code is the runtime
     truth (R-018) — confirm with the user before trusting the doc.
   - unreadable/archive: zips/binaries -> list, ask whether to extract.
4. Connect: link triaged items to components (registry) and to open tasks (purpose_ref) when obvious;
   leave status: needs_user otherwise.
5. Report: counts per type, all flags with the exact question per flag, and what onboarding will use.
```

Docs that live INSIDE a service folder are fine — they are indexed as component docs, never demanded
to move (task fidelity: never restructure the user's repo uninvited).

## Required rules

```text
00-core-rules.md
02-onboarding-rules.md
13-security-secret-rules.md
18-doc-precedence-rules.md
24-purpose-chain-rules.md
```

## Stop conditions

```text
Secret/PII material found (report + user decision; never propagate contents)
Any move/rename/extract of user files (explicit approval per item)
```

## Output format

```text
✅ Intake: <n> items triaged (<spec/bug/log/...> counts)
⚠️ Flags: <k> — each with the question the user must answer
📁 Index: docs/INDEX.md + .maestro/registry/inputs.yaml
🔜 Next: answer flags -> /onboard consumes the triaged evidence
```
