---
name: skill-auth-oauth2
description: Best practices implement OAuth2/OIDC: authorization code flow với PKCE, token exchange, provider integration và security patterns.
---

# Skill: OAuth2 / OpenID Connect

## Authorization Code Flow với PKCE

```typescript
import crypto from 'crypto'

// ✅ PKCE — bắt buộc cho public clients (SPA, mobile)
function generatePKCE(): { verifier: string; challenge: string } {
  const verifier = crypto.randomBytes(32).toString('base64url')
  const challenge = crypto
    .createHash('sha256')
    .update(verifier)
    .digest('base64url')
  return { verifier, challenge }
}

// Step 1: Build authorization URL
function buildAuthorizationUrl(provider: OAuthProvider, state: string, pkce: { challenge: string }): string {
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: provider.clientId,
    redirect_uri: provider.redirectUri,
    scope: 'openid email profile',
    state,  // CSRF protection
    code_challenge: pkce.challenge,
    code_challenge_method: 'S256',
  })
  return `${provider.authorizationEndpoint}?${params}`
}

// Step 2: Initiate login
router.get('/auth/login', (req, res) => {
  const state = crypto.randomBytes(16).toString('hex')
  const pkce = generatePKCE()

  // Store in session (server-side) — không dùng cookie/localStorage cho verifier!
  req.session.oauthState = state
  req.session.pkceVerifier = pkce.verifier

  res.redirect(buildAuthorizationUrl(googleProvider, state, pkce))
})
```

## Callback & Token Exchange

```typescript
// Step 3: Handle callback
router.get('/auth/callback', async (req, res, next) => {
  const { code, state, error } = req.query

  // ✅ Validate state (CSRF check)
  if (state !== req.session.oauthState) {
    return next(new UnauthorizedError('Invalid OAuth state'))
  }

  if (error) {
    return next(new UnauthorizedError(`OAuth error: ${error}`))
  }

  try {
    // Step 4: Exchange code for tokens
    const tokens = await exchangeCodeForTokens({
      code: code as string,
      verifier: req.session.pkceVerifier!,
    })

    // Step 5: Get user info from ID token or userinfo endpoint
    const userInfo = await getUserInfo(tokens.idToken || tokens.accessToken)

    // Step 6: Find or create user
    const user = await userService.findOrCreateByOAuth({
      provider: 'google',
      providerId: userInfo.sub,
      email: userInfo.email,
      name: userInfo.name,
    })

    // Step 7: Issue app tokens
    const appTokens = generateTokens(user)
    setRefreshTokenCookie(res, appTokens.refreshToken)

    // Clean up session
    delete req.session.oauthState
    delete req.session.pkceVerifier

    res.redirect(`/dashboard?token=${appTokens.accessToken}`)
  } catch (err) {
    next(err)
  }
})

async function exchangeCodeForTokens(params: { code: string; verifier: string }) {
  const response = await fetch(googleProvider.tokenEndpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code: params.code,
      redirect_uri: googleProvider.redirectUri,
      client_id: googleProvider.clientId,
      client_secret: googleProvider.clientSecret,
      code_verifier: params.verifier,
    }),
  })

  if (!response.ok) throw new UnauthorizedError('Token exchange failed')
  return response.json()
}
```

## Provider Configuration

```typescript
interface OAuthProvider {
  name: string
  clientId: string
  clientSecret: string
  redirectUri: string
  authorizationEndpoint: string
  tokenEndpoint: string
  userInfoEndpoint: string
  scopes: string[]
}

const googleProvider: OAuthProvider = {
  name: 'google',
  clientId: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  redirectUri: `${process.env.APP_URL}/auth/callback`,
  authorizationEndpoint: 'https://accounts.google.com/o/oauth2/v2/auth',
  tokenEndpoint: 'https://oauth2.googleapis.com/token',
  userInfoEndpoint: 'https://www.googleapis.com/oauth2/v3/userinfo',
  scopes: ['openid', 'email', 'profile'],
}

// ✅ Verify ID token với JWKS
import * as jose from 'jose'

async function verifyIdToken(idToken: string) {
  const JWKS = jose.createRemoteJWKSet(
    new URL('https://www.googleapis.com/oauth2/v3/certs')
  )
  const { payload } = await jose.jwtVerify(idToken, JWKS, {
    issuer: 'https://accounts.google.com',
    audience: process.env.GOOGLE_CLIENT_ID,
  })
  return payload
}
```

## Database Schema cho OAuth

```sql
-- ✅ Separate table cho OAuth accounts (user có thể link nhiều providers)
CREATE TABLE oauth_accounts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider    VARCHAR(50) NOT NULL,       -- 'google', 'github', etc.
    provider_id VARCHAR(255) NOT NULL,      -- Provider's user ID
    email       VARCHAR(255),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (provider, provider_id)
);
```

```typescript
// ✅ findOrCreateByOAuth — atomic operation
async function findOrCreateByOAuth(data: {
  provider: string
  providerId: string
  email: string
  name: string
}): Promise<User> {
  // Try to find existing OAuth link
  const existing = await db.oauthAccounts.findOne({
    where: { provider: data.provider, providerId: data.providerId },
    include: ['user'],
  })
  if (existing) return existing.user

  // Find user by email or create new
  const user = await db.users.findOrCreate({
    where: { email: data.email },
    defaults: { name: data.name, emailVerified: true },
  })

  // Link OAuth account
  await db.oauthAccounts.create({
    userId: user.id,
    provider: data.provider,
    providerId: data.providerId,
    email: data.email,
  })

  return user
}
```

## Anti-patterns

```typescript
// ❌ Không validate state parameter (CSRF vulnerability)
router.get('/callback', async (req, res) => {
  const { code } = req.query
  const tokens = await exchange(code)  // State không check!
})

// ❌ Lưu client_secret trong frontend code
const clientSecret = 'abc123'  // Exposed to users!
// ✅ Token exchange chỉ xảy ra ở backend

// ❌ Không dùng PKCE cho public clients
// PKCE bắt buộc cho SPA và mobile apps

// ❌ Trust unverified user info từ provider response
const email = response.email  // Không verify ID token!
// ✅ Luôn verify ID token với provider's JWKS trước khi dùng claims

// ❌ Lưu OAuth access tokens lâu dài trong DB
// Provider tokens nên được dùng ngay, không lưu trừ khi cần offline access
```
