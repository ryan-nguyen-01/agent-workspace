# BLUEPRINT-005 — Real-time Features (WebSocket/SSE)

**Goal**: Realtime channel (chat/notifications/presence) có auth, scale pattern, và fallback.

---

## When to use

- Chat, live updates, notification center, presence, collaborative UI

---

## Choose transport

```yaml
transport_choice:
  websocket: bidirectional, best for chat/presence
  sse: server->client only, simpler for notifications/stream updates
  webhook: server->server fanout (partners)
```

---

## Reference architecture

- App servers are stateless
- Realtime servers scale horizontally
- Use pub/sub for fan-out (Redis/Kafka)

---

## Auth & security

- Authenticate connection (JWT)
- Authorize channel join (room/tenant)
- Rate limit messages per connection/user

---

## Data model (notifications)

- `Notification` table (persist)
- `NotificationDelivery` log (optional)

---

## Patterns

### Notifications

1) Domain event occurs (e.g., OrderPaid)
2) Publish to broker (Redis/Kafka)
3) Realtime server consumes and emits to user room
4) Persist notification for unread inbox

### Presence

- Track online users with TTL heartbeats
- Use distributed store (Redis) for consistent presence

---

## Tests (minimum)

- Connect with valid token ok
- Connect without token rejected
- Join unauthorized room rejected
- Message rate limit enforced

