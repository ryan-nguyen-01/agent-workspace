---
name: skill-dev-verification
description: Decide Code Done using critical checks, service test policy, scope compliance, and >=80% dev verification score.
---

# Skill: Dev Verification

Use after coder outputs are collected.

## Code Done formula

```text
critical_checks_passed = 100%
score = passed_applicable_checks / total_applicable_checks
code_done = score >= 0.80 and critical_checks_passed and no_open_blocker
```

## Evidence required

```text
acceptance criteria mapping
changed files and scope check
test results or manual verification notes
critical check results
known risks
handoff readiness
```

## Rules

```text
Critical failure overrides score.
Do not create test files when policy forbids them.
Report DEV_BLOCKED when evidence is missing for critical checks.
```

## Reuse and convention verification

Dev Verification must check whether coder outputs respected reusable assets and project conventions.

Check:

- Reusable assets from task-analysis.yaml were used or explicitly waived with reason.
- New helpers do not duplicate known assets from common/generics.md or service_deep_intelligence.
- Shared reusable assets were changed only inside approved scope.
- Project conventions and anti-patterns were addressed in coder-results.yaml.

If duplicate helper risk is high or shared asset scope is violated, return NEEDS_FIX or DEV_BLOCKED depending on severity.
