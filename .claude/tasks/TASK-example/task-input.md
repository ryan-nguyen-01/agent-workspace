# TASK-example — Demo Workflow End-to-End

## Mô tả

Đây là task mẫu minh họa workflow đầy đủ của agent-platform.
Dùng để tham khảo khi apply framework vào project khách.

## User Request (ví dụ)

> "Thêm API endpoint GET /api/users/:id trả về thông tin user từ database"

## Ghi chú

- Task này là **template tham khảo**, không phải task thật
- Mỗi file trong folder này tương ứng với 1 artifact trong workflow
- Xem flow: task-input → task-analysis → implementation-plan → service-assignments → coder-results → dev-verification → qc-handoff → qc-test-results
