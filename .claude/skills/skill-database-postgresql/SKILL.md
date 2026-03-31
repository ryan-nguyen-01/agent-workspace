---
name: skill-database-postgresql
description: Best practices dùng PostgreSQL: schema design, indexes, query optimization, transactions và connection pooling.
---

# Skill: PostgreSQL

## Schema Design

```sql
-- ✅ UUID primary key, timestamps, soft delete
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) NOT NULL UNIQUE,
    name        VARCHAR(100) NOT NULL,
    password    TEXT NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ  -- NULL = not deleted (soft delete)
);

-- ✅ Foreign key với proper ON DELETE
CREATE TABLE posts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(500) NOT NULL,
    content     TEXT,
    status      VARCHAR(50) NOT NULL DEFAULT 'draft'
                CHECK (status IN ('draft', 'published', 'archived')),
    published_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ✅ Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

## Indexes

```sql
-- ✅ Index trên foreign keys (PostgreSQL không tự tạo)
CREATE INDEX idx_posts_user_id ON posts(user_id);

-- ✅ Partial index — chỉ index rows cần thiết
CREATE INDEX idx_posts_published ON posts(published_at DESC)
    WHERE status = 'published' AND deleted_at IS NULL;

-- ✅ Composite index — thứ tự column quan trọng (equality first, range last)
CREATE INDEX idx_posts_user_status ON posts(user_id, status, created_at DESC);

-- ✅ GIN index cho JSONB hoặc full-text search
CREATE INDEX idx_users_search ON users
    USING gin(to_tsvector('english', name || ' ' || email));

-- ❌ Không index columns ít selectivity (boolean, status với ít giá trị)
-- Dùng partial index thay thế
```

## Queries chuẩn

```sql
-- ✅ Dùng RETURNING sau INSERT/UPDATE/DELETE
INSERT INTO users (email, name, password)
VALUES ($1, $2, $3)
RETURNING id, email, name, created_at;

-- ✅ CTE cho queries phức tạp
WITH active_users AS (
    SELECT id, name, email
    FROM users
    WHERE is_active = TRUE AND deleted_at IS NULL
),
user_post_counts AS (
    SELECT user_id, COUNT(*) AS post_count
    FROM posts
    WHERE status = 'published'
    GROUP BY user_id
)
SELECT u.id, u.name, u.email, COALESCE(pc.post_count, 0) AS posts
FROM active_users u
LEFT JOIN user_post_counts pc ON u.id = pc.user_id
ORDER BY posts DESC
LIMIT 20 OFFSET $1;

-- ✅ Upsert
INSERT INTO user_profiles (user_id, bio, avatar_url)
VALUES ($1, $2, $3)
ON CONFLICT (user_id) DO UPDATE SET
    bio        = EXCLUDED.bio,
    avatar_url = EXCLUDED.avatar_url,
    updated_at = NOW();
```

## Transactions

```sql
-- ✅ Explicit transaction với savepoint
BEGIN;

INSERT INTO orders (user_id, total) VALUES ($1, $2) RETURNING id INTO order_id;
INSERT INTO order_items (order_id, product_id, qty) VALUES (order_id, $3, $4);
UPDATE products SET stock = stock - $4 WHERE id = $3 AND stock >= $4;

-- Check rows affected
GET DIAGNOSTICS rows_affected = ROW_COUNT;
IF rows_affected = 0 THEN
    ROLLBACK;
    RAISE EXCEPTION 'Insufficient stock';
END IF;

COMMIT;
```

## Connection Pooling (với pgBouncer hoặc application-level)

```typescript
// ✅ pg pool config
import { Pool } from 'pg'

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,              // max connections
  min: 2,               // min idle connections
  idleTimeoutMillis: 30_000,
  connectionTimeoutMillis: 5_000,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: true } : false,
})

// ✅ Release connection sau dùng
async function withClient<T>(fn: (client: PoolClient) => Promise<T>): Promise<T> {
  const client = await pool.connect()
  try {
    return await fn(client)
  } finally {
    client.release()
  }
}
```

## Query Optimization

```sql
-- ✅ EXPLAIN ANALYZE trước khi deploy query phức tạp
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM posts WHERE user_id = $1 AND status = 'published';

-- ✅ Avoid SELECT * trong production
SELECT id, title, published_at FROM posts WHERE ...;

-- ✅ Pagination với keyset thay cursor cho large datasets
-- Cursor-based (hiệu quả hơn OFFSET trên large tables)
SELECT id, title, created_at
FROM posts
WHERE created_at < $1  -- last_seen_created_at
  AND status = 'published'
ORDER BY created_at DESC
LIMIT 20;
```

## Anti-patterns

```sql
-- ❌ OFFSET lớn (full table scan)
SELECT * FROM posts LIMIT 20 OFFSET 10000;  -- Slow!

-- ❌ N+1: loop queries trong application
-- Dùng JOIN hoặc batch fetch thay thế

-- ❌ Không dùng parameterized queries (SQL injection)
db.query(`SELECT * FROM users WHERE email = '${email}'`)  -- ❌ Nguy hiểm!
db.query('SELECT * FROM users WHERE email = $1', [email])  -- ✅

-- ❌ LIKE với leading wildcard không dùng index
WHERE name LIKE '%john%'  -- Full scan!
-- ✅ Dùng full-text search hoặc trigram index
```
