---
name: skill-database-turso
description: Best practices Turso (LibSQL) — edge SQLite, Drizzle ORM integration, embedded replicas, multi-tenancy, Cloudflare Workers deployment.
---

# Skill: Turso (LibSQL)

## Khi nào dùng

- Edge deployment (Cloudflare Workers, Deno Deploy, Vercel Edge)
- SQLite với distributed read replicas
- Low-latency global data, per-tenant DB isolation
- Muốn PostgreSQL-compatible SQL nhưng lightweight

---

## Setup

```typescript
import { createClient } from "@libsql/client";

// HTTP client (edge-compatible)
export const db = createClient({
  url: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
});

// Local dev (embedded SQLite)
export const db = createClient({
  url: "file:local.db",
});

// In-memory (testing)
export const db = createClient({ url: ":memory:" });
```

---

## Raw SQL queries

```typescript
// Single row
const result = await db.execute({
  sql: "SELECT * FROM users WHERE id = ?",
  args: [userId],
});
const user = result.rows[0];

// Multiple rows
const results = await db.execute({
  sql: "SELECT * FROM users WHERE role = ? LIMIT ? OFFSET ?",
  args: [role, limit, offset],
});
const users = results.rows;

// Insert + lastInsertRowid
const result = await db.execute({
  sql: "INSERT INTO users (email, name) VALUES (?, ?) RETURNING id",
  args: [email, name],
});
const newId = result.rows[0].id;

// Batch (atomic)
await db.batch(
  [
    {
      sql: "INSERT INTO orders (user_id, total) VALUES (?, ?)",
      args: [userId, total],
    },
    {
      sql: "UPDATE users SET order_count = order_count + 1 WHERE id = ?",
      args: [userId],
    },
  ],
  "write",
);
```

---

## Drizzle ORM integration (recommended)

```typescript
// drizzle.config.ts
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "turso",
  dbCredentials: {
    url: process.env.TURSO_DATABASE_URL!,
    authToken: process.env.TURSO_AUTH_TOKEN!,
  },
});
```

```typescript
// db/schema.ts
import { text, integer, sqliteTable } from "drizzle-orm/sqlite-core";
import { createId } from "@paralleldrive/cuid2";

export const users = sqliteTable("users", {
  id: text("id")
    .primaryKey()
    .$defaultFn(() => createId()),
  email: text("email").notNull().unique(),
  name: text("name").notNull(),
  role: text("role", { enum: ["user", "admin"] })
    .default("user")
    .notNull(),
  createdAt: integer("created_at", { mode: "timestamp" }).$defaultFn(
    () => new Date(),
  ),
});

export const posts = sqliteTable("posts", {
  id: text("id")
    .primaryKey()
    .$defaultFn(() => createId()),
  title: text("title").notNull(),
  userId: text("user_id").references(() => users.id),
  publishedAt: integer("published_at", { mode: "timestamp" }),
});
```

```typescript
// db/index.ts
import { drizzle } from "drizzle-orm/libsql";
import { createClient } from "@libsql/client";
import * as schema from "./schema";

const client = createClient({
  url: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
});

export const db = drizzle(client, { schema });
```

```typescript
// Queries với Drizzle
import { db } from "./db";
import { users, posts } from "./db/schema";
import { eq, desc, like } from "drizzle-orm";

// Select
const user = await db.select().from(users).where(eq(users.id, userId)).get();

// With join
const postsWithAuthors = await db
  .select()
  .from(posts)
  .leftJoin(users, eq(posts.userId, users.id))
  .where(eq(users.role, "admin"))
  .orderBy(desc(posts.publishedAt))
  .limit(10);

// Insert
const [newUser] = await db.insert(users).values({ email, name }).returning();

// Update
await db.update(users).set({ name }).where(eq(users.id, userId));

// Delete
await db.delete(users).where(eq(users.id, userId));
```

---

## Migrations

```bash
# Generate migration
npx drizzle-kit generate

# Push schema (dev)
npx drizzle-kit push

# Run migrations
npx drizzle-kit migrate
```

```typescript
// Run migrations in app startup (production)
import { migrate } from "drizzle-orm/libsql/migrator";

await migrate(db, { migrationsFolder: "./drizzle" });
```

---

## Cloudflare Workers

```typescript
// worker.ts
import { createClient } from "@libsql/client/web"; // ← web variant
import { drizzle } from "drizzle-orm/libsql";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const client = createClient({
      url: env.TURSO_DATABASE_URL,
      authToken: env.TURSO_AUTH_TOKEN,
    });
    const db = drizzle(client);

    const users = await db.select().from(usersTable).all();
    return Response.json(users);
  },
};
```

```toml
# wrangler.toml
[vars]
TURSO_DATABASE_URL = "libsql://..."

[[secrets]]
name = "TURSO_AUTH_TOKEN"
```

---

## Multi-tenancy (DB-per-tenant)

```typescript
// Mỗi tenant có DB riêng
function getTenantDb(tenantId: string) {
  const client = createClient({
    url: `libsql://${tenantId}-myapp.turso.io`,
    authToken: process.env.TURSO_AUTH_TOKEN!,
  });
  return drizzle(client, { schema });
}

// Tạo DB mới cho tenant
async function provisionTenant(tenantId: string) {
  // Dùng Turso API
  const response = await fetch(
    "https://api.turso.tech/v1/organizations/myorg/databases",
    {
      method: "POST",
      headers: { Authorization: `Bearer ${process.env.TURSO_API_TOKEN}` },
      body: JSON.stringify({ name: tenantId, group: "default" }),
    },
  );
  return response.json();
}
```

---

## Embedded replica (local reads + remote writes)

```typescript
// Fast local reads, writes go to Turso
const client = createClient({
  url: "file:replica.db",
  syncUrl: process.env.TURSO_DATABASE_URL,
  authToken: process.env.TURSO_AUTH_TOKEN,
  syncInterval: 60, // sync every 60 seconds
});

await client.sync(); // manual sync
```

---

## Checklist

- ✅ Dùng `@libsql/client/web` cho Cloudflare Workers (không dùng Node variant)
- ✅ Parameterized queries — không interpolate values vào SQL string
- ✅ `db.batch()` cho multi-statement transactions
- ✅ Drizzle migrations thay vì raw SQL migrations
- ✅ Embedded replica cho read-heavy edge deployments
- ✅ DB-per-tenant cho isolation cứng (không phải RLS)
