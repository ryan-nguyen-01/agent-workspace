# Workflow Narrative — TASK-example-full

> Tài liệu này mô tả **luồng hoạt động đầy đủ** của hệ thống multi-agent khi xử lý
> task "JWT Authentication" từ lúc nhận yêu cầu đến khi hoàn thành.
> Mỗi phase ghi rõ: agent nào chạy, input/output là gì, và quyết định tại đâu.

---

## Phase 0: Bootstrap — Kiểm tra Project Brain

```
Agent:      coordinator
Input:      User request "Implement JWT auth cho hệ thống"
Action:     Kiểm tra .claude/context/project-brain.yaml
Decision:   Project Brain tồn tại và fresh → TIẾP TỤC
            (Nếu missing → route sang /onboard trước)
Output:     Hiểu project context: 3 services (api, frontend, database), stack, conventions
```

**Tại sao?** Coordinator luôn check Project Brain trước (R-001-01). Nếu Brain stale hoặc missing, toàn bộ workflow dừng để onboarding.

---

## Phase 1: Task Analysis — Normalize yêu cầu

```
Agent:      task-analysis
Input:      User text + project brain context
Output:     .claude/tasks/TASK-example-full/task-analysis.yaml
```

**Quyết định quan trọng:**

- Xác định 3 services bị ảnh hưởng: `api`, `frontend`, `database`
- Viết 7 acceptance criteria có thể test được (AC-1 → AC-7)
- Xác định 4 critical checks bảo mật (password leak, hardcoded secret, bcrypt salt, token validation)
- Phân tích risks: token leakage, timing attacks, CORS
- Gắn reuse analysis: patterns nào trong codebase có thể tái sử dụng

**Gate check:** Nếu thiếu thông tin critical → đánh dấu `requires_user_clarification` và DỪNG.

**User Approval Gate (R-004-08, R-011-10):**
Sau khi viết task-analysis.yaml, agent trình bày spec cho user review:

- User xem: intent, 7 ACs, 3 impacted services, risks, critical checks
- User approve → `user_approved: true` → tiếp tục Phase 2
- User yêu cầu chỉnh sửa → update task-analysis.yaml → trình lại
- **Không được chuyển sang Coder Leader khi chưa có user approval.**

---

## Phase 2: Coder Leader — Lên kế hoạch implementation

```
Agent:      coder-leader
Input:      task-analysis.yaml + agent-registry.yaml
Output:     implementation-plan.yaml + service-assignments.yaml
```

**Bước 2a: Implementation Plan**

- Chia thành 8 steps theo dependency order
- Steps 1-5: database + api (có thể parallel phần nào)
- Steps 6-8: frontend (depends on API contract)
- Xác định 3 integration points (api ↔ frontend)
- Định nghĩa 4 contracts (register, login, auth header, users table)

**Bước 2b: Service Assignments**

- `coder-database` → step 1 (migration only)
- `coder-api` → steps 2-5 (core auth logic)
- `coder-frontend` → steps 6-8 (UI + integration)
- Mỗi coder có `allowed_write_paths` và `forbidden_paths` rõ ràng

**Execution order:**

```
Phase 1: coder-database (schema first)
     ↓
Phase 2: coder-api (auth logic, depends on users table)
     ↓
Phase 3: coder-frontend (UI, depends on API contract)
```

**Gate check:** Nếu không có active coder cho service nào → DỪNG, yêu cầu tạo coder (R-005-06).

---

## Phase 3: Service Coders — Implementation

### 3a: coder-database chạy step 1

```
Agent:      coder-database
Input:      service-assignments.yaml (step 1)
Scope:      WRITE: src/database/migrations/, src/database/schema/
            FORBIDDEN: src/api/, frontend/
Output:     Migration file + schema definition
Status:     done
```

**Tạo:**

- `src/database/migrations/20250417_create_users.ts` — Users table
- `src/database/schema/users.ts` — TypeScript schema definition

### 3b: coder-api chạy steps 2-5

```
Agent:      coder-api
Input:      service-assignments.yaml (steps 2-5)
Scope:      WRITE: src/api/auth/, src/api/middleware/, src/utils/jwt.ts, src/config/auth.ts
            FORBIDDEN: frontend/, src/database/migrations/
Output:     JWT utils, AuthService, auth middleware, AuthController + tests
Status:     done
```

**Tạo 7 files:**

- `src/utils/jwt.ts` — sign/verify/decode JWT
- `src/config/auth.ts` — JWT_SECRET từ env, token expiry config
- `src/api/auth/auth.service.ts` — register() + login() với bcrypt
- `src/api/auth/auth.controller.ts` — POST endpoints
- `src/api/auth/auth.dto.ts` — UserDto (exclude password_hash)
- `src/api/middleware/auth.middleware.ts` — JWT verification middleware
- Tests cho service + middleware

**Conventions followed:** Async bcrypt (salt=12), env vars cho secrets, DTO pattern.

### 3c: coder-frontend chạy steps 6-8

```
Agent:      coder-frontend
Input:      service-assignments.yaml (steps 6-8) + API contract từ coder-api
Scope:      WRITE: frontend/src/contexts/, frontend/src/pages/auth/, frontend/src/lib/api/, frontend/src/components/auth/
            FORBIDDEN: src/api/, src/database/
Output:     AuthContext, Login/Register pages, HTTP interceptor, ProtectedRoute
Status:     done
```

**Tạo 5 files:**

- `frontend/src/contexts/AuthContext.tsx` — Auth state management
- `frontend/src/lib/api/client.ts` (modified) — Bearer token interceptor
- `frontend/src/pages/auth/LoginPage.tsx` + `RegisterPage.tsx`
- `frontend/src/components/auth/ProtectedRoute.tsx` — Route guard

**Design decisions:**

- Token trong memory (không localStorage) → bảo mật hơn
- 401 → auto clear token → redirect /login

### Kết quả tổng hợp

**Bước 3d: Mỗi coder viết Handoff**

Sau khi implementation xong, mỗi coder bàn giao bằng file `coder-handoff-<service>.yaml`:

```
coder-database  → coder-handoff-database.yaml  (1 step, 2 files, UUID PK decision)
coder-api       → coder-handoff-api.yaml       (4 steps, 7 files, bcrypt/JWT decisions, 8 curl tests)
coder-frontend  → coder-handoff-frontend.yaml  (3 steps, 5 files, memory token strategy, 9 browser tests)
```

Handoff chứa: summary, decisions, files changed, integration notes (contracts provided/consumed),
risks, reuse report, và verification evidence.

**Bước 3e: Coder Leader review và tổng hợp**

```
Agent:      coder-leader
Input:      3 coder-handoff files
Action:     Cross-check contracts (api provides → frontend consumes),
            verify env vars, resolve cross_service_requests
Output:     coder-results.yaml
Status:     all_done, integration_verified: false
```

Coder Leader đọc từng handoff, kiểm tra contracts alignment, ghi nhận reuse report, rồi tổng hợp thành coder-results.yaml. Chuyển sang Dev Verification.

---

## Phase 4: Dev Verification — Kiểm tra Code Done

```
Agent:      dev-verification
Input:      coder-results.yaml + task-analysis.yaml (critical checks + ACs)
Output:     dev-verification.yaml
Decision:   DEV_DONE (score 92%, all critical checks pass)
```

**Checklist:**

| Check                  | Result                                 |
| ---------------------- | -------------------------------------- |
| Score ≥ 80%            | ✅ 92% (11/12)                         |
| Critical checks pass   | ✅ Tất cả 4/4 pass                     |
| Zero known blockers    | ✅ Không có blocker                    |
| Scope compliance       | ✅ Mọi file trong allowed paths        |
| Test policy compliance | ✅ Unit tests added + pass             |
| AC coverage            | ✅ 6/7 pass, 1 partial (refresh token) |

**Quyết định:** `DEV_DONE` → chuyển sang QC Handoff.

> ⚠️ Nếu score < 80% hoặc critical check fail → `NEEDS_FIX` → quay lại Coder Leader.

---

## Phase 5: QC Handoff — Chuyển giao cho QC

```
Agent:      qc-handoff
Input:      dev-verification.yaml + coder-results.yaml + task-analysis.yaml
Output:     qc-handoff.md
```

QC Handoff tạo tài liệu cho QC Runner với:

- Summary thay đổi (files, services, scope)
- Acceptance criteria + dev status
- Critical checks đã pass
- Known issues (refresh token deferred)
- Environment setup + test commands
- QC focus areas (security, edge cases, cross-service)

---

## Phase 6: QC Runner — Chạy QC tests

```
Agent:      qc-runner
Input:      qc-handoff.md
Output:     qc-test-results.yaml
Decision:   QC_DONE (0 blockers, 13 tests, 12 pass, 1 known limitation)
```

**Test execution:**

| Category    | Tests | Pass | Fail | Notes                                   |
| ----------- | ----- | ---- | ---- | --------------------------------------- |
| Functional  | 4     | 4    | 0    | Register, login, protected endpoint     |
| Security    | 5     | 5    | 0    | Password leak, timing, token validation |
| Edge cases  | 2     | 2    | 0    | Duplicate email, missing fields         |
| Integration | 2     | 2    | 0    | Frontend token, 401 redirect            |

**Known limitation:** Refresh token chưa implement (non-blocker, deferred).

> ⚠️ Nếu có blocker bug → QC DỪNG NGAY → route sang Bug Router (R-008-04).

---

## Phase 6b: QC Delivery Report — Bàn giao cho User

```
Agent:      qc-runner
Input:      qc-test-results.yaml + coder-results.yaml
Output:     qc-delivery-report.md
```

Sau QC_DONE, QC Runner viết **delivery report** bàn giao cho user (R-008-09):

- **Tóm tắt**: JWT Auth QC_DONE, 13 tests, 0 blockers
- **Những gì đã hoàn thành**: 5 feature areas (DB, API auth, middleware, frontend, security)
- **Files thay đổi**: 13 files across 3 services
- **Test Results Summary**: table theo category (functional/security/edge/integration)
- **Known Limitations**: refresh token deferred
- **Hướng dẫn verify**: curl commands + frontend URLs user có thể chạy để verify
- **Đề xuất tiếp theo**: refresh token, password reset, email verification, rate limiting

**Target audience:** User — không phải agent khác. Mục đích để user biết chính xác
những gì đã làm, cách verify, và nên làm gì tiếp.

---

## Phase 7: Memory Update — Ghi nhận learnings

```
Agent:      memory-update
Input:      Tất cả artifacts (task-analysis, coder-results, dev-verification, qc-test-results)
Output:     memory-updates.yaml
```

**Những gì được ghi nhận:**

| Target                 | Content                                                     |
| ---------------------- | ----------------------------------------------------------- |
| project-brain.yaml     | JWT Auth capability added                                   |
| services/api.yaml      | Auth patterns, endpoints, bcrypt convention                 |
| services/frontend.yaml | AuthContext, token-in-memory strategy                       |
| services/database.yaml | Users table schema                                          |
| conventions.md         | Bcrypt async, env vars for secrets, DTO pattern             |
| anti-patterns.md       | No localStorage token, no password in response, no hashSync |
| bug-patterns           | Timing attack mitigation, generic error messages            |

**Tại sao?** Memory giúp agents tương lai không lặp lại sai lầm và tái sử dụng patterns đã proven.

---

## Phase 8: DONE — Coordinator đóng task

```
Agent:      coordinator
Input:      qc-test-results.yaml (QC_DONE) + memory-updates.yaml
Output:     Task state → DONE
```

Coordinator xác nhận:

1. ✅ Task analysis tồn tại + user đã approve
2. ✅ Implementation plan + assignments tồn tại
3. ✅ Coder results: all_done
4. ✅ Dev verification: DEV_DONE (92%)
5. ✅ QC handoff tồn tại
6. ✅ QC results: QC_DONE, 0 blockers
7. ✅ QC delivery report đã gửi cho user
8. ✅ Memory updates recorded

**Task DONE.**

---

## Diagram tổng hợp

```
User Request
     │
     ▼
┌─────────────┐
│ Coordinator │ ← Check Project Brain
└──────┬──────┘
       │
       ▼
┌──────────────┐
│Task Analysis │ → task-analysis.yaml (ACs, risks, critical checks)
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ User Review & Approve│ ← user_approved: true
└──────┬───────────────┘
       │
       ▼
┌──────────────┐
│ Coder Leader │ → implementation-plan.yaml + service-assignments.yaml
└──────┬───────┘
       │
       ├──→ coder-database ──→ migration ──────────────┐
       ├──→ coder-api ──→ auth logic + middleware ──────┤
       └──→ coder-frontend ──→ UI + interceptor ───────┤
                                                        │
                                                        ▼
                                         coder-handoff-<service>.yaml (×3)
                                                        │
                                                        ▼
                                         ┌──────────────────────┐
                                         │  Coder Leader review │
                                         │  Cross-check + merge │
                                         └──────────┬───────────┘
                                                    │
                                                    ▼
                                              coder-results.yaml
                                                        │
                                                        ▼
                                         ┌──────────────────────┐
                                         │  Dev Verification    │
                                         │  Score 92% → PASS    │
                                         └──────────┬───────────┘
                                                    │
                                                    ▼
                                         ┌──────────────────────┐
                                         │  QC Handoff          │
                                         └──────────┬───────────┘
                                                    │
                                                    ▼
                                         ┌──────────────────────┐
                                         │  QC Runner           │
                                         │  13 tests, 0 blocker │
                                         └──────────┬───────────┘
                                                    │
                                                    ▼
                                         ┌──────────────────────┐
                                         │  QC Delivery Report  │
                                         │  → User handover     │
                                         └──────────┬───────────┘
                                                    │
                                                    ▼
                                         ┌──────────────────────┐
                                         │  Memory Update       │
                                         └──────────┬───────────┘
                                                    │
                                                    ▼
                                         ┌──────────────────────┐
                                         │  Coordinator → DONE  │
                                         └──────────────────────┘
```

---

## Lưu ý quan trọng

1. **Không phase nào bị bỏ qua.** Mỗi phase có gate check riêng.
2. **Blocker bug tại bất kỳ phase nào** → workflow dừng → Bug Router → Coder Leader fix → re-verify.
3. **Mỗi coder chỉ write trong scope** được phép. Vi phạm → blocked.
4. **Cross-service changes** phải qua Coder Leader, không để coders tự coordinate.
5. **Memory update** là bước cuối nhưng quan trọng — giúp agent sessions tương lai hoạt động hiệu quả hơn.
