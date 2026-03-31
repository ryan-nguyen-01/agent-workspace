---
name: skill-queue-kafka
description: Best practices dùng Apache Kafka: topics, partitions, consumer groups, exactly-once semantics, schema registry và error handling.
---

# Skill: Apache Kafka

## Producer Setup

```typescript
import { Kafka, Producer, CompressionTypes, Partitioners } from 'kafkajs'

const kafka = new Kafka({
  clientId: 'my-service',
  brokers: process.env.KAFKA_BROKERS!.split(','),
  ssl: process.env.NODE_ENV === 'production',
  sasl: process.env.KAFKA_SASL_ENABLED ? {
    mechanism: 'plain',
    username: process.env.KAFKA_USERNAME!,
    password: process.env.KAFKA_PASSWORD!,
  } : undefined,
  retry: {
    initialRetryTime: 300,
    retries: 10,
    maxRetryTime: 30000,
  },
})

// ✅ Singleton producer — expensive to create
let producer: Producer | null = null

async function getProducer(): Promise<Producer> {
  if (!producer) {
    producer = kafka.producer({
      allowAutoTopicCreation: false,  // ✅ Explicit topic creation only
      compression: CompressionTypes.GZIP,
      createPartitioner: Partitioners.LegacyPartitioner,
    })
    await producer.connect()
  }
  return producer
}
```

## Publishing Events

```typescript
interface KafkaEvent<T = unknown> {
  eventId: string
  eventType: string
  aggregateId: string
  timestamp: string
  payload: T
  version: number
}

async function publishEvent<T>(
  topic: string,
  event: Omit<KafkaEvent<T>, 'eventId' | 'timestamp'>,
): Promise<void> {
  const producer = await getProducer()
  const fullEvent: KafkaEvent<T> = {
    ...event,
    eventId: crypto.randomUUID(),
    timestamp: new Date().toISOString(),
  }

  await producer.send({
    topic,
    messages: [
      {
        // ✅ Key = aggregateId → same entity goes to same partition (ordering guarantee)
        key: event.aggregateId,
        value: JSON.stringify(fullEvent),
        headers: {
          eventType: event.eventType,
          version: String(event.version),
          'content-type': 'application/json',
        },
      },
    ],
  })
}

// Usage
await publishEvent('user-events', {
  eventType: 'UserCreated',
  aggregateId: user.id,
  version: 1,
  payload: { email: user.email, name: user.name },
})
```

## Consumer Group

```typescript
import { Consumer, EachMessagePayload } from 'kafkajs'

class KafkaConsumer {
  private consumer: Consumer

  constructor(groupId: string) {
    this.consumer = kafka.consumer({
      groupId,
      sessionTimeout: 30000,
      heartbeatInterval: 3000,
      maxBytesPerPartition: 1048576,  // 1MB
    })
  }

  async start(
    topics: string[],
    handler: (event: KafkaEvent, payload: EachMessagePayload) => Promise<void>,
  ): Promise<void> {
    await this.consumer.connect()
    await this.consumer.subscribe({ topics, fromBeginning: false })

    await this.consumer.run({
      eachMessage: async (payload) => {
        const { topic, partition, message } = payload

        if (!message.value) return

        try {
          const event: KafkaEvent = JSON.parse(message.value.toString())
          await handler(event, payload)
        } catch (err) {
          // ✅ Log with context for debugging
          console.error('Failed to process message', {
            topic, partition,
            offset: message.offset,
            error: err,
          })
          // ✅ Do NOT throw — committing offset moves past the bad message
          // Send to DLQ (Dead Letter Queue) manually
          await this.publishToDLQ(topic, message, err as Error)
        }
      },
    })
  }

  private async publishToDLQ(topic: string, message: any, error: Error): Promise<void> {
    const dlqProducer = await getProducer()
    await dlqProducer.send({
      topic: `${topic}.dlq`,
      messages: [{
        key: message.key,
        value: message.value,
        headers: {
          ...message.headers,
          'dlq-original-topic': topic,
          'dlq-error': error.message,
          'dlq-timestamp': new Date().toISOString(),
        },
      }],
    })
  }

  async stop(): Promise<void> {
    await this.consumer.disconnect()
  }
}

// Usage
const consumer = new KafkaConsumer('notification-service')
await consumer.start(['user-events', 'order-events'], async (event) => {
  switch (event.eventType) {
    case 'UserCreated':
      await notificationService.sendWelcome(event.payload)
      break
    case 'OrderCompleted':
      await notificationService.sendReceipt(event.payload)
      break
  }
})
```

## Transactions (Exactly-Once)

```typescript
// ✅ Transactional producer cho exactly-once semantics
const transactionalProducer = kafka.producer({
  transactionalId: 'my-service-transactional',
  maxInFlightRequests: 1,
  idempotent: true,
})

await transactionalProducer.connect()

const transaction = await transactionalProducer.transaction()

try {
  await transaction.send({
    topic: 'order-events',
    messages: [{ key: orderId, value: JSON.stringify(orderCreatedEvent) }],
  })

  await transaction.send({
    topic: 'inventory-events',
    messages: [{ key: productId, value: JSON.stringify(reserveStockEvent) }],
  })

  // Send offsets to transaction (for consumer-producer pattern)
  await transaction.sendOffsets({
    consumerGroupId: 'order-service',
    topics: [{ topic: 'payment-events', partitions: [{ partition: 0, offset: '100' }] }],
  })

  await transaction.commit()
} catch (err) {
  await transaction.abort()
  throw err
}
```

## Admin — Topic Management

```typescript
const admin = kafka.admin()
await admin.connect()

// ✅ Create topics with proper config
await admin.createTopics({
  topics: [
    {
      topic: 'user-events',
      numPartitions: 6,        // Based on throughput needs
      replicationFactor: 3,    // Production: min 3
      configEntries: [
        { name: 'retention.ms', value: String(7 * 24 * 60 * 60 * 1000) },  // 7 days
        { name: 'compression.type', value: 'gzip' },
        { name: 'cleanup.policy', value: 'delete' },
      ],
    },
  ],
})
```

## Anti-patterns

```typescript
// ❌ No partition key → messages distributed randomly → no ordering
producer.send({ topic, messages: [{ value: JSON.stringify(event) }] })  // ❌
// ✅ Use aggregateId as key

// ❌ Throw trong eachMessage handler → consumer crash loop
eachMessage: async (payload) => {
  throw new Error('Bad message')  // ❌ Consumer restart loop!
}
// ✅ Catch + DLQ

// ❌ Consumer group với 1 partition → chỉ 1 consumer active
// Số partitions = số consumers tối đa trong cùng group

// ❌ allowAutoTopicCreation: true trong production
// Auto-created topics có default config, không phù hợp production

// ❌ Không monitor consumer lag → silent queue backup
// ✅ Monitor với Kafka UI hoặc Burrow
```
