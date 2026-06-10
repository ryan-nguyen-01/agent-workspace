# R-013: Security and Secret Rules

## Applies to

All agents and commands.

## Rules

```text
R-013-01: Never write real secrets to .maestro/runtime artifacts or tool adapter files.
R-013-02: Never store passwords, raw tokens, private keys, API keys, or session cookies.
R-013-03: Do not paste long logs containing possible PII or credentials.
R-013-04: Redact sensitive values before writing bug, QC, memory, or handoff artifacts.
R-013-05: Auth, permission, token, password, PII, payment, or encryption tasks require explicit critical checks.
R-013-06: Security-sensitive blocker bugs stop QC.
R-013-07: Generated coders must not change auth/security behavior without Coder Leader and critical check coverage.
```

## Required evidence

```text
Security-sensitive tasks must list critical checks in task-analysis.yaml and dev-verification.yaml.
```

## Violation handling

Stop, redact, and route to Coordinator or Workflow Policy.
