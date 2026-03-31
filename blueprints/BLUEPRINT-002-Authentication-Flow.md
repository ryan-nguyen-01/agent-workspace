# BLUEPRINT-002 — Authentication Flow

**Goal**: Thêm auth end-to-end: register/login/logout/refresh + password reset + route protection, kèm hardening tối thiểu.

---

## When to use

- Project chưa có auth
- Cần chuẩn hóa auth flow cho multi-service/monorepo
- Cần refresh token rotation + httpOnly cookies

---

## Decisions (make explicit)

```yaml
auth:
  mode: jwt
  access_token_ttl_minutes: 15
  refresh_token_ttl_days: 7
  refresh_storage: httpOnly_cookie
  rotation: true
password:
  hash: argon2
  policy: "min 8, at least 1 number"
account:
  login_identifier: email
  email_verification: optional
security:
  rate_limit_login: "5 per 15m per IP"
  lock_after_failed_attempts: 10
rbac:
  enabled: true
  roles: [admin, member]
```

---

## API contract (REST)

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET  /auth/me`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`
- `POST /auth/change-password` (auth)

---

## Token model (recommended)

- **Access token**: short-lived JWT (memory on client)
- **Refresh token**: long-lived JWT stored in **httpOnly cookie**
- **Rotation**: mỗi lần refresh → issue refresh token mới + revoke refresh token cũ

Data model (server-side):
- `RefreshToken` table/collection:
  - `id`, `userId`, `tokenHash`, `revokedAt`, `expiresAt`, `createdAt`, `ip`, `userAgent`

---

## Steps

### Step 1 — Identity model

- User fields: `id`, `email`, `passwordHash`, `status`, `roles`, `tenantId?`, `lastLoginAt`
- Unique index: `(tenantId, email)` nếu multi-tenant

### Step 2 — Implement auth service

- register: validate + hash password + create user
- login: verify password + issue tokens + record refresh token
- refresh: verify refresh token + rotation + issue new tokens
- logout: revoke refresh token(s)

### Step 3 — Guards/middleware

- require-auth: verify access token
- roles/policies: authorize actions

### Step 4 — Password reset

- forgot: generate single-use reset token + expiry + email send
- reset: validate token + update password + revoke sessions

### Step 5 — Security hardening (minimum)

- Rate limit login/forgot/reset
- Prevent user enumeration (generic messages)
- Set cookie flags: `httpOnly`, `secure`, `sameSite=lax|strict`
- Audit log for auth events (optional)

### Step 6 — Tests

Must-have scenarios:
- register ok / duplicate
- login ok / wrong password / locked
- refresh ok / revoked / expired
- logout ok
- me: auth required
- forgot/reset happy + expired token

---

## Reference skeletons

### NestJS

- `JwtStrategy`, `JwtAuthGuard`, `RolesGuard`
- `AuthController` + `AuthService`
- Cookie set in controller (reply headers)

### FastAPI

- OAuth2PasswordRequestForm or JSON body
- Dependency for current user
- httpOnly cookies via response.set_cookie

### Spring Boot

- Spring Security filters
- JWT verifier + method security (`@PreAuthorize`)

