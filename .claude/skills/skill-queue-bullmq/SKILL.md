---
name: skill-queue-bullmq
description: Best practices dùng BullMQ (Redis-based): queue setup, job types, workers, retry strategies, scheduled jobs và monitoring.
---

# Skill: BullMQ

## Queue & Worker Setup

```typescript
import { Queue, Worker, QueueEvents, Job } from 'bullmq'
import { Redis } from 'ioredis'

// ✅ Shared Redis connection config
const redisConnection = new Redis({
  host: process.env.REDIS_HOST,
  port: Number(process.env.REDIS_PORT) || 6379,
  password: process.env.REDIS_PASSWORD,
  maxRetriesPerRequest: null,  // ✅ Required for BullMQ
  enableReadyCheck: false,
})

// ✅ Queue definition
export const emailQueue = new Queue('email', {
  connection: redisConnection,
  defaultJobOptions: {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000,  // 2s, 4s, 8s...
    },
    removeOnComplete: { count: 100 },  // Keep last 100 completed jobs
    removeOnFail: { count: 500 },       // Keep last 500 failed jobs
  },
})
```

## Job Types & Adding Jobs

```typescript
// ✅ Typed job data
interface EmailJobData {
  to: string
  subject: string
  template: 'welcome' | 'reset-password' | 'notification'
  variables: Record<string, string>
}

interface ReportJobData {
  userId: string
  reportType: 'monthly' | 'weekly'
  startDate: string
  endDate: string
}

// ✅ Add regular job
await emailQueue.add('send-welcome', {
  to: user.email,
  subject: 'Welcome!',
  template: 'welcome',
  variables: { name: user.name },
} satisfies EmailJobData)

// ✅ Add delayed job
await emailQueue.add('send-reminder', data, {
  delay: 24 * 60 * 60 * 1000,  // 24 hours
})

// ✅ Add job with priority (lower = higher priority)
await emailQueue.add('send-urgent', data, { priority: 1 })

// ✅ Scheduled (cron) job
await emailQueue.add('weekly-report', {}, {
  repeat: { cron: '0 9 * * MON' },  // Every Monday 9 AM
  jobId: 'weekly-report',  // ✅ Stable ID prevents duplicates
})

// ✅ Bulk add (atomic)
await emailQueue.addBulk(
  users.map(user => ({
    name: 'send-newsletter',
    data: { to: user.email, template: 'newsletter', variables: { name: user.name } },
  }))
)
```

## Worker

```typescript
// ✅ Worker với typed data
const emailWorker = new Worker<EmailJobData>(
  'email',
  async (job: Job<EmailJobData>) => {
    const { to, subject, template, variables } = job.data

    // Update progress
    await job.updateProgress(10)

    const html = await templateService.render(template, variables)
    await job.updateProgress(50)

    await emailProvider.send({ to, subject, html })
    await job.updateProgress(100)

    // Return value stored in job result
    return { sentAt: new Date().toISOString(), messageId: 'msg-123' }
  },
  {
    connection: redisConnection,
    concurrency: 5,        // Process 5 jobs simultaneously
    limiter: {
      max: 100,            // ✅ Rate limit: max 100 jobs per duration
      duration: 60_000,    // per minute
    },
  }
)

// ✅ Worker event handlers
emailWorker.on('completed', (job, result) => {
  console.log(`Job ${job.id} completed:`, result)
})

emailWorker.on('failed', (job, err) => {
  console.error(`Job ${job?.id} failed:`, err.message)
})

emailWorker.on('error', (err) => {
  console.error('Worker error:', err)
})

// ✅ Graceful shutdown
process.on('SIGTERM', async () => {
  await emailWorker.close()
  await emailQueue.close()
  redisConnection.disconnect()
})
```

## Queue Events (Monitoring)

```typescript
const queueEvents = new QueueEvents('email', { connection: redisConnection })

queueEvents.on('waiting', ({ jobId }) => {
  console.log(`Job ${jobId} waiting`)
})

queueEvents.on('active', ({ jobId, prev }) => {
  console.log(`Job ${jobId} started from ${prev}`)
})

queueEvents.on('completed', ({ jobId, returnvalue }) => {
  console.log(`Job ${jobId} completed with`, returnvalue)
})

queueEvents.on('failed', ({ jobId, failedReason }) => {
  console.error(`Job ${jobId} failed:`, failedReason)
})

// ✅ Wait for job completion
const job = await emailQueue.add('send', data)
const result = await job.waitUntilFinished(queueEvents, 30_000)  // Timeout 30s
```

## Flow (Job Dependencies)

```typescript
import { FlowProducer } from 'bullmq'

const flowProducer = new FlowProducer({ connection: redisConnection })

// ✅ Parent job waits for all children to complete
await flowProducer.add({
  name: 'generate-report',
  queueName: 'reports',
  data: { userId: 'user-123' },
  children: [
    {
      name: 'fetch-orders',
      queueName: 'data-fetch',
      data: { userId: 'user-123', type: 'orders' },
    },
    {
      name: 'fetch-analytics',
      queueName: 'data-fetch',
      data: { userId: 'user-123', type: 'analytics' },
    },
  ],
})
```

## Anti-patterns

```typescript
// ❌ Tạo nhiều Queue/Worker instances (mỗi request)
app.post('/send-email', async (req, res) => {
  const queue = new Queue('email', ...)  // ❌ Tạo mới mỗi request!
})
// ✅ Singleton queue, share connection

// ❌ Không handle worker 'error' event → unhandled rejection
const worker = new Worker('q', handler, { connection })
// Worker error event không caught → process crash!

// ❌ maxRetriesPerRequest: 3 (default Redis) → BullMQ errors
// ✅ maxRetriesPerRequest: null

// ❌ Store large data in job payload
await queue.add('process', { imageData: base64String })  // Bloats Redis!
// ✅ Store reference, fetch in worker
await queue.add('process', { imageId: 'img-123', s3Key: 'images/abc.jpg' })

// ❌ Không set removeOnComplete/removeOnFail → Redis memory leak
await queue.add('job', data)  // Jobs accumulate forever!
```
