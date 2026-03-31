---
name: skill-arch-realtime
description: Real-time system design — WebSocket architecture, scaling WebSocket servers, pub/sub patterns, push notifications, Server-Sent Events (SSE), presence system, và fan-out strategies.
---

# Skill: Real-time Architecture

## Technology Choice

```yaml
websocket:
  protocol: Full-duplex, persistent TCP connection
  when: Bi-directional real-time (chat, gaming, collaborative editing)
  latency: ~1ms (persistent connection, no handshake per message)
  scaling: Complex (stateful connections)

sse (Server-Sent Events):
  protocol: Uni-directional server → client over HTTP
  when: Server push only (notifications, live feeds, dashboard updates)
  latency: ~1ms
  scaling: Simpler (HTTP/2 multiplexing)
  limitation: Server → client only, max 6 connections per browser (HTTP/1.1)

long_polling:
  protocol: Client polls, server holds until data available
  when: Legacy browser support, simple setup
  latency: ~100ms - seconds
  scaling: Simple but resource-intensive

webhook:
  protocol: Server → server HTTP POST
  when: External system notifications, async results
  latency: ~100ms - seconds
  scaling: Simple, stateless

decision:
  bidirectional_needed: → WebSocket
  server_push_only: → SSE (simpler) or WebSocket
  infrequent_updates: → Long polling or SSE
  server_to_server: → Webhook or message queue
```

---

## WebSocket Architecture

### Basic Setup

```typescript
// Server (Socket.IO — most popular abstraction)
import { Server } from 'socket.io'
import { createAdapter } from '@socket.io/redis-adapter'

const io = new Server(httpServer, {
  cors: { origin: 'https://myapp.com', credentials: true },
  pingInterval: 25000,
  pingTimeout: 20000,
  maxHttpBufferSize: 1e6, // 1MB max message
})

// Authentication middleware
io.use(async (socket, next) => {
  const token = socket.handshake.auth.token
  try {
    const user = await verifyJWT(token)
    socket.data.userId = user.id
    socket.data.roles = user.roles
    next()
  } catch {
    next(new Error('Authentication failed'))
  }
})

// Connection handling
io.on('connection', (socket) => {
  const userId = socket.data.userId

  // Join user's personal room (for targeted messages)
  socket.join(`user:${userId}`)

  // Join organization room
  socket.join(`org:${socket.data.orgId}`)

  socket.on('message:send', async (data) => {
    const message = await messageService.create(data)
    // Broadcast to room (all members except sender)
    socket.to(`room:${data.roomId}`).emit('message:new', message)
  })

  socket.on('disconnect', (reason) => {
    presenceService.setOffline(userId)
  })
})
```

### Scaling WebSocket Servers

```yaml
problem: |
  WebSocket = stateful connection
  User A connected to Server 1
  User B connected to Server 2
  User A sends message to User B → Server 1 doesn't know about User B

solutions:
  redis_adapter:
    description: Pub/sub via Redis — broadcast across all servers
    implementation: |
      import { createAdapter } from '@socket.io/redis-adapter'
      const pubClient = createClient({ url: 'redis://redis:6379' })
      const subClient = pubClient.duplicate()
      io.adapter(createAdapter(pubClient, subClient))
      // Now io.to('room').emit() broadcasts via Redis to ALL servers
    capacity: "~100K connections per server node"
    recommended: true

  redis_streams_adapter:
    description: Redis Streams for ordered, persistent messages
    when: Message ordering important, message replay needed

  kafka_adapter:
    description: Kafka as message bus between WS servers
    when: Very high throughput, message persistence

  sticky_sessions:
    description: LB routes same user to same server
    implementation: |
      # Nginx
      upstream websocket_servers {
        ip_hash;  # or cookie-based
        server ws1:3000;
        server ws2:3000;
      }
    limitation: "Uneven distribution, failover loses connections"
    use_with: Redis adapter for cross-server messaging

architecture: |
  Client → Load Balancer (L7, sticky sessions)
    → WS Server 1 ─┐
    → WS Server 2 ─┤── Redis Pub/Sub ── All servers receive broadcasts
    → WS Server 3 ─┘
```

### Connection Management

```yaml
heartbeat:
  client_ping: Every 25s
  server_pong_timeout: 20s
  purpose: Detect dead connections, NAT timeout prevention

reconnection:
  strategy: Exponential backoff
  config: |
    const socket = io('https://api.myapp.com', {
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,      // start 1s
      reconnectionDelayMax: 30000,  // max 30s
      randomizationFactor: 0.5,     // jitter
    })
  message_recovery: |
    // On reconnect, fetch missed messages
    socket.on('connect', async () => {
      const lastSeenId = localStorage.getItem('lastMessageId')
      const missed = await api.getMessages({ after: lastSeenId })
      missed.forEach(msg => handleMessage(msg))
    })

connection_limits:
  per_user: "Max 5 concurrent connections (browser tabs)"
  per_ip: "Max 100 connections"
  total: "Max connections per server = available file descriptors / 2"
  implementation: |
    io.use((socket, next) => {
      const userId = socket.data.userId
      const userSockets = io.of('/').sockets.size // simplified
      if (getUserConnectionCount(userId) >= 5) {
        next(new Error('Too many connections'))
      }
      next()
    })
```

---

## Pub/Sub Patterns

### Fan-out Strategies

```yaml
fan_out_on_write (push model):
  description: Khi user post → push to all followers' feeds immediately
  implementation: |
    async function publishPost(authorId, post) {
      const followers = await getFollowers(authorId)  // 10K followers
      for (const followerId of followers) {
        await redis.lpush(`feed:${followerId}`, JSON.stringify(post))
        await redis.ltrim(`feed:${followerId}`, 0, 199)  // keep last 200
        // Also push real-time notification
        io.to(`user:${followerId}`).emit('feed:new', post)
      }
    }
  pros: Fast reads (feed pre-computed)
  cons: Slow writes (celebrity with 10M followers), storage heavy
  best_for: "Most users (< 10K followers)"

fan_out_on_read (pull model):
  description: Khi user opens feed → query posts from all followed users
  implementation: |
    async function getFeed(userId) {
      const following = await getFollowing(userId)
      const posts = await db.query(`
        SELECT * FROM posts
        WHERE author_id = ANY($1)
        ORDER BY created_at DESC LIMIT 50
      `, [following])
      return posts
    }
  pros: Simple writes, no storage overhead
  cons: Slow reads (query N users), real-time difficult
  best_for: "Celebrities (> 10K followers)"

hybrid (Twitter approach):
  description: Fan-out-on-write for normal users, fan-out-on-read for celebrities
  threshold: "> 10K followers → pull model, otherwise push model"
  implementation: |
    async function publishPost(authorId, post) {
      const followerCount = await getFollowerCount(authorId)
      if (followerCount < 10_000) {
        await fanOutOnWrite(authorId, post)  // push to follower feeds
      } else {
        await markAsCelebrity(post)  // merge at read time
      }
    }
```

### Room/Channel Management

```typescript
// Room-based messaging (chat rooms, channels)
class RoomManager {
  async joinRoom(socket: Socket, roomId: string): Promise<void> {
    const canJoin = await this.checkAccess(socket.data.userId, roomId)
    if (!canJoin) throw new ForbiddenError('Not a member')

    socket.join(`room:${roomId}`)
    await this.presenceService.addToRoom(roomId, socket.data.userId)

    socket.to(`room:${roomId}`).emit('room:user_joined', {
      userId: socket.data.userId,
      roomId,
    })
  }

  async sendToRoom(roomId: string, event: string, data: unknown): Promise<void> {
    this.io.to(`room:${roomId}`).emit(event, data)
  }

  async sendToUser(userId: string, event: string, data: unknown): Promise<void> {
    this.io.to(`user:${userId}`).emit(event, data)
  }

  async broadcastToOrg(orgId: string, event: string, data: unknown): Promise<void> {
    this.io.to(`org:${orgId}`).emit(event, data)
  }
}
```

---

## Push Notifications

```yaml
architecture: |
  Event (order shipped, message received, etc.)
    → Notification Service
      → Route by channel:
        ├── In-app (WebSocket / SSE)
        ├── Mobile push (FCM / APNs)
        ├── Email (SendGrid / SES)
        ├── SMS (Twilio)
        └── Slack / Teams webhook

notification_service:
  responsibilities:
    - Receive notification requests from any service
    - Check user preferences (opt-in/out per channel)
    - Deduplicate (same notification sent twice)
    - Rate limit (max 10 push/hour per user)
    - Template rendering
    - Delivery tracking

  schema: |
    interface Notification {
      id: string
      userId: string
      type: 'order_update' | 'new_message' | 'system_alert'
      channels: ('in_app' | 'push' | 'email' | 'sms')[]
      title: string
      body: string
      data: Record<string, unknown>  // deep link, action buttons
      priority: 'high' | 'normal' | 'low'
      read: boolean
      createdAt: Date
    }

mobile_push:
  fcm: |
    // Firebase Cloud Messaging (Android + iOS)
    const message = {
      notification: { title, body },
      data: { type: 'order_update', orderId: '123' },
      token: userDeviceToken,
      android: { priority: 'high', ttl: '3600s' },
      apns: { payload: { aps: { badge: 1, sound: 'default' } } },
    }
    await admin.messaging().send(message)

  batching: |
    // Send to multiple devices (max 500 per batch)
    await admin.messaging().sendEachForMulticast({
      tokens: userDeviceTokens,
      notification: { title, body },
    })

  token_management:
    - Store device tokens per user (multiple devices)
    - Remove invalid tokens (FCM returns error)
    - Refresh tokens periodically
```

---

## Server-Sent Events (SSE)

```typescript
// ✅ Simple SSE implementation
app.get('/api/events', authenticate, (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Accel-Buffering': 'no', // Disable nginx buffering
  })

  const userId = req.user.id

  // Send heartbeat every 30s (keep connection alive through proxies)
  const heartbeat = setInterval(() => {
    res.write(': heartbeat\n\n')
  }, 30000)

  // Subscribe to user-specific events
  const handler = (event: AppEvent) => {
    res.write(`event: ${event.type}\n`)
    res.write(`data: ${JSON.stringify(event.data)}\n`)
    res.write(`id: ${event.id}\n\n`)
  }

  eventBus.subscribe(`user:${userId}`, handler)

  req.on('close', () => {
    clearInterval(heartbeat)
    eventBus.unsubscribe(`user:${userId}`, handler)
  })
})

// Client
const eventSource = new EventSource('/api/events', {
  headers: { Authorization: `Bearer ${token}` }
})
eventSource.addEventListener('notification', (e) => {
  const data = JSON.parse(e.data)
  showNotification(data)
})
eventSource.addEventListener('error', () => {
  // Auto-reconnects with Last-Event-ID header
})
```

---

## Presence System

```yaml
online_status:
  implementation: |
    // Redis sorted set: score = last active timestamp
    // Online = score > (now - 60s)
    await redis.zadd('presence', Date.now(), userId)

    // Get online users in a room
    const cutoff = Date.now() - 60000  // 60s threshold
    const onlineUsers = await redis.zrangebyscore('presence', cutoff, '+inf')

  heartbeat:
    client: "Send 'ping' every 30s via WebSocket"
    server: "Update presence score on each ping"
    offline: "No ping for 60s → considered offline"

typing_indicator:
  implementation: |
    // Client sends typing event
    socket.emit('typing:start', { roomId })

    // Server broadcasts (with throttle)
    socket.on('typing:start', (data) => {
      socket.to(`room:${data.roomId}`).emit('typing', {
        userId: socket.data.userId,
        roomId: data.roomId,
      })
    })

    // Auto-stop after 5s of no typing events
    // Client-side: debounce typing events, send stop after 3s idle
```

---

## Anti-patterns

```yaml
no_auth_on_websocket:
  bad: "WebSocket connection without authentication"
  fix: "Verify JWT in handshake middleware"

broadcast_everything:
  bad: "Broadcast all events to all connected users"
  fix: "Room-based targeting, only send relevant events"

no_reconnection_handling:
  bad: "Connection drops → user loses all updates"
  fix: "Auto-reconnect + fetch missed messages via REST"

no_rate_limit_on_ws:
  bad: "Client can send unlimited messages via WebSocket"
  fix: "Rate limit per-user on WebSocket messages"

storing_connections_in_memory:
  bad: "Track user connections in Map (single server only)"
  fix: "Redis for connection state, pub/sub for cross-server"
```
