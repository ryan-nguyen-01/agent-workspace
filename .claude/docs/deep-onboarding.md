# Deep Onboarding Standard

![Deep onboarding](diagrams/07-deep-onboarding.svg)

Deep onboarding extracts project-specific reusable knowledge. Its goal is to prevent generated coder agents from writing code that ignores existing helpers, conventions, and business flow.

## Purpose

Deep onboarding must answer these questions before coder agents are generated:

- What reusable assets already exist?
- What coding flow does this project follow?
- What business and technical flows already exist?
- What helper or abstraction should coders reuse instead of recreating?
- What project-specific anti-patterns should coders avoid?
- Which facts are proven by evidence, and which are only low-confidence inference?

## Required scan categories

Reusable assets:

- Utilities
- Shared components
- Base classes
- Hooks
- Middleware
- Validators
- Mappers and serializers
- API clients
- Repository abstractions
- Error handling helpers
- Logging helpers
- Auth helpers
- Database transaction helpers
- Event and queue helpers
- Payment helpers
- Notification helpers
- Test helpers

Coding flow:

- Request lifecycle
- Command or use-case lifecycle
- Data access flow
- Transaction flow
- Event publish flow
- Event consume flow
- Error handling flow
- Logging flow
- Migration flow
- Configuration flow
- Test flow

Business and technical flows:

- Auth
- User onboarding
- Payment
- Notification
- Order or checkout
- Admin operations
- Background jobs
- Data sync
- Event-driven producer and consumer flow
- External integration flow

## Evidence standard

Every discovered item must include:

- Name
- Path
- Purpose
- When to reuse
- Used by or related services
- Evidence paths
- Confidence: low, medium, or high

Do not store large source snippets. Store references and summaries only.

## Outputs

Structured outputs:

- project-brain.yaml under deep_project_intelligence
- services/<service>.yaml under service_deep_intelligence
- task-analysis.yaml under reuse_and_convention_analysis
- dev-verification.yaml under reuse_and_convention_check
- memory-updates.yaml under reuse_and_convention_memory_updates

Human-readable outputs:

- context/common/generics.md
- context/conventions.md
- context/architecture.md

## Coder enforcement

Generated service coders must check reusable assets and conventions before implementation.

Coder result must include:

- reusable_assets_used
- conventions_followed
- anti_patterns_avoided
- new_reusable_assets_created
- reason_existing_assets_were_not_used, when applicable

If a coder needs to create or modify shared reusable assets outside its allowed write scope, it must stop and ask Coder Leader.

## Quality gate

Dev Verification must block or request fixes when:

- Known reusable assets were ignored without reason.
- New helper code duplicates existing reusable assets.
- Shared assets were changed outside approved scope.
- Project conventions were violated.
- Anti-patterns were introduced.

## Related

- [visual-flow.md](visual-flow.md) — All workflow diagrams including deep onboarding
- [skill-composition.md](skill-composition.md) — How skills are attached to coder agents after onboarding
- [folder-guide.md](folder-guide.md) — Full `.claude` folder reference
