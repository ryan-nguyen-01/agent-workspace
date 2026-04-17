# `.claude` Changelog

## Dynamic agent architecture installed

Replaced static agent and technology skill set with a project-aware workflow:

```text
Coordinator
Onboarding
Agent Factory
Task Analysis
Coder Leader
Generated Service Coders
Dev Verification
QC Handoff
QC Runner
Bug Router
Memory Update
Workflow Policy
```

Project brain now starts in `NEED_ONBOARDING` state.

## Skill registry hardening

Implemented review fixes without running project onboarding:

```text
settings.json and settings.local.json are now valid JSON objects.
workflow.md duplicate skill-composition section removed.
rules/README.md rule 14 formatting fixed.
context/skill-registry.yaml added as machine-readable skill selection source of truth.
Agent Factory and /create-coders now use skill-registry.yaml before external-skills.md.
High-risk and failed external skills are represented as explicit registry gates.
```

## Deep onboarding and reuse enforcement

Added deeper onboarding support without scanning the real project:

- project-brain.yaml now has deep_project_intelligence placeholder sections.
- project-brain and service-brain templates now include reusable assets, coding flow, business flows, reuse rules, anti-patterns, evidence, and confidence fields.
- task-analysis template now includes reuse_and_convention_analysis.
- dev-verification template now includes reuse_and_convention_check.
- memory-update template now includes reuse_and_convention_memory_updates.
- Onboarding, Task Analysis, Coder Leader, Service Coder, Dev Verification, and Memory Update instructions now enforce reuse-before-create behavior.
- Added docs/deep-onboarding.md as the human-readable standard.
