---
name: skill-framework-encore
description: Best practices Encore.ts — TypeScript backend framework với built-in infra (API, PubSub, Cron, Secrets, DB), local dashboard, và cloud deployment.
---

# Skill: Encore.ts

## Khi nào dùng

- TypeScript backend cần infra built-in (không muốn cấu hình thủ công)
- Multi-service architecture với type-safe service-to-service calls
- PubSub, Cron, Secrets không cần config bên ngoài
- Deploy lên Encore Cloud, AWS, hoặc GCP

---

## Project structure

```
encore.app              # App manifest
services/
  users/
    encore.service.ts   # Service declaration
    users.ts            # API endpoints
    db.ts               # Database schema
  payments/
    encore.service.ts
    payments.ts
    subscription.ts     # PubSub subscriber
shared/
  types.ts
```

---

## Service declaration

```typescript
// services/users/encore.service.ts
import { Service } from "encore.dev/service";

export default new Service("users");
```

---

## API endpoints

```typescript
// services/users/users.ts
import { api } from "encore.dev/api";
import { db } from "./db";

interface GetUserParams {
  id: string;
}

interface User {
  id: string;
  email: string;
  name: string;
}

// GET /users/:id — public
export const getUser = api(
  { expose: true, method: "GET", path: "/users/:id" },
  async ({ id }: GetUserParams): Promise<User> => {
    const user = await db.queryRow`
      SELECT id, email, name FROM users WHERE id = ${id}
    `;
    if (!user) throw new Error(`User ${id} not found`);
    return user;
  },
);

// POST /users — requires auth
export const createUser = api(
  { expose: true, method: "POST", path: "/users", auth: true },
  async (params: { email: string; name: string }): Promise<User> => {
    const user = await db.queryRow`
      INSERT INTO users (email, name)
      VALUES (${params.email}, ${params.name})
      RETURNING id, email, name
    `;
    // Publish event
    await userCreated.publish({ userId: user!.id });
    return user!;
  },
);

// Internal endpoint — service-to-service only
export const getUserInternal = api(
  { expose: false },
  async ({ id }: GetUserParams): Promise<User> => {
    // ...
  },
);
```

---

## Database (SQLite / PostgreSQL)

```typescript
// services/users/db.ts
import { SQLDatabase } from "encore.dev/storage/sqldb";

export const db = new SQLDatabase("users", {
  migrations: "./migrations",
});

// migrations/1_create_users.up.sql
// CREATE TABLE users (
//   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
//   email TEXT UNIQUE NOT NULL,
//   name TEXT NOT NULL,
//   created_at TIMESTAMPTZ DEFAULT NOW()
// );
```

---

## PubSub

```typescript
// services/users/events.ts
import { Topic, Subscription } from "encore.dev/pubsub";

interface UserCreatedEvent {
  userId: string;
}

export const userCreated = new Topic<UserCreatedEvent>("user-created", {
  deliveryGuarantee: "at-least-once",
});

// services/payments/subscription.ts — subscriber trong service khác
import { Subscription } from "encore.dev/pubsub";
import { userCreated } from "../../services/users/events";

export const _ = new Subscription(userCreated, "send-welcome-email", {
  handler: async ({ userId }) => {
    const user = await users.getUserInternal({ id: userId });
    await sendWelcomeEmail(user.email);
  },
});
```

---

## Cron jobs

```typescript
// services/users/cleanup.ts
import { CronJob } from "encore.dev/cron";

export const dailyCleanup = new CronJob("daily-cleanup", {
  title: "Daily Cleanup",
  schedule: "0 2 * * *", // 2am daily
  endpoint: cleanupInactiveUsers,
});

export const cleanupInactiveUsers = api(
  { expose: false },
  async (): Promise<{ deleted: number }> => {
    const result = await db.exec`
      DELETE FROM users WHERE last_active < NOW() - INTERVAL '90 days'
    `;
    return { deleted: result.rowsAffected };
  },
);
```

---

## Secrets

```typescript
import { secret } from "encore.dev/config"

const stripeKey = secret("StripeSecretKey")
const jwtSecret = secret("JWTSecret")

// Dùng trong handler
export const charge = api(...)
async (params) => {
  const stripe = new Stripe(stripeKey())
  // ...
}

// Set secret: encore secret set --type local StripeSecretKey <value>
```

---

## Service-to-service calls (type-safe)

```typescript
// Gọi users service từ payments service
import * as users from "~encore/clients/users"

export const createPayment = api(...)
async ({ userId, amount }) => {
  // Type-safe — no HTTP boilerplate
  const user = await users.getUser({ id: userId })
  // ...
}
```

---

## Auth handler

```typescript
// auth/auth.ts
import { Gateway, Header } from "encore.dev/api";
import { authHandler } from "encore.dev/auth";

interface AuthParams {
  token: Header<"Authorization">;
}

interface AuthData {
  userID: string;
  role: "user" | "admin";
}

export const myAuthHandler = authHandler<AuthParams, AuthData>(
  async ({ token }) => {
    const jwt = token.replace("Bearer ", "");
    const payload = verifyJWT(jwt);
    return { userID: payload.sub, role: payload.role };
  },
);

export const gateway = new Gateway({ authHandler: myAuthHandler });
```

---

## Checklist

- ✅ `encore.service.ts` trong mỗi service directory
- ✅ DB migrations trong `./migrations/` folder
- ✅ Secrets qua `secret()` — không hardcode env vars
- ✅ Internal endpoints không `expose: true` — không bị gọi từ ngoài
- ✅ PubSub cho async workflows (không gọi sync giữa services)
- ✅ `encore run` để local dev với dashboard tại http://localhost:9400
- ✅ `encore test ./...` để test toàn bộ services
