---
name: skill-database-migration
description: Best practices database migrations — Prisma Migrate, TypeORM migrations, Alembic (Python), Flyway (Java), zero-downtime strategies, rollback plans, và data migration patterns.
---

# Skill: Database Migrations

## Migration Principles

```yaml
rules:
  - Migrations PHẢI idempotent (chạy lại không lỗi)
  - Migrations PHẢI có rollback (down migration)
  - KHÔNG bao giờ sửa migration đã chạy trên shared environment
  - Mỗi migration làm 1 việc nhỏ (không gộp schema + data migration)
  - Test migration trên staging trước production
  - Backup database trước khi chạy migration trên production
  - Migration file names PHẢI ordered (timestamp hoặc sequence)
```

---

## Prisma Migrate (TypeScript/Node.js)

```bash
# Create migration from schema changes
npx prisma migrate dev --name add_user_role

# Apply pending migrations (production)
npx prisma migrate deploy

# Reset database (DEV only)
npx prisma migrate reset
```

```prisma
// schema.prisma — declarative schema
model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String
  role      Role     @default(MEMBER)    // ← new field
  posts     Post[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([email])
  @@map("users")
}

enum Role {
  ADMIN
  MEMBER
  VIEWER
}
```

```sql
-- Generated migration: 20250115_add_user_role
ALTER TABLE "users" ADD COLUMN "role" "Role" NOT NULL DEFAULT 'MEMBER';
```

### Prisma Best Practices

```yaml
schema_changes:
  add_column: "Add with DEFAULT → safe, no lock"
  remove_column: "2 steps: (1) remove from code, deploy (2) remove column in migration"
  rename_column: "3 steps: (1) add new column (2) migrate data (3) remove old column"
  add_index: "CREATE INDEX CONCURRENTLY (PostgreSQL) — no table lock"

data_migration:
  approach: "Separate script, NOT in Prisma migration"
  reason: "Prisma migrations are SQL-only, data migrations need business logic"
  pattern: |
    // scripts/migrate-user-roles.ts
    const users = await prisma.user.findMany({ where: { role: null } })
    for (const batch of chunk(users, 100)) {
      await prisma.$transaction(
        batch.map(u => prisma.user.update({
          where: { id: u.id },
          data: { role: 'MEMBER' },
        }))
      )
    }
```

---

## TypeORM Migrations (TypeScript/Node.js)

```bash
# Generate migration from entity changes
npx typeorm migration:generate -n AddUserRole -d src/data-source.ts

# Create empty migration (custom SQL)
npx typeorm migration:create -n SeedDefaultRoles

# Run pending migrations
npx typeorm migration:run -d src/data-source.ts

# Revert last migration
npx typeorm migration:revert -d src/data-source.ts
```

```typescript
import { MigrationInterface, QueryRunner, TableColumn } from 'typeorm'

export class AddUserRole1705312000000 implements MigrationInterface {
  public async up(queryRunner: QueryRunner): Promise<void> {
    // Create enum type
    await queryRunner.query(`
      CREATE TYPE "user_role" AS ENUM ('admin', 'member', 'viewer')
    `)

    // Add column with default
    await queryRunner.addColumn('users', new TableColumn({
      name: 'role',
      type: 'user_role',
      default: "'member'",
      isNullable: false,
    }))

    // Backfill existing users
    await queryRunner.query(`
      UPDATE users SET role = 'member' WHERE role IS NULL
    `)
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.dropColumn('users', 'role')
    await queryRunner.query(`DROP TYPE "user_role"`)
  }
}
```

---

## Alembic (Python/SQLAlchemy)

```bash
# Initialize
alembic init alembic

# Generate migration from model changes
alembic revision --autogenerate -m "add user role"

# Apply migrations
alembic upgrade head

# Rollback 1 step
alembic downgrade -1

# Show current revision
alembic current
```

```python
# alembic/versions/20250115_add_user_role.py
from alembic import op
import sqlalchemy as sa

revision = 'abc123'
down_revision = 'def456'

def upgrade() -> None:
    # Create enum
    role_enum = sa.Enum('admin', 'member', 'viewer', name='user_role')
    role_enum.create(op.get_bind())

    # Add column
    op.add_column('users',
        sa.Column('role', sa.Enum('admin', 'member', 'viewer', name='user_role'),
                  nullable=False, server_default='member')
    )

    # Create index
    op.create_index('ix_users_role', 'users', ['role'])

def downgrade() -> None:
    op.drop_index('ix_users_role', table_name='users')
    op.drop_column('users', 'role')
    sa.Enum(name='user_role').drop(op.get_bind())
```

---

## Flyway (Java/Spring Boot)

```sql
-- V1__create_users_table.sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- V2__add_user_role.sql
CREATE TYPE user_role AS ENUM ('admin', 'member', 'viewer');
ALTER TABLE users ADD COLUMN role user_role NOT NULL DEFAULT 'member';

-- R__seed_admin_user.sql (repeatable migration — re-runs if changed)
INSERT INTO users (email, name, role)
VALUES ('admin@myapp.com', 'Admin', 'admin')
ON CONFLICT (email) DO NOTHING;
```

```yaml
# application.yml
spring:
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: true
    validate-on-migrate: true
```

---

## Zero-Downtime Migration Strategies

### Expand-Contract Pattern

```yaml
problem: "Rename column 'name' → 'full_name' without downtime"

expand_phase (backward compatible):
  migration_1: |
    ALTER TABLE users ADD COLUMN full_name VARCHAR(100);
    -- Trigger: sync old → new
    CREATE TRIGGER sync_name BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION sync_name_columns();
  deploy: "New code writes BOTH columns, reads from full_name with fallback to name"

contract_phase (cleanup):
  migration_2: |
    -- After all instances read from full_name
    UPDATE users SET full_name = name WHERE full_name IS NULL;
    ALTER TABLE users ALTER COLUMN full_name SET NOT NULL;
  migration_3: |
    -- After old code fully removed
    ALTER TABLE users DROP COLUMN name;
    DROP TRIGGER sync_name ON users;
```

### Safe Operations (No Lock)

```yaml
safe:
  - "ADD COLUMN with DEFAULT (PG 11+: instant, no rewrite)"
  - "ADD COLUMN nullable (always safe)"
  - "CREATE INDEX CONCURRENTLY (no table lock)"
  - "DROP INDEX CONCURRENTLY"
  - "ADD CHECK CONSTRAINT NOT VALID + VALIDATE separately"

unsafe (requires downtime or expand-contract):
  - "ALTER COLUMN type (table rewrite)"
  - "ADD COLUMN NOT NULL without DEFAULT (PG < 11)"
  - "DROP COLUMN (safe but risky — code may still reference)"
  - "RENAME COLUMN (breaks old code)"
  - "CREATE INDEX (without CONCURRENTLY — locks writes)"

postgresql_specific:
  add_not_null_safely: |
    -- Step 1: Add constraint as NOT VALID (no full table scan)
    ALTER TABLE users ADD CONSTRAINT users_role_not_null
      CHECK (role IS NOT NULL) NOT VALID;
    -- Step 2: Validate in background (no lock)
    ALTER TABLE users VALIDATE CONSTRAINT users_role_not_null;
    -- Step 3: Set NOT NULL (instant, constraint already validated)
    ALTER TABLE users ALTER COLUMN role SET NOT NULL;
    ALTER TABLE users DROP CONSTRAINT users_role_not_null;
```

### Large Data Migration

```yaml
problem: "Backfill 10M rows without locking table or killing performance"

batch_approach:
  implementation: |
    -- Process in batches of 1000
    DO $$
    DECLARE
      batch_size INT := 1000;
      affected INT;
    BEGIN
      LOOP
        UPDATE users
        SET role = 'member'
        WHERE id IN (
          SELECT id FROM users
          WHERE role IS NULL
          LIMIT batch_size
          FOR UPDATE SKIP LOCKED
        );
        GET DIAGNOSTICS affected = ROW_COUNT;
        EXIT WHEN affected = 0;
        PERFORM pg_sleep(0.1);  -- throttle
        COMMIT;
      END LOOP;
    END $$;
  
  application_level: |
    // Node.js batch migration
    let cursor = null
    while (true) {
      const batch = await db.query(`
        SELECT id FROM users
        WHERE role IS NULL AND ($1::uuid IS NULL OR id > $1)
        ORDER BY id LIMIT 1000
      `, [cursor])

      if (batch.rows.length === 0) break

      await db.query(`
        UPDATE users SET role = 'member'
        WHERE id = ANY($1)
      `, [batch.rows.map(r => r.id)])

      cursor = batch.rows[batch.rows.length - 1].id
      await sleep(100) // throttle
    }
```

---

## Migration Workflow

```yaml
development:
  1. Change model/entity/schema
  2. Generate migration (auto or manual)
  3. Review generated SQL
  4. Run migration locally
  5. Test rollback works
  6. Commit migration file with code changes

ci_cd:
  1. PR includes migration + code
  2. CI runs migrations on test DB
  3. CI runs tests against migrated schema
  4. Reviewer checks migration SQL for safety
  5. Merge → CD applies migration BEFORE deploying new code

production:
  1. Backup database
  2. Run migration (expand phase)
  3. Deploy new code (reads both old + new)
  4. Verify everything works
  5. Run cleanup migration (contract phase)
  6. Deploy code without old column support
```

---

## Anti-patterns

```yaml
edit_applied_migration:
  bad: "Change migration file that's already run on staging/production"
  fix: "Create new migration to fix issues"

schema_and_data_together:
  bad: "One migration: add column + backfill 10M rows + add constraint"
  fix: "Split into 3 migrations: (1) add column (2) backfill script (3) add constraint"

no_rollback:
  bad: "Migration without down() method"
  fix: "Every migration MUST have rollback"

manual_production:
  bad: "SSH into server, run SQL manually"
  fix: "Automated migration in CI/CD pipeline"

big_bang_rename:
  bad: "Rename column → deploy → everything breaks until deploy complete"
  fix: "Expand-contract pattern: add new, sync, remove old"
```
