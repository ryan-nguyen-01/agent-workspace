---
name: skill-queue-rabbitmq
description: Best practices dùng RabbitMQ: exchange types, routing, dead letter queues, consumer patterns và retry mechanisms.
---

# Skill: RabbitMQ

## Connection & Channel Setup

```typescript
import amqplib, { Connection, Channel } from 'amqplib'

class RabbitMQClient {
  private connection: Connection | null = null
  private channel: Channel | null = null

  async connect(): Promise<void> {
    this.connection = await amqplib.connect(process.env.RABBITMQ_URL!)

    // Reconnect on close
    this.connection.on('close', async () => {
      console.log('RabbitMQ connection closed, reconnecting...')
      await this.connect()
    })

    this.connection.on('error', (err) => {
      console.error('RabbitMQ connection error:', err)
    })

    this.channel = await this.connection.createChannel()
    await this.channel.prefetch(10)  // ✅ Limit unacked messages per consumer
  }

  getChannel(): Channel {
    if (!this.channel) throw new Error('RabbitMQ not connected')
    return this.channel
  }

  async close(): Promise<void> {
    await this.channel?.close()
    await this.connection?.close()
  }
}

export const rabbitmq = new RabbitMQClient()
```

## Exchange & Queue Setup

```typescript
// ✅ Topic exchange — flexible routing với pattern matching
async function setupExchanges(channel: Channel): Promise<void> {
  // Declare exchange
  await channel.assertExchange('app.events', 'topic', {
    durable: true,      // Survive broker restart
    autoDelete: false,
  })

  // Dead Letter Exchange (DLX)
  await channel.assertExchange('app.dlx', 'topic', { durable: true })
  await channel.assertQueue('app.dead-letters', { durable: true })
  await channel.bindQueue('app.dead-letters', 'app.dlx', '#')

  // Main queue với DLX config
  await channel.assertQueue('user.events', {
    durable: true,
    arguments: {
      'x-dead-letter-exchange': 'app.dlx',
      'x-dead-letter-routing-key': 'dead.user.events',
      'x-message-ttl': 86400000,   // Messages expire after 24h
      'x-max-length': 10000,        // Max queue size
    },
  })

  await channel.bindQueue('user.events', 'app.events', 'user.*')
  // 'user.created', 'user.updated', 'user.deleted' all route here
}
```

## Publisher

```typescript
interface EventMessage<T = unknown> {
  eventId: string
  eventType: string
  timestamp: string
  payload: T
  metadata?: Record<string, string>
}

class EventPublisher {
  constructor(private channel: Channel) {}

  async publish<T>(routingKey: string, payload: T, options?: {
    delay?: number
    priority?: number
  }): Promise<void> {
    const message: EventMessage<T> = {
      eventId: crypto.randomUUID(),
      eventType: routingKey,
      timestamp: new Date().toISOString(),
      payload,
    }

    const buffer = Buffer.from(JSON.stringify(message))

    const published = this.channel.publish(
      'app.events',
      routingKey,
      buffer,
      {
        persistent: true,          // ✅ Survive broker restart
        contentType: 'application/json',
        messageId: message.eventId,
        timestamp: Date.now(),
        headers: options?.delay ? { 'x-delay': options.delay } : undefined,
        priority: options?.priority,
      }
    )

    // ✅ Handle backpressure
    if (!published) {
      await new Promise(resolve => this.channel.once('drain', resolve))
    }
  }
}

// Usage
await publisher.publish('user.created', { userId: user.id, email: user.email })
```

## Consumer với Retry

```typescript
interface ConsumerOptions {
  maxRetries?: number
  retryDelay?: number  // ms
}

class EventConsumer {
  constructor(private channel: Channel) {}

  async consume(
    queue: string,
    handler: (message: EventMessage) => Promise<void>,
    options: ConsumerOptions = {},
  ): Promise<void> {
    const { maxRetries = 3, retryDelay = 1000 } = options

    await this.channel.consume(queue, async (msg) => {
      if (!msg) return

      const retryCount = (msg.properties.headers?.['x-retry-count'] as number) ?? 0

      try {
        const message: EventMessage = JSON.parse(msg.content.toString())
        await handler(message)
        this.channel.ack(msg)  // ✅ Acknowledge on success
      } catch (err) {
        console.error(`Failed to process message (attempt ${retryCount + 1}):`, err)

        if (retryCount < maxRetries) {
          // ✅ Retry với delay (republish với incremented retry count)
          setTimeout(() => {
            this.channel.publish(
              'app.events',
              msg.fields.routingKey,
              msg.content,
              {
                ...msg.properties,
                headers: { ...msg.properties.headers, 'x-retry-count': retryCount + 1 },
              }
            )
            this.channel.ack(msg)
          }, retryDelay * Math.pow(2, retryCount))  // Exponential backoff
        } else {
          // ❌ Max retries exceeded → send to DLX
          this.channel.nack(msg, false, false)
        }
      }
    })
  }
}

// Usage
await consumer.consume('user.events', async (message) => {
  switch (message.eventType) {
    case 'user.created':
      await emailService.sendWelcome(message.payload.email)
      break
    case 'user.deleted':
      await cleanupService.removeUserData(message.payload.userId)
      break
  }
}, { maxRetries: 3, retryDelay: 2000 })
```

## Work Queue Pattern (Task Distribution)

```typescript
// ✅ Round-robin distribution với fair dispatch
async function setupWorkQueue(channel: Channel): Promise<void> {
  await channel.assertQueue('email.tasks', {
    durable: true,
    arguments: { 'x-dead-letter-exchange': 'app.dlx' },
  })

  channel.prefetch(1)  // Process one task at a time per worker
}

// Worker
await channel.consume('email.tasks', async (msg) => {
  if (!msg) return
  const task = JSON.parse(msg.content.toString())

  try {
    await emailService.send(task)
    channel.ack(msg)
  } catch {
    channel.nack(msg, false, true)  // Requeue on failure
  }
})
```

## Anti-patterns

```typescript
// ❌ autoAck — mất message nếu consumer crash
channel.consume(queue, handler, { noAck: true })  // ❌

// ❌ Không set prefetch (consumer nhận quá nhiều messages)
// channel.prefetch(10) ✅

// ❌ Không persistent messages (mất khi broker restart)
channel.publish(exchange, key, buffer, { persistent: false })  // ❌

// ❌ Không có DLX → failed messages mất hoàn toàn

// ❌ Nack với requeue: true vô điều kiện (infinite loop!)
channel.nack(msg, false, true)  // ❌ Nếu message luôn fail → vòng lặp vô tận
// ✅ Đếm retry count, nack với requeue: false khi hết retry
```
