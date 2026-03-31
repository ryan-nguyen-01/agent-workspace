---
name: skill-discovery-risk-assessment
description: Đánh giá rủi ro cho ý tưởng sản phẩm: phân loại rủi ro theo market/technical/execution/financial, xác định mức độ nghiêm trọng và đề xuất mitigation trước khi đầu tư build.
---

# Skill: Risk Assessment

## Risk Categories

```markdown
### 4 loại rủi ro chính

MARKET RISK — Thị trường không như kỳ vọng
- Vấn đề không đủ đau để người dùng thay đổi hành vi
- Thị trường quá nhỏ để sustainable
- Timing sai (quá sớm hoặc quá muộn)
- Competitor lớn copy feature và crush

TECHNICAL RISK — Không build được như kỳ vọng
- Technology chưa đủ trưởng thành (AI accuracy, hardware)
- Performance không đạt yêu cầu ở scale
- Integration với third-party phức tạp hơn dự kiến
- Team thiếu expertise cho stack cần thiết

EXECUTION RISK — Không thực thi được
- Team size không đủ để deliver đúng hạn
- Key person dependency (chỉ 1 người biết làm)
- Founder commitment thấp (side project, không full-time)
- Budget cạn trước khi reach product-market fit

EXTERNAL RISK — Yếu tố ngoài tầm kiểm soát
- Regulation/compliance thay đổi
- Dependency vào platform (Apple, Google, API provider)
- Economic downturn ảnh hưởng willingness to pay
```

## Risk Matrix

```markdown
### Đánh giá từng rủi ro

| # | Risk | Category | Probability | Impact | Score | Mitigation |
|---|------|----------|-------------|--------|-------|------------|
| R1 | Users không chuyển sang app mới | Market | High (3) | High (3) | 9 | Validate với 10 user interviews trước khi build |
| R2 | API của third-party thay đổi pricing | External | Medium (2) | High (3) | 6 | Multi-provider fallback, không lock-in |
| R3 | Chỉ có 1 dev biết codebase | Execution | Medium (2) | High (3) | 6 | Documentation, pair programming |
| R4 | Feature X khó implement hơn dự kiến | Technical | Low (1) | Medium (2) | 2 | Technical spike tuần 1 |

Score = Probability × Impact (1-3 each)
Score 7-9: Critical — phải address trước khi invest
Score 4-6: High — có plan mitigation rõ ràng
Score 1-3: Medium/Low — monitor, không block

### Top 3 Critical Risks
[List 3 rủi ro cao nhất và action plan cụ thể]
```

## Kill Signals — Khi nào nên dừng/pivot

```
🔴 STOP ngay nếu:
- Sau 10 user interviews: không ai thật sự đau với vấn đề này
- Core assumption sai và toàn bộ model phụ thuộc vào nó
- Technical feasibility assessment: không thể build với constraint hiện tại

🟡 PIVOT nếu:
- User pain thật nhưng solution proposed không được đón nhận
- Market size quá nhỏ cho business model dự kiến
- Có segment khác pain hơn segment đang target

🟢 CONTINUE với điều kiện:
- Có ít nhất 5 người sẵn sàng trả tiền / join waitlist sau khi nghe idea
- Technical feasibility confirmed với spike
- Ít nhất 1 người có thể commit 20h+/tuần
```

## Pre-mortem Exercise

```
Tưởng tượng: 1 năm sau, dự án thất bại hoàn toàn.
Nguyên nhân thất bại có thể là gì?

→ List 5-10 nguyên nhân thất bại phổ biến nhất
→ Với mỗi nguyên nhân: "Chúng ta có thể làm gì ngay bây giờ để ngăn?"

Ví dụ:
- "Users không adopt vì switching cost cao"
  → Làm onboarding cực kỳ dễ, import data từ competitor
- "Chạy hết tiền trước khi có revenue"
  → Định nghĩa runway và revenue milestone rõ ràng từ đầu
```
