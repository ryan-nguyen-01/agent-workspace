---
name: skill-arch-microservices
description: Best practices thiết kế và implement microservices — service decomposition, communication patterns, data management, resilience, API gateway, service discovery, và deployment strategies.
---

# Skill: Microservices Architecture

## Khi nào dùng Microservices

```yaml
NÊN dùng khi:
  - Team lớn (> 8 devs) cần deploy độc lập
  - Domains rõ ràng, bounded contexts tách biệt
  - Scale requirements khác nhau giữa các phần (auth vs media processing)
  - Tech stack khác nhau phù hợp cho từng service (Go cho realtime, Python cho ML)
  - Deployment frequency cao, cần release từng phần

KHÔNG nên dùng khi:
  - Team nhỏ (< 5 devs) — overhead quản lý vượt quá lợi ích
  - MVP / prototype — monolith nhanh hơn nhiều
  - Domain chưa rõ — tách sai expensive hơn monolith sai
  - Chưa có DevOps maturity (CI/CD, monitoring, container orchestration)
```

---

## Service Decomposition

### Strategies

```yaml
by_business_capability:
  description: Mỗi service = 1 business capability
  example:
    - user-service → quản lý users, profiles, preferences
    - order-service → quản lý orders, order items, order status
    - payment-service → xử lý payments, refunds, invoices
    - notification-service → email, SMS, push notifications
    - inventory-service → stock management, warehouse
  rule: "Nếu domain expert gọi nó bằng 1 tên → 1 service"

by_subdomain (DDD):
  description: Dùng Domain-Driven Design bounded contexts
  steps:
    1. Identify core domain (competitive advantage)
    2. Identify supporting domains (cần nhưng không unique)
    3. Identify generic domains (commodity — dùng SaaS)
  example:
    core: order-processing, pricing-engine
    supporting: user-management, inventory
    generic: email (SendGrid), payment (Stripe), auth (Auth0)

strangler_fig (migration từ monolith):
  description: Dần dần extract services từ monolith
  steps:
    1. Identify module ít coupling nhất
    2. Tạo service mới, replicate logic
    3. Route traffic sang service mới (proxy/facade)
    4. Verify behavior identical
    5. Remove old code từ monolith
    6. Repeat cho module tiếp theo
  rule: "Không bao giờ big bang rewrite — từng phần một"
```

### Decomposition Rules

```yaml
good_boundaries:
  - Mỗi service own 1 database (không share DB)
  - Mỗi service deployable độc lập
  - Mỗi service có API contract rõ ràng
  - Team size: 1 service = 1 team (2-pizza team)
  - Nếu 2 services luôn deploy cùng nhau → gộp lại

bad_boundaries:
  - Service quá nhỏ (1-2 endpoints) → nanoservice antipattern
  - Service share database → distributed monolith
  - Circular dependencies giữa services → sai boundary
  - Service cần biết internal implementation của service khác → coupling quá cao
```

---

## Communication Patterns

### Synchronous (Request-Response)

```yaml
REST:
  when: CRUD operations, simple queries, public APIs
  pros: Simple, well-understood, tooling tốt
  cons: Coupling temporal, cascading failures
  example: |
    # User service gọi Order service
    GET /api/orders?userId=123
    Response: { data: [...], pagination: {...} }

gRPC:
  when: Internal service-to-service, high throughput, streaming
  pros: Fast (HTTP/2 + Protobuf), type-safe, bi-directional streaming
  cons: Không browser-friendly (cần proxy), debugging khó hơn REST
  example: |
    // order.proto
    service OrderService {
      rpc GetUserOrders(GetOrdersRequest) returns (OrderList);
      rpc StreamOrderUpdates(OrderFilter) returns (stream OrderEvent);
    }
  skill_ref: skill-api-grpc

GraphQL:
  when: BFF (Backend for Frontend), mobile clients cần flexible queries
  pros: Client chọn fields, 1 request nhiều resources
  cons: Complexity, N+1 nếu không DataLoader, caching khó
  skill_ref: skill-api-graphql
```

### Asynchronous (Event-Driven)

```yaml
event_notification:
  description: Service emit event, interested services consume
  when: Decoupled workflows, eventual consistency ok
  pattern: |
    Order Service → emit "order.created" → Message Broker
                                              ↓
                                   Payment Service (process payment)
                                   Inventory Service (reserve stock)
                                   Notification Service (send confirmation)
  skill_ref: skill-arch-event-driven

command:
  description: Service gửi command cho service khác thực hiện
  when: Cần đảm bảo action được thực hiện
  pattern: |
    Order Service → send "ProcessPayment" command → Payment Queue
                                                        ↓
                                              Payment Service (process)
                                              → emit "payment.succeeded" event

event_sourcing:
  description: Lưu events thay vì state, rebuild state từ events
  when: Audit trail bắt buộc, complex business workflows
  skill_ref: skill-arch-event-driven
```

### Communication Decision Matrix

```
                    ┌─────────────────┬──────────────────┐
                    │   Need Response  │ Fire & Forget    │
┌───────────────────┼─────────────────┼──────────────────┤
│ Low latency       │ gRPC            │ Message Queue    │
│ High throughput   │                 │ (Kafka/RabbitMQ) │
├───────────────────┼─────────────────┼──────────────────┤
│ Simple / External │ REST            │ Webhook          │
│ Public API        │                 │                  │
├───────────────────┼─────────────────┼──────────────────┤
│ Flexible queries  │ GraphQL (BFF)   │ Event Stream     │
│ Multiple clients  │                 │ (SSE/WebSocket)  │
└───────────────────┴─────────────────┴──────────────────┘
```

---

## Data Management

### Database per Service

```yaml
principle: Mỗi service OWN database riêng — KHÔNG share

patterns:
  private_table:
    description: Shared DB nhưng mỗi service có schema riêng
    isolation: Low (cùng DB instance)
    use_when: Budget thấp, team nhỏ
    risk: Dễ bị tempted to join cross-schema

  private_database:
    description: Mỗi service có DB instance riêng
    isolation: High
    use_when: Production, scale independently
    benefit: Mỗi service chọn DB phù hợp (SQL vs NoSQL)

  polyglot_persistence:
    description: Mỗi service dùng DB type phù hợp nhất
    example:
      user-service: PostgreSQL (relational, ACID)
      product-catalog: MongoDB (flexible schema, nested docs)
      session-store: Redis (fast key-value)
      search-service: Elasticsearch (full-text search)
      analytics: ClickHouse (columnar, fast aggregation)
```

### Cross-Service Queries

```yaml
problem: "Lấy order + user info + product details — data ở 3 services"

solutions:
  api_composition:
    description: API Gateway / BFF gọi nhiều services, aggregate response
    implementation: |
      // BFF endpoint
      async function getOrderDetail(orderId) {
        const order = await orderService.getOrder(orderId)
        const [user, products] = await Promise.all([
          userService.getUser(order.userId),
          productService.getProducts(order.productIds)
        ])
        return { ...order, user, products }
      }
    pros: Simple, flexible
    cons: Latency (multiple calls), coupling

  cqrs:
    description: Tách read model riêng, denormalized cho queries
    implementation: |
      // Write: order-service stores order
      // Read: query-service maintains denormalized view
      //   order + user_name + product_names in 1 table
      // Sync via events: order.created → update read model
    pros: Fast reads, scale reads independently
    cons: Eventual consistency, complexity
    skill_ref: skill-arch-event-driven

  data_replication:
    description: Service giữ local copy của data cần thiết
    implementation: |
      // Order service subscribes to user.updated events
      // Keeps local cache/table of user names + emails
      // No need to call user-service for order display
    pros: No runtime dependency, fast
    cons: Stale data, storage duplication
```

### Distributed Transactions

```yaml
problem: "Create order + deduct stock + charge payment — phải all-or-nothing"

solutions:
  saga_choreography:
    description: Mỗi service emit event, service tiếp theo react
    flow: |
      Order Service: create order (PENDING)
        → emit order.created
      Inventory Service: reserve stock
        → emit stock.reserved
      Payment Service: charge
        → emit payment.charged
      Order Service: confirm order (CONFIRMED)

      ROLLBACK (nếu payment fail):
      Payment Service: emit payment.failed
        → Inventory Service: release stock
        → Order Service: cancel order
    pros: Decoupled, no orchestrator
    cons: Hard to understand full flow, debugging difficult

  saga_orchestration:
    description: Central orchestrator điều phối từng step
    flow: |
      Order Saga Orchestrator:
        1. Call Inventory: reserveStock()
           - Success → step 2
           - Fail → abort, no compensation needed
        2. Call Payment: charge()
           - Success → step 3
           - Fail → compensate: Inventory.releaseStock()
        3. Call Order: confirmOrder()
           - Done
    pros: Clear flow, easy debugging, centralized logic
    cons: Single point of failure (orchestrator)
    preferred: YES — cho hầu hết cases
    skill_ref: skill-arch-event-driven

  avoid:
    - "❌ KHÔNG dùng distributed 2-phase commit (2PC) — quá chậm, lock resources"
    - "❌ KHÔNG dùng shared database — phá vỡ service independence"
```

---

## API Gateway

### Responsibilities

```yaml
routing:
  description: Route requests tới đúng service
  example: |
    /api/users/*    → user-service:3001
    /api/orders/*   → order-service:3002
    /api/products/* → product-service:3003

cross_cutting:
  authentication: Verify JWT token trước khi forward
  rate_limiting: Per-client, per-endpoint limits
  cors: Centralized CORS config
  logging: Request/response logging
  metrics: Latency, error rate per service

transformation:
  request_aggregation: Combine multiple service calls
  response_shaping: Filter fields cho mobile vs web
  protocol_translation: REST → gRPC (cho internal)

resilience:
  circuit_breaker: Ngừng gọi service down
  timeout: Per-service timeout config
  retry: Retry with backoff cho transient failures
  fallback: Return cached/default response khi service unavailable
```

### Implementation Options

```yaml
kong:
  type: API Gateway
  language: Lua/Go
  features: plugins, rate limiting, auth, logging
  deploy: self-hosted hoặc cloud

aws_api_gateway:
  type: Managed
  features: Lambda integration, throttling, caching
  deploy: AWS managed

nginx:
  type: Reverse proxy + basic gateway
  features: load balancing, SSL termination, rate limiting
  deploy: self-hosted, lightweight

custom_bff:
  type: Backend for Frontend
  description: Viết custom gateway per client type
  example: |
    // web-bff.ts — gateway cho web app
    // mobile-bff.ts — gateway cho mobile (less data, different shape)
  when: Clients có requirements rất khác nhau
```

---

## Resilience Patterns

### Circuit Breaker

```typescript
enum CircuitState { CLOSED, OPEN, HALF_OPEN }

class CircuitBreaker {
  private state = CircuitState.CLOSED
  private failureCount = 0
  private lastFailureTime: number = 0

  private readonly failureThreshold = 5
  private readonly resetTimeout = 30_000 // 30s
  private readonly halfOpenMaxCalls = 3

  async call<T>(fn: () => Promise<T>, fallback?: () => T): Promise<T> {
    if (this.state === CircuitState.OPEN) {
      if (Date.now() - this.lastFailureTime > this.resetTimeout) {
        this.state = CircuitState.HALF_OPEN
      } else {
        if (fallback) return fallback()
        throw new ServiceUnavailableError('Circuit is OPEN')
      }
    }

    try {
      const result = await fn()
      this.onSuccess()
      return result
    } catch (error) {
      this.onFailure()
      if (fallback) return fallback()
      throw error
    }
  }

  private onSuccess() {
    this.failureCount = 0
    this.state = CircuitState.CLOSED
  }

  private onFailure() {
    this.failureCount++
    this.lastFailureTime = Date.now()
    if (this.failureCount >= this.failureThreshold) {
      this.state = CircuitState.OPEN
    }
  }
}
```

### Retry with Exponential Backoff

```typescript
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number
    baseDelay?: number
    maxDelay?: number
    retryableErrors?: string[]
  } = {}
): Promise<T> {
  const { maxRetries = 3, baseDelay = 1000, maxDelay = 30000 } = options

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      if (attempt === maxRetries) throw error
      if (!isRetryable(error)) throw error

      const delay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay)
      const jitter = delay * 0.1 * Math.random()
      await sleep(delay + jitter)
    }
  }
  throw new Error('Unreachable')
}

function isRetryable(error: unknown): boolean {
  if (error instanceof HttpError) {
    return [408, 429, 500, 502, 503, 504].includes(error.status)
  }
  return false
}
```

### Bulkhead Pattern

```yaml
description: Isolate resources per service để failure không cascade

thread_pool_bulkhead:
  implementation: |
    // Mỗi service client có connection pool riêng
    const userServicePool = new ConnectionPool({ max: 10 })
    const orderServicePool = new ConnectionPool({ max: 20 })
    // User service down → chỉ user pool exhausted
    // Order service vẫn hoạt động bình thường

semaphore_bulkhead:
  implementation: |
    // Giới hạn concurrent calls per service
    const userServiceSemaphore = new Semaphore(10)
    await userServiceSemaphore.acquire()
    try {
      return await userService.getUser(id)
    } finally {
      userServiceSemaphore.release()
    }
```

### Timeout Pattern

```yaml
rules:
  - Mọi external call PHẢI có timeout
  - Timeout = expected P99 latency × 2
  - Timeout cascade: gateway > service > DB

example:
  api_gateway: 10s
  service_to_service: 5s
  database_query: 3s
  cache_lookup: 500ms
  external_api: 15s (third-party không kiểm soát)
```

---

## Service Discovery

```yaml
client_side:
  description: Client tự biết service addresses (qua registry)
  tools: Consul, Eureka, etcd
  flow: |
    Service A → query Registry: "Where is order-service?"
    Registry → returns: ["10.0.1.5:3002", "10.0.1.6:3002"]
    Service A → call 10.0.1.5:3002 (load balance client-side)

server_side:
  description: Load balancer/proxy route cho client
  tools: Kubernetes Service, AWS ALB, Nginx
  flow: |
    Service A → call http://order-service:3002 (DNS name)
    K8s DNS → resolve to pod IPs
    kube-proxy → load balance to healthy pods
  preferred: YES (trong K8s environment)

dns_based:
  description: DNS records cho service endpoints
  tools: CoreDNS (K8s), Route53 (AWS), Consul DNS
  pattern: "{service-name}.{namespace}.svc.cluster.local"
```

---

## Health Checks

```typescript
// Mỗi service PHẢI expose health endpoints

// Liveness: service process alive? (K8s restart nếu fail)
app.get('/health/live', (req, res) => {
  res.status(200).json({ status: 'alive' })
})

// Readiness: service ready nhận traffic? (K8s remove từ LB nếu fail)
app.get('/health/ready', async (req, res) => {
  const checks = await Promise.allSettled([
    checkDatabase(),
    checkRedis(),
    checkMessageBroker(),
  ])

  const results = checks.map((c, i) => ({
    name: ['database', 'redis', 'broker'][i],
    status: c.status === 'fulfilled' ? 'up' : 'down',
    ...(c.status === 'rejected' && { error: c.reason.message }),
  }))

  const allHealthy = results.every(r => r.status === 'up')
  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'ready' : 'degraded',
    checks: results,
    uptime: process.uptime(),
  })
})

// Startup: service đã init xong? (K8s chờ trước khi check liveness)
app.get('/health/startup', (req, res) => {
  res.status(isInitialized ? 200 : 503).json({
    status: isInitialized ? 'started' : 'starting'
  })
})
```

---

## Observability

```yaml
three_pillars:
  logs:
    format: Structured JSON
    correlation: Request ID propagated across services
    fields: [timestamp, service, requestId, traceId, level, message, context]
    skill_ref: skill-observability-logging

  metrics:
    types:
      - RED: Rate, Errors, Duration (per endpoint)
      - USE: Utilization, Saturation, Errors (per resource)
    tools: Prometheus + Grafana
    essential_metrics:
      - request_count (by service, endpoint, status)
      - request_duration_seconds (histogram)
      - error_rate (by service, error_type)
      - circuit_breaker_state (by target_service)
      - queue_depth (by queue_name)
      - db_connection_pool_usage

  traces:
    description: Distributed tracing across service calls
    tools: Jaeger, Zipkin, OpenTelemetry
    implementation: |
      // Propagate trace context in headers
      headers: {
        'x-trace-id': 'abc123',
        'x-span-id': 'def456',
        'x-parent-span-id': 'ghi789'
      }
    skill_ref: skill-observability-tracing

correlation_id:
  description: Unique ID per user request, propagated qua mọi service
  implementation: |
    // API Gateway generates correlation ID
    const correlationId = req.headers['x-correlation-id'] || uuid()
    // Forward to all downstream calls
    // Include in all log entries
    // Include in all error responses
```

---

## Deployment Patterns

```yaml
one_service_per_container:
  description: Mỗi service = 1 Docker container
  benefit: Isolate dependencies, scale independently
  skill_ref: skill-devops-docker

blue_green:
  description: 2 environments (blue=current, green=new), switch traffic
  flow: |
    1. Deploy new version to green
    2. Run smoke tests on green
    3. Switch load balancer from blue → green
    4. Keep blue as rollback
  rollback: Switch traffic back to blue (instant)

canary:
  description: Route % traffic sang new version, gradually increase
  flow: |
    1. Deploy new version alongside old
    2. Route 5% traffic to new
    3. Monitor error rate, latency
    4. If OK → increase to 25% → 50% → 100%
    5. If NOT OK → rollback to 0%
  tools: Istio, Argo Rollouts, AWS CodeDeploy

rolling:
  description: Update instances one-by-one
  config: |
    # K8s rolling update
    spec:
      strategy:
        type: RollingUpdate
        rollingUpdate:
          maxUnavailable: 1
          maxSurge: 1
```

---

## Configuration Management

```yaml
principles:
  - Config externalized (env vars, config server) — KHÔNG hardcode
  - Secrets trong vault (HashiCorp Vault, AWS Secrets Manager)
  - Environment-specific config (dev, staging, prod)
  - Feature flags cho gradual rollout

patterns:
  env_vars:
    simplest: true
    example: |
      DATABASE_URL=postgres://...
      REDIS_URL=redis://...
      ORDER_SERVICE_URL=http://order-service:3002
    limitation: Restart needed to change

  config_server:
    tools: Spring Cloud Config, Consul KV, AWS AppConfig
    benefit: Dynamic config without restart
    example: |
      // Feature flag check
      const config = await configClient.get('features.new-checkout')
      if (config.enabled) { useNewCheckout() }
```

---

## Anti-patterns

```yaml
distributed_monolith:
  description: Microservices nhưng deploy/change cùng nhau, share DB
  symptom: Mỗi thay đổi cần deploy 5 services
  fix: Refactor boundaries, database-per-service

shared_database:
  description: Nhiều services đọc/ghi cùng 1 database
  symptom: Schema change break nhiều services
  fix: Mỗi service own DB riêng, communicate qua APIs/events

synchronous_chain:
  description: A → B → C → D (sync chain dài)
  symptom: Latency = sum(all services), 1 service down = all down
  fix: Async events cho non-critical paths, cache, CQRS

chatty_communication:
  description: Services gọi nhau quá nhiều cho 1 operation
  symptom: 1 user request → 20+ inter-service calls
  fix: API composition, BFF, denormalized read models

wrong_service_size:
  too_small: 1 CRUD endpoint per service → nanoservice hell
  too_large: 1 service chứa 5 bounded contexts → mini-monolith
  right_size: 1 service = 1 bounded context = 1 team
```

---

## Migration Path: Monolith → Microservices

```
Phase 1: Modular Monolith
  - Tách code thành modules rõ ràng (in-process)
  - Modules communicate qua interfaces (không import trực tiếp)
  - Mỗi module có DB schema riêng (same DB instance)
  - Deploy vẫn là 1 unit

Phase 2: Extract First Service
  - Chọn module ÍT coupling nhất (thường: notification, email)
  - Extract thành service riêng
  - Replace in-process call bằng HTTP/gRPC
  - Setup CI/CD cho service mới
  - Verify behavior identical

Phase 3: Extract Core Services
  - Extract modules theo priority (value vs effort)
  - Setup message broker cho async communication
  - Implement saga cho distributed transactions
  - Setup distributed tracing

Phase 4: Full Microservices
  - Tất cả modules đã extract
  - API Gateway in place
  - Monitoring + alerting cho mọi service
  - Team ownership per service
```
