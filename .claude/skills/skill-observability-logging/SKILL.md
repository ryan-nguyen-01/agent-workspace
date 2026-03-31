---
name: skill-observability-logging
description: Best practices structured logging: Winston/Pino (Node.js), loguru (Python), log levels, correlation IDs, request logging và production patterns.
---

# Skill: Structured Logging

## Node.js — Pino (Recommended)

```typescript
// lib/logger.ts
import pino from 'pino'

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  // ✅ JSON in production, pretty in dev
  transport: process.env.NODE_ENV !== 'production' ? {
    target: 'pino-pretty',
    options: { colorize: true, translateTime: 'SYS:standard' },
  } : undefined,
  base: {
    service: process.env.SERVICE_NAME || 'my-service',
    version: process.env.APP_VERSION || '1.0.0',
    env: process.env.NODE_ENV,
  },
  // ✅ Redact sensitive fields
  redact: {
    paths: ['req.headers.authorization', 'body.password', 'body.token', '*.creditCard'],
    censor: '[REDACTED]',
  },
  serializers: {
    err: pino.stdSerializers.err,
    req: pino.stdSerializers.req,
    res: pino.stdSerializers.res,
  },
})

// ✅ Child logger với context
export function createContextLogger(context: Record<string, unknown>) {
  return logger.child(context)
}
```

## Request Logging Middleware (Express/Fastify)

```typescript
// ✅ Request ID propagation
import { randomUUID } from 'crypto'

export function requestLogger(req: Request, res: Response, next: NextFunction): void {
  const requestId = req.headers['x-request-id'] as string || randomUUID()
  const start = Date.now()

  // ✅ Attach to request for use in handlers
  req.logger = logger.child({
    requestId,
    method: req.method,
    url: req.url,
    ip: req.ip,
    userAgent: req.headers['user-agent'],
  })

  res.setHeader('X-Request-ID', requestId)

  res.on('finish', () => {
    req.logger.info({
      statusCode: res.statusCode,
      duration: Date.now() - start,
    }, 'Request completed')
  })

  next()
}
```

## Python — Loguru

```python
# lib/logger.py
import sys
import json
from loguru import logger

def setup_logger(env: str = 'production', level: str = 'INFO') -> None:
    logger.remove()  # Remove default handler

    if env == 'development':
        # ✅ Pretty output for development
        logger.add(
            sys.stdout,
            level=level,
            colorize=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - {message}",
        )
    else:
        # ✅ JSON output for production (log aggregation)
        def json_sink(message):
            record = message.record
            log_entry = {
                "time": record["time"].isoformat(),
                "level": record["level"].name,
                "service": "my-service",
                "message": record["message"],
                "module": record["module"],
                "function": record["function"],
                "line": record["line"],
                **record["extra"],
            }
            if record["exception"]:
                log_entry["exception"] = str(record["exception"])
            print(json.dumps(log_entry), flush=True)

        logger.add(json_sink, level=level, serialize=False)

# FastAPI request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    start = time.time()

    with logger.contextualize(request_id=request_id, method=request.method, url=str(request.url)):
        logger.info("Request started")
        response = await call_next(request)
        duration = (time.time() - start) * 1000

        logger.info(
            "Request completed",
            status_code=response.status_code,
            duration_ms=round(duration, 2),
        )

    response.headers["X-Request-ID"] = request_id
    return response
```

## Log Levels — Khi nào dùng

```typescript
// ✅ ERROR — Lỗi cần action ngay, ảnh hưởng user
logger.error({ err, userId, orderId }, 'Payment processing failed')

// ✅ WARN — Bất thường nhưng hệ thống vẫn hoạt động
logger.warn({ retryCount, endpoint }, 'External API retry attempt')

// ✅ INFO — Events quan trọng trong normal flow
logger.info({ userId, plan }, 'User subscription upgraded')

// ✅ DEBUG — Chi tiết cho debugging (không log trong production)
logger.debug({ query, params, duration }, 'Database query executed')

// ✅ TRACE — Chi tiết cực kỳ, chỉ khi diagnose specific issue
logger.trace({ payload }, 'Message received from queue')
```

## Structured Log Fields

```typescript
// ✅ Consistent field names (follow OpenTelemetry conventions)
logger.info({
  // Identification
  traceId: context.traceId,
  spanId: context.spanId,
  requestId: req.id,
  userId: req.user?.id,

  // Action
  event: 'user.created',        // What happened
  resource: 'user',             // Resource type
  resourceId: user.id,          // Resource identifier

  // Context
  duration: Date.now() - start, // ms
  statusCode: 201,
}, 'User created successfully')

// ✅ Error logging với full context
logger.error({
  err: {
    message: err.message,
    stack: err.stack,
    code: err.code,
  },
  context: { userId, action: 'createUser' },
}, 'Failed to create user')
```

## Anti-patterns

```typescript
// ❌ String interpolation (mất structured data)
logger.info(`User ${userId} created order ${orderId}`)  // ❌
// ✅ Structured fields
logger.info({ userId, orderId }, 'User created order')

// ❌ console.log trong production
console.log('Processing request...')  // ❌ No level, no structure

// ❌ Log sensitive data
logger.info({ password: req.body.password, token })  // ❌
// ✅ Redact tự động với pino redact config

// ❌ Log quá nhiều ở INFO level (log noise)
logger.info('Checking if user exists...')  // ❌ Too verbose for INFO
logger.debug('Checking if user exists...')  // ✅

// ❌ Không có requestId → không trace được request qua services
// ✅ Luôn propagate X-Request-ID header
```
