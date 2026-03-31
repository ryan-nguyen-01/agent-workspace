---
name: skill-database-prisma
description: Best practices dùng Prisma ORM: schema design, migrations, queries, transactions, relations và performance optimization với TypeScript.
---

# Skill: Prisma ORM

## Schema Design

```prisma
// schema.prisma
generator client {
  provider = "prisma-client-js"
  previewFeatures = ["fullTextSearch", "fullTextIndex"]
}

datasource db {
  provider = "postgresql"  // hoặc "mysql", "sqlite"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String
  password  String
  isActive  Boolean  @default(true)
  role      Role     @default(USER)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  posts     Post[]
  profile   Profile?
  sessions  Session[]

  @@index([createdAt(sort: Desc)])
  @@map("users")
}

model Post {
  id          String     @id @default(cuid())
  title       String
  content     String?    @db.Text
  status      PostStatus @default(DRAFT)
  publishedAt DateTime?
  createdAt   DateTime   @default(now())

  authorId    String
  author      User       @relation(fields: [authorId], references: [id], onDelete: Cascade)

  tags        Tag[]      @relation("PostToTag")

  @@index([authorId])
  @@index([status, publishedAt(sort: Desc)])
  @@map("posts")
}

enum Role { USER ADMIN MODERATOR }
enum PostStatus { DRAFT PUBLISHED ARCHIVED }
```

## Prisma Client — Singleton

```typescript
// lib/prisma.ts
import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient }

export const prisma = globalForPrisma.prisma ?? new PrismaClient({
  log: process.env.NODE_ENV === 'development'
    ? ['query', 'error', 'warn']
    : ['error'],
})

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma

// ✅ Disconnect on app shutdown
process.on('beforeExit', async () => {
  await prisma.$disconnect()
})
```

## CRUD Queries

```typescript
// ✅ Find with select (avoid over-fetching)
const user = await prisma.user.findUnique({
  where: { id },
  select: {
    id: true,
    email: true,
    name: true,
    role: true,
    createdAt: true,
  },
})

// ✅ Find with relations
const userWithPosts = await prisma.user.findUniqueOrThrow({
  where: { id },
  include: {
    posts: {
      where: { status: 'PUBLISHED' },
      orderBy: { publishedAt: 'desc' },
      take: 10,
      select: { id: true, title: true, publishedAt: true },
    },
    profile: true,
  },
})

// ✅ Pagination
const [users, total] = await prisma.$transaction([
  prisma.user.findMany({
    where: { isActive: true },
    skip: (page - 1) * pageSize,
    take: pageSize,
    orderBy: { createdAt: 'desc' },
  }),
  prisma.user.count({ where: { isActive: true } }),
])

// ✅ Upsert
const user = await prisma.user.upsert({
  where: { email: dto.email },
  update: { name: dto.name },
  create: { email: dto.email, name: dto.name, password: hashedPassword },
})

// ✅ Update with nested create
const post = await prisma.post.update({
  where: { id: postId },
  data: {
    title: dto.title,
    tags: {
      connectOrCreate: dto.tags.map(tag => ({
        where: { name: tag },
        create: { name: tag },
      })),
    },
  },
})
```

## Transactions

```typescript
// ✅ Interactive transaction (recommended for complex logic)
const result = await prisma.$transaction(async (tx) => {
  const from = await tx.account.findUniqueOrThrow({
    where: { id: fromId },
    select: { balance: true },
  })

  if (from.balance < amount) {
    throw new Error('Insufficient balance')
  }

  const [fromAccount, toAccount] = await Promise.all([
    tx.account.update({
      where: { id: fromId },
      data: { balance: { decrement: amount } },
    }),
    tx.account.update({
      where: { id: toId },
      data: { balance: { increment: amount } },
    }),
  ])

  await tx.transaction.create({
    data: { fromId, toId, amount, type: 'TRANSFER' },
  })

  return { from: fromAccount, to: toAccount }
}, {
  maxWait: 5000,   // Max time to acquire transaction
  timeout: 10000,  // Max transaction duration
})
```

## Raw Queries

```typescript
// ✅ Raw SQL khi Prisma query không đủ
const users = await prisma.$queryRaw<User[]>`
  SELECT u.*, COUNT(p.id)::int AS post_count
  FROM users u
  LEFT JOIN posts p ON p.author_id = u.id AND p.status = 'PUBLISHED'
  WHERE u.is_active = true
  GROUP BY u.id
  ORDER BY post_count DESC
  LIMIT ${limit} OFFSET ${offset}
`

// ✅ Execute (INSERT/UPDATE/DELETE)
const result = await prisma.$executeRaw`
  UPDATE users SET last_seen_at = NOW() WHERE id = ${userId}
`
```

## Middleware & Soft Delete

```typescript
// ✅ Prisma middleware cho soft delete
prisma.$use(async (params, next) => {
  // Redirect delete to soft delete
  if (params.model === 'User' && params.action === 'delete') {
    params.action = 'update'
    params.args.data = { deletedAt: new Date() }
  }

  // Filter out soft-deleted by default
  if (params.model === 'User' && ['findMany', 'findFirst', 'count'].includes(params.action)) {
    params.args.where = { ...params.args.where, deletedAt: null }
  }

  return next(params)
})
```

## Anti-patterns

```typescript
// ❌ Không dùng select → over-fetching (kéo cả password, sensitive data)
prisma.user.findMany()  // ❌ Trả về tất cả fields

// ❌ N+1 — fetch relations trong loop
const users = await prisma.user.findMany()
for (const user of users) {
  user.posts = await prisma.post.findMany({ where: { authorId: user.id } })  // N+1!
}
// ✅ Dùng include

// ❌ Nhiều prisma instances
const prisma = new PrismaClient()  // Trong mỗi file!
// ✅ Singleton

// ❌ Không handle NotFoundError
const user = await prisma.user.findUnique({ where: { id } })
user.name  // TypeError nếu user = null!
// ✅ findUniqueOrThrow hoặc check null
```
