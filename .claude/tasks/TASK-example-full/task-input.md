# TASK-example-full — Ví dụ workflow đầy đủ multi-service

## Mô tả

Đây là task mẫu minh họa **workflow đầy đủ end-to-end** với multi-service coordination.
Bao gồm tất cả artifacts từ task-input đến memory-updates.

> Xem [workflow-narrative.md](workflow-narrative.md) để hiểu luồng hoạt động chi tiết.

## User Request (ví dụ)

> "Thêm JWT authentication cho hệ thống: API backend cần verify token, frontend cần gửi token trong header, và thêm endpoint login/register."

## Scope

- **Backend API**: Thêm auth middleware, login/register endpoints, JWT token generation
- **Frontend**: Thêm auth context, login page, token management trong HTTP client
- **Database**: Thêm bảng users với password hash

## Ghi chú

- Task này là **template tham khảo**, không phải task thật
- Minh họa multi-service coordination (API + Frontend + Database)
- Mỗi file trong folder tương ứng với 1 artifact trong workflow
- Xem [workflow-narrative.md](workflow-narrative.md) cho mô tả luồng chạy step-by-step
