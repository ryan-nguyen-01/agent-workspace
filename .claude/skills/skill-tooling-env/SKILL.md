---
name: skill-tooling-env
description: Best practices quản lý environment variables: .env files, validate config với Zod, secrets management và tránh leak credentials.
---

# Skill: Environment & Config Management

## .env File Structure

```bash
# .env.example  ← commit vào git (template, không có values thật)
# .env          ← KHÔNG commit (gitignore)
# .env.local    ← override local, KHÔNG commit
# .env.test     ← cho test environment

# Server
NODE_ENV=development
PORT=3000
APP_URL=http://localhost:3000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# Redis
REDIS_URL=redis://localhost:6379

# Auth
JWT_SECRET=your-secret-here
JWT_EXPIRES_IN=15m
JWT_REFRESH_EXPIRES_IN=7d

# Storage
S3_ENDPOINT=http://localhost:9000
S3_BUCKET=myapp
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin

# External APIs
SENDGRID_API_KEY=SG.xxx
```

## Validate với Zod (TypeScript)

```typescript
// config/env.ts
import { z } from 'zod'

const envSchema = z.object({
  // Server
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.coerce.number().default(3000),
  APP_URL: z.string().url(),

  // Database
  DATABASE_URL: z.string().min(1, 'DATABASE_URL is required'),

  // Redis
  REDIS_URL: z.string().url().optional(),

  // Auth
  JWT_SECRET: z.string().min(32, 'JWT_SECRET must be at least 32 characters'),
  JWT_EXPIRES_IN: z.string().default('15m'),

  // External
  SENDGRID_API_KEY: z.string().optional(),
})

// ✅ Validate khi app start — fail fast nếu thiếu biến
const parsed = envSchema.safeParse(process.env)

if (!parsed.success) {
  console.error('❌ Invalid environment variables:')
  console.error(parsed.error.flatten().fieldErrors)
  process.exit(1)
}

export const env = parsed.data

// Usage: import { env } from '@/config/env'
// env.DATABASE_URL → type-safe, validated
```

## NestJS Config Module

```typescript
// config/configuration.ts
import { z } from 'zod'

const schema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string(),
  JWT_SECRET: z.string().min(32),
  REDIS_URL: z.string().optional(),
})

export type AppConfig = z.infer<typeof schema>

export default () => {
  const parsed = schema.safeParse(process.env)
  if (!parsed.success) {
    throw new Error(`Config validation error: ${parsed.error.message}`)
  }
  return parsed.data
}

// app.module.ts
import { ConfigModule } from '@nestjs/config'
import configuration from './config/configuration'

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [configuration],
      cache: true,
    }),
  ],
})
export class AppModule {}

// Usage trong service
constructor(private config: ConfigService<AppConfig>) {}
const secret = this.config.get('JWT_SECRET', { infer: true }) // type-safe
```

## Python (Pydantic Settings)

```python
# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, PostgresDsn

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
    )

    # Server
    node_env: str = 'development'
    port: int = 8000
    app_url: str

    # Database
    database_url: PostgresDsn

    # Auth
    jwt_secret: str
    jwt_expires_in: int = 900  # seconds

    @field_validator('jwt_secret')
    @classmethod
    def jwt_secret_min_length(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError('JWT_SECRET must be at least 32 characters')
        return v

# Singleton
settings = Settings()

# Usage: from config import settings
```

## Secrets Management

```
Local Development:
→ .env file (gitignored)
→ Chia sẻ qua password manager (1Password, Bitwarden)
→ KHÔNG chia sẻ qua Slack/email

Staging/Production:
→ Cloud provider secrets:
   AWS: Secrets Manager / Parameter Store
   GCP: Secret Manager
   Azure: Key Vault
→ Kubernetes: Sealed Secrets / External Secrets Operator
→ HashiCorp Vault (self-hosted)

CI/CD:
→ GitHub Actions: Settings → Secrets and variables
→ KHÔNG hardcode secrets trong workflow files
```

```yaml
# ✅ GitHub Actions — dùng secrets
- name: Deploy
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    JWT_SECRET: ${{ secrets.JWT_SECRET }}
  run: npm run deploy
```

## .gitignore — env files

```gitignore
# Environment files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# ✅ Commit những file này (templates):
# .env.example
# .env.test (nếu chỉ có values không nhạy cảm)
```

## Anti-patterns

```
❌ Hardcode secrets trong code
const secret = 'my-super-secret'  // ❌

❌ .env trong git (kể cả private repo)
→ Rotate tất cả credentials ngay nếu đã commit

❌ Không validate env khi start → app crash ở runtime với lỗi khó debug
→ Validate với Zod/Pydantic và fail fast khi start

❌ process.env.MY_VAR trực tiếp khắp nơi trong code
→ Centralize trong config module, type-safe

❌ Cùng 1 .env cho local và production
→ Mỗi environment có values riêng

❌ Chia sẻ secrets qua Slack/email/chat
→ Dùng password manager hoặc secrets vault
```
