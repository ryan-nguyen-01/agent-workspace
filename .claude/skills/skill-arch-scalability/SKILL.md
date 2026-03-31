---
name: skill-arch-scalability
description: Best practices thiết kế hệ thống scalable — load balancing, horizontal/vertical scaling, database sharding & replication, CDN, caching layers, rate limiting, auto-scaling.
---

# Skill: Scalability

## Scaling Strategies

### Vertical vs Horizontal

```yaml
vertical_scaling:
  description: Tăng resource cho 1 machine (CPU, RAM, SSD)
  pros: Simple, no code changes
  cons: Hardware limit, single point of failure, expensive
  when: Database (trước khi shard), early stage

horizontal_scaling:
  description: Thêm machines, phân tải
  pros: No hardware limit, fault tolerant, cost-efficient
  cons: Complexity (stateless, data sync, consistency)
  when: Web servers, application tier, read-heavy workloads
  requirement: Application PHẢI stateless (no in-memory session)
```

### Stateless Application Design

```typescript
// ❌ Stateful — không scale được
class OrderService {
  private cart = new Map<string, CartItem[]>()  // in-memory!
  addToCart(userId: string, item: CartItem) {
    this.cart.get(userId)?.push(item)
  }
}

// ✅ Stateless — mọi state ở external store
class OrderService {
  constructor(private redis: RedisClient) {}
  async addToCart(userId: string, item: CartItem) {
    await this.redis.rpush(`cart:${userId}`, JSON.stringify(item))
  }
}

// Checklist stateless:
// ✅ Session → Redis / JWT (không in-memory)
// ✅ File uploads → S3 / object storage (không local disk)
// ✅ Cache → Redis / Memcached (không in-process Map)
// ✅ Scheduled jobs → external scheduler (không setTimeout)
// ✅ WebSocket → Redis adapter (không in-memory rooms)
```

---

## Load Balancing

### Algorithms

```yaml
round_robin:
  description: Lần lượt gửi request tới từng server
  when: Servers cùng capacity, requests cùng cost
  limitation: Không biết server nào đang busy

weighted_round_robin:
  description: Server mạnh hơn nhận nhiều request hơn
  when: Servers khác capacity (4 core vs 8 core)
  config: "server1 weight=3; server2 weight=1"

least_connections:
  description: Gửi tới server có ít active connections nhất
  when: Requests có processing time khác nhau (file upload vs API)
  best_for: Long-lived connections, WebSocket

ip_hash:
  description: Hash client IP → luôn tới cùng server
  when: Cần sticky sessions (legacy app stateful)
  cons: Uneven distribution nếu nhiều users từ 1 IP (office NAT)

consistent_hashing:
  description: Hash ring — minimize redistribution khi add/remove server
  when: Distributed cache, partition assignment
  benefit: Thêm/bớt node chỉ ảnh hưởng ~1/N data
```

### Layer 4 vs Layer 7

```yaml
layer_4 (Transport):
  operates_on: TCP/UDP packets
  tools: [HAProxy (TCP mode), AWS NLB, keepalived]
  pros: Fast (không parse HTTP), simple
  cons: Không route theo URL/header
  when: TCP services, gRPC, database connections

layer_7 (Application):
  operates_on: HTTP requests
  tools: [Nginx, HAProxy (HTTP mode), AWS ALB, Envoy, Traefik]
  pros: Route theo path/header/cookie, SSL termination, caching
  cons: Chậm hơn L4 (parse HTTP)
  when: Web apps, API routing, A/B testing, canary deploys
```

### Nginx Config Example

```nginx
upstream api_servers {
    least_conn;
    server 10.0.1.1:3000 weight=3;
    server 10.0.1.2:3000 weight=2;
    server 10.0.1.3:3000 weight=1;

    # Health checks
    server 10.0.1.4:3000 backup;  # chỉ dùng khi main down
}

server {
    listen 443 ssl;
    
    # SSL termination tại LB
    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;
    
    location /api/ {
        proxy_pass http://api_servers;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
    }
    
    # Static files → CDN hoặc serve trực tiếp
    location /static/ {
        root /var/www;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## Database Scaling

### Read Replicas

```yaml
pattern:
  write: Primary (master) → 1 instance
  read: Replicas (slaves) → N instances (async replication)

architecture: |
  Application
    ├── WRITE (INSERT/UPDATE/DELETE) → Primary DB
    └── READ (SELECT) → Read Replica Pool (round robin)

implementation:
  # TypeORM example
  TypeOrmModule.forRoot({
    replication: {
      master: { host: 'primary.db.com', port: 5432 },
      slaves: [
        { host: 'replica-1.db.com', port: 5432 },
        { host: 'replica-2.db.com', port: 5432 },
      ],
    },
  })

considerations:
  replication_lag: "Read-after-write có thể trả old data (100ms-1s lag)"
  solution_1: "Read from primary cho critical reads (own profile after update)"
  solution_2: "Read from replica + version check"
  solution_3: "Session-based routing: user vừa write → route reads to primary 5s"
```

### Database Sharding

```yaml
concept: Split data across multiple DB instances by shard key

strategies:
  hash_based:
    description: hash(shard_key) % num_shards = shard_index
    example: "hash(userId) % 4 → shard 0-3"
    pros: Even distribution
    cons: Reshard khi thêm node (dùng consistent hashing)

  range_based:
    description: Chia theo range giá trị
    example: "userId 1-1M → shard1, 1M-2M → shard2"
    pros: Simple, range queries efficient
    cons: Hotspot nếu traffic tập trung 1 range

  geo_based:
    description: Chia theo geography
    example: "Asia → shard-asia, EU → shard-eu, US → shard-us"
    pros: Low latency cho users, data residency compliance
    cons: Cross-region queries expensive

shard_key_selection:
  rules:
    - High cardinality (nhiều unique values)
    - Even distribution (không hotspot)
    - Query pattern aligned (queries thường filter by shard key)
  good: userId, tenantId, orderId
  bad: country (uneven), status (low cardinality), createdDate (hotspot)

cross_shard_queries:
  problem: "JOIN users ON orders WHERE region = 'asia' — data ở 2 shards"
  solutions:
    - Scatter-gather (query tất cả shards, merge results) — slow
    - Denormalize data (copy needed fields to same shard)
    - Application-level join (2 queries + merge in code)
    - CQRS read model (denormalized view, single DB)
```

### Connection Pooling

```yaml
why: DB connections expensive (TCP handshake, auth, memory)

per_service:
  tool: Built-in pool (pg Pool, HikariCP)
  config:
    min: 2
    max: 20  # Rule: max = (core_count * 2) + disk_spindles
    idle_timeout: 30s
    connection_timeout: 5s

shared_proxy:
  tool: PgBouncer, ProxySQL, RDS Proxy
  when: Many service instances, serverless (Lambda)
  benefit: Pool connections across all instances
  mode:
    transaction: "Release connection after each transaction (recommended)"
    session: "Hold connection per client session"
    statement: "Release after each statement (most aggressive)"
```

---

## Caching Layers

```
Request flow with caching:

Client → CDN (static assets, cached API responses)
  ↓ miss
API Gateway → Response cache (Redis)
  ↓ miss
Application → Application cache (in-memory LRU / Redis)
  ↓ miss
Database → Query cache (PG query cache)
  ↓
Store result in all cache layers on the way back
```

### Cache Strategies

```yaml
cache_aside (lazy loading):
  read: Check cache → miss → query DB → store in cache → return
  write: Update DB → invalidate cache
  best_for: Read-heavy, tolerance for stale data
  code: |
    async getUser(id: string): Promise<User> {
      const cached = await redis.get(`user:${id}`)
      if (cached) return JSON.parse(cached)
      const user = await db.users.findById(id)
      await redis.setEx(`user:${id}`, 300, JSON.stringify(user))
      return user
    }

write_through:
  read: Always from cache
  write: Write cache + DB synchronously
  best_for: Read-heavy, consistency important
  cons: Write latency (2 writes)

write_behind (write-back):
  read: Always from cache
  write: Write cache → async write DB (batch)
  best_for: Write-heavy, eventual consistency OK
  risk: Data loss nếu cache node dies trước khi flush

refresh_ahead:
  description: Proactively refresh cache trước khi expire
  when: Predictable access patterns, hot keys
  implementation: Refresh khi TTL < 20% remaining
```

### Cache Invalidation Patterns

```yaml
time_based:
  TTL: "Set expiry — simple nhưng stale window"
  config: "Short TTL (60s) cho volatile data, long (1h) cho static"

event_based:
  description: Invalidate khi data change (via events/pub-sub)
  implementation: |
    // On user update
    await db.users.update(id, data)
    await redis.del(`user:${id}`)
    await redis.del(`user:list:*`)  // pattern delete
  best: Most accurate, minimal stale data

version_based:
  description: Include version/hash trong cache key
  implementation: |
    const version = await redis.get(`user:${id}:version`)
    const cacheKey = `user:${id}:v${version}`
    // On update: increment version → old cache key orphaned

stampede_prevention:
  problem: Cache expires → 1000 requests hit DB simultaneously
  solutions:
    lock: "First request acquires lock, others wait"
    probabilistic: "Refresh random time before TTL expires"
    stale_while_revalidate: "Return stale, refresh in background"
```

### CDN

```yaml
what: Content Delivery Network — cache static content at edge locations

cache_what:
  static: [images, CSS, JS, fonts, videos]
  dynamic: [API responses with Cache-Control headers]
  never: [authenticated responses, personalized content, POST requests]

headers:
  Cache-Control: |
    # Static assets (immutable, long cache)
    Cache-Control: public, max-age=31536000, immutable

    # API responses (short cache, revalidate)
    Cache-Control: public, max-age=60, stale-while-revalidate=30

    # Private/authenticated
    Cache-Control: private, no-cache

    # Never cache
    Cache-Control: no-store

  ETag: |
    # Conditional request — 304 Not Modified if unchanged
    Response: ETag: "abc123"
    Next request: If-None-Match: "abc123"
    → 304 (no body transfer) or 200 (new content)

providers: [CloudFront, Cloudflare, Fastly, Akamai, Vercel Edge]

cache_invalidation:
  path_based: "Invalidate /images/logo.png"
  wildcard: "Invalidate /api/products/*"
  versioned_urls: "/assets/app.a1b2c3.js (hash in filename — never invalidate)"
```

---

## Rate Limiting

### Algorithms

```yaml
fixed_window:
  description: Count requests per fixed time window (e.g., per minute)
  pros: Simple, low memory
  cons: Burst at window boundary (double rate)
  example: "100 req/min → reset counter every minute"

sliding_window_log:
  description: Track timestamp of each request, count in sliding window
  pros: Accurate, no boundary burst
  cons: Memory (store all timestamps)

sliding_window_counter:
  description: Weighted average of current + previous window
  pros: Accurate, low memory
  implementation: |
    rate = (prev_window_count * overlap%) + current_window_count
    if rate > limit → reject

token_bucket:
  description: Bucket fills at constant rate, request takes 1 token
  pros: Allows burst (bucket capacity), smooth rate
  best_for: API rate limiting
  config: |
    bucket_size: 100      # max burst
    refill_rate: 10/sec   # sustained rate

leaky_bucket:
  description: Requests enter bucket, process at fixed rate
  pros: Smooth output rate, no burst
  best_for: Traffic shaping, queue processing
```

### Implementation

```typescript
// Token bucket with Redis (distributed)
class RateLimiter {
  constructor(
    private redis: RedisClient,
    private config: {
      key_prefix: string
      bucket_size: number    // max burst
      refill_rate: number    // tokens per second
      window: number         // seconds
    }
  ) {}

  async isAllowed(clientId: string): Promise<{ allowed: boolean; remaining: number; retryAfter?: number }> {
    const key = `${this.config.key_prefix}:${clientId}`
    const now = Date.now()

    const result = await this.redis.eval(`
      local key = KEYS[1]
      local bucket_size = tonumber(ARGV[1])
      local refill_rate = tonumber(ARGV[2])
      local now = tonumber(ARGV[3])

      local bucket = redis.call('hmget', key, 'tokens', 'last_refill')
      local tokens = tonumber(bucket[1]) or bucket_size
      local last_refill = tonumber(bucket[2]) or now

      -- Refill tokens
      local elapsed = (now - last_refill) / 1000
      tokens = math.min(bucket_size, tokens + elapsed * refill_rate)

      if tokens >= 1 then
        tokens = tokens - 1
        redis.call('hmset', key, 'tokens', tokens, 'last_refill', now)
        redis.call('expire', key, 60)
        return {1, math.floor(tokens)}
      else
        redis.call('hmset', key, 'last_refill', now)
        return {0, 0}
      end
    `, 1, key, this.config.bucket_size, this.config.refill_rate, now)

    return {
      allowed: result[0] === 1,
      remaining: result[1],
      retryAfter: result[0] === 0 ? Math.ceil(1 / this.config.refill_rate) : undefined,
    }
  }
}

// HTTP response headers
res.set({
  'X-RateLimit-Limit': config.bucket_size.toString(),
  'X-RateLimit-Remaining': result.remaining.toString(),
  'X-RateLimit-Reset': resetTime.toString(),
  ...(result.retryAfter && { 'Retry-After': result.retryAfter.toString() }),
})
if (!result.allowed) {
  res.status(429).json({ error: { code: 'RATE_LIMITED', message: 'Too many requests' } })
}
```

### Rate Limit Tiers

```yaml
tiers:
  per_ip:
    scope: Anonymous users
    limit: "60 req/min"
    when: Public endpoints

  per_user:
    scope: Authenticated users
    limit: "300 req/min"
    when: Authenticated endpoints

  per_api_key:
    scope: API consumers (B2B)
    limit: "1000 req/min (configurable per plan)"
    when: Public API

  per_endpoint:
    scope: Sensitive endpoints
    limit: "5 req/min (login), 10 req/min (register)"
    when: Auth, payment, expensive operations
```

---

## Auto-Scaling

```yaml
metrics_based:
  cpu:
    target: 70%
    scale_up: "> 70% for 3 minutes → add instance"
    scale_down: "< 30% for 10 minutes → remove instance"

  memory:
    target: 75%
    scale_up: "> 75% → add instance"

  custom:
    queue_depth: "> 1000 messages → add consumer"
    request_latency: "P99 > 2s → add instance"
    concurrent_connections: "> 500/instance → add instance"

kubernetes_hpa:
  config: |
    apiVersion: autoscaling/v2
    kind: HorizontalPodAutoscaler
    spec:
      scaleTargetRef:
        apiVersion: apps/v1
        kind: Deployment
        name: api-server
      minReplicas: 2
      maxReplicas: 20
      metrics:
        - type: Resource
          resource:
            name: cpu
            target:
              type: Utilization
              averageUtilization: 70

cooldown:
  scale_up: 3 minutes (react fast)
  scale_down: 10 minutes (react slow — avoid flapping)

predictive:
  description: Scale trước peak dựa trên historical patterns
  example: "Traffic peak 9am daily → pre-scale at 8:45am"
```

---

## Anti-patterns

```yaml
premature_optimization:
  bad: "Shard database khi chỉ có 10K rows"
  fix: "Scale khi cần — vertical first, horizontal khi vertical limit"

session_in_memory:
  bad: "Express session stored in process memory"
  fix: "Redis/DB session store"

no_connection_pooling:
  bad: "New DB connection per request"
  fix: "Connection pool (pg Pool, HikariCP)"

cache_everything:
  bad: "Cache mọi thứ, no invalidation strategy"
  fix: "Cache hot data, clear invalidation rules, monitor hit rate"

single_point_of_failure:
  bad: "1 DB, 1 server, 1 region"
  fix: "Replicas, multi-AZ, health checks, failover"
```
