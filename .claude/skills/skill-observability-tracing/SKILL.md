---
name: skill-observability-tracing
description: Best practices distributed tracing với OpenTelemetry: instrumentation, spans, context propagation, sampling và integration với Jaeger/Tempo.
---

# Skill: OpenTelemetry Distributed Tracing

## Setup — Node.js

```typescript
// instrumentation.ts — ✅ Load BEFORE anything else (--require flag)
import { NodeSDK } from '@opentelemetry/sdk-node'
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node'
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http'
import { Resource } from '@opentelemetry/resources'
import { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION } from '@opentelemetry/semantic-conventions'
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base'
import { TraceIdRatioBasedSampler } from '@opentelemetry/sdk-trace-base'

const exporter = new OTLPTraceExporter({
  url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318/v1/traces',
})

const sdk = new NodeSDK({
  resource: new Resource({
    [ATTR_SERVICE_NAME]: process.env.SERVICE_NAME || 'my-service',
    [ATTR_SERVICE_VERSION]: process.env.APP_VERSION || '1.0.0',
    environment: process.env.NODE_ENV || 'production',
  }),
  spanProcessor: new BatchSpanProcessor(exporter, {
    maxQueueSize: 1000,
    maxExportBatchSize: 100,
    scheduledDelayMillis: 5000,
  }),
  sampler: process.env.NODE_ENV === 'production'
    ? new TraceIdRatioBasedSampler(0.1)  // ✅ Sample 10% in production
    : new TraceIdRatioBasedSampler(1.0), // 100% in dev
  instrumentations: [
    getNodeAutoInstrumentations({
      '@opentelemetry/instrumentation-http': { enabled: true },
      '@opentelemetry/instrumentation-express': { enabled: true },
      '@opentelemetry/instrumentation-pg': { enabled: true },
      '@opentelemetry/instrumentation-redis': { enabled: true },
      '@opentelemetry/instrumentation-fs': { enabled: false },  // Too noisy
    }),
  ],
})

sdk.start()

process.on('SIGTERM', () => sdk.shutdown())
```

## Manual Instrumentation

```typescript
import { trace, context, SpanStatusCode, SpanKind } from '@opentelemetry/api'

const tracer = trace.getTracer('my-service', '1.0.0')

// ✅ Custom span
async function processOrder(orderId: string): Promise<Order> {
  return tracer.startActiveSpan('processOrder', async (span) => {
    span.setAttributes({
      'order.id': orderId,
      'order.type': 'standard',
    })

    try {
      const order = await orderRepo.findById(orderId)
      span.setAttribute('order.userId', order.userId)

      await paymentService.charge(order)
      span.addEvent('payment.processed', { amount: order.total })

      await inventoryService.reserve(order.items)
      span.setStatus({ code: SpanStatusCode.OK })

      return order
    } catch (err) {
      span.recordException(err as Error)
      span.setStatus({ code: SpanStatusCode.ERROR, message: (err as Error).message })
      throw err
    } finally {
      span.end()
    }
  })
}

// ✅ External HTTP call span
async function callExternalAPI(url: string, data: unknown) {
  return tracer.startActiveSpan('external.http.post', {
    kind: SpanKind.CLIENT,
    attributes: {
      'http.url': url,
      'http.method': 'POST',
    },
  }, async (span) => {
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: JSON.stringify(data),
        // ✅ Inject trace context into outgoing headers
        headers: propagateTraceContext({}),
      })
      span.setAttribute('http.status_code', response.status)
      return response.json()
    } catch (err) {
      span.recordException(err as Error)
      throw err
    } finally {
      span.end()
    }
  })
}
```

## Context Propagation

```typescript
import { propagation, context } from '@opentelemetry/api'
import { W3CTraceContextPropagator } from '@opentelemetry/core'

// ✅ Extract trace context from incoming request headers
function extractTraceContext(headers: Record<string, string>) {
  return propagation.extract(context.active(), headers)
}

// ✅ Inject trace context into outgoing request headers
function propagateTraceContext(headers: Record<string, string>) {
  const carrier: Record<string, string> = { ...headers }
  propagation.inject(context.active(), carrier)
  return carrier
}

// Express middleware
app.use((req, res, next) => {
  const ctx = extractTraceContext(req.headers as Record<string, string>)
  context.with(ctx, next)
})
```

## Setup — Python (FastAPI)

```python
# instrumentation.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

def setup_tracing(app, engine):
    exporter = OTLPSpanExporter(endpoint=settings.OTEL_ENDPOINT)

    provider = TracerProvider(
        resource=Resource.create({
            SERVICE_NAME: settings.SERVICE_NAME,
            SERVICE_VERSION: settings.APP_VERSION,
        })
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    # ✅ Auto-instrument frameworks
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument(engine=engine)
    HTTPXClientInstrumentor().instrument()

# Manual span
tracer = trace.get_tracer(__name__)

async def process_payment(order_id: str, amount: float):
    with tracer.start_as_current_span("process_payment") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("payment.amount", amount)

        try:
            result = await payment_gateway.charge(amount)
            span.add_event("payment.charged", {"transaction_id": result.id})
            return result
        except Exception as e:
            span.record_exception(e)
            span.set_status(StatusCode.ERROR, str(e))
            raise
```

## Semantic Conventions

```typescript
// ✅ Use standard attribute names (OpenTelemetry semantic conventions)
span.setAttributes({
  // HTTP
  'http.method': 'POST',
  'http.url': 'https://api.example.com/users',
  'http.status_code': 201,

  // Database
  'db.system': 'postgresql',
  'db.name': 'myapp',
  'db.operation': 'SELECT',
  'db.statement': 'SELECT * FROM users WHERE id = $1',

  // Message queue
  'messaging.system': 'rabbitmq',
  'messaging.operation': 'publish',
  'messaging.destination': 'user.events',

  // Custom business
  'user.id': userId,
  'order.id': orderId,
  'tenant.id': tenantId,
})
```

## Anti-patterns

```typescript
// ❌ Tạo tracer ở mỗi function
const tracer = trace.getTracer('service')  // In every file
// ✅ Singleton tracer, module-level

// ❌ Không end span trong error path
tracer.startActiveSpan('op', (span) => {
  throw new Error('oops')  // span.end() never called!
})
// ✅ try/finally luôn gọi span.end()

// ❌ Log sensitive data vào span attributes
span.setAttribute('user.password', password)  // ❌

// ❌ Sample rate 100% trong production (quá nhiều data + overhead)
new TraceIdRatioBasedSampler(1.0)  // ❌ In prod
// ✅ 1-10% sampling, hoặc dùng ParentBased sampler

// ❌ Không propagate context → broken traces
const response = await fetch(url)  // ❌ Missing traceparent header
// ✅ Inject context vào headers
```
