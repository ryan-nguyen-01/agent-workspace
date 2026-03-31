---
name: skill-role-write-user-stories
description: Viết User Stories chuẩn Agile: format As a/I want/So that, Acceptance Criteria dạng Given/When/Then, MoSCoW prioritization, và test scenarios. Dùng khi BA cần chuyển requirements thành backlog.
---

# Skill: Write User Stories

## User Story Format

```markdown
## US-[EPIC_ID]-[NNN]: [Tên hành động ngắn gọn]

**As a** [role / actor]
**I want** [what they want to do]
**So that** [why — business value]

### Acceptance Criteria

**Scenario 1: [Happy path — tên mô tả]**
- **Given** [trạng thái ban đầu / precondition]
- **When** [hành động người dùng thực hiện]
- **Then** [kết quả quan sát được]
- **And** [thêm assertion nếu cần]

**Scenario 2: [Edge case / Error path]**
- **Given** [điều kiện dẫn đến error]
- **When** [hành động]
- **Then** [error message / behavior rõ ràng]

### Notes
- Dependency: phải hoàn thành US-XX-YYY trước
- API: `POST /api/v1/[endpoint]`
- Business rule: BR-X01 (ref domain-model.md)
- Out of scope: [gì không làm trong story này]

### Definition of Done
- [ ] Unit tests cover happy + error paths
- [ ] API endpoint match spec trong api-design.md
- [ ] UI validation hiển thị đúng
- [ ] Code reviewed
```

## Viết AC chất lượng cao

```
✅ Good AC:
Given user chưa đăng nhập
When user truy cập /dashboard
Then redirect về /login với query param ?next=/dashboard

❌ Bad AC:
User không được truy cập nếu chưa đăng nhập
(Thiếu Given, không nói redirect đi đâu)

✅ Good AC:
Given user nhập email "test@example.com" đã tồn tại
When user submit form đăng ký
Then hiển thị error inline tại field email: "Email already registered"
And không tạo account mới

❌ Bad AC:
Hiển thị lỗi khi email trùng
(Không nói lỗi gì, ở đâu)
```

## Story Sizing (Fibonacci)

```
1 pt  — Thay đổi nhỏ, logic đơn giản, < 2h
2 pts — 1 endpoint đơn, CRUD cơ bản, ~half day
3 pts — 1 feature hoàn chỉnh với validation, ~1 day
5 pts — Feature có business logic phức tạp hoặc multi-step, 2-3 days
8 pts — Feature lớn, nhiều edge cases, ~1 week
13 pts → SPLIT IT. Story quá lớn để estimate chính xác.
```

## MoSCoW Prioritization

```
Must Have — không có thì không ship, core value proposition
Should Have — quan trọng nhưng có workaround tạm thời
Could Have — nice-to-have, làm nếu còn capacity
Won't Have (v1) — consciously deferred, ghi rõ lý do
```

## Story Splitting Patterns

```
❌ Story quá lớn: "User quản lý profile"
✅ Split theo operations:
   - US-02-001: Xem profile (1pt)
   - US-02-002: Cập nhật tên và avatar (2pts)
   - US-02-003: Đổi password (3pts)
   - US-02-004: Xóa tài khoản (5pts)

❌ Story quá lớn: "Admin quản lý users"
✅ Split theo roles:
   - US-03-001: Admin xem danh sách users (2pts)
   - US-03-002: Admin kích hoạt/vô hiệu hóa user (2pts)
   - US-03-003: Admin thay đổi role của user (3pts)

❌ Story ôm cả happy + unhappy path phức tạp
✅ Tách thành story riêng nếu unhappy path cần UI phức tạp
```

## Epic Structure Template

```markdown
# Epic EP-[NNN]: [Tên Epic]

**Mục tiêu:** [1 câu mô tả business goal]
**Bounded Context:** [từ domain-model.md]

## Stories trong Epic

| Story ID | Title | Points | Priority | Dependency |
|----------|-------|--------|----------|------------|
| US-01-001 | ... | 3 | Must Have | — |
| US-01-002 | ... | 2 | Must Have | US-01-001 |
| US-01-003 | ... | 5 | Should Have | US-01-001 |

**Total Must Have:** X points
**Total Should Have:** Y points
```

## Anti-patterns

```
❌ Technical story: "Implement JWT middleware"
→ Đây là task của dev, không phải user story
✅ "User đăng nhập và session được duy trì"

❌ Story không có actor: "Hệ thống gửi email xác nhận"
✅ "As a new user, I want to receive a confirmation email..."

❌ AC không verifiable: "Hệ thống phải nhanh"
✅ AC: "Response time < 200ms tại p95 với 100 concurrent users"

❌ AC chứa implementation detail: "Dùng bcrypt để hash password"
✅ AC: "Password được lưu dưới dạng hash (không plain text)"

❌ 1 story cover quá nhiều: "User có thể đăng ký, đăng nhập và quản lý profile"
✅ 3 stories riêng biệt
```
