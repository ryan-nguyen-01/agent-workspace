---
name: skill-arch-event-driven
description: Best practices event-driven architecture — Event Sourcing, CQRS, Saga patterns, event schema design, idempotency, ordering, và dead letter queues.
---

# Skill: Event-Driven Architecture

## Khi nào dùng

```yaml
NÊN dùng:
  - Decouple services trong microservices
  - Workflow phức tạp qua nhiều services (checkout, onboarding)
  - Audit trail / compliance requirements
  - Real-time reactions (notifications, analytics, cache invalidation)
  - Scale producers và consumers độc lập

KHÔNG nên dùng:
  - Simple CRUD không cần async processing
  - Strong consistency bắt buộc (banking ledger → dùng ACID transactions)
  - Team chưa quen debugging async systems
  - Monolith đơn giản (in-process events đủ)
```

---

## Event Design

### Event Types

```yaml
domain_event:
  description: Something that happened in the business domain
  naming: Past tense — "{Entity}{Action}"
  examples:
    - OrderCreated
    - PaymentProcessed
    - UserRegistered
    - InventoryReserved
    - ShipmentDispatched
  rule: "Events are FACTS — đã xảy ra, không thể undo"

integration_event:
  description: Domain event published ra ngoài service boundary
  naming: Same as domain event
  difference: |
    Domain event: internal, rich data, in-process
    Integration event: external, minimal data, via broker

command:
  description: Request to perform an action
  naming: Imperative — "{Action}{Entity}"
  examples:
    - ProcessPayment
    - SendNotification
    - ReserveInventory
  difference: "Event = đã xảy ra | Command = yêu cầu làm"
```

### Event Schema

```typescript
// ✅ Standard event envelope
interface Event<T = unknown> {
  id: string              // UUID — unique per event
  type: string            // "order.created" | "payment.processed"
  source: string          // "order-service"
  specversion: string     // CloudEvents spec: "1.0"
  time: string            // ISO 8601
  datacontenttype: string // "application/json"
  subject?: string        // Entity ID: "order/123"

  // Tracing
  correlationId: string   // Track across services
  causationId: string     // Event that caused this event

  // Payload
  data: T

  // Metadata
  metadata: {
    userId?: string       // Who triggered
    version: number       // Schema version
  }
}

// ✅ Concrete event
interface OrderCreatedEvent extends Event<{
  orderId: string
  userId: string
  items: Array<{
    productId: string
    quantity: number
    price: number
  }>
  total: number
  currency: string
}> {
  type: 'order.created'
}
```

### Event Naming Convention

```yaml
format: "{domain}.{entity}.{action}"
examples:
  - order.created
  - order.confirmed
  - order.cancelled
  - payment.processed
  - payment.failed
  - payment.refunded
  - user.registered
  - user.email_verified
  - inventory.reserved
  - inventory.released
  - shipment.dispatched
  - shipment.delivered

versioning:
  strategy: Include version in event type or metadata
  example: "order.created.v2" hoặc metadata.version = 2
  rule: "NEVER break existing consumers — add fields, don't remove"
```

---

## Event Sourcing

### Concept

```
Traditional:     Save current STATE → User { name: "John", email: "john@new.com" }
Event Sourcing:  Save all EVENTS → [UserCreated, EmailChanged, NameChanged, ...]
                 Rebuild state by replaying events
```

### Implementation

```typescript
// ✅ Event Store interface
interface EventStore {
  append(streamId: string, events: DomainEvent[], expectedVersion: number): Promise<void>
  getStream(streamId: string): Promise<DomainEvent[]>
  getStreamFrom(streamId: string, fromVersion: number): Promise<DomainEvent[]>
}

// ✅ Aggregate with event sourcing
class Order {
  private id: string
  private status: OrderStatus
  private items: OrderItem[] = []
  private total: number = 0
  private version: number = 0
  private uncommittedEvents: DomainEvent[] = []

  // Rebuild state from events
  static fromEvents(events: DomainEvent[]): Order {
    const order = new Order()
    for (const event of events) {
      order.apply(event, false)
    }
    return order
  }

  // Command: create order
  static create(userId: string, items: OrderItem[]): Order {
    const order = new Order()
    order.applyChange(new OrderCreated({
      orderId: uuid(),
      userId,
      items,
      total: items.reduce((sum, i) => sum + i.price * i.quantity, 0),
    }))
    return order
  }

  // Command: confirm order
  confirm(): void {
    if (this.status !== 'pending') {
      throw new Error('Can only confirm pending orders')
    }
    this.applyChange(new OrderConfirmed({ orderId: this.id }))
  }

  // Command: cancel order
  cancel(reason: string): void {
    if (this.status === 'delivered') {
      throw new Error('Cannot cancel delivered orders')
    }
    this.applyChange(new OrderCancelled({ orderId: this.id, reason }))
  }

  // Apply event to state (no side effects!)
  private apply(event: DomainEvent, isNew: boolean = true): void {
    switch (event.type) {
      case 'order.created':
        this.id = event.data.orderId
        this.status = 'pending'
        this.items = event.data.items
        this.total = event.data.total
        break
      case 'order.confirmed':
        this.status = 'confirmed'
        break
      case 'order.cancelled':
        this.status = 'cancelled'
        break
    }
    this.version++
    if (isNew) this.uncommittedEvents.push(event)
  }

  private applyChange(event: DomainEvent): void {
    this.apply(event, true)
  }

  getUncommittedEvents(): DomainEvent[] {
    return [...this.uncommittedEvents]
  }

  clearUncommittedEvents(): void {
    this.uncommittedEvents = []
  }
}

// ✅ Repository using event store
class OrderRepository {
  constructor(private eventStore: EventStore) {}

  async save(order: Order): Promise<void> {
    const events = order.getUncommittedEvents()
    await this.eventStore.append(
      `order-${order.id}`,
      events,
      order.version - events.length // expected version (optimistic concurrency)
    )
    order.clearUncommittedEvents()
  }

  async findById(id: string): Promise<Order | null> {
    const events = await this.eventStore.getStream(`order-${id}`)
    if (events.length === 0) return null
    return Order.fromEvents(events)
  }
}
```

### Snapshots (Performance)

```typescript
// Khi event stream dài (> 100 events), snapshot để tránh replay toàn bộ
interface Snapshot<T> {
  streamId: string
  version: number
  state: T
  createdAt: Date
}

async findById(id: string): Promise<Order | null> {
  // 1. Load latest snapshot
  const snapshot = await this.snapshotStore.getLatest(`order-${id}`)

  // 2. Load events AFTER snapshot
  const fromVersion = snapshot ? snapshot.version + 1 : 0
  const events = await this.eventStore.getStreamFrom(`order-${id}`, fromVersion)

  if (!snapshot && events.length === 0) return null

  // 3. Rebuild from snapshot + recent events
  const order = snapshot
    ? Order.fromSnapshot(snapshot.state)
    : new Order()

  for (const event of events) {
    order.apply(event, false)
  }

  // 4. Create new snapshot if too many events since last
  if (events.length > 50) {
    await this.snapshotStore.save({
      streamId: `order-${id}`,
      version: order.version,
      state: order.toSnapshot(),
      createdAt: new Date(),
    })
  }

  return order
}
```

---

## CQRS (Command Query Responsibility Segregation)

### Concept

```
Traditional:  Same model for READ and WRITE
CQRS:         Separate WRITE model (normalized) and READ model (denormalized)

WRITE side (Commands):
  → Validate business rules
  → Store in event store / write DB
  → Emit events

READ side (Queries):
  → Listen to events
  → Update denormalized views
  → Optimized for specific query patterns
```

### Implementation

```typescript
// ===== WRITE SIDE =====

// Command handler
class CreateOrderHandler {
  constructor(
    private orderRepo: OrderRepository,
    private eventBus: EventBus,
  ) {}

  async execute(command: CreateOrderCommand): Promise<string> {
    const order = Order.create(command.userId, command.items)
    await this.orderRepo.save(order)

    // Publish events for read side + other services
    for (const event of order.getUncommittedEvents()) {
      await this.eventBus.publish(event)
    }

    return order.id
  }
}

// ===== READ SIDE =====

// Projection (event handler that builds read model)
class OrderListProjection {
  constructor(private readDb: ReadDatabase) {}

  @OnEvent('order.created')
  async onOrderCreated(event: OrderCreatedEvent): Promise<void> {
    // Denormalized view: order + user name + product names
    const user = await this.readDb.users.findById(event.data.userId)

    await this.readDb.orderViews.insert({
      orderId: event.data.orderId,
      userId: event.data.userId,
      userName: user.name,               // denormalized!
      items: event.data.items,
      total: event.data.total,
      status: 'pending',
      createdAt: event.time,
    })
  }

  @OnEvent('order.confirmed')
  async onOrderConfirmed(event: OrderConfirmedEvent): Promise<void> {
    await this.readDb.orderViews.update(
      { orderId: event.data.orderId },
      { status: 'confirmed' }
    )
  }

  @OnEvent('user.name_changed')
  async onUserNameChanged(event: UserNameChangedEvent): Promise<void> {
    // Update denormalized user name in ALL order views
    await this.readDb.orderViews.updateMany(
      { userId: event.data.userId },
      { userName: event.data.newName }
    )
  }
}

// Query handler (reads from denormalized view)
class GetOrderListHandler {
  constructor(private readDb: ReadDatabase) {}

  async execute(query: GetOrderListQuery): Promise<OrderListView[]> {
    return this.readDb.orderViews.find({
      userId: query.userId,
      status: query.status,
    })
    .sort({ createdAt: -1 })
    .skip(query.offset)
    .limit(query.limit)
  }
}
```

### CQRS + Event Sourcing Combined

```
Command → Validate → Store Events (Write DB) → Publish Events
                                                      ↓
                                              Event Handler / Projection
                                                      ↓
                                              Update Read Model (Read DB)
                                                      ↓
                                              Query → Return Denormalized View
```

---

## Saga Pattern

### Choreography (Event-based)

```
Mỗi service emit event → service tiếp theo react

Order Service                 Inventory Service             Payment Service
     │                              │                            │
     │── OrderCreated ──────────────▶                            │
     │                              │── StockReserved ──────────▶│
     │                              │                            │── PaymentProcessed ─┐
     │◀─────────────────────────────┼────────────────────────────┼─────────────────────┘
     │── OrderConfirmed             │                            │
     │                              │                            │

ROLLBACK:
     │                              │                            │── PaymentFailed ────┐
     │                              │◀───────────────────────────┼────────────────────┘
     │                              │── StockReleased ──────────▶│
     │◀─────────────────────────────│                            │
     │── OrderCancelled             │                            │
```

```typescript
// Choreography — mỗi service tự biết react thế nào
// inventory.service.ts
@OnEvent('order.created')
async handleOrderCreated(event: OrderCreatedEvent) {
  try {
    await this.reserveStock(event.data.items)
    await this.eventBus.publish(new StockReservedEvent({
      orderId: event.data.orderId,
      items: event.data.items,
    }))
  } catch (error) {
    await this.eventBus.publish(new StockReservationFailedEvent({
      orderId: event.data.orderId,
      reason: error.message,
    }))
  }
}
```

### Orchestration (Preferred)

```
Central Saga Orchestrator controls the flow

Orchestrator ──── Step 1 ───▶ Inventory: reserveStock()
     │                              │
     │◀── Success ──────────────────┘
     │
     │──── Step 2 ───▶ Payment: processPayment()
     │                              │
     │◀── Success ──────────────────┘
     │
     │──── Step 3 ───▶ Order: confirmOrder()
     │
     │── DONE ✅

ROLLBACK (payment fails):
     │◀── Failure (step 2) ─────────┘
     │
     │──── Compensate Step 1 ───▶ Inventory: releaseStock()
     │
     │──── Cancel Order ───▶ Order: cancelOrder()
     │
     │── FAILED ❌ (notify user)
```

```typescript
// ✅ Saga Orchestrator
interface SagaStep<T> {
  name: string
  execute: (context: T) => Promise<void>
  compensate: (context: T) => Promise<void>
}

class SagaOrchestrator<T> {
  private steps: SagaStep<T>[] = []
  private executedSteps: SagaStep<T>[] = []

  addStep(step: SagaStep<T>): this {
    this.steps.push(step)
    return this
  }

  async execute(context: T): Promise<void> {
    for (const step of this.steps) {
      try {
        await step.execute(context)
        this.executedSteps.push(step)
      } catch (error) {
        logger.error(`Saga step "${step.name}" failed`, { error, context })
        await this.compensate(context)
        throw new SagaFailedError(step.name, error)
      }
    }
  }

  private async compensate(context: T): Promise<void> {
    // Compensate in REVERSE order
    for (const step of [...this.executedSteps].reverse()) {
      try {
        await step.compensate(context)
        logger.info(`Compensated step "${step.name}"`)
      } catch (error) {
        logger.error(`Compensation failed for "${step.name}"`, { error })
        // Alert: manual intervention needed
      }
    }
  }
}

// Usage
const orderSaga = new SagaOrchestrator<OrderContext>()
  .addStep({
    name: 'Reserve Inventory',
    execute: async (ctx) => {
      ctx.reservationId = await inventoryService.reserve(ctx.items)
    },
    compensate: async (ctx) => {
      await inventoryService.release(ctx.reservationId)
    },
  })
  .addStep({
    name: 'Process Payment',
    execute: async (ctx) => {
      ctx.paymentId = await paymentService.charge(ctx.userId, ctx.total)
    },
    compensate: async (ctx) => {
      await paymentService.refund(ctx.paymentId)
    },
  })
  .addStep({
    name: 'Confirm Order',
    execute: async (ctx) => {
      await orderService.confirm(ctx.orderId)
    },
    compensate: async (ctx) => {
      await orderService.cancel(ctx.orderId, 'Saga compensation')
    },
  })

await orderSaga.execute({
  orderId: 'order-123',
  userId: 'user-456',
  items: [...],
  total: 99.99,
})
```

---

## Idempotency

```typescript
// ✅ CRITICAL: Event handlers PHẢI idempotent (xử lý cùng event 2 lần = kết quả giống nhau)

class PaymentEventHandler {
  constructor(
    private processedEvents: ProcessedEventStore,
    private paymentService: PaymentService,
  ) {}

  @OnEvent('order.created')
  async handleOrderCreated(event: OrderCreatedEvent): Promise<void> {
    // 1. Check if already processed
    if (await this.processedEvents.exists(event.id)) {
      logger.info('Event already processed, skipping', { eventId: event.id })
      return
    }

    // 2. Process
    await this.paymentService.createPaymentIntent(event.data)

    // 3. Mark as processed (atomic with step 2 if possible)
    await this.processedEvents.markProcessed(event.id)
  }
}
```

---

## Dead Letter Queue (DLQ)

```yaml
purpose: Handle events that repeatedly fail processing

flow: |
  Main Queue → Consumer → Fail
                  ↓ retry (3 times with backoff)
              Still fails
                  ↓
          Dead Letter Queue → Alert team → Manual investigation

implementation:
  max_retries: 3
  backoff: [1s, 5s, 30s]
  dlq_retention: 14 days
  alerting: Alert after N messages in DLQ

  monitoring:
    - DLQ depth (> 0 = something wrong)
    - Processing error rate
    - Consumer lag (how far behind)
```

```typescript
// ✅ Consumer with DLQ handling
async processMessage(message: Message): Promise<void> {
  const retryCount = message.headers['x-retry-count'] ?? 0

  try {
    await this.handler.handle(message.body)
    await message.ack()
  } catch (error) {
    if (retryCount >= 3) {
      await this.sendToDLQ(message, error)
      await message.ack() // Remove from main queue
      alertService.notify(`Message sent to DLQ: ${message.id}`)
    } else {
      await message.nack() // Retry with backoff
    }
  }
}
```

---

## Event Ordering

```yaml
problem: "Events arrive out of order — order.confirmed before order.created"

solutions:
  partition_key:
    description: Route events for same entity to same partition
    implementation: |
      // Kafka: partition by entity ID
      await producer.send({
        topic: 'order-events',
        messages: [{
          key: orderId,   // Same orderId → same partition → ordered
          value: JSON.stringify(event),
        }]
      })
    guarantee: Ordered within partition (same entity)

  sequence_number:
    description: Attach sequence number, consumer reorders
    implementation: |
      event.metadata.sequenceNumber = aggregate.version
      // Consumer checks: expected next = last processed + 1
      // If gap → wait and buffer until missing event arrives

  eventual_consistency:
    description: Accept out-of-order, design handlers to be tolerant
    implementation: |
      // Handler checks current state before applying
      if (order.status === 'confirmed' && event.type === 'order.created') {
        // Already past this state — skip or log
        return
      }
```

---

## Anti-patterns

```yaml
event_as_command:
  bad: "Event name = DoSomething (imperative)"
  fix: "Events are past tense: SomethingDone"

fat_events:
  bad: "Event chứa toàn bộ entity data (100+ fields)"
  fix: "Event chứa minimum data: entity ID + changed fields"

no_schema_versioning:
  bad: "Change event structure → break all consumers"
  fix: "Version events, support old + new format"

sync_over_async:
  bad: "Publish event → poll queue waiting for response"
  fix: "Dùng request-response (REST/gRPC) nếu cần sync"

event_sourcing_everywhere:
  bad: "Dùng event sourcing cho simple CRUD"
  fix: "Event sourcing chỉ cho complex domains cần audit trail"

missing_idempotency:
  bad: "Process same event twice → charge customer twice"
  fix: "ALWAYS check event ID before processing"

ignoring_dlq:
  bad: "Messages fail silently, no one knows"
  fix: "DLQ + monitoring + alerting"
```
