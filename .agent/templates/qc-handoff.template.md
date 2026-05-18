# QC Handoff: {{TASK_ID}}

## Summary

{{SUMMARY}}

## Scope

{{SCOPE}}

## Out Of Scope

{{OUT_OF_SCOPE}}

## Changed Areas

```yaml
services: []
files: []
apis: []
events: []
schemas: []
ui: []
config: []
```

## Acceptance Criteria

{{ACCEPTANCE_CRITERIA}}

## Dev Verification Result

```yaml
result: {{DEV_VERIFICATION_RESULT}}
score: {{DEV_VERIFICATION_SCORE}}
critical_checks: {{CRITICAL_CHECK_STATUS}}
manual_verification: {{MANUAL_VERIFICATION_SUMMARY}}
tests: {{TEST_SUMMARY}}
```

## Suggested QC Test Cases

1. {{QC_CASE_1}}

## Test Data Notes

{{TEST_DATA_NOTES}}

## Environment Notes

{{ENVIRONMENT_NOTES}}

## Known Risks

{{KNOWN_RISKS}}

## Blocking Conditions For QC

QC must stop immediately if:

```text
Main happy path cannot continue
Core API/app crashes
Auth/security is broken
Data corruption risk appears
Required test setup is blocked
```

## Retest Scope

{{RETEST_SCOPE}}
