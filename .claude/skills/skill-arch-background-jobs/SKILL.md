---
name: skill-arch-background-jobs
description: Best practices background jobs — cron scheduling, recurring tasks, job deduplication, idempotent workers, delayed jobs, priority queues, dead letter handling, và distributed job locking.
---

# Skill: Background Jobs & Scheduling

## Job Types

```yaml
one_off: "Run once — email after order, resize image, generate report"
delayed: "Run after X time — send reminder 24h after cart abandon"
recurring: "Run on schedule — daily report, weekly cleanup, hourly sync"
triggered: "Run when event fires — webhook received, file uploaded"
```

---

## BullMQ (Node.js — Recommended)

### Setup & Basic Job

```typescript
import { Queue, Worker, QueueScheduler } from 'bullmq'
import { Redis } from 'ioredis'

const connection = new Redis({ host: 'localhost', port: 6379, maxRetriesPerRequest: null })

// Queue
const emailQueue = new Queue('email', { connection })

// Add job
await emailQueue.add('welcome', {
  userId: 'usr_123',
  email: 'user@example.com',
  template: 'welcome',
}, {
  attempts: 3,
  backoff: { type: 'exponential', delay: 1000 },
  removeOnComplete: { count: 1000 },
  removeOnFail: { count: 5000 },
})

// Worker
const worker = new Worker('email', async (job) => {
  const { userId, email, template } = job.data
  await emailService.send(email, template, { userId })
}, {
  connection,
  concurrency: 5,
  limiter: { max: 10, duration: 1000 },  // max 10 jobs/second
})

worker.on('completed', (job) => console.log(`Job ${job.id} completed`))
worker.on('failed', (job, err) => console.error(`Job ${job?.id} failed:`, err.message))
```

### Recurring Jobs (Cron)

```typescript
// Add repeatable job
await emailQueue.add('daily-digest', {}, {
  repeat: {
    pattern: '0 9 * * *',    // every day at 9:00 AM
    tz: 'Asia/Ho_Chi_Minh',
  },
})

await emailQueue.add('weekly-report', {}, {
  repeat: {
    pattern: '0 8 * * 1',    // every Monday at 8:00 AM
  },
})

await emailQueue.add('cleanup-expired', {}, {
  repeat: {
    every: 60_000,            // every 60 seconds
  },
})

// List repeatable jobs
const repeatables = await emailQueue.getRepeatableJobs()

// Remove repeatable job
await emailQueue.removeRepeatableByKey(repeatables[0].key)
```

### Delayed Jobs

```typescript
// Send reminder 24 hours after cart abandonment
await reminderQueue.add('cart-abandon', {
  userId: 'usr_123',
  cartId: 'cart_456',
}, {
  delay: 24 * 60 * 60 * 1000,  // 24 hours
})

// Cancel delayed job if user completes purchase
await reminderQueue.remove(jobId)
```

### Priority Queues

```typescript
// Higher priority = processed first (lower number = higher priority)
await notificationQueue.add('critical-alert', data, { priority: 1 })
await notificationQueue.add('normal-notification', data, { priority: 5 })
await notificationQueue.add('low-priority-email', data, { priority: 10 })
```

---

## Celery (Python)

```python
from celery import Celery
from celery.schedules import crontab

app = Celery('myapp', broker='redis://localhost:6379/0')

# Task
@app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email(self, user_id: str, template: str):
    try:
        user = User.objects.get(id=user_id)
        email_service.send(user.email, template)
    except Exception as exc:
        self.retry(exc=exc)

# Call task
send_email.delay('usr_123', 'welcome')           # async
send_email.apply_async(args=['usr_123', 'welcome'], countdown=3600)  # delayed 1h

# Periodic tasks (celery beat)
app.conf.beat_schedule = {
    'daily-digest': {
        'task': 'tasks.send_daily_digest',
        'schedule': crontab(hour=9, minute=0),
    },
    'cleanup-expired': {
        'task': 'tasks.cleanup_expired_sessions',
        'schedule': 60.0,  # every 60 seconds
    },
}
```

---

## Job Deduplication

```yaml
problem: "Same job added twice → user gets 2 emails"
solutions:
  job_id_dedup: "Set explicit jobId — BullMQ ignores duplicate"
  idempotency_key: "Check if already processed before executing"
  distributed_lock: "Acquire lock before processing"
```

```typescript
// ✅ BullMQ — jobId deduplication
await emailQueue.add('welcome', { userId: 'usr_123' }, {
  jobId: `welcome:usr_123`,  // same ID = ignored if already exists
})

// ✅ Idempotent worker — check before processing
const worker = new Worker('orders', async (job) => {
  const { orderId } = job.data

  // Check if already processed
  const processed = await redis.get(`job:processed:${job.id}`)
  if (processed) {
    console.log(`Job ${job.id} already processed, skipping`)
    return
  }

  // Process
  await processOrder(orderId)

  // Mark as processed (with TTL)
  await redis.set(`job:processed:${job.id}`, '1', 'EX', 86400)
}, { connection })

// ✅ Distributed lock for recurring jobs
const worker = new Worker('daily-report', async (job) => {
  const lockKey = `lock:daily-report:${new Date().toISOString().split('T')[0]}`
  const acquired = await redis.set(lockKey, '1', 'NX', 'EX', 3600)

  if (!acquired) {
    console.log('Another worker already running daily report')
    return
  }

  await generateDailyReport()
}, { connection })
```

---

## Job Monitoring & Dead Letter

```yaml
monitoring:
  dashboard: "Bull Board, Arena, or custom admin panel"
  metrics:
    - "Jobs waiting (queue depth)"
    - "Jobs active (being processed)"
    - "Jobs completed / failed per minute"
    - "Average processing time"
    - "DLQ size"
  alerts:
    - "Queue depth > 1000 → alert"
    - "DLQ growth > 10/hour → alert"
    - "Worker down (no heartbeat) → alert"

dead_letter:
  after_max_retries: "Move to DLQ (separate queue or DB table)"
  review: "Daily review of failed jobs — fix systematic issues"
  retry: "Manual retry from DLQ after fix"
```

```typescript
// Bull Board dashboard
import { createBullBoard } from '@bull-board/api'
import { BullMQAdapter } from '@bull-board/api/bullMQAdapter'
import { ExpressAdapter } from '@bull-board/express'

const serverAdapter = new ExpressAdapter()
createBullBoard({
  queues: [
    new BullMQAdapter(emailQueue),
    new BullMQAdapter(orderQueue),
  ],
  serverAdapter,
})
app.use('/admin/queues', serverAdapter.getRouter())
```

---

## Anti-patterns

```yaml
job_in_request:
  bad: "Process heavy task synchronously in HTTP request → timeout"
  fix: "Add to queue, return 202 Accepted, process in background"

no_retry:
  bad: "Job fails once → data lost forever"
  fix: "Retry with exponential backoff, DLQ after max retries"

no_timeout:
  bad: "Worker hangs on external API → blocks queue forever"
  fix: "Set job timeout, worker auto-kills stuck jobs"

cron_without_lock:
  bad: "3 server instances → 3 copies of cron job run simultaneously"
  fix: "Distributed lock OR single scheduler instance (Celery Beat, BullMQ QueueScheduler)"

large_payload_in_job:
  bad: "Store entire file content in job payload (100MB)"
  fix: "Store reference (S3 URL, DB ID), fetch in worker"
```
