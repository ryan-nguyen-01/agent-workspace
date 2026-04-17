# /verify-dev

## Purpose

Evaluate whether implementation qualifies as Code Done.

## Responsible agent

dev-verification

## Required rules

```text
00-core-rules.md
07-dev-verification-rules.md
12-artifact-contracts.md
13-security-secret-rules.md
```

## Workflow

```text
1. Read task-analysis.yaml.
2. Read implementation-plan.yaml.
3. Read service-assignments.yaml.
4. Read coder-results.yaml.
5. Verify scope compliance.
6. Verify acceptance criteria mapping.
7. Verify critical checks.
8. Verify test policy compliance.
9. Calculate score.
10. Write dev-verification.yaml.
```

## Decision

```text
DEV_DONE: score >= 80%, all critical checks pass, no blocker
DEV_BLOCKED: critical failure, blocker, or missing critical evidence
NEEDS_FIX: non-critical failure below threshold
NEEDS_USER_DECISION: policy conflict or approval needed
```
