---
name: skill-arch-transactional
description: Best practices transaction management — ACID, isolation levels, optimistic/pessimistic locking, Outbox pattern, idempotency keys, Unit of Work, savepoints, distributed transactions (2PC, TCC, Saga), và deadlock prevention.
---

# Skill: Transactional Patterns

## ACID Fundamentals

```yaml
Atomicity: "All or nothing — nếu 1 operation fail, toàn bộ transaction rollback"
Consistency: "Database luôn ở trạng thái hợp lệ sau transaction"
Isolation: "Transactions chạy đồng thời không ảnh hưởng lẫn nhau"
Durability: "Khi commit xong, data được persist vĩnh viễn (survive crash)"
```

---

## Isolation Levels

### Anomalies & Protection

```
┌───────────────────┬──────────┬────────────────┬───────────────┬──────────┐
│ Isolation Level   │ Dirty    │ Non-Repeatable │ Phantom       │ Perf     │
│                   │ Read     │ Read           │ Read          │          │
├───────────────────┼──────────┼────────────────┼───────────────┼──────────┤
│ READ UNCOMMITTED  │ ❌ Yes   │ ❌ Yes         │ ❌ Yes        │ Fastest  │
│ READ COMMITTED    │ ✅ No    │ ❌ Yes         │ ❌ Yes        │ Fast     │
│ REPEATABLE READ   │ ✅ No    │ ✅ No          │ ❌ Yes*       │ Medium   │
│ SERIALIZABLE      │ ✅ No    │ ✅ No          │ ✅ No         │ Slowest  │
└───────────────────┴──────────┴────────────────┴───────────────┴──────────┘

* PostgreSQL's REPEATABLE READ also prevents phantom reads (SSI)
```

### When to Use

```yaml
READ_COMMITTED:
  default_for: "PostgreSQL, Oracle, SQL Server"
  use_when: "Most CRUD operations, reporting queries"
  example: "List users, get profile, search products"

REPEATABLE_READ:
  default_for: "MySQL/InnoDB"
  use_when: "Read-then-write patterns, price calculations"
  example: "Check balance → transfer funds (within single DB)"

SERIALIZABLE:
  use_when: "Financial transactions, inventory that MUST NOT oversell"
  warning: "High contention → deadlocks. Use retry logic."
  example: "Stock reservation, seat booking, auction closing"

rule_of_thumb:
  - "Start with READ COMMITTED (default PostgreSQL)"
  - "Upgrade to REPEATABLE READ only for specific transactions"
  - "Use SERIALIZABLE only when correctness > throughput"
  - "NEVER use READ UNCOMMITTED in production"
```

### Implementation

```typescript
// PostgreSQL — set per transaction
await db.$transaction(async (tx) => {
  await tx.$executeRaw`SET TRANSACTION ISOLATION LEVEL SERIALIZABLE`
  
  const account = await tx.account.findUniqueOrThrow({
    where: { id: fromAccountId },
  })
  
  if (account.balance < amount) {
    throw new InsufficientBalanceError()
  }
  
  await tx.account.update({
    where: { id: fromAccountId },
    data: { balance: { decrement: amount } },
  })
  
  await tx.account.update({
    where: { id: toAccountId },
    data: { balance: { increment: amount } },
  })
  
  await tx.transaction.create({
    data: { fromAccountId, toAccountId, amount, type: 'TRANSFER' },
  })
}, {
  isolationLevel: Prisma.TransactionIsolationLevel.Serializable,
  timeout: 5000,
})
```

```python
# SQLAlchemy — isolation level per session
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine("postgresql://...", isolation_level="READ COMMITTED")

with Session(engine) as session:
    session.connection(execution_options={
        "isolation_level": "SERIALIZABLE"
    })
    
    account = session.query(Account).filter_by(id=from_id).with_for_update().one()
    
    if account.balance < amount:
        raise InsufficientBalanceError()
    
    account.balance -= amount
    target.balance += amount
    session.add(TransferRecord(from_id=from_id, to_id=to_id, amount=amount))
    session.commit()
```

---

## Locking Strategies

### Optimistic Locking (version-based)

```yaml
concept: "Assume no conflict, check at commit time"
how: "Version column — read version, increment on update, fail if version changed"
best_for: "Low contention, read-heavy, web forms"
tradeoff: "No locks held → better throughput, but retry needed on conflict"
```

```typescript
// Prisma — optimistic locking with version field
async function updateProduct(id: string, data: UpdateProductDto, expectedVersion: number) {
  try {
    return await prisma.product.update({
      where: {
        id,
        version: expectedVersion, // only update if version matches
      },
      data: {
        ...data,
        version: { increment: 1 },
      },
    })
  } catch (error) {
    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2025') {
      throw new ConflictError(
        'Product was modified by another user. Please refresh and try again.'
      )
    }
    throw error
  }
}

// TypeORM — @VersionColumn decorator
@Entity()
class Product {
  @PrimaryGeneratedColumn('uuid')
  id: string

  @Column()
  name: string

  @Column('decimal')
  price: number

  @VersionColumn()
  version: number  // auto-incremented on save, throws on conflict
}
```

```sql
-- Raw SQL — optimistic lock
UPDATE products
SET name = 'New Name', price = 29.99, version = version + 1
WHERE id = 'abc123' AND version = 5;
-- If affected_rows = 0 → conflict detected → retry or error
```

### Pessimistic Locking (row-level)

```yaml
concept: "Lock rows before modifying — block other transactions"
how: "SELECT ... FOR UPDATE — acquire exclusive lock"
best_for: "High contention, critical sections, inventory/financial"
tradeoff: "Prevents conflicts but reduces throughput, risk of deadlocks"

variants:
  FOR_UPDATE: "Exclusive lock — blocks reads AND writes"
  FOR_NO_KEY_UPDATE: "Exclusive but allows FK reads (PostgreSQL)"
  FOR_SHARE: "Shared lock — blocks writes, allows reads"
  FOR_KEY_SHARE: "Shared lock on key only (PostgreSQL)"
  SKIP_LOCKED: "Skip already-locked rows (queue pattern)"
  NOWAIT: "Fail immediately if row locked (no wait)"
```

```typescript
// Prisma — pessimistic lock (raw query needed)
async function reserveStock(productId: string, quantity: number) {
  return prisma.$transaction(async (tx) => {
    // Lock the row — other transactions wait here
    const [product] = await tx.$queryRaw<Product[]>`
      SELECT * FROM products WHERE id = ${productId} FOR UPDATE
    `
    
    if (product.stock < quantity) {
      throw new InsufficientStockError()
    }
    
    await tx.product.update({
      where: { id: productId },
      data: { stock: { decrement: quantity } },
    })
    
    return tx.orderItem.create({
      data: { productId, quantity, unitPrice: product.price },
    })
  })
}
```

```python
# SQLAlchemy — with_for_update()
def reserve_stock(session, product_id: str, quantity: int):
    product = (
        session.query(Product)
        .filter_by(id=product_id)
        .with_for_update()  # SELECT ... FOR UPDATE
        .one()
    )
    
    if product.stock < quantity:
        raise InsufficientStockError()
    
    product.stock -= quantity
    session.add(OrderItem(product_id=product_id, quantity=quantity))
    session.commit()
```

### Advisory Locks (application-level)

```yaml
concept: "Application requests named lock from database — not tied to rows"
best_for: "Process-level mutual exclusion, cron job dedup, migration locks"
```

```typescript
// PostgreSQL advisory lock
async function withAdvisoryLock<T>(
  lockKey: number,
  fn: () => Promise<T>,
): Promise<T> {
  await prisma.$executeRaw`SELECT pg_advisory_lock(${lockKey})`
  try {
    return await fn()
  } finally {
    await prisma.$executeRaw`SELECT pg_advisory_unlock(${lockKey})`
  }
}

// Try lock (non-blocking)
const acquired = await prisma.$queryRaw<[{ pg_try_advisory_lock: boolean }]>`
  SELECT pg_try_advisory_lock(${lockKey})
`
if (!acquired[0].pg_try_advisory_lock) {
  throw new LockNotAcquiredError()
}
```

### Decision Matrix

```
┌─────────────────────┬─────────────┬─────────────┬─────────────┐
│ Scenario            │ Optimistic  │ Pessimistic │ Advisory    │
├─────────────────────┼─────────────┼─────────────┼─────────────┤
│ Edit user profile   │ ✅ Best     │ Overkill    │ ─           │
│ Update cart item    │ ✅ Best     │ ─           │ ─           │
│ Transfer money      │ ─           │ ✅ Best     │ ─           │
│ Reserve inventory   │ ─           │ ✅ Best     │ ─           │
│ Seat booking        │ ─           │ ✅ Best     │ ─           │
│ Run scheduled job   │ ─           │ ─           │ ✅ Best     │
│ Run DB migration    │ ─           │ ─           │ ✅ Best     │
│ Process queue item  │ ─           │ SKIP LOCKED │ ─           │
└─────────────────────┴─────────────┴─────────────┴─────────────┘
```

---

## Transaction Boundaries

### Unit of Work Pattern

```yaml
principle: "1 business operation = 1 transaction"
rules:
  - "Transaction bắt đầu ở service layer, KHÔNG ở repository"
  - "Controller KHÔNG quản lý transactions"
  - "Repository methods KHÔNG tự commit"
  - "Transaction scope = business operation scope"
```

```typescript
// ✅ Correct — transaction at service layer
class OrderService {
  async createOrder(dto: CreateOrderDto): Promise<Order> {
    return this.prisma.$transaction(async (tx) => {
      const order = await this.orderRepo.create(tx, dto)
      
      for (const item of dto.items) {
        await this.inventoryRepo.decrementStock(tx, item.productId, item.quantity)
        await this.orderItemRepo.create(tx, { orderId: order.id, ...item })
      }
      
      await this.paymentRepo.createCharge(tx, {
        orderId: order.id,
        amount: order.totalAmount,
      })
      
      return order
    })
  }
}

// ❌ Wrong — transaction in repository
class OrderRepo {
  async create(dto) {
    return this.prisma.$transaction(async (tx) => { // DON'T — caller can't compose
      return tx.order.create({ data: dto })
    })
  }
}

// ❌ Wrong — transaction in controller
class OrderController {
  async create(req, res) {
    await this.prisma.$transaction(async (tx) => { // DON'T — controller shouldn't know DB
      await this.orderService.create(tx, req.body)
    })
  }
}
```

### Savepoints (Nested Transactions)

```yaml
concept: "Checkpoint within transaction — partial rollback without aborting whole tx"
use_when: "Optional sub-operation that can fail without killing main transaction"
```

```typescript
// PostgreSQL savepoints via Prisma
await prisma.$transaction(async (tx) => {
  const order = await tx.order.create({ data: orderData })
  
  // Try to send notification — failure is non-critical
  try {
    await tx.$executeRaw`SAVEPOINT send_notification`
    await tx.notification.create({
      data: { userId: order.userId, type: 'ORDER_CREATED', orderId: order.id },
    })
  } catch {
    await tx.$executeRaw`ROLLBACK TO SAVEPOINT send_notification`
    // Log but don't fail the order
  }
  
  return order
})
```

```python
# SQLAlchemy — nested transaction (savepoint)
with session.begin():  # outer transaction
    order = Order(...)
    session.add(order)
    session.flush()
    
    try:
        with session.begin_nested():  # SAVEPOINT
            notification = Notification(order_id=order.id)
            session.add(notification)
    except Exception:
        pass  # savepoint rolled back, outer tx continues
    
    # order is still committed
```

---

## Transactional Outbox Pattern

```yaml
problem: |
  "Cần update DB + publish event atomically"
  "DB commit thành công nhưng event publish fail → data inconsistency"
  "Event publish thành công nhưng DB rollback → phantom event"

solution: |
  "Write event vào outbox TABLE trong cùng transaction với business data"
  "Separate process (poller/CDC) reads outbox → publishes to message broker"
  "Guarantees: event published if and only if DB committed"
```

```
Business Transaction
  ┌─────────────────────────────┐
  │  BEGIN                      │
  │  INSERT INTO orders (...)   │
  │  INSERT INTO outbox (...)   │  ← event stored in same tx
  │  COMMIT                     │
  └─────────────────────────────┘
                │
        Outbox Relay (poll or CDC)
                │
                ▼
  ┌─────────────────────────────┐
  │  Message Broker             │
  │  (Kafka / RabbitMQ / SQS)  │
  └─────────────────────────────┘
```

### Implementation

```typescript
// Outbox table schema
// CREATE TABLE outbox (
//   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
//   aggregate_type VARCHAR(100) NOT NULL,
//   aggregate_id VARCHAR(100) NOT NULL,
//   event_type VARCHAR(100) NOT NULL,
//   payload JSONB NOT NULL,
//   created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
//   published_at TIMESTAMPTZ,
//   retry_count INT NOT NULL DEFAULT 0
// );

class OrderService {
  async createOrder(dto: CreateOrderDto) {
    return this.prisma.$transaction(async (tx) => {
      const order = await tx.order.create({ data: dto })
      
      // Write event to outbox in SAME transaction
      await tx.outbox.create({
        data: {
          aggregateType: 'Order',
          aggregateId: order.id,
          eventType: 'OrderCreated',
          payload: {
            orderId: order.id,
            userId: order.userId,
            totalAmount: order.totalAmount,
            items: dto.items,
          },
        },
      })
      
      return order
    })
  }
}

// Outbox relay — polls and publishes
class OutboxRelay {
  async processOutbox() {
    const events = await this.prisma.outbox.findMany({
      where: { publishedAt: null, retryCount: { lt: 5 } },
      orderBy: { createdAt: 'asc' },
      take: 100,
    })
    
    for (const event of events) {
      try {
        await this.messageBroker.publish(event.eventType, event.payload)
        
        await this.prisma.outbox.update({
          where: { id: event.id },
          data: { publishedAt: new Date() },
        })
      } catch {
        await this.prisma.outbox.update({
          where: { id: event.id },
          data: { retryCount: { increment: 1 } },
        })
      }
    }
  }
}
```

---

## Idempotency Keys

```yaml
problem: "Client retries request (network timeout) → duplicate order/payment"
solution: "Client sends unique idempotency key → server deduplicates"
```

```typescript
// Idempotency key table
// CREATE TABLE idempotency_keys (
//   key VARCHAR(255) PRIMARY KEY,
//   response JSONB,
//   status VARCHAR(20) NOT NULL DEFAULT 'processing',
//   created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
//   expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '24 hours'
// );

class PaymentService {
  async processPayment(dto: PaymentDto, idempotencyKey: string) {
    // Check if already processed
    const existing = await this.prisma.idempotencyKey.findUnique({
      where: { key: idempotencyKey },
    })
    
    if (existing?.status === 'completed') {
      return existing.response // return cached response
    }
    
    if (existing?.status === 'processing') {
      throw new ConflictError('Payment is being processed. Please wait.')
    }
    
    return this.prisma.$transaction(async (tx) => {
      // Claim the key (or fail if race condition)
      await tx.idempotencyKey.upsert({
        where: { key: idempotencyKey },
        create: { key: idempotencyKey, status: 'processing' },
        update: {}, // no-op if already exists (race condition caught above)
      })
      
      // Process payment
      const payment = await this.processPaymentInternal(tx, dto)
      
      // Store result
      await tx.idempotencyKey.update({
        where: { key: idempotencyKey },
        data: { status: 'completed', response: payment as any },
      })
      
      return payment
    })
  }
}

// Client-side: generate idempotency key
// const idempotencyKey = `payment-${orderId}-${Date.now()}`
// Header: Idempotency-Key: <key>
```

---

## Deadlock Prevention

```yaml
causes:
  - "TX-A locks row 1, waits for row 2. TX-B locks row 2, waits for row 1"
  - "Different lock ordering across transactions"
  - "Long-running transactions holding many locks"

prevention:
  consistent_ordering: |
    ALWAYS lock resources in deterministic order (e.g., sorted by ID)
    
    # ❌ Deadlock risk — random order
    lock(account_A)
    lock(account_B)
    
    # ✅ Safe — sorted order
    accounts = sorted([account_A, account_B], key=lambda a: a.id)
    lock(accounts[0])
    lock(accounts[1])

  short_transactions: |
    Keep transactions as short as possible
    - Do validation BEFORE starting transaction
    - Do external API calls OUTSIDE transaction
    - Do heavy computation OUTSIDE transaction

  lock_timeout: |
    SET lock_timeout = '5s';  -- fail fast instead of waiting forever

  retry_on_deadlock: |
    PostgreSQL error code: 40P01 (deadlock_detected)
    MySQL error code: 1213

    Retry with exponential backoff (max 3 retries)
```

```typescript
// Deadlock-safe transfer with consistent ordering
async function transfer(fromId: string, toId: string, amount: number) {
  const [firstId, secondId] = [fromId, toId].sort()
  
  return withRetry(async () => {
    return prisma.$transaction(async (tx) => {
      // Lock in consistent order
      const [first] = await tx.$queryRaw<Account[]>`
        SELECT * FROM accounts WHERE id = ${firstId} FOR UPDATE
      `
      const [second] = await tx.$queryRaw<Account[]>`
        SELECT * FROM accounts WHERE id = ${secondId} FOR UPDATE
      `
      
      const from = firstId === fromId ? first : second
      const to = firstId === toId ? first : second
      
      if (from.balance < amount) throw new InsufficientBalanceError()
      
      await tx.account.update({ where: { id: fromId }, data: { balance: { decrement: amount } } })
      await tx.account.update({ where: { id: toId }, data: { balance: { increment: amount } } })
    }, { isolationLevel: 'Serializable', timeout: 5000 })
  }, { maxRetries: 3, retryOn: ['P2034'] }) // Prisma deadlock code
}

// Generic retry wrapper
async function withRetry<T>(
  fn: () => Promise<T>,
  opts: { maxRetries: number; retryOn: string[] },
): Promise<T> {
  for (let attempt = 0; attempt <= opts.maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error: any) {
      const isRetryable = opts.retryOn.some(code =>
        error.code === code || error.message?.includes(code)
      )
      if (!isRetryable || attempt === opts.maxRetries) throw error
      await new Promise(r => setTimeout(r, 100 * 2 ** attempt)) // exponential backoff
    }
  }
  throw new Error('Unreachable')
}
```

---

## Distributed Transactions

### Two-Phase Commit (2PC)

```yaml
use_when: "Strong consistency across 2+ databases (rare in microservices)"
tradeoff: "Blocking protocol — coordinator failure blocks ALL participants"

flow:
  phase_1_prepare:
    - "Coordinator asks all participants: Can you commit?"
    - "Each participant acquires locks, writes to WAL, responds YES/NO"
  phase_2_commit:
    - "If ALL yes → Coordinator sends COMMIT to all"
    - "If ANY no → Coordinator sends ROLLBACK to all"

warning: "Avoid in microservices — use Saga instead"
```

### Try-Confirm-Cancel (TCC)

```yaml
use_when: "Need reservation semantics across services"
flow:
  try: "Reserve resources (tentative state)"
  confirm: "Finalize reservation (commit)"
  cancel: "Release reservation (rollback)"

example:
  try: "Reserve inventory + block payment amount + reserve delivery slot"
  confirm: "Deduct inventory + charge payment + confirm delivery"
  cancel: "Release inventory + unblock payment + release delivery slot"
```

```typescript
// TCC implementation
class OrderOrchestrator {
  async placeOrder(dto: PlaceOrderDto) {
    const reservations: Reservation[] = []
    
    try {
      // TRY phase — reserve all resources
      const inventoryRes = await this.inventoryService.tryReserve(dto.items)
      reservations.push({ service: 'inventory', id: inventoryRes.reservationId })
      
      const paymentRes = await this.paymentService.tryBlock(dto.userId, dto.totalAmount)
      reservations.push({ service: 'payment', id: paymentRes.blockId })
      
      const deliveryRes = await this.deliveryService.tryReserveSlot(dto.deliveryDate)
      reservations.push({ service: 'delivery', id: deliveryRes.slotId })
      
      // CONFIRM phase — all reservations successful
      await this.inventoryService.confirm(inventoryRes.reservationId)
      await this.paymentService.confirm(paymentRes.blockId)
      await this.deliveryService.confirm(deliveryRes.slotId)
      
      return { status: 'confirmed' }
    } catch (error) {
      // CANCEL phase — rollback all reservations
      for (const res of reservations) {
        try {
          await this[`${res.service}Service`].cancel(res.id)
        } catch {
          // Log and handle manually — compensation failure
        }
      }
      throw error
    }
  }
}
```

### Saga → see `skill-arch-event-driven` for choreography/orchestration patterns

---

## Common Transaction Patterns

### Read-Modify-Write

```yaml
pattern: "Read current state → compute new state → write"
danger: "Race condition if 2 transactions read same old state"
solutions:
  - "Pessimistic: SELECT ... FOR UPDATE"
  - "Optimistic: version column + retry"
  - "Atomic: UPDATE ... SET x = x + 1 (single statement, no read needed)"
```

```typescript
// ❌ Race condition — read-modify-write without lock
const product = await prisma.product.findUnique({ where: { id } })
if (product.stock >= quantity) {
  await prisma.product.update({
    where: { id },
    data: { stock: product.stock - quantity }, // stale read!
  })
}

// ✅ Atomic update — no separate read needed
await prisma.product.update({
  where: { id },
  data: { stock: { decrement: quantity } },
})
// Still needs check: stock can go negative!

// ✅ Safe — atomic decrement with check (raw SQL)
const [result] = await prisma.$queryRaw`
  UPDATE products SET stock = stock - ${quantity}
  WHERE id = ${id} AND stock >= ${quantity}
  RETURNING *
`
if (!result) throw new InsufficientStockError()
```

### Queue Processing (SKIP LOCKED)

```yaml
pattern: "Multiple workers consuming from DB queue without conflict"
```

```sql
-- Worker picks next available task, skipping locked ones
BEGIN;
SELECT * FROM tasks
WHERE status = 'pending'
ORDER BY priority DESC, created_at ASC
LIMIT 1
FOR UPDATE SKIP LOCKED;

-- Process task...

UPDATE tasks SET status = 'completed', completed_at = NOW()
WHERE id = <task_id>;
COMMIT;
```

---

## Anti-patterns

```yaml
long_running_transactions:
  bad: "Transaction holds locks for seconds while calling external API"
  fix: "Do external calls OUTSIDE transaction, only DB operations inside"

transaction_per_request:
  bad: "Wrap entire HTTP request in one big transaction"
  fix: "Transaction per business operation, not per request"

silent_swallow:
  bad: "catch (e) {} inside transaction — error swallowed, tx commits bad state"
  fix: "Let errors propagate to trigger rollback"

no_retry_on_serialization_failure:
  bad: "SERIALIZABLE isolation without retry logic → user sees error"
  fix: "Always retry on serialization/deadlock errors (40001, 40P01)"

optimistic_on_hot_rows:
  bad: "Optimistic locking on inventory counter updated 1000x/sec"
  fix: "High contention → use pessimistic locking or atomic operations"

outbox_without_cleanup:
  bad: "Outbox table grows forever — never delete published events"
  fix: "Delete or archive events after published_at > 7 days"
```
