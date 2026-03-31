---
name: skill-arch-notification
description: Best practices notification system — multi-channel delivery (email, SMS, push, in-app, webhook), template engine, user preferences, digest/batching, retry/DLQ, provider abstraction, và notification center UI.
---

# Skill: Notification Architecture

## System Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Notification Service                    │
│                                                            │
│  ┌─────────┐   ┌──────────┐   ┌───────────┐   ┌───────┐ │
│  │ Trigger  │──▶│ Router   │──▶│ Template  │──▶│ Queue │ │
│  │ (event)  │   │ (rules)  │   │ (render)  │   │ (send)│ │
│  └─────────┘   └──────────┘   └───────────┘   └───┬───┘ │
│                                                     │     │
│                    ┌────────────────┬───────────┬───┘     │
│                    ▼                ▼           ▼         │
│              ┌──────────┐   ┌──────────┐  ┌─────────┐   │
│              │  Email    │   │   SMS    │  │  Push   │   │
│              │ Provider  │   │ Provider │  │Provider │   │
│              │(SendGrid) │   │(Twilio)  │  │(FCM)   │   │
│              └──────────┘   └──────────┘  └─────────┘   │
│                                                            │
│              ┌──────────┐   ┌──────────┐                  │
│              │ In-App   │   │ Webhook  │                  │
│              │(WebSocket)│   │(HTTP)    │                  │
│              └──────────┘   └──────────┘                  │
└──────────────────────────────────────────────────────────┘
```

---

## Channel Selection

```yaml
channels:
  email:
    latency: "seconds to minutes"
    best_for: "Transactional (receipt, password reset), marketing, digest"
    providers: [SendGrid, AWS SES, Postmark, Resend]
    cost: "~$0.001/email"

  sms:
    latency: "seconds"
    best_for: "OTP, critical alerts, time-sensitive"
    providers: [Twilio, AWS SNS, Vonage]
    cost: "~$0.01-0.05/SMS"

  push:
    latency: "near real-time"
    best_for: "Engagement, activity updates, reminders"
    providers: [FCM (Android+Web), APNs (iOS)]
    cost: "Free (FCM/APNs)"

  in_app:
    latency: "real-time"
    best_for: "Notification bell, activity feed, live updates"
    delivery: "WebSocket + DB persistence"
    cost: "Infrastructure only"

  webhook:
    latency: "seconds"
    best_for: "B2B integrations, external system notifications"
    delivery: "HTTP POST with retry"
    cost: "Infrastructure only"
```

### Channel Priority by Event

```yaml
channel_matrix:
  order_confirmed:
    required: [email, in_app]
    optional: [push]

  payment_failed:
    required: [email, in_app, push]
    optional: [sms]  # only if user opted in

  new_comment:
    required: [in_app]
    optional: [push, email]  # email only if user not online

  password_reset:
    required: [email]
    never: [push, sms, in_app]  # security: only email

  otp_verification:
    required: [sms]
    fallback: [email]

  system_maintenance:
    required: [email, in_app]
    optional: [push]

  invoice_generated:
    required: [email]
    optional: [in_app, webhook]
```

---

## Data Model

```sql
-- Notification types (templates)
CREATE TABLE notification_types (
  id VARCHAR(100) PRIMARY KEY,            -- 'order.confirmed'
  name VARCHAR(255) NOT NULL,
  description TEXT,
  channels VARCHAR(20)[] NOT NULL,        -- {'email', 'push', 'in_app'}
  category VARCHAR(50) NOT NULL,          -- 'transactional', 'marketing', 'system'
  is_mandatory BOOLEAN DEFAULT false,     -- user can't opt out (password reset)
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User notification preferences
CREATE TABLE notification_preferences (
  user_id UUID NOT NULL REFERENCES users(id),
  notification_type_id VARCHAR(100) NOT NULL REFERENCES notification_types(id),
  channel VARCHAR(20) NOT NULL,           -- 'email', 'push', 'sms'
  enabled BOOLEAN NOT NULL DEFAULT true,
  PRIMARY KEY (user_id, notification_type_id, channel)
);

-- Notification log
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  type_id VARCHAR(100) NOT NULL,
  channel VARCHAR(20) NOT NULL,
  title VARCHAR(500),
  body TEXT,
  data JSONB,                             -- payload for deep linking
  status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, sent, delivered, failed, read
  sent_at TIMESTAMPTZ,
  read_at TIMESTAMPTZ,
  failed_reason TEXT,
  retry_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_unread
  ON notifications(user_id, created_at DESC) WHERE read_at IS NULL;

-- Device tokens for push
CREATE TABLE push_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  token TEXT NOT NULL UNIQUE,
  platform VARCHAR(20) NOT NULL,          -- 'web', 'ios', 'android'
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_used_at TIMESTAMPTZ
);
```

---

## Provider Abstraction

```typescript
// Abstract provider — swap without code changes
interface NotificationChannel {
  send(notification: ChannelNotification): Promise<SendResult>
}

interface ChannelNotification {
  to: string           // email, phone, device token
  subject?: string
  body: string
  htmlBody?: string
  data?: Record<string, any>
}

interface SendResult {
  success: boolean
  providerId?: string  // external message ID
  error?: string
}

// Email provider
class SendGridEmailChannel implements NotificationChannel {
  async send(notification: ChannelNotification): Promise<SendResult> {
    try {
      const [response] = await sgMail.send({
        to: notification.to,
        from: 'noreply@myapp.com',
        subject: notification.subject,
        html: notification.htmlBody ?? notification.body,
      })
      return { success: true, providerId: response.headers['x-message-id'] }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }
}

// Push provider
class FCMPushChannel implements NotificationChannel {
  async send(notification: ChannelNotification): Promise<SendResult> {
    try {
      const result = await admin.messaging().send({
        token: notification.to,
        notification: { title: notification.subject, body: notification.body },
        data: notification.data,
      })
      return { success: true, providerId: result }
    } catch (error) {
      if (error.code === 'messaging/registration-token-not-registered') {
        await this.deactivateToken(notification.to)
      }
      return { success: false, error: error.message }
    }
  }
}

// Provider registry
class ChannelRegistry {
  private channels: Map<string, NotificationChannel> = new Map()

  register(channelType: string, provider: NotificationChannel) {
    this.channels.set(channelType, provider)
  }

  get(channelType: string): NotificationChannel {
    const channel = this.channels.get(channelType)
    if (!channel) throw new Error(`No provider for channel: ${channelType}`)
    return channel
  }
}
```

---

## Template Engine

```typescript
// Templates stored in DB or files
interface NotificationTemplate {
  typeId: string
  channel: string
  locale: string
  subject?: string   // for email
  body: string       // handlebars/mustache template
}

// Template rendering
class TemplateService {
  async render(
    typeId: string,
    channel: string,
    locale: string,
    variables: Record<string, any>,
  ): Promise<{ subject?: string; body: string; htmlBody?: string }> {
    const template = await this.getTemplate(typeId, channel, locale)

    return {
      subject: template.subject ? Handlebars.compile(template.subject)(variables) : undefined,
      body: Handlebars.compile(template.body)(variables),
      htmlBody: template.htmlBody ? Handlebars.compile(template.htmlBody)(variables) : undefined,
    }
  }
}

// Example templates
// order.confirmed / email / en:
//   subject: "Order #{{orderId}} confirmed!"
//   body: "Hi {{userName}}, your order of {{amount}} has been confirmed."

// order.confirmed / push / en:
//   body: "Order #{{orderId}} confirmed! 🎉"

// order.confirmed / email / vi:
//   subject: "Đơn hàng #{{orderId}} đã được xác nhận!"
//   body: "Xin chào {{userName}}, đơn hàng {{amount}} đã được xác nhận."
```

---

## Notification Router

```typescript
class NotificationRouter {
  constructor(
    private preferences: PreferenceService,
    private templates: TemplateService,
    private channels: ChannelRegistry,
    private queue: NotificationQueue,
  ) {}

  async dispatch(event: NotificationEvent) {
    const { typeId, userId, variables } = event
    const notificationType = await this.getType(typeId)
    const user = await this.getUser(userId)

    for (const channel of notificationType.channels) {
      // Check user preferences (skip if user opted out)
      if (!notificationType.isMandatory) {
        const pref = await this.preferences.get(userId, typeId, channel)
        if (!pref?.enabled) continue
      }

      // Check if user has channel capability
      const target = await this.getChannelTarget(user, channel)
      if (!target) continue

      // Render template
      const rendered = await this.templates.render(
        typeId, channel, user.locale ?? 'en', variables
      )

      // Queue for delivery
      await this.queue.add({
        notificationId: uuid(),
        userId,
        typeId,
        channel,
        target,
        ...rendered,
        data: event.data,
      })
    }
  }

  private async getChannelTarget(user: User, channel: string): Promise<string | null> {
    switch (channel) {
      case 'email': return user.email
      case 'sms': return user.phone
      case 'push':
        const token = await this.getActivePushToken(user.id)
        return token?.token ?? null
      case 'in_app': return user.id
      default: return null
    }
  }
}
```

---

## Digest & Batching

```yaml
problem: "User gets 50 'new comment' notifications in 1 hour"

solution:
  digest:
    rule: "If > 3 notifications of same type in 1 hour → batch into 1 digest"
    implementation: |
      // Instead of sending immediately, buffer in Redis
      await redis.lpush(`digest:${userId}:${typeId}`, JSON.stringify(notification))
      await redis.expire(`digest:${userId}:${typeId}`, 3600) // 1 hour window

      // Cron job every hour: flush digests
      const buffered = await redis.lrange(`digest:${userId}:${typeId}`, 0, -1)
      if (buffered.length > 3) {
        // Send single digest email: "You have 12 new comments"
        await sendDigest(userId, typeId, buffered)
        await redis.del(`digest:${userId}:${typeId}`)
      } else {
        // Send individually
        for (const n of buffered) await sendIndividual(n)
      }

  smart_suppression:
    - "Don't send push if user is currently active (WebSocket connected)"
    - "Don't send email if user read in-app notification within 5 min"
    - "Quiet hours: no push between 22:00-08:00 (user timezone)"
```

---

## Retry & Dead Letter Queue

```yaml
retry_strategy:
  email: "3 retries, exponential backoff (1min, 5min, 30min)"
  sms: "2 retries (1min, 5min) — SMS is expensive"
  push: "3 retries (30s, 2min, 10min)"
  webhook: "5 retries (1min, 5min, 30min, 2h, 24h)"

dead_letter:
  after_max_retries: "Move to DLQ table"
  alert: "If DLQ > 100 items → alert ops team"
  review: "Manual review weekly, fix systematic failures"

webhook_specifics:
  - "Verify endpoint responds 2xx within 30s"
  - "Include signature header for verification (HMAC-SHA256)"
  - "Log attempt + response status for debugging"
```

---

## Notification Center (In-App)

```typescript
// API endpoints
// GET /notifications?unread=true&limit=20 — list notifications
// PATCH /notifications/:id/read — mark as read
// POST /notifications/read-all — mark all as read
// GET /notifications/unread-count — badge count

// Real-time: push new notifications via WebSocket
// ws.send({ type: 'notification', data: notification })

// Frontend component
function NotificationBell() {
  const { data: count } = useQuery({
    queryKey: ['notifications', 'unread-count'],
    queryFn: () => api.getUnreadCount(),
    refetchInterval: 30_000, // poll every 30s (fallback if WS down)
  })

  // Also listen to WebSocket for real-time updates
  useWebSocket('notification', (notification) => {
    queryClient.setQueryData(['notifications', 'unread-count'], (old) => old + 1)
    toast({ title: notification.title, description: notification.body })
  })

  return (
    <Popover>
      <PopoverTrigger>
        <Bell />
        {count > 0 && <Badge>{count > 99 ? '99+' : count}</Badge>}
      </PopoverTrigger>
      <PopoverContent>
        <NotificationList />
      </PopoverContent>
    </Popover>
  )
}
```

---

## Anti-patterns

```yaml
no_user_preferences:
  bad: "Blast all channels for every event — user gets email + SMS + push for 'new like'"
  fix: "User preferences per notification type per channel. Respect opt-out."

no_provider_abstraction:
  bad: "SendGrid SDK called directly in 50 places"
  fix: "Abstract behind interface. Swap provider = change 1 class."

no_templates:
  bad: "Email HTML built with string concatenation in service code"
  fix: "Templates stored separately, rendered with variables"

no_rate_limiting:
  bad: "Bug triggers 1000 emails to same user in 1 minute"
  fix: "Per-user rate limit: max 10 emails/hour, max 50 push/day"

fire_and_forget:
  bad: "Send notification, don't check if delivered"
  fix: "Track status (sent, delivered, failed), retry on failure, alert on DLQ growth"
```
