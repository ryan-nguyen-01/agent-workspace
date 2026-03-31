---
name: skill-devops-container-security
description: Container security — image scanning, non-root user, minimal base images, secrets handling, runtime security, read-only filesystem, resource limits, và supply chain protection.
---

# Skill: Container Security

## Secure Dockerfile

```dockerfile
# ✅ Multi-stage build — minimal final image
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build

# ✅ Minimal runtime image
FROM node:20-alpine AS runtime
WORKDIR /app

# ✅ Non-root user
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser

# ✅ Only copy what's needed
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/package.json ./

# ✅ Drop all capabilities
USER appuser

# ✅ Health check
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

EXPOSE 3000
CMD ["node", "dist/main.js"]
```

### Dockerfile Rules

```yaml
base_image:
  do: "Use specific tag: node:20.11-alpine (not node:latest)"
  why: "Reproducible builds, known vulnerabilities"
  prefer: "Alpine (5MB) or Distroless (no shell, no package manager)"
  avoid: "Ubuntu/Debian full images (100MB+ attack surface)"

non_root:
  do: "Create dedicated user, switch with USER directive"
  why: "Container escape as root = host root access"
  exception: "Only root for port < 1024 (use port > 1024 instead)"

no_secrets:
  do: "Use runtime env vars or mounted secrets"
  never: "COPY .env, ARG PASSWORD=xxx, ENV API_KEY=xxx in Dockerfile"
  why: "Docker image layers are inspectable (docker history)"

minimal_copy:
  do: "COPY only built artifacts + dependencies"
  never: "COPY . . in final stage (includes source, tests, .git)"

.dockerignore: |
  .git
  .env*
  node_modules
  *.md
  tests/
  .github/
  docker-compose*.yml
```

---

## Image Scanning

```yaml
tools:
  trivy: "Open source, fast, comprehensive (Aqua Security)"
  grype: "Open source, Anchore ecosystem"
  snyk_container: "Commercial, deep analysis"
  docker_scout: "Docker native scanning"

ci_integration: |
  # GitHub Actions — scan on every PR
  - name: Scan image with Trivy
    uses: aquasecurity/trivy-action@master
    with:
      image-ref: myapp:${{ github.sha }}
      format: table
      exit-code: 1                    # fail CI on HIGH/CRITICAL
      severity: HIGH,CRITICAL
      ignore-unfixed: true

  # Local scan
  trivy image myapp:latest
  trivy image --severity HIGH,CRITICAL --exit-code 1 myapp:latest

scan_frequency:
  build_time: "Every CI build (catch new vulns in code/deps)"
  registry: "Daily scan of stored images (catch newly disclosed CVEs)"
  runtime: "Weekly scan of running containers"

vulnerability_policy:
  critical: "Block deployment. Fix within 24h."
  high: "Block deployment. Fix within 7 days."
  medium: "Warning. Fix within 30 days."
  low: "Track. Fix when convenient."
```

---

## Runtime Security

### Read-Only Filesystem

```yaml
# docker-compose.yml
services:
  api:
    image: myapp:latest
    read_only: true                # ✅ read-only root filesystem
    tmpfs:
      - /tmp                       # writable tmp (for uploads, temp files)
      - /app/logs                  # writable logs directory
    security_opt:
      - no-new-privileges:true     # ✅ prevent privilege escalation
```

```yaml
# Kubernetes
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: api
      image: myapp:latest
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        readOnlyRootFilesystem: true
        allowPrivilegeEscalation: false
        capabilities:
          drop: ["ALL"]            # ✅ drop all Linux capabilities
      volumeMounts:
        - name: tmp
          mountPath: /tmp
  volumes:
    - name: tmp
      emptyDir:
        sizeLimit: 100Mi
```

### Resource Limits

```yaml
# Prevent container from consuming all host resources
# docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M

# Kubernetes
resources:
  requests:
    cpu: 250m
    memory: 128Mi
  limits:
    cpu: "1"
    memory: 512Mi
```

### Network Policies

```yaml
# Kubernetes — restrict container communication
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-policy
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: ingress-controller
      ports:
        - port: 3000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: database
      ports:
        - port: 5432
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - port: 6379
```

---

## Secrets in Containers

```yaml
never:
  - "Environment variables in docker-compose.yml (committed to git)"
  - "Secrets baked into image (COPY .env)"
  - "Docker build args for secrets (visible in image history)"

do:
  docker_compose: |
    # Use .env file (not committed) or Docker secrets
    services:
      api:
        env_file: .env  # gitignored
        # OR Docker secrets (Swarm mode)
        secrets:
          - db_password

  kubernetes: |
    # Kubernetes Secrets (base64, not encrypted by default)
    apiVersion: v1
    kind: Secret
    metadata:
      name: api-secrets
    type: Opaque
    data:
      DATABASE_URL: <base64>

    # Better: External Secrets Operator + Vault/AWS Secrets Manager
    apiVersion: external-secrets.io/v1
    kind: ExternalSecret
    spec:
      secretStoreRef:
        name: vault-backend
      target:
        name: api-secrets
      data:
        - secretKey: DATABASE_URL
          remoteRef:
            key: myapp/database
            property: url
```

---

## Supply Chain Security

```yaml
signed_images:
  tool: "cosign (Sigstore)"
  workflow: |
    # Sign image after build
    cosign sign myregistry/myapp:v1.0.0

    # Verify before deploy
    cosign verify myregistry/myapp:v1.0.0

base_image_pinning:
  do: "Pin by digest: FROM node:20@sha256:abc123..."
  why: "Tag can be overwritten, digest is immutable"

sbom:
  tool: "syft (generate SBOM), grype (scan SBOM)"
  command: |
    syft myapp:latest -o spdx-json > sbom.json
    grype sbom:sbom.json
```

---

## Anti-patterns

```yaml
root_user:
  bad: "Container runs as root (default)"
  fix: "USER directive + runAsNonRoot in K8s"

latest_tag:
  bad: "FROM node:latest — unpredictable, unreproducible"
  fix: "FROM node:20.11-alpine — specific version"

secrets_in_env:
  bad: "ENV DATABASE_PASSWORD=mysecret in Dockerfile"
  fix: "Runtime injection: docker run -e or Kubernetes secrets"

no_resource_limits:
  bad: "Container can use 100% CPU/RAM → affects other containers"
  fix: "Set CPU/memory limits in compose/K8s"

writable_filesystem:
  bad: "Container has full write access to filesystem"
  fix: "readOnlyRootFilesystem: true + tmpfs for writable dirs"
```
