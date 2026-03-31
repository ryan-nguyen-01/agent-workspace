---
name: skill-database-mysql
description: Best practices dùng MySQL 8+: schema design, indexes, query optimization, transactions, JSON operations và connection pooling.
---

# Skill: MySQL 8+

## Schema Design

```sql
-- ✅ UUID primary key với BINARY(16) cho performance
CREATE TABLE users (
    id          BINARY(16) PRIMARY KEY DEFAULT (UUID_TO_BIN(UUID())),
    email       VARCHAR(255) NOT NULL,
    name        VARCHAR(100) NOT NULL,
    password    VARCHAR(255) NOT NULL,
    is_active   TINYINT(1) NOT NULL DEFAULT 1,
    created_at  DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    updated_at  DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
    deleted_at  DATETIME(3) NULL,
    CONSTRAINT uq_users_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ✅ Helper functions cho UUID
CREATE FUNCTION uuid_to_id(uuid CHAR(36)) RETURNS BINARY(16)
    DETERMINISTIC RETURN UUID_TO_BIN(uuid, 1);

CREATE FUNCTION id_to_uuid(bin BINARY(16)) RETURNS CHAR(36)
    DETERMINISTIC RETURN BIN_TO_UUID(bin, 1);

-- ✅ Foreign key
CREATE TABLE posts (
    id          BINARY(16) PRIMARY KEY DEFAULT (UUID_TO_BIN(UUID())),
    user_id     BINARY(16) NOT NULL,
    title       VARCHAR(500) NOT NULL,
    content     TEXT,
    status      ENUM('draft', 'published', 'archived') NOT NULL DEFAULT 'draft',
    published_at DATETIME(3) NULL,
    created_at  DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    CONSTRAINT fk_posts_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_posts_user_id (user_id),
    INDEX idx_posts_status_published (status, published_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Indexes

```sql
-- ✅ Composite index — equality columns first, range last
CREATE INDEX idx_orders_user_status_date ON orders (user_id, status, created_at DESC);

-- ✅ Covering index — tránh table lookup
CREATE INDEX idx_users_email_name ON users (email, name, is_active);

-- ✅ Prefix index cho TEXT columns
CREATE INDEX idx_posts_content ON posts (content(100));

-- ✅ Invisible index để test trước khi drop
ALTER TABLE users ALTER INDEX idx_old_col INVISIBLE;
-- Verify no performance regression, then:
DROP INDEX idx_old_col ON users;

-- ✅ EXPLAIN để check index usage
EXPLAIN FORMAT=JSON
SELECT * FROM posts WHERE user_id = UUID_TO_BIN('...') AND status = 'published';
```

## Queries

```sql
-- ✅ RETURNING-like với LAST_INSERT_ID hoặc SELECT sau INSERT
INSERT INTO users (id, email, name, password)
VALUES (UUID_TO_BIN(UUID()), 'user@test.com', 'Name', 'hashed');

SELECT BIN_TO_UUID(id, 1) AS id, email, name, created_at
FROM users WHERE id = LAST_INSERT_ID();

-- ✅ Upsert với ON DUPLICATE KEY
INSERT INTO user_profiles (user_id, bio, avatar_url)
VALUES (UUID_TO_BIN('...'), 'Bio text', 'https://...')
ON DUPLICATE KEY UPDATE
    bio = VALUES(bio),
    avatar_url = VALUES(avatar_url),
    updated_at = CURRENT_TIMESTAMP(3);

-- ✅ Window functions (MySQL 8+)
SELECT
    id,
    name,
    salary,
    RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS salary_rank,
    AVG(salary) OVER (PARTITION BY department_id) AS dept_avg
FROM employees;

-- ✅ CTE
WITH active_users AS (
    SELECT BIN_TO_UUID(id, 1) AS id, name, email
    FROM users
    WHERE is_active = 1 AND deleted_at IS NULL
)
SELECT u.id, u.name, COUNT(p.id) AS post_count
FROM active_users u
LEFT JOIN posts p ON p.user_id = UUID_TO_BIN(u.id, 1)
GROUP BY u.id, u.name
ORDER BY post_count DESC
LIMIT 10;
```

## JSON Operations (MySQL 8+)

```sql
-- ✅ JSON column
ALTER TABLE users ADD COLUMN metadata JSON;

-- Insert
INSERT INTO users (metadata) VALUES ('{"theme": "dark", "notifications": true}');

-- Query với JSON_EXTRACT / ->
SELECT id, metadata->>'$.theme' AS theme
FROM users
WHERE metadata->>'$.notifications' = 'true';

-- Update JSON field
UPDATE users
SET metadata = JSON_SET(metadata, '$.theme', 'light')
WHERE id = UUID_TO_BIN('...');

-- ✅ Generated column từ JSON (indexable)
ALTER TABLE users
    ADD COLUMN theme VARCHAR(20)
    GENERATED ALWAYS AS (metadata->>'$.theme') STORED,
    ADD INDEX idx_users_theme (theme);
```

## Transactions

```typescript
// ✅ Transaction với mysql2
import mysql from 'mysql2/promise'

const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  connectionLimit: 20,
  waitForConnections: true,
  queueLimit: 0,
  timezone: '+00:00',
  charset: 'utf8mb4',
})

async function transferFunds(fromId: string, toId: string, amount: number) {
  const conn = await pool.getConnection()
  await conn.beginTransaction()

  try {
    const [rows] = await conn.execute<RowDataPacket[]>(
      'SELECT balance FROM accounts WHERE id = UUID_TO_BIN(?, 1) FOR UPDATE',
      [fromId]
    )
    if (rows[0].balance < amount) throw new Error('Insufficient balance')

    await conn.execute(
      'UPDATE accounts SET balance = balance - ? WHERE id = UUID_TO_BIN(?, 1)',
      [amount, fromId]
    )
    await conn.execute(
      'UPDATE accounts SET balance = balance + ? WHERE id = UUID_TO_BIN(?, 1)',
      [amount, toId]
    )

    await conn.commit()
  } catch (err) {
    await conn.rollback()
    throw err
  } finally {
    conn.release()  // ✅ Always release
  }
}
```

## Anti-patterns

```sql
-- ❌ SELECT * trong production
SELECT * FROM users;  -- Over-fetches, breaks covering indexes

-- ❌ OFFSET lớn
SELECT * FROM posts LIMIT 20 OFFSET 100000;  -- Full scan!
-- ✅ Keyset pagination
SELECT * FROM posts WHERE id > ? ORDER BY id LIMIT 20;

-- ❌ Không dùng prepared statements
$sql = "SELECT * FROM users WHERE email = '$email'";  -- SQL injection!
-- ✅ Parameterized
conn.execute('SELECT * FROM users WHERE email = ?', [email])

-- ❌ LIKE với leading wildcard
WHERE name LIKE '%john%';  -- Full table scan!
-- ✅ FULLTEXT index
ALTER TABLE users ADD FULLTEXT INDEX ft_name (name);
SELECT * FROM users WHERE MATCH(name) AGAINST('john' IN BOOLEAN MODE);
```
