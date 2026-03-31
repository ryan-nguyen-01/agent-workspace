---
name: skill-api-rest
description: Best practices thiết kế RESTful APIs: naming conventions, HTTP methods, status codes, versioning, pagination và error responses.
---

# Skill: REST API Design

## URL Naming Conventions

```
# ✅ Resource-based URLs (nouns, not verbs)
GET    /api/v1/users              # List users
POST   /api/v1/users              # Create user
GET    /api/v1/users/{id}         # Get user
PATCH  /api/v1/users/{id}         # Partial update
PUT    /api/v1/users/{id}         # Full replace
DELETE /api/v1/users/{id}         # Delete user

# ✅ Nested resources (max 2 levels deep)
GET    /api/v1/users/{id}/posts   # User's posts
POST   /api/v1/users/{id}/posts   # Create post for user
GET    /api/v1/posts/{id}         # Direct access (avoid deeper nesting)

# ✅ Actions as sub-resources
POST   /api/v1/users/{id}/activate
POST   /api/v1/orders/{id}/cancel
POST   /api/v1/users/{id}/password/reset

# ❌ Verbs in URL
GET    /api/v1/getUsers           # ❌
POST   /api/v1/createUser         # ❌
POST   /api/v1/users/delete/{id}  # ❌
```

## HTTP Methods & Status Codes

```
GET    200 OK | 404 Not Found
POST   201 Created | 400 Bad Request | 409 Conflict
PUT    200 OK | 201 Created | 404 Not Found
PATCH  200 OK | 404 Not Found | 422 Unprocessable Entity
DELETE 204 No Content | 404 Not Found

# Auth
401 Unauthorized     — Missing or invalid credentials
403 Forbidden        — Authenticated but no permission
429 Too Many Requests — Rate limit exceeded

# Server
500 Internal Server Error  — Unexpected error
503 Service Unavailable    — Downstream dependency down
```

## Request/Response Formats

```typescript
// ✅ Consistent error response
interface ErrorResponse {
  error: {
    code: string        // Machine-readable: USER_NOT_FOUND
    message: string     // Human-readable description
    details?: Record<string, string[]>  // Validation errors per field
    requestId: string   // For debugging
  }
}

// Example 400 response
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Request validation failed",
    "details": {
      "email": ["Must be a valid email address"],
      "name": ["Must be at least 2 characters"]
    },
    "requestId": "req-abc123"
  }
}

// ✅ Consistent success response (optional wrapper)
interface ApiResponse<T> {
  data: T
  meta?: {
    total?: number
    page?: number
    pageSize?: number
  }
}
```

## Pagination

```typescript
// ✅ Cursor-based (cho large datasets, real-time data)
// Request
GET /api/v1/posts?cursor=eyJpZCI6MTAwfQ&limit=20

// Response
{
  "data": [...],
  "pagination": {
    "nextCursor": "eyJpZCI6MTIwfQ",
    "hasMore": true,
    "limit": 20
  }
}

// ✅ Offset-based (cho search results, admin panels)
// Request
GET /api/v1/users?page=2&pageSize=20

// Response
{
  "data": [...],
  "pagination": {
    "page": 2,
    "pageSize": 20,
    "total": 150,
    "totalPages": 8
  }
}
```

## Filtering, Sorting, Field Selection

```
# ✅ Filtering
GET /api/v1/users?status=active&role=admin
GET /api/v1/posts?createdAfter=2024-01-01&createdBefore=2024-12-31

# ✅ Sorting (prefix - for descending)
GET /api/v1/users?sort=-createdAt,name
GET /api/v1/posts?sort=-publishedAt

# ✅ Field selection (sparse fieldsets)
GET /api/v1/users?fields=id,email,name

# ✅ Search
GET /api/v1/users?search=john
```

## Versioning

```typescript
// ✅ URL versioning (most common, explicit)
/api/v1/users
/api/v2/users

// ✅ Header versioning (cleaner URLs)
GET /api/users
Accept: application/vnd.myapp.v2+json

// ✅ Version migration — support old + new
// Never break v1 — add new fields, don't remove
// Deprecate with Sunset header
res.set('Sunset', 'Sat, 31 Dec 2025 00:00:00 GMT')
res.set('Deprecation', 'true')
```

## Idempotency

```typescript
// ✅ Idempotency key cho POST (prevent duplicate requests)
router.post('/api/v1/payments', async (req, res) => {
  const idempotencyKey = req.headers['idempotency-key']

  if (idempotencyKey) {
    const cached = await cache.get(`idempotency:${idempotencyKey}`)
    if (cached) {
      return res.status(200).json(JSON.parse(cached))  // Return cached result
    }
  }

  const result = await paymentService.process(req.body)

  if (idempotencyKey) {
    await cache.setEx(`idempotency:${idempotencyKey}`, 86400, JSON.stringify(result))
  }

  res.status(201).json(result)
})
```

## Response Headers chuẩn

```typescript
// ✅ Standard response headers
res.set({
  'X-Request-ID': requestId,
  'X-RateLimit-Limit': '100',
  'X-RateLimit-Remaining': remaining.toString(),
  'X-RateLimit-Reset': resetTime.toString(),
  'Content-Type': 'application/json',
  'Cache-Control': 'no-store',  // For sensitive data
})
```

## Anti-patterns

```
# ❌ Inconsistent naming
/api/getUsers vs /api/user-list vs /api/UserList

# ❌ Exposing internal details
/api/v1/database/users/query
{ "sqlQuery": "SELECT * FROM users" }

# ❌ Using GET for state-changing operations
GET /api/v1/users/123/delete  ❌

# ❌ Returning 200 for errors
HTTP 200
{ "status": "error", "message": "Not found" }  ❌

# ❌ No versioning (breaking changes)
# ❌ Returning all fields including sensitive (password, tokens)
# ❌ Infinite pagination — always cap pageSize (max 100)
```
