---
name: skill-context-compress
description: Nén tài liệu, README, code thành YAML context ngắn gọn tối đa mà vẫn giữ đủ thông tin cần thiết cho agents.
---

# Skill: Compress To Context

## Mục đích
Chuyển đổi tài liệu dài, code files, README thành YAML context nhỏ gọn. Mục tiêu: **giảm 80-90% token** mà vẫn giữ đủ thông tin để agents làm việc chính xác.

## Nguyên tắc nén
- Chỉ giữ **facts** — bỏ hết explanation, examples, tutorials
- Dùng YAML thay vì prose
- 1 dòng = 1 fact quan trọng
- Không viết những gì có thể suy ra từ context khác
- Không viết những gì không thay đổi bao giờ (nguyên tắc chung của ngôn ngữ)

## Quy tắc nén theo loại nội dung

### Nén README / Documentation
```
GIỮ LẠI:
✅ Mục đích của project/module (1 câu)
✅ Setup commands (dev, build, test)
✅ Cấu trúc thư mục chính
✅ Environment variables cần thiết
✅ External dependencies quan trọng
✅ Deployment notes nếu có

BỎ ĐI:
❌ Introduction / motivation / why we built this
❌ Tutorials và step-by-step guides
❌ Code examples trong README (đã có trong code)
❌ Lịch sử thay đổi
❌ Contributing guidelines
❌ License information
```

### Nén Source Code → Module Context
```
GIỮ LẠI:
✅ Tên và purpose của module (1 câu)
✅ Danh sách exports (function/class names + type)
✅ Dependencies (imports từ đâu)
✅ Environment variables được dùng
✅ Các edge cases hoặc constraints quan trọng

BỎ ĐI:
❌ Implementation details (body của function)
❌ Comments giải thích logic
❌ Private helper functions
❌ Test files
```

### Nén Config Files
```
GIỮ LẠI:
✅ Key commands (scripts)
✅ Main dependencies (không cần version)
✅ Build/compile targets
✅ Port/host config

BỎ ĐI:
❌ Dev dependencies (chỉ giữ test framework)
❌ Peer dependencies
❌ Lockfile content
```

## Tỷ lệ nén mục tiêu

| Loại nội dung | Trước | Sau | Tỷ lệ |
|---|---|---|---|
| README 500 dòng | ~4000 tokens | ~300 tokens | 92% |
| Module 200 dòng | ~1500 tokens | ~150 tokens | 90% |
| package.json | ~800 tokens | ~100 tokens | 87% |
| Full docs folder | ~20000 tokens | ~800 tokens | 96% |

## Ví dụ nén thực tế

### Trước (README section — 150 tokens):
```
The authentication module is responsible for handling all user authentication
flows in our application. It implements JWT-based authentication with refresh
token rotation. When a user logs in, they receive an access token (valid for
15 minutes) and a refresh token (valid for 7 days). The refresh token is
stored in an HTTP-only cookie for security...
```

### Sau (YAML — 25 tokens):
```yaml
module: auth
purpose: JWT authentication with refresh token rotation
access_token_ttl: 15m
refresh_token_ttl: 7d
storage: httponly-cookie
```

## Quy trình thực hiện
```
1. Đọc nội dung gốc
2. Xác định loại nội dung (README / code / config)
3. Áp dụng quy tắc nén tương ứng
4. Viết YAML output
5. Kiểm tra: "Nếu tôi là agent cần làm việc, thông tin này có đủ không?"
6. Nếu thiếu → thêm vào. Nếu dư → cắt bớt.
```

## Kiểm tra chất lượng sau nén
Tự hỏi:
- [ ] Agent có biết module này làm gì không?
- [ ] Agent có biết cách gọi module này không (exports)?
- [ ] Agent có biết dependencies nào cần import không?
- [ ] Agent có biết env vars nào cần thiết không?
- [ ] Có thông tin nào bị mất làm agent sẽ sai không?
