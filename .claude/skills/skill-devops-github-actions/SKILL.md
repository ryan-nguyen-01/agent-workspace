---
name: skill-devops-github-actions
description: Best practices viết GitHub Actions workflows: CI/CD pipelines, caching, secrets management, matrix builds, reusable workflows và security hardening.
---

# Skill: GitHub Actions

## CI Pipeline — Node.js

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # ✅ Cancel stale runs on new push

jobs:
  lint-and-test:
    name: Lint & Test
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4
        with:
          version: 9

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm

      # ✅ Cache node_modules
      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.pnpm-store
          key: pnpm-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}
          restore-keys: pnpm-${{ runner.os }}-

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Lint
        run: pnpm lint

      - name: Type check
        run: pnpm type-check

      - name: Run tests
        run: pnpm test --coverage
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379

      # ✅ Upload coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: ./coverage/lcov.info
```

## CD Pipeline — Deploy to Production

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [staging, production]
        default: staging

jobs:
  build-and-push:
    name: Build & Push Docker Image
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      image-digest: ${{ steps.build.outputs.digest }}

    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha,prefix=sha-
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max  # ✅ GitHub Actions cache for Docker layers

  deploy:
    name: Deploy to ${{ inputs.environment || 'staging' }}
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment || 'staging' }}  # ✅ Environment protection rules

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Kubernetes
        uses: azure/k8s-deploy@v4
        with:
          manifests: k8s/
          images: ghcr.io/${{ github.repository }}@${{ needs.build-and-push.outputs.image-digest }}
```

## Reusable Workflow

```yaml
# .github/workflows/_test.yml (reusable)
name: Test (Reusable)

on:
  workflow_call:
    inputs:
      node-version:
        type: string
        default: "20"
    secrets:
      CODECOV_TOKEN:
        required: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
      # ... test steps

# Usage in another workflow
jobs:
  test:
    uses: ./.github/workflows/_test.yml
    with:
      node-version: "20"
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

## Matrix Build

```yaml
# Test across multiple Node versions and OS
jobs:
  test-matrix:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false  # ✅ Don't cancel other jobs if one fails
      matrix:
        os: [ubuntu-latest, macos-latest]
        node-version: [18, 20, 22]
        exclude:
          - os: macos-latest
            node-version: 18  # Skip this combination

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm test
```

## Security Best Practices

```yaml
# ✅ Minimal permissions
permissions:
  contents: read
  packages: write  # Only what's needed

# ✅ Pin action versions (not @main or @v1)
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2

# ✅ Never log secrets
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: |
    # ✅ Use env var, don't echo it
    curl -H "Authorization: Bearer $API_KEY" https://api.example.com/deploy

# ✅ Validate inputs in workflow_dispatch
- name: Validate environment
  run: |
    if [[ "${{ github.event.inputs.environment }}" != "staging" && \
          "${{ github.event.inputs.environment }}" != "production" ]]; then
      echo "Invalid environment"
      exit 1
    fi
```

## Anti-patterns

```yaml
# ❌ Không cache dependencies (chậm)
- run: npm install  # Downloads mỗi run!
# ✅ actions/cache hoặc cache: npm trong setup-node

# ❌ Secrets trong run commands
- run: echo "DB_PASSWORD=mysecret" >> .env  # Hiện trong logs!

# ❌ Không pin action versions
- uses: actions/checkout@main  # Có thể bị compromised!

# ❌ Quá nhiều permissions
permissions:
  contents: write
  packages: write
  pull-requests: write  # Cho workflow chỉ cần test!

# ❌ Không có concurrency control → nhiều deployments song song
```
