---
name: skill-role-blueprints
description: Skill cung cấp blueprints/templates cho patterns phổ biến (CRUD, auth, file upload, payment, real-time). Agent-coder dùng blueprints thay vì viết từ đầu, đảm bảo consistency.
---

# Skill: Blueprints

## Mục đích
Thư viện blueprints cho các coding patterns phổ biến. Thay vì mỗi lần viết CRUD module từ đầu, agent-coder chọn blueprint phù hợp → customize theo project conventions → implement nhanh, consistent, ít bug.

---

## Khi nào dùng

```yaml
triggers:
  - new_module_common_pattern
  - task_matches_blueprint_section_below

detection_keywords:
  crud: [create, read, update, delete, CRUD, module mới, entity mới, resource mới]
  auth: [login, register, authentication, forgot password, reset password, OAuth]
  file_upload: [upload, file, image, S3, storage, attachment]
  payment: [payment, checkout, subscription, billing, Stripe, invoice]
  realtime: [websocket, real-time, notification, chat, live, SSE, socket]
  search: [search, filter, full-text, elasticsearch, autocomplete]
  pagination: [pagination, infinite scroll, cursor, offset, page]
  caching: [cache, invalidation, TTL, Redis cache, memoize]
```

---

## Blueprint catalog (inline trong skill này)

> **Lưu ý:** Bản `agent-platform` tối giản **không** ship thư mục `blueprints/` ở root repo. Toàn bộ mẫu dưới đây nằm **trong file `SKILL.md` này**. Team có thể copy excerpt sang `docs/` của project nếu cần.

Khi điều phối: **không** bắt buộc field `blueprint` trên subtask; analyst/orchestrator có thể nhắc coder **mở đúng section** trong skill này khi task khớp pattern.

### BLUEPRINT-001: CRUD Module

```yaml
id: BLUEPRINT-001
name: CRUD Module
description: Complete CRUD cho 1 entity/resource với validation, pagination, error handling
applicable_when: Tạo module mới quản lý 1 entity (user, product, order, ...)
complexity: medium

structure:
  backend:
    files:
      - {module}/dto/create-{entity}.dto.ts       # Input validation
      - {module}/dto/update-{entity}.dto.ts
      - {module}/dto/query-{entity}.dto.ts         # Pagination + filter
      - {module}/{entity}.entity.ts                # DB model
      - {module}/{entity}.service.ts               # Business logic
      - {module}/{entity}.controller.ts            # HTTP handlers
      - {module}/{entity}.module.ts                # DI wiring
      - {module}/__tests__/{entity}.service.spec.ts

  frontend:
    files:
      - {module}/hooks/use-{entity}.ts             # Data fetching hook
      - {module}/components/{Entity}List.tsx
      - {module}/components/{Entity}Form.tsx
      - {module}/components/{Entity}Detail.tsx
      - {module}/pages/{entity}/index.tsx           # List page
      - {module}/pages/{entity}/[id].tsx            # Detail page
      - {module}/pages/{entity}/new.tsx             # Create page

patterns:
  api_endpoints:
    - POST   /api/{entities}          → create
    - GET    /api/{entities}          → list (paginated)
    - GET    /api/{entities}/:id      → get by id
    - PATCH  /api/{entities}/:id      → update
    - DELETE /api/{entities}/:id      → delete

  validation:
    create: required fields + type checks + custom rules
    update: partial (all optional) + type checks
    query: page, limit, sort, filter fields

  error_handling:
    not_found: 404 + message "{Entity} not found"
    validation: 400 + field-level errors
    duplicate: 409 + message "{Entity} already exists"
    unauthorized: 401 + message

  pagination:
    input: { page, limit, sort, order }
    output: { data, meta: { total, page, limit, totalPages } }

  testing:
    unit: service methods (create, findAll, findOne, update, remove)
    integration: controller endpoints (happy + error paths)
    min_cases: 3 per method (happy, validation error, not found)

customization_points:
  - Entity name + fields
  - Validation rules per field
  - Which fields are searchable/filterable
  - Soft delete vs hard delete
  - Relations (belongs to, has many)
  - Custom business rules (e.g., can't delete if has children)
```

### BLUEPRINT-002: Authentication Flow

```yaml
id: BLUEPRINT-002
name: Authentication Flow
description: Login, register, forgot/reset password, token management
applicable_when: Module auth mới, hoặc thêm auth vào project chưa có
complexity: complex

structure:
  backend:
    files:
      - auth/dto/login.dto.ts
      - auth/dto/register.dto.ts
      - auth/dto/forgot-password.dto.ts
      - auth/dto/reset-password.dto.ts
      - auth/dto/change-password.dto.ts
      - auth/auth.service.ts
      - auth/auth.controller.ts
      - auth/auth.module.ts
      - auth/guards/jwt-auth.guard.ts
      - auth/guards/roles.guard.ts
      - auth/strategies/jwt.strategy.ts
      - auth/decorators/current-user.decorator.ts
      - auth/decorators/roles.decorator.ts

  frontend:
    files:
      - auth/hooks/use-auth.ts                  # Auth state + methods
      - auth/context/auth-provider.tsx          # Auth context
      - auth/components/LoginForm.tsx
      - auth/components/RegisterForm.tsx
      - auth/components/ForgotPasswordForm.tsx
      - auth/components/ResetPasswordForm.tsx
      - auth/pages/login.tsx
      - auth/pages/register.tsx
      - auth/middleware.ts                       # Route protection

patterns:
  endpoints:
    - POST /auth/register     → register (public)
    - POST /auth/login        → login, return tokens (public)
    - POST /auth/refresh      → refresh access token (public)
    - POST /auth/forgot       → send reset email (public)
    - POST /auth/reset        → reset password with token (public)
    - POST /auth/change       → change password (authenticated)
    - GET  /auth/me           → get current user (authenticated)
    - POST /auth/logout       → invalidate tokens (authenticated)

  token_management:
    access_token: JWT, 15min TTL, in memory (FE)
    refresh_token: JWT, 7d TTL, httpOnly cookie
    rotation: new refresh token on each refresh call

  password:
    hash: bcrypt (cost 12) | argon2
    policy: min 8 chars, at least 1 uppercase, 1 number
    reset_token: crypto random, 1h expiry, single use

  security:
    rate_limit: 5 login attempts per 15min per IP
    brute_force: lock account after 10 failed attempts
    session: invalidate all sessions on password change
    headers: secure, httpOnly, sameSite for cookies

  testing:
    scenarios:
      - Register with valid data → 201 + tokens
      - Register with existing email → 409
      - Login with correct credentials → 200 + tokens
      - Login with wrong password → 401
      - Access protected route without token → 401
      - Access protected route with expired token → 401
      - Refresh with valid refresh token → new tokens
      - Forgot password → email sent (mock)
      - Reset password with valid token → success
      - Reset password with expired token → 400
```

### BLUEPRINT-003: File Upload

```yaml
id: BLUEPRINT-003
name: File Upload
description: Upload files to S3/local storage với validation, resize, presigned URLs
applicable_when: Feature yêu cầu upload file (avatar, document, image)
complexity: medium

structure:
  backend:
    files:
      - storage/storage.service.ts        # Abstract storage interface
      - storage/s3.service.ts             # S3 implementation
      - storage/local.service.ts          # Local FS (dev)
      - storage/storage.module.ts
      - upload/upload.controller.ts
      - upload/upload.service.ts
      - upload/pipes/file-validation.pipe.ts
      - upload/interceptors/file.interceptor.ts

patterns:
  upload_flow:
    option_a_direct:
      1. Client → POST /upload (multipart) → Server
      2. Server validate → upload to S3 → return URL
      pros: simple
      cons: server bandwidth bottleneck

    option_b_presigned:
      1. Client → GET /upload/presign → Server returns presigned URL
      2. Client → PUT directly to S3
      3. Client → POST /upload/confirm { key } → Server saves reference
      pros: no server bandwidth bottleneck
      cons: more complex

  validation:
    file_type: whitelist MIME types (image/jpeg, image/png, application/pdf)
    file_size: max 10MB (configurable)
    filename: sanitize (remove special chars, limit length)
    virus_scan: optional (ClamAV integration)

  processing:
    images: resize to standard sizes (thumbnail: 150x150, medium: 600x600, large: 1200x1200)
    documents: extract metadata (page count, author)
    storage_path: {entity_type}/{entity_id}/{uuid}.{ext}

  cleanup:
    orphaned_files: cron job to delete files not referenced in DB
    soft_delete: keep file 30 days after entity deleted
```

### BLUEPRINT-004: Payment Integration

```yaml
id: BLUEPRINT-004
name: Payment Integration
description: Checkout flow, webhook handling, subscription management
applicable_when: Feature yêu cầu thanh toán (one-time hoặc subscription)
complexity: complex

structure:
  backend:
    files:
      - payment/payment.service.ts
      - payment/payment.controller.ts
      - payment/payment.module.ts
      - payment/dto/create-checkout.dto.ts
      - payment/dto/webhook-event.dto.ts
      - payment/webhooks/stripe.webhook.ts
      - payment/entities/payment.entity.ts
      - payment/entities/subscription.entity.ts

patterns:
  checkout_flow:
    1. Client → POST /payments/checkout { items, return_url }
    2. Server → create Stripe Checkout Session → return session URL
    3. Client → redirect to Stripe
    4. Stripe → webhook → Server confirms payment
    5. Server → update order status, send confirmation

  webhook_handling:
    verify: ALWAYS verify webhook signature
    idempotency: store event ID, skip duplicates
    retry_safe: handle same event multiple times gracefully
    events:
      - checkout.session.completed → fulfill order
      - payment_intent.payment_failed → notify user
      - customer.subscription.updated → update subscription
      - customer.subscription.deleted → cancel subscription

  security:
    webhook_secret: verify signature, reject unsigned
    amount_verification: verify amount matches expected
    currency: always explicit, never assume
    pci_compliance: NEVER store card numbers, use Stripe tokens

  testing:
    mock_stripe: jest mock for Stripe SDK
    webhook_tests: simulate events with correct signatures
    idempotency_tests: send same event twice → only processed once
```

### BLUEPRINT-005: Real-time Features

```yaml
id: BLUEPRINT-005
name: Real-time Features
description: WebSocket/SSE cho notifications, chat, live updates
applicable_when: Feature cần real-time data (notifications, chat, dashboard live data)
complexity: medium

structure:
  backend:
    files:
      - gateway/events.gateway.ts          # WebSocket gateway
      - gateway/gateway.module.ts
      - notifications/notification.service.ts
      - notifications/notification.entity.ts
      - notifications/dto/create-notification.dto.ts

  frontend:
    files:
      - hooks/use-socket.ts                # WebSocket connection hook
      - hooks/use-notifications.ts         # Notifications specific
      - context/socket-provider.tsx

patterns:
  connection:
    protocol: WebSocket (Socket.IO) | SSE
    auth: JWT token in handshake / query param
    reconnection: auto-reconnect with exponential backoff
    heartbeat: ping every 30s, timeout 60s

  events:
    server_to_client:
      - notification:new → new notification received
      - data:update → entity changed (real-time dashboard)
      - user:online → user presence change
    client_to_server:
      - notification:read → mark notification as read
      - room:join → join specific channel/room
      - room:leave → leave channel

  scaling:
    single_server: in-memory adapter
    multi_server: Redis adapter (pub/sub)
    message_ordering: timestamp-based, client-side sort
```

### BLUEPRINT-006: Search & Filter

```yaml
id: BLUEPRINT-006
name: Search & Filter
description: Full-text search, advanced filtering, autocomplete
applicable_when: Feature cần search/filter phức tạp hơn simple WHERE

patterns:
  simple_search:
    backend: SQL LIKE/ILIKE, good for < 100k records
    query: GET /api/{entities}?q=keyword&status=active&sort=-createdAt

  full_text:
    backend: Elasticsearch / PostgreSQL tsvector
    features: fuzzy matching, relevance scoring, highlighting
    indexing: async via queue on entity create/update/delete

  autocomplete:
    backend: prefix search, max 10 results, < 200ms
    frontend: debounce 300ms, show results in dropdown

  filter_pattern:
    backend: build dynamic query from filter params
    operators: eq, ne, gt, gte, lt, lte, in, like, between
    query: GET /api/products?price[gte]=10&price[lte]=100&category[in]=a,b
```

### BLUEPRINT-007: Caching Strategy

```yaml
id: BLUEPRINT-007
name: Caching Strategy
description: Cache patterns cho API responses, DB queries, computed data
applicable_when: Performance optimization, reduce DB load

patterns:
  cache_aside:
    read: check cache → miss → query DB → store in cache → return
    write: update DB → invalidate cache
    ttl: 5min (default), configurable per resource

  cache_key_convention:
    format: "{entity}:{id}" hoặc "{entity}:list:{hash(query)}"
    example: "user:123", "products:list:a1b2c3"

  invalidation:
    single: delete key on update/delete
    pattern: delete "products:*" when any product changes
    event_driven: publish event on change → subscriber invalidates

  layers:
    L1: in-memory (LRU, cho computed values, < 100 items)
    L2: Redis (cho shared state, session, rate limit)
    L3: CDN/HTTP cache headers (cho static assets, public API responses)

  http_caching:
    public_endpoints: Cache-Control: public, max-age=300
    private_endpoints: Cache-Control: private, no-cache
    etag: hash of response body for conditional requests
```

---

## Cách sử dụng blueprints

### Agent-analyst:

```
1. Phân tích task → detect xem task match blueprint nào
2. Attach blueprint ID vào subtask:
   subtask:
     blueprint: BLUEPRINT-001
     customization:
       entity: Product
       fields: [name, price, category, description, image]
```

### Agent-coder:

```
1. Nhận subtask có blueprint reference
2. Đọc blueprint → hiểu structure + patterns
3. Customize theo:
   - Project conventions (naming, imports, style)
   - Entity fields và business rules cụ thể
   - UI library của project
   - Database/ORM của project
4. Generate code theo blueprint structure
5. KHÔNG copy-paste blueprint — adapt theo context
```

### Agent-orchestrator:

```
1. Khi inject context cho coder, attach relevant blueprint
2. Blueprint giúp coder viết nhanh + consistent
3. Blueprint KHÔNG thay thế task description — chỉ là reference
```

---

## Blueprint vs Context

```
Blueprint = "HOW to implement a pattern" (generic, reusable)
Context   = "WHAT to implement for this project" (specific, from analysis)

Agent-coder cần CẢ HAI:
- Context: entity nào, fields gì, business rules gì, conventions gì
- Blueprint: file structure, API patterns, validation patterns, error handling
```

---

## Tạo Blueprint mới

```
Khi nào tạo blueprint mới:
- Pattern xuất hiện ≥ 3 lần trong feedback/patterns.md
- Agent-coder lặp lại cùng structure > 2 lần
- User request template cho pattern mới

Format: follow schema ở trên
Location: thêm section vào `skill-role-blueprints/SKILL.md`, hoặc `docs/` của project (không bắt buộc `.agent/blueprints/`)
```

---

## Nguyên tắc

- **Blueprints là reference, không phải copy-paste** — luôn adapt theo conventions
- **Stack-agnostic ở mức concept** — patterns áp dụng cho mọi framework
- **Stack-specific ở mức implementation** — file names, imports, syntax theo stack
- **Customization points rõ ràng** — mỗi blueprint ghi rõ cần customize gì
- **Test cases kèm theo** — blueprint luôn include test scenarios
- **Security by default** — validation, sanitization, auth built into patterns
