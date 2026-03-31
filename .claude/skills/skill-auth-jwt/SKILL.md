---
name: skill-auth-jwt
description: Best practices implement JWT authentication: token generation, validation, refresh token rotation, security headers và common attack prevention.
---

# Skill: JWT Authentication

## Token Structure & Generation

```typescript
import jwt from 'jsonwebtoken'
import crypto from 'crypto'

interface TokenPayload {
  sub: string       // user ID
  email: string
  roles: string[]
  type: 'access' | 'refresh'
  jti: string       // unique token ID (for revocation)
}

const ACCESS_TOKEN_TTL = '15m'
const REFRESH_TOKEN_TTL = '7d'

function generateTokens(user: { id: string; email: string; roles: string[] }) {
  const jti = crypto.randomUUID()

  const accessToken = jwt.sign(
    {
      sub: user.id,
      email: user.email,
      roles: user.roles,
      type: 'access',
      jti,
    } satisfies TokenPayload,
    process.env.JWT_SECRET!,
    { expiresIn: ACCESS_TOKEN_TTL, issuer: 'myapp', audience: 'myapp-client' }
  )

  const refreshToken = jwt.sign(
    { sub: user.id, type: 'refresh', jti: crypto.randomUUID() } satisfies Partial<TokenPayload>,
    process.env.JWT_REFRESH_SECRET!,
    { expiresIn: REFRESH_TOKEN_TTL }
  )

  return { accessToken, refreshToken }
}
```

## Token Validation

```typescript
// ✅ Verify with all claims
function verifyAccessToken(token: string): TokenPayload {
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET!, {
      issuer: 'myapp',
      audience: 'myapp-client',
    }) as TokenPayload

    if (payload.type !== 'access') {
      throw new UnauthorizedError('Invalid token type')
    }

    return payload
  } catch (err) {
    if (err instanceof jwt.TokenExpiredError) {
      throw new UnauthorizedError('Token expired')
    }
    if (err instanceof jwt.JsonWebTokenError) {
      throw new UnauthorizedError('Invalid token')
    }
    throw err
  }
}

// ✅ Auth middleware
function authenticate(req: Request, res: Response, next: NextFunction): void {
  const authHeader = req.headers.authorization
  if (!authHeader?.startsWith('Bearer ')) {
    return next(new UnauthorizedError('Missing authorization header'))
  }

  const token = authHeader.slice(7)  // Remove "Bearer "
  try {
    req.user = verifyAccessToken(token)
    next()
  } catch (err) {
    next(err)
  }
}
```

## Refresh Token Rotation

```typescript
// ✅ Rotate refresh tokens — one-time use
async function refreshTokens(refreshToken: string): Promise<{ accessToken: string; refreshToken: string }> {
  // 1. Verify signature
  const payload = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET!) as TokenPayload

  if (payload.type !== 'refresh') {
    throw new UnauthorizedError('Invalid token type')
  }

  // 2. Check if token has been used (revoked)
  const isRevoked = await tokenStore.isRevoked(payload.jti)
  if (isRevoked) {
    // Possible token theft — revoke all tokens for user
    await tokenStore.revokeAllForUser(payload.sub)
    throw new UnauthorizedError('Refresh token reuse detected')
  }

  // 3. Revoke current refresh token
  await tokenStore.revoke(payload.jti)

  // 4. Issue new token pair
  const user = await userRepo.findById(payload.sub)
  if (!user || !user.isActive) {
    throw new UnauthorizedError('User not found or inactive')
  }

  return generateTokens(user)
}
```

## Secure Cookie Setup

```typescript
// ✅ HttpOnly cookie cho refresh token
function setRefreshTokenCookie(res: Response, token: string): void {
  res.cookie('refresh_token', token, {
    httpOnly: true,         // Không accessible via JS
    secure: true,           // HTTPS only
    sameSite: 'strict',     // CSRF protection
    maxAge: 7 * 24 * 60 * 60 * 1000,  // 7 days
    path: '/api/auth/refresh',  // Chỉ gửi đến refresh endpoint
  })
}

// Login endpoint
router.post('/login', async (req, res) => {
  const { email, password } = req.body
  const user = await authService.validateCredentials(email, password)
  const { accessToken, refreshToken } = generateTokens(user)

  setRefreshTokenCookie(res, refreshToken)

  // ✅ Access token trong response body (short-lived, ok)
  // ✅ Refresh token trong HttpOnly cookie (long-lived, safe)
  res.json({ accessToken, user: { id: user.id, email: user.email } })
})
```

## Role-Based Authorization

```typescript
// ✅ Role guard middleware
function requireRoles(...roles: string[]) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const userRoles = req.user?.roles ?? []
    const hasRole = roles.some(role => userRoles.includes(role))

    if (!hasRole) {
      return next(new ForbiddenError(`Requires one of: ${roles.join(', ')}`))
    }
    next()
  }
}

// Usage
router.delete('/users/:id', authenticate, requireRoles('admin'), controller.delete)
router.get('/users', authenticate, requireRoles('admin', 'moderator'), controller.list)
```

## Security Best Practices

```typescript
// ✅ Brute force protection
const loginAttemptCache = new Map<string, { count: number; lockedUntil?: Date }>()

async function checkLoginAttempts(email: string): Promise<void> {
  const record = loginAttemptCache.get(email)
  if (record?.lockedUntil && record.lockedUntil > new Date()) {
    throw new TooManyRequestsError('Account temporarily locked')
  }
}

async function recordFailedAttempt(email: string): Promise<void> {
  const record = loginAttemptCache.get(email) ?? { count: 0 }
  record.count++
  if (record.count >= 5) {
    record.lockedUntil = new Date(Date.now() + 15 * 60 * 1000)  // 15 min
  }
  loginAttemptCache.set(email, record)
}
```

## Anti-patterns

```typescript
// ❌ Lưu sensitive data trong JWT payload
jwt.sign({ password: user.password, ssn: '123-45-6789' }, secret)
// JWT payload chỉ được base64 encoded, không encrypted!

// ❌ Không set expiration
jwt.sign({ sub: userId }, secret)  // Never expires! ❌
// ✅ Luôn set expiresIn

// ❌ Dùng cùng secret cho access và refresh tokens
jwt.sign(accessPayload, process.env.JWT_SECRET)
jwt.sign(refreshPayload, process.env.JWT_SECRET)  // ❌ Same secret!

// ❌ Lưu JWT trong localStorage (XSS vulnerability)
localStorage.setItem('token', accessToken)  // ❌
// ✅ Access token in memory, refresh token in HttpOnly cookie

// ❌ Verify không check type
const payload = jwt.verify(token, secret)  // Refresh token passed as access? ❌
```
