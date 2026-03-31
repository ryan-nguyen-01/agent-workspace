---
name: skill-discovery-mvp-scope
description: Xác định MVP scope tối giản: tìm core value loop, loại bỏ feature không cần thiết, định nghĩa success criteria và đề xuất validation approach trước khi build full product.
---

# Skill: MVP Scoping

## Core Value Loop

```
Trước khi list features, tìm Core Value Loop:

"Người dùng [hành động] → nhận được [giá trị] → vì vậy họ [quay lại/trả tiền]"

Ví dụ:
- Airbnb: "Host đăng phòng → nhận booking → kiếm tiền → đăng thêm phòng"
- Notion: "User tạo note → organize + tìm kiếm dễ → tiết kiệm thời gian → dùng nhiều hơn"

MVP chỉ cần đủ để complete 1 vòng loop này.
Mọi feature không thuộc loop → defer.
```

## Feature Filtering Framework

```markdown
### Test từng feature với 3 câu hỏi:

1. "Nếu không có feature này, user có còn nhận được core value không?"
   → Có: Feature không cần trong MVP
   → Không: Feature có thể là core

2. "Feature này giải quyết assumption nào cần validate?"
   → Nếu không validate assumption quan trọng → defer

3. "Có cách nào thủ công (manual) để deliver value này mà không cần code?"
   → Có → làm thủ công trước, tự động hóa sau (Concierge MVP)

### Feature Priority Table

| Feature | Core Loop? | Validates Assumption? | Manual Alternative? | Decision |
|---------|-----------|----------------------|--------------------| ---------|
| User registration | Yes | No | No | ✅ MVP |
| Social login (Google) | No | No | Yes (email/pw) | ❌ Defer |
| Email notifications | Yes | Yes (re-engagement) | Yes (manual email) | 🤔 Manual first |
| Dashboard analytics | No | No | Yes (spreadsheet) | ❌ Defer |
| Mobile app | No | No | Yes (responsive web) | ❌ Defer |
```

## MVP Types — Chọn đúng loại

```
CONCIERGE MVP
Bạn làm thủ công 100%, user không biết.
→ Dùng khi: muốn test nhu cầu cực nhanh, trước khi viết 1 dòng code
→ Ví dụ: Zapier ban đầu manually connect apps cho mỗi customer

WIZARD OF OZ MVP
UI có, backend là người làm thủ công.
→ Dùng khi: cần test UI/UX và flow, nhưng backend phức tạp
→ Ví dụ: AI feature thật ra là human review

LANDING PAGE MVP
Trang mô tả sản phẩm + waitlist/pre-order
→ Dùng khi: validate demand trước khi build bất kỳ thứ gì
→ Success: X% conversion từ visitor → signup

FUNCTIONAL MVP
Build tối giản, chỉ core loop, không polish.
→ Dùng khi: assumptions đã validated, cần product thật để iterate
→ Timeline: 2-6 tuần với team nhỏ
```

## MVP Scope Document

```markdown
## MVP Definition

### Core Value Proposition (1 câu)
[User nhận được gì, tại sao quan trọng]

### Core Loop
[User action] → [System response] → [Value received]

### In Scope (MVP)
| Feature | Why essential | Effort estimate |
|---------|--------------|-----------------|
| [Feature 1] | Completes core loop | M |
| [Feature 2] | Validates assumption A1 | S |

### Out of Scope (v1) — và lý do
| Feature | Why deferred | When to add |
|---------|-------------|-------------|
| [Feature X] | Nice-to-have, không block core loop | v2 nếu users request |
| [Feature Y] | Complex, có manual workaround | v2 nếu scale cần |

### Success Criteria (sau MVP)
Sau X tuần/tháng deploy, MVP thành công nếu:
- [ ] [Metric 1]: [X users] đã complete core loop
- [ ] [Metric 2]: [Y%] retention sau 1 tuần
- [ ] [Metric 3]: [Z người] sẵn sàng trả tiền

### Validation Approach
Trước khi build MVP, validate bằng:
- [ ] [X] user interviews với target segment
- [ ] Landing page với waitlist → target [N] signups trong [T] tuần
- [ ] Concierge cho [5] users đầu tiên
```

## Common MVP Mistakes

```
❌ "MVP xong rồi mới deploy" — MVP luôn cảm thấy chưa xong
→ Deploy sớm, iterate dựa trên real usage

❌ "Thêm feature này cho complete" — MVP không cần complete
→ Cut ruthlessly, 1 thing done well > 10 things mediocre

❌ MVP = prototype — MVP phải production-quality về reliability
→ Ít features, nhưng những features có phải hoạt động tốt

❌ Skip validation vì "tôi biết users cần cái này"
→ Founders thường wrong về user needs. Validate trước.

❌ MVP timeline > 3 tháng với team nhỏ
→ Scope lại. Nếu không fit trong 6-8 tuần, đang over-scope.
```
