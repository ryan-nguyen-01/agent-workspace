# QC Delivery Report: {{TASK_ID}}

## Summary

{{SUMMARY}}

## QC results

- **Status**: {{QC_STATUS}} (QC_DONE | BLOCKED_BY_BUG)
- **Test cases**: {{TOTAL_TESTS}} total, {{PASSED}} pass, {{FAILED}} fail, {{BLOCKED}} blocked
- **Blocker bugs**: {{BLOCKER_COUNT}}
- **Non-blocker bugs**: {{NON_BLOCKER_COUNT}}

## What was completed

{{COMPLETED_FEATURES}}

## Files changed

```yaml
services: []
files_changed: []
```

## Test Results Summary

| Category     | Tests     | Pass     | Fail     | Notes     |
| ------------ | --------- | -------- | -------- | --------- |
| {{CATEGORY}} | {{COUNT}} | {{PASS}} | {{FAIL}} | {{NOTES}} |

## Known Limitations

{{KNOWN_LIMITATIONS}}

## Open bugs (if any)

### Blockers

{{BLOCKERS_OR_NONE}}

### Non-blockers

{{NON_BLOCKERS_OR_NONE}}

## Verification guide for the User

{{USER_VERIFY_STEPS}}

## Postman Collection

{{POSTMAN_COLLECTION_NOTE}}

<!-- If the API changed: -->
<!-- File: .maestro/work/tasks/{{TASK_ID}}/postman-collection.json -->
<!-- How to use: -->
<!--   1. Open Postman → Import → choose postman-collection.json -->
<!--   2. Create an environment, set BASE_URL = http://localhost:<port> -->
<!--   3. Set AUTH_TOKEN if the endpoint needs auth -->
<!--   4. Run each request, or use the Collection Runner to run all -->

## Next steps

{{NEXT_STEPS}}
