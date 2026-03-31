---
name: skill-arch-security
description: Security architecture — defense in depth, zero-trust, encryption (at rest/in transit), network security, secrets management, threat modeling (STRIDE), compliance basics.
---

# Skill: Security Architecture

## Defense in Depth

```
Internet → WAF/DDoS Protection → Load Balancer (SSL termination)
  → API Gateway (auth, rate limit) → Application (validation, authz)
    → Service Mesh (mTLS) → Database (encryption at rest, ACL)
      → Secrets Manager → Audit Log
```

---

## Zero-Trust Architecture

```yaml
principle: "Never trust, always verify — regardless of network location"

rules:
  verify_explicitly:
    - Authenticate every request (no implicit trust from VPN/internal network)
    - Verify user identity + device health + context
    - MFA for sensitive operations

  least_privilege:
    - Minimum permissions needed for the task
    - Time-limited access (just-in-time)
    - Scope tokens to specific resources

  assume_breach:
    - Encrypt all traffic (even internal — mTLS)
    - Segment network (microsegmentation)
    - Log everything for forensics
    - Minimize blast radius

implementation:
  internal_services: "mTLS between all services (Istio/Linkerd)"
  database: "Per-service DB credentials, no shared accounts"
  secrets: "Vault with auto-rotation, never in code/config"
  network: "Network policies deny-all by default, allow-list specific flows"
```

---

## Encryption

### In Transit

```yaml
external:
  protocol: TLS 1.3 (minimum TLS 1.2)
  config: |
    # Nginx
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers on;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
  cert_management: "Let's Encrypt (auto-renew) or AWS ACM"

internal (service-to-service):
  protocol: mTLS (mutual TLS — both sides verify)
  tools: [Istio, Linkerd, Consul Connect]
  benefit: "Zero-trust internal network, service identity verification"
  implementation: |
    # Istio PeerAuthentication
    apiVersion: security.istio.io/v1
    kind: PeerAuthentication
    spec:
      mtls:
        mode: STRICT  # Reject non-mTLS traffic
```

### At Rest

```yaml
database:
  transparent_encryption: "TDE (PostgreSQL, MySQL) — encrypt data files on disk"
  column_level: "Encrypt specific columns (PII, payment data)"
  application_level: |
    // Encrypt before storing, decrypt after reading
    import { createCipheriv, createDecipheriv, randomBytes } from 'crypto'
    
    function encrypt(data: string, key: Buffer): { encrypted: string; iv: string } {
      const iv = randomBytes(16)
      const cipher = createCipheriv('aes-256-gcm', key, iv)
      let encrypted = cipher.update(data, 'utf8', 'hex')
      encrypted += cipher.final('hex')
      const tag = cipher.getAuthTag().toString('hex')
      return { encrypted: encrypted + tag, iv: iv.toString('hex') }
    }

file_storage:
  s3: "SSE-S3 (AWS managed) or SSE-KMS (customer managed key)"
  config: |
    aws s3api put-bucket-encryption --bucket my-bucket --server-side-encryption-configuration '{
      "Rules": [{ "ApplyServerSideEncryptionByDefault": { "SSEAlgorithm": "aws:kms" } }]
    }'

key_management:
  tools: [AWS KMS, HashiCorp Vault, Google Cloud KMS, Azure Key Vault]
  rotation: "Rotate keys every 90 days (automated)"
  envelope_encryption: |
    Data encrypted with DEK (Data Encryption Key)
    DEK encrypted with KEK (Key Encryption Key in KMS)
    → Only KEK needs secure storage in HSM
```

---

## Secrets Management

```yaml
NEVER:
  - Hardcode secrets in source code
  - Commit .env files to git
  - Pass secrets via command line arguments (visible in ps)
  - Log secrets (even accidentally)
  - Share secrets via Slack/email

DO:
  - Use secrets manager (Vault, AWS Secrets Manager, Doppler)
  - Inject at runtime via environment variables
  - Rotate automatically
  - Audit access logs

tools:
  hashicorp_vault:
    features: [dynamic secrets, auto-rotation, audit log, encryption as service]
    pattern: |
      // App requests DB credentials at startup
      const creds = await vault.read('database/creds/my-role')
      // Vault generates short-lived credentials (1h TTL)
      // Auto-renew before expiry

  aws_secrets_manager:
    features: [auto-rotation, CloudFormation integration, cross-account]
    pattern: |
      const secret = await secretsManager.getSecretValue({ SecretId: 'prod/db/password' })
      // Cache in memory, refresh every 1h

  env_files:
    acceptable: ".env for LOCAL development only"
    required: ".env in .gitignore ALWAYS"
    template: ".env.example with placeholder values committed"
```

---

## Threat Modeling (STRIDE)

```yaml
framework: STRIDE — 6 threat categories

S - Spoofing (giả mạo danh tính):
  threat: "Attacker pretends to be another user/service"
  mitigations:
    - Strong authentication (JWT with proper validation)
    - mTLS for service-to-service
    - API keys with rotation
  check: "Mọi endpoint có auth? Service calls có mTLS?"

T - Tampering (giả mạo dữ liệu):
  threat: "Attacker modifies data in transit or at rest"
  mitigations:
    - TLS for all communication
    - Input validation (server-side, never trust client)
    - Digital signatures for critical data
    - Database integrity constraints
  check: "Input validation mọi endpoint? Signed tokens?"

R - Repudiation (chối bỏ hành động):
  threat: "User denies performing action, no proof"
  mitigations:
    - Audit logging (immutable)
    - Timestamp + user ID on every action
    - Digital signatures for critical transactions
  check: "Sensitive actions có audit log? Logs tamper-proof?"

I - Information Disclosure (lộ thông tin):
  threat: "Sensitive data exposed to unauthorized parties"
  mitigations:
    - Encryption at rest and in transit
    - Principle of least privilege
    - Error messages don't leak internals
    - PII masking in logs
  check: "Error responses có leak stack trace? Logs có PII?"

D - Denial of Service:
  threat: "Attacker makes system unavailable"
  mitigations:
    - Rate limiting
    - WAF (Web Application Firewall)
    - DDoS protection (CloudFlare, AWS Shield)
    - Resource limits (request size, timeout)
    - Auto-scaling
  check: "Rate limit trên mọi public endpoint? Max request size?"

E - Elevation of Privilege:
  threat: "User gains higher permissions than authorized"
  mitigations:
    - RBAC/ABAC with proper checks
    - Authorization on every endpoint (not just frontend)
    - No default admin accounts
    - Principle of least privilege
  check: "Server-side authz check? IDOR prevention? Admin endpoints protected?"
```

---

## Network Security

```yaml
waf:
  description: Web Application Firewall — filter malicious HTTP traffic
  rules: [SQL injection, XSS, path traversal, bot detection]
  tools: [AWS WAF, Cloudflare WAF, ModSecurity]

network_segmentation:
  description: Isolate networks by trust level
  zones:
    public: "Load balancer, CDN edge"
    dmz: "API gateway, reverse proxy"
    application: "App servers (no direct internet)"
    data: "Databases, caches (no internet, app access only)"
  implementation: |
    # Kubernetes NetworkPolicy
    apiVersion: networking.k8s.io/v1
    kind: NetworkPolicy
    spec:
      podSelector:
        matchLabels:
          app: database
      ingress:
        - from:
            - podSelector:
                matchLabels:
                  app: api-server
          ports:
            - port: 5432

security_headers:
  required: |
    Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
    Content-Security-Policy: default-src 'self'; script-src 'self'
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY
    X-XSS-Protection: 0  (deprecated, rely on CSP)
    Referrer-Policy: strict-origin-when-cross-origin
    Permissions-Policy: camera=(), microphone=(), geolocation=()

cors:
  config: |
    // ✅ Restrictive
    {
      origin: ['https://myapp.com', 'https://admin.myapp.com'],
      methods: ['GET', 'POST', 'PUT', 'DELETE'],
      credentials: true,
      maxAge: 86400,
    }
    // ❌ NEVER: origin: '*' with credentials: true

ddos_protection:
  layers:
    L3/L4: "AWS Shield, Cloudflare (volumetric attacks)"
    L7: "WAF rules, rate limiting, CAPTCHA"
    application: "Request size limits, timeout, connection limits"
```

---

## Compliance Basics

```yaml
gdpr:
  scope: EU user data
  requirements:
    - Right to erasure (delete user data on request)
    - Data portability (export user data)
    - Consent tracking (opt-in, not opt-out)
    - DPO (Data Protection Officer) for large orgs
    - 72h breach notification
  implementation:
    - PII inventory (know where PII lives)
    - Soft delete with hard delete scheduler
    - Consent management system
    - Audit trail for data access

pci_dss:
  scope: Payment card data
  requirements:
    - Never store CVV
    - Encrypt cardholder data
    - Network segmentation for cardholder data environment
    - Regular security assessments
  implementation:
    - Use payment provider (Stripe, Braintree) — they handle PCI
    - Never let card numbers touch your servers
    - Tokenization for recurring payments

hipaa:
  scope: Healthcare data (US)
  requirements:
    - Encryption at rest and in transit
    - Access controls and audit logs
    - BAA (Business Associate Agreement) with cloud providers
```

---

## Anti-patterns

```yaml
security_through_obscurity:
  bad: "Hide admin panel at /secret-admin-panel-xyz"
  fix: "Proper auth + authz, assume URLs discoverable"

client_side_validation_only:
  bad: "Validate in React, not in API"
  fix: "ALWAYS validate server-side (client validation = UX only)"

overly_permissive_cors:
  bad: "Access-Control-Allow-Origin: *"
  fix: "Whitelist specific origins"

logging_sensitive_data:
  bad: "logger.info('User login', { password: req.body.password })"
  fix: "Sanitize logs, redact PII/secrets"

shared_service_account:
  bad: "All services use same DB user 'admin'"
  fix: "Per-service credentials with minimum permissions"
```
