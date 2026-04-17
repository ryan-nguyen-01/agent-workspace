# QC Handoff — TASK-example-full

## Task Summary

JWT Authentication cho hệ thống multi-service (API + Frontend + Database).
Users có thể register, login, và access protected endpoints.

## Scope

| Service  | Changes                                                 |
| -------- | ------------------------------------------------------- |
| database | Users table migration (id, email, password_hash, ...)   |
| api      | Auth endpoints, JWT middleware, bcrypt password hashing |
| frontend | AuthContext, Login/Register pages, HTTP interceptor     |

## Acceptance Criteria (from task-analysis)

| ID   | Criteria                                                 | Dev Status |
| ---- | -------------------------------------------------------- | ---------- |
| AC-1 | POST /api/auth/register tạo user mới, trả JWT token      | ✅ pass    |
| AC-2 | POST /api/auth/login xác thực credentials, trả JWT token | ✅ pass    |
| AC-3 | Auth middleware reject 401 khi không có valid token      | ✅ pass    |
| AC-4 | Frontend gửi JWT token trong Authorization header        | ✅ pass    |
| AC-5 | Frontend redirect login khi token expired/invalid        | ✅ pass    |
| AC-6 | Password hash bằng bcrypt (salt rounds ≥ 10)             | ✅ pass    |
| AC-7 | Token expiry 24h, refresh token 7 ngày                   | ⚠️ partial |

## Critical Checks (tất cả PASS)

1. ✅ Password không log/return trong response
2. ✅ JWT secret không hardcode
3. ✅ Bcrypt salt rounds = 12
4. ✅ Token validation: expiry + signature + issuer

## Known Issues

- **AC-7 partial**: Refresh token chưa implement. Access token 24h hoạt động. Refresh token deferred cho sprint sau.

## Dev Verification Score

**92%** (11/12 checks passed, threshold 80%)

## Files Changed

### Database

- `src/database/migrations/20250417_create_users.ts` (new)
- `src/database/schema/users.ts` (new)

### API

- `src/utils/jwt.ts` (new)
- `src/config/auth.ts` (new)
- `src/api/auth/auth.service.ts` (new)
- `src/api/auth/auth.controller.ts` (new)
- `src/api/auth/auth.dto.ts` (new)
- `src/api/middleware/auth.middleware.ts` (new)
- `src/api/routes.ts` (modified)
- `src/api/auth/__tests__/auth.service.test.ts` (new)
- `src/api/middleware/__tests__/auth.middleware.test.ts` (new)

### Frontend

- `frontend/src/contexts/AuthContext.tsx` (new)
- `frontend/src/lib/api/client.ts` (modified)
- `frontend/src/pages/auth/LoginPage.tsx` (new)
- `frontend/src/pages/auth/RegisterPage.tsx` (new)
- `frontend/src/components/auth/ProtectedRoute.tsx` (new)

## QC Focus Areas

1. **Security**: Password leak, token exposure, SQL injection
2. **Edge cases**: Duplicate email, wrong password, expired token, malformed token
3. **Cross-service**: Frontend xử lý 401 từ API đúng cách
4. **Performance**: bcrypt không block event loop

## Environment

- Local dev: `npm run dev` (API port 3000, Frontend port 5173)
- Database: PostgreSQL local hoặc Docker
- Env vars cần: `JWT_SECRET`, `DATABASE_URL`

## How to Test

```bash
# 1. Start services
npm run dev

# 2. Register
curl -X POST http://localhost:3000/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"Test123!","name":"Test User"}'

# 3. Login
curl -X POST http://localhost:3000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"Test123!"}'

# 4. Access protected endpoint
curl http://localhost:3000/api/users/me \
  -H 'Authorization: Bearer <token_from_step_3>'

# 5. Test invalid token
curl http://localhost:3000/api/users/me \
  -H 'Authorization: Bearer invalid-token'
# Expected: 401
```
