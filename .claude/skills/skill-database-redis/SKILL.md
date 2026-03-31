---
name: skill-database-redis
description: Best practices dùng Redis: caching patterns, session management, pub/sub, rate limiting và data structures.
---

# Skill: Redis

## Connection Setup

```typescript
import { createClient } from 'redis'

const redis = createClient({
  url: process.env.REDIS_URL,
  socket: {
    reconnectStrategy: (retries) => Math.min(retries * 50, 2000),
    connectTimeout: 5000,
  },
})

redis.on('error', err => console.error('Redis error:', err))
redis.on('reconnecting', () => console.log('Redis reconnecting...'))

await redis.connect()

export { redis }
```

## Caching Patterns

```typescript
// ✅ Cache-aside pattern với TTL
async function getUser(id: string): Promise<User | null> {
  const key = `user:${id}`

  // Try cache first
  const cached = await redis.get(key)
  if (cached) return JSON.parse(cached)

  // Fallback to DB
  const user = await db.users.findById(id)
  if (!user) return null

  // Store with TTL (15 minutes)
  await redis.setEx(key, 900, JSON.stringify(user))
  return user
}

// ✅ Invalidate on update
async function updateUser(id: string, data: Partial<User>): Promise<User> {
  const user = await db.users.update(id, data)
  await redis.del(`user:${id}`)  // Invalidate cache
  return user
}

// ✅ Bulk invalidation với pattern
async function invalidateUserCache(userId: string): Promise<void> {
  const keys = await redis.keys(`user:${userId}:*`)
  if (keys.length > 0) await redis.del(keys)
}
```

## Rate Limiting

```typescript
// ✅ Sliding window rate limiter
async function checkRateLimit(
  identifier: string,
  limit: number,
  windowSeconds: number,
): Promise<{ allowed: boolean; remaining: number; resetAt: number }> {
  const key = `rate:${identifier}`
  const now = Date.now()
  const windowStart = now - windowSeconds * 1000

  // Remove old entries + count current
  const [, count] = await redis
    .multi()
    .zRemRangeByScore(key, '-inf', windowStart)
    .zCard(key)
    .exec() as [unknown, number]

  if (count >= limit) {
    const oldest = await redis.zRange(key, 0, 0, { REV: false, BY: 'SCORE' })
    const resetAt = oldest.length ? Number(oldest[0]) + windowSeconds * 1000 : now
    return { allowed: false, remaining: 0, resetAt }
  }

  // Add current request
  await redis
    .multi()
    .zAdd(key, [{ score: now, value: `${now}-${Math.random()}` }])
    .expire(key, windowSeconds)
    .exec()

  return { allowed: true, remaining: limit - count - 1, resetAt: now + windowSeconds * 1000 }
}
```

## Session Management

```typescript
// ✅ Session store
interface Session {
  userId: string
  email: string
  roles: string[]
  expiresAt: number
}

const SESSION_TTL = 7 * 24 * 60 * 60  // 7 days

async function createSession(userId: string, data: Omit<Session, 'expiresAt'>): Promise<string> {
  const sessionId = crypto.randomUUID()
  const session: Session = { ...data, expiresAt: Date.now() + SESSION_TTL * 1000 }
  await redis.setEx(`session:${sessionId}`, SESSION_TTL, JSON.stringify(session))
  return sessionId
}

async function getSession(sessionId: string): Promise<Session | null> {
  const raw = await redis.get(`session:${sessionId}`)
  if (!raw) return null
  return JSON.parse(raw)
}

async function destroySession(sessionId: string): Promise<void> {
  await redis.del(`session:${sessionId}`)
}
```

## Pub/Sub

```typescript
// ✅ Publisher
async function publishEvent(channel: string, data: unknown): Promise<void> {
  await redis.publish(channel, JSON.stringify(data))
}

// ✅ Subscriber (separate connection!)
const subscriber = redis.duplicate()
await subscriber.connect()

await subscriber.subscribe('user:events', (message) => {
  const event = JSON.parse(message)
  handleUserEvent(event)
})
```

## Data Structures

```typescript
// ✅ Hash cho objects
await redis.hSet(`user:profile:${id}`, {
  bio: user.bio,
  avatar: user.avatar,
  updatedAt: new Date().toISOString(),
})
const profile = await redis.hGetAll(`user:profile:${id}`)

// ✅ Sorted Set cho leaderboard
await redis.zAdd('leaderboard', [{ score: points, value: userId }])
const top10 = await redis.zRange('leaderboard', 0, 9, { REV: true })

// ✅ List cho queue/recent items
await redis.lPush(`user:${id}:recent`, itemId)
await redis.lTrim(`user:${id}:recent`, 0, 49)  // Keep last 50
const recentItems = await redis.lRange(`user:${id}:recent`, 0, -1)

// ✅ Set cho unique members
await redis.sAdd(`post:${postId}:likes`, userId)
const likeCount = await redis.sCard(`post:${postId}:likes`)
const hasLiked = await redis.sIsMember(`post:${postId}:likes`, userId)
```

## Anti-patterns

```typescript
// ❌ Lưu quá nhiều data trong 1 key (max ~1MB reasonable)
await redis.set('all_users', JSON.stringify(millionUsers))  // ❌

// ❌ Không đặt TTL cho cached data
await redis.set(key, data)  // Memory leak!
// ✅ Luôn setEx hoặc expire

// ❌ KEYS command trong production (blocks Redis)
const keys = await redis.keys('user:*')  // Blocks all ops!
// ✅ Dùng SCAN
for await (const key of redis.scanIterator({ MATCH: 'user:*', COUNT: 100 })) {
  // process key
}

// ❌ Không handle connection errors
redis.get(key)  // Crash nếu Redis down
// ✅ Fallback to DB if Redis unavailable
```
