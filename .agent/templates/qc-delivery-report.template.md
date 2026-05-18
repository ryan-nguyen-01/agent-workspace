# QC Delivery Report: {{TASK_ID}}

## Tóm tắt

{{SUMMARY}}

## Kết quả QC

- **Trạng thái**: {{QC_STATUS}} (QC_DONE | BLOCKED_BY_BUG)
- **Test cases**: {{TOTAL_TESTS}} total, {{PASSED}} pass, {{FAILED}} fail, {{BLOCKED}} blocked
- **Blocker bugs**: {{BLOCKER_COUNT}}
- **Non-blocker bugs**: {{NON_BLOCKER_COUNT}}

## Những gì đã hoàn thành

{{COMPLETED_FEATURES}}

## Files thay đổi

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

## Bugs mở (nếu có)

### Blockers

{{BLOCKERS_OR_NONE}}

### Non-blockers

{{NON_BLOCKERS_OR_NONE}}

## Hướng dẫn verify cho User

{{USER_VERIFY_STEPS}}

## Postman Collection

{{POSTMAN_COLLECTION_NOTE}}

<!-- Nếu có API thay đổi: -->
<!-- File: .runtime/tasks/{{TASK_ID}}/postman-collection.json -->
<!-- Cách dùng: -->
<!--   1. Mở Postman → Import → chọn file postman-collection.json -->
<!--   2. Tạo environment, set BASE_URL = http://localhost:<port> -->
<!--   3. Set AUTH_TOKEN nếu endpoint cần auth -->
<!--   4. Chạy từng request hoặc dùng Collection Runner để chạy toàn bộ -->

## Đề xuất tiếp theo

{{NEXT_STEPS}}
