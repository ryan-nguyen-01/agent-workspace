---
name: skill-discovery-problem-analysis
description: Phân tích ý tưởng sản phẩm: xác định vấn đề thật sự, validate problem-solution fit, phát hiện assumption nguy hiểm và đánh giá độ rõ ràng của ý tưởng trước khi đầu tư xây dựng.
---

# Skill: Problem Analysis & Validation

## Interview Questions để hiểu sâu ý tưởng

```
Tầng 1 — Vấn đề
Q: "Vấn đề cụ thể bạn muốn giải quyết là gì?"
Q: "Ai đang gặp vấn đề này? Bao nhiêu người?"
Q: "Họ đang giải quyết vấn đề này như thế nào hiện tại?"
Q: "Tại sao giải pháp hiện tại chưa đủ tốt?"

Tầng 2 — Giải pháp
Q: "Giải pháp của bạn khác gì so với hiện tại?"
Q: "Tại sao bạn nghĩ giải pháp này sẽ hiệu quả?"
Q: "Bạn đã nói chuyện với người dùng tiềm năng chưa? Họ nói gì?"

Tầng 3 — Bản thân founder
Q: "Tại sao bạn là người phù hợp để làm điều này?"
Q: "Bạn sẵn sàng dành bao nhiêu thời gian/tiền cho điều này?"
Q: "Đây là dự án cá nhân hay có plan scale?"
```

## Problem Statement Scoring

```
Đánh giá vấn đề theo 4 chiều (1-5):

PAIN LEVEL — Vấn đề đau đến mức nào?
1 = "nice to have" — không có cũng không sao
3 = gây bất tiện thường xuyên
5 = cực kỳ đau, chặn workflow hàng ngày

FREQUENCY — Xảy ra bao thường xuyên?
1 = vài lần/năm
3 = vài lần/tuần
5 = nhiều lần/ngày

MARKET SIZE — Bao nhiêu người gặp vấn đề này?
1 = < 1,000 người (niche)
3 = 10,000 - 100,000 người
5 = > 1,000,000 người

WILLINGNESS TO PAY — Người dùng có sẵn sàng trả tiền không?
1 = "Hay đó nhưng tôi không trả tiền"
3 = Trả nếu rẻ (< $10/tháng)
5 = Đang trả tiền cho giải pháp tệ hơn

Score ≥ 16: Tiếp tục → SA
Score 10-15: Cần validate thêm trước khi build
Score < 10: Reconsider — vấn đề chưa đủ thật/đủ lớn
```

## Assumption Mapping

```markdown
### Critical Assumptions (nếu sai → toàn bộ idea sụp đổ)

| # | Assumption | Validation Method | Risk |
|---|-----------|-------------------|------|
| A1 | Users hiện tại thật sự bị đau bởi vấn đề X | User interview (5-10 người) | High |
| A2 | Users sẵn sàng chuyển sang giải pháp mới | Prototype test / waitlist | High |
| A3 | Có thể build được với team/budget hiện có | Technical spike | Medium |

### Validation Priority
Build / Buy / Partner trước khi code:
→ Ai có thể validate assumption A1 trong 1 tuần mà không cần code?
```

## Problem vs Solution Confusion

```
❌ Idea mô tả solution, không phải problem:
"Tôi muốn làm app nhắc uống thuốc"
→ Hỏi lại: "Vấn đề là gì? Người dùng quên uống thuốc? Tại sao quên?"

✅ Problem rõ ràng:
"Người cao tuổi sống một mình quên uống thuốc theo giờ, không có ai nhắc,
dẫn đến bỏ liều, ảnh hưởng điều trị. Con cái không theo dõi được từ xa."

Rule: Problem statement tốt KHÔNG mention technology/solution.
```
