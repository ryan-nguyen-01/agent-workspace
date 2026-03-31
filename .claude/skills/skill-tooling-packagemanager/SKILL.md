---
name: skill-tooling-packagemanager
description: Best practices dùng package managers cho Node.js: npm, yarn, pnpm, bun — khi nào dùng cái nào, lockfile, workspace monorepo, scripts và security audit.
---

# Skill: Package Managers (npm / yarn / pnpm / bun)

## Chọn Package Manager

```
pnpm  ← Default recommend cho project mới
  + Nhanh nhất (hard links, content-addressable store)
  + Tiết kiệm disk (không duplicate packages)
  + Strict (không phantom dependencies)
  + Monorepo support tốt
  - Một số tool cũ chưa compatible

bun   ← Khi cần tốc độ tối đa, all-in-one
  + Cực nhanh (install + runtime)
  + Built-in test runner, bundler
  - Ecosystem chưa 100% stable, còn bugs edge cases

yarn (berry/v4) ← Khi team đã quen hoặc cần Plug'n'Play
  + Workspaces mature
  + Zero-install option
  - Config phức tạp hơn

npm   ← Khi cần compatibility tối đa
  + Mặc định với Node.js, không cần cài thêm
  + Mọi tool đều support
  - Chậm hơn pnpm, tốn disk hơn
```

## pnpm — Các lệnh thường dùng

```bash
# Install
pnpm install              # install từ lockfile
pnpm add express          # add dependency
pnpm add -D typescript    # add devDependency
pnpm add -g tsx           # global install
pnpm remove express       # remove

# Run scripts
pnpm dev
pnpm build
pnpm test
pnpm run <script>

# Update
pnpm update               # update trong range của package.json
pnpm update --latest      # update lên latest (ignore range)
pnpm outdated             # xem packages lỗi thời

# Workspace (monorepo)
pnpm --filter @app/backend add express
pnpm --filter @app/frontend dev
pnpm -r build             # chạy build trên tất cả packages

# Audit
pnpm audit
pnpm audit --fix
```

## npm — Các lệnh thường dùng

```bash
npm install               # install từ lockfile
npm install express       # add dependency
npm install -D typescript # add devDependency
npm uninstall express     # remove

npm run dev
npm run build

npm update
npm outdated
npm audit
npm audit fix

# npx — chạy package không cần install global
npx create-next-app@latest my-app
npx prisma migrate dev
```

## yarn — Các lệnh thường dùng

```bash
yarn install
yarn add express
yarn add -D typescript
yarn remove express

yarn dev
yarn build

yarn upgrade
yarn outdated
yarn audit
```

## bun — Các lệnh thường dùng

```bash
bun install
bun add express
bun add -d typescript
bun remove express

bun dev
bun run build
bun test              # built-in test runner

bun update
bun outdated
bun audit
```

## package.json Best Practices

```json
{
  "name": "@myapp/backend",
  "version": "1.0.0",
  "private": true,
  "engines": {
    "node": ">=20.0.0",
    "pnpm": ">=9.0.0"
  },
  "scripts": {
    "dev": "tsx watch src/main.ts",
    "build": "tsc -p tsconfig.build.json",
    "start": "node dist/main.js",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:cov": "vitest run --coverage",
    "lint": "eslint src --ext .ts",
    "lint:fix": "eslint src --ext .ts --fix",
    "format": "prettier --write \"src/**/*.ts\""
  },
  "dependencies": {
    "express": "^4.18.2"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0"
  }
}
```

## Lockfile Rules

```
✅ LUÔN commit lockfile vào git:
  package-lock.json  (npm)
  yarn.lock          (yarn)
  pnpm-lock.yaml     (pnpm)
  bun.lockb          (bun)

✅ Không mix package managers trong 1 project
  → Thêm vào package.json:
  "packageManager": "pnpm@9.0.0"

✅ CI/CD dùng frozen install (không update lockfile):
  npm ci              ← npm
  yarn install --frozen-lockfile
  pnpm install --frozen-lockfile
  bun install --frozen-lockfile
```

## Monorepo với pnpm Workspaces

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

```
project/
├── apps/
│   ├── backend/      package.json: { "name": "@myapp/backend" }
│   └── frontend/     package.json: { "name": "@myapp/frontend" }
├── packages/
│   └── shared/       package.json: { "name": "@myapp/shared" }
├── package.json      (root — chứa scripts và devDeps dùng chung)
└── pnpm-workspace.yaml
```

```bash
# Install shared package vào backend
pnpm --filter @myapp/backend add @myapp/shared

# Chạy lệnh trên tất cả packages
pnpm -r build
pnpm -r test

# Chỉ chạy packages bị ảnh hưởng bởi thay đổi
pnpm --filter "...[origin/main]" build
```

## Security

```bash
# Audit dependencies
pnpm audit                         # xem vulnerabilities
pnpm audit --audit-level=high      # chỉ report high+critical

# Pin exact versions cho production-critical deps
"express": "4.18.2"   ← exact (không ^)

# Review trước khi install package lạ
# Kiểm tra: downloads/week, last publish date, maintainers, repo
```

## Anti-patterns

```
❌ Không commit lockfile → team mỗi người install version khác nhau
❌ npm install trong CI (dùng npm ci thay)
❌ Install global packages trong project setup (dùng npx hoặc pnpm dlx)
❌ Mix package managers (có cả yarn.lock và package-lock.json)
❌ devDependencies trong dependencies → bloat production bundle
❌ * hoặc latest trong version range → non-deterministic builds
```
