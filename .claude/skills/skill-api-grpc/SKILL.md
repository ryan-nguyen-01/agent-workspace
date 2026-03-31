---
name: skill-api-grpc
description: Best practices implement gRPC — Protobuf schema design, service definitions, streaming patterns, error handling, interceptors, và production deployment.
---

# Skill: gRPC & Protocol Buffers

## Khi nào dùng gRPC

```yaml
NÊN dùng:
  - Service-to-service communication (internal)
  - High throughput, low latency requirements
  - Bi-directional streaming (real-time data, chat)
  - Polyglot services (Go ↔ TypeScript ↔ Python ↔ Java)
  - Strong contract enforcement (schema-first)

KHÔNG nên dùng:
  - Public-facing APIs (browsers không native support gRPC)
  - Simple CRUD không cần performance cao
  - Team chưa quen gRPC (learning curve)
  - Cần human-readable payloads (debug, curl)

Kết hợp:
  External → REST/GraphQL (qua API Gateway)
  Internal → gRPC (giữa services)
```

---

## Protobuf Schema Design

### File Structure

```
proto/
├── common/
│   ├── pagination.proto     ← shared types
│   ├── timestamp.proto
│   └── error.proto
├── user/
│   └── v1/
│       └── user.proto       ← user service definition
├── order/
│   └── v1/
│       └── order.proto
└── buf.yaml                 ← buf lint/breaking config
```

### Message Definitions

```protobuf
syntax = "proto3";

package user.v1;

option go_package = "github.com/myapp/proto/user/v1;userv1";
option java_package = "com.myapp.proto.user.v1";

import "google/protobuf/timestamp.proto";
import "common/pagination.proto";

// ✅ Clear field numbers — never reuse deleted field numbers
message User {
  string id = 1;
  string email = 2;
  string name = 3;
  UserRole role = 4;
  bool is_active = 5;
  google.protobuf.Timestamp created_at = 6;
  google.protobuf.Timestamp updated_at = 7;

  // Reserved: removed fields — prevent accidental reuse
  reserved 8, 9;
  reserved "phone", "address";
}

// ✅ Enum with UNSPECIFIED default
enum UserRole {
  USER_ROLE_UNSPECIFIED = 0;  // PHẢI có — default value
  USER_ROLE_ADMIN = 1;
  USER_ROLE_MEMBER = 2;
  USER_ROLE_VIEWER = 3;
}

// ✅ Request/Response per RPC — không reuse
message GetUserRequest {
  string id = 1;
}

message GetUserResponse {
  User user = 1;
}

message ListUsersRequest {
  common.PaginationRequest pagination = 1;
  UserFilter filter = 2;
}

message ListUsersResponse {
  repeated User users = 1;
  common.PaginationResponse pagination = 2;
}

message UserFilter {
  optional UserRole role = 1;
  optional bool is_active = 2;
  optional string search = 3;  // search by name or email
}

// ✅ Create/Update dùng separate messages
message CreateUserRequest {
  string email = 1;
  string name = 2;
  string password = 3;
  UserRole role = 4;
}

message UpdateUserRequest {
  string id = 1;
  optional string name = 2;      // optional = chỉ update nếu provided
  optional string email = 3;
  optional UserRole role = 4;
}
```

### Service Definitions

```protobuf
service UserService {
  // Unary RPCs
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc CreateUser(CreateUserRequest) returns (GetUserResponse);
  rpc UpdateUser(UpdateUserRequest) returns (GetUserResponse);
  rpc DeleteUser(DeleteUserRequest) returns (google.protobuf.Empty);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);

  // Server streaming: server gửi nhiều responses
  rpc WatchUserChanges(WatchUserRequest) returns (stream UserEvent);

  // Client streaming: client gửi nhiều requests
  rpc BatchCreateUsers(stream CreateUserRequest) returns (BatchCreateResponse);

  // Bi-directional streaming
  rpc SyncUsers(stream SyncRequest) returns (stream SyncResponse);
}
```

### Shared Types

```protobuf
// common/pagination.proto
syntax = "proto3";
package common;

message PaginationRequest {
  int32 page = 1;
  int32 page_size = 2;      // max 100
  string sort_by = 3;       // field name
  SortOrder sort_order = 4;
}

message PaginationResponse {
  int32 total = 1;
  int32 page = 2;
  int32 page_size = 3;
  int32 total_pages = 4;
}

enum SortOrder {
  SORT_ORDER_UNSPECIFIED = 0;
  SORT_ORDER_ASC = 1;
  SORT_ORDER_DESC = 2;
}
```

---

## Error Handling

### gRPC Status Codes (mapping từ HTTP)

```yaml
codes:
  OK: 0                    # 200 — Success
  CANCELLED: 1             # 499 — Client cancelled
  UNKNOWN: 2               # 500 — Unknown error
  INVALID_ARGUMENT: 3      # 400 — Validation error
  DEADLINE_EXCEEDED: 4     # 504 — Timeout
  NOT_FOUND: 5             # 404 — Resource not found
  ALREADY_EXISTS: 6        # 409 — Duplicate
  PERMISSION_DENIED: 7     # 403 — Forbidden
  UNAUTHENTICATED: 16      # 401 — Not authenticated
  RESOURCE_EXHAUSTED: 8    # 429 — Rate limited
  FAILED_PRECONDITION: 9   # 400 — State invalid
  ABORTED: 10              # 409 — Concurrency conflict
  UNIMPLEMENTED: 12        # 501 — Not implemented
  INTERNAL: 13             # 500 — Internal error
  UNAVAILABLE: 14          # 503 — Service unavailable
```

### Error Implementation

```typescript
// ✅ Rich error details
import { status } from '@grpc/grpc-js'
import { Status } from '@grpc/grpc-js/build/src/constants'

function notFound(resource: string, id: string): ServiceError {
  const error = new Error(`${resource} ${id} not found`) as ServiceError
  error.code = status.NOT_FOUND
  error.details = JSON.stringify({
    code: 'NOT_FOUND',
    resource,
    id,
  })
  return error
}

function validationError(fields: Record<string, string[]>): ServiceError {
  const error = new Error('Validation failed') as ServiceError
  error.code = status.INVALID_ARGUMENT
  error.details = JSON.stringify({
    code: 'VALIDATION_FAILED',
    fields,
  })
  return error
}

// Usage in service
async getUser(call: ServerUnaryCall<GetUserRequest, GetUserResponse>, callback: sendUnaryData<GetUserResponse>) {
  const user = await this.userRepo.findById(call.request.id)
  if (!user) {
    return callback(notFound('User', call.request.id))
  }
  callback(null, { user: toProto(user) })
}
```

---

## Interceptors (Middleware)

### Server-side

```typescript
// ✅ Logging interceptor
function loggingInterceptor(
  call: ServerUnaryCall<any, any>,
  callback: sendUnaryData<any>,
  next: () => void
) {
  const start = Date.now()
  const method = call.getPath()

  const originalCallback = callback
  callback = (error, response) => {
    const duration = Date.now() - start
    logger.info('gRPC call', {
      method,
      duration,
      status: error ? error.code : 'OK',
    })
    originalCallback(error, response)
  }

  next()
}

// ✅ Auth interceptor
function authInterceptor(
  call: ServerUnaryCall<any, any>,
  callback: sendUnaryData<any>,
  next: () => void
) {
  const metadata = call.metadata
  const token = metadata.get('authorization')[0] as string

  if (!token?.startsWith('Bearer ')) {
    return callback({
      code: status.UNAUTHENTICATED,
      details: 'Missing authorization token',
    } as ServiceError)
  }

  try {
    const payload = verifyToken(token.slice(7))
    call.metadata.set('user-id', payload.sub)
    call.metadata.set('user-roles', payload.roles.join(','))
    next()
  } catch {
    callback({
      code: status.UNAUTHENTICATED,
      details: 'Invalid or expired token',
    } as ServiceError)
  }
}
```

### Client-side

```typescript
// ✅ Retry interceptor (client)
function retryInterceptor(options, nextCall) {
  const maxRetries = 3
  const retryableCodes = [
    status.UNAVAILABLE,
    status.DEADLINE_EXCEEDED,
    status.RESOURCE_EXHAUSTED,
  ]

  let attempt = 0
  function makeCall() {
    attempt++
    const call = nextCall(options)

    call.on('status', (statusObj) => {
      if (retryableCodes.includes(statusObj.code) && attempt < maxRetries) {
        const delay = Math.pow(2, attempt) * 100
        setTimeout(makeCall, delay)
      }
    })

    return call
  }

  return makeCall()
}
```

---

## Streaming Patterns

### Server Streaming

```typescript
// Server sends multiple responses (e.g., watch changes)
async watchUserChanges(
  call: ServerWritableStream<WatchUserRequest, UserEvent>
) {
  const subscription = eventBus.subscribe('user.*', (event) => {
    call.write({
      type: event.type,
      user: toProto(event.payload),
      timestamp: Timestamp.fromDate(new Date()),
    })
  })

  call.on('cancelled', () => {
    subscription.unsubscribe()
  })
}
```

### Client Streaming

```typescript
// Client sends multiple requests (e.g., batch upload)
async batchCreateUsers(
  call: ServerReadableStream<CreateUserRequest, BatchCreateResponse>,
  callback: sendUnaryData<BatchCreateResponse>
) {
  const users: User[] = []
  const errors: string[] = []

  call.on('data', async (request: CreateUserRequest) => {
    try {
      const user = await this.userService.create(request)
      users.push(user)
    } catch (err) {
      errors.push(`${request.email}: ${err.message}`)
    }
  })

  call.on('end', () => {
    callback(null, {
      created_count: users.length,
      error_count: errors.length,
      errors,
    })
  })
}
```

---

## Production Config

### Deadlines (Timeouts)

```typescript
// ✅ LUÔN set deadline cho mọi RPC call
const deadline = new Date()
deadline.setSeconds(deadline.getSeconds() + 5) // 5s timeout

client.getUser(request, { deadline }, (err, response) => {
  if (err?.code === status.DEADLINE_EXCEEDED) {
    // Handle timeout
  }
})
```

### Connection Management

```typescript
// ✅ Channel options
const client = new UserServiceClient(
  'user-service:50051',
  grpc.credentials.createInsecure(),
  {
    'grpc.max_receive_message_length': 4 * 1024 * 1024,  // 4MB
    'grpc.max_send_message_length': 4 * 1024 * 1024,
    'grpc.keepalive_time_ms': 10000,
    'grpc.keepalive_timeout_ms': 5000,
    'grpc.keepalive_permit_without_calls': 1,
    'grpc.max_reconnect_backoff_ms': 10000,
  }
)
```

### Load Balancing

```yaml
client_side:
  description: Client biết tất cả server addresses, tự balance
  policies: [round_robin, pick_first, weighted_round_robin]
  config: |
    // DNS-based service discovery + round robin
    const client = new Client('dns:///user-service:50051', creds, {
      'grpc.service_config': JSON.stringify({
        loadBalancingConfig: [{ round_robin: {} }]
      })
    })

proxy_based:
  description: L7 proxy (Envoy, Linkerd) handle load balancing
  benefit: No client logic needed, advanced routing
  tools: [Envoy, Istio, Linkerd]
```

---

## Schema Evolution Rules

```yaml
backward_compatible (safe):
  - Add new fields (new field number)
  - Add new RPC methods
  - Add new enum values (NOT the default 0)
  - Mark fields as deprecated

breaking (AVOID):
  - Remove fields → use 'reserved' instead
  - Change field types
  - Change field numbers
  - Rename fields (wire format unaffected, but code breaks)
  - Remove enum values

versioning:
  strategy: Package versioning (user.v1, user.v2)
  migration: Support v1 + v2 simultaneously
  deprecation: Sunset v1 after all clients migrated
```

---

## Anti-patterns

```yaml
huge_messages:
  bad: "Message > 4MB → gRPC default limit, performance hit"
  fix: "Chunk large data, use streaming RPCs"

no_deadline:
  bad: "RPC calls without timeout → hang forever"
  fix: "ALWAYS set deadline on every call"

shared_proto:
  bad: "1 giant proto file cho mọi services"
  fix: "1 proto package per service, shared types in common/"

string_for_everything:
  bad: "Dùng string cho dates, numbers, enums"
  fix: "google.protobuf.Timestamp, int32/int64, proper enums"

no_unspecified_enum:
  bad: "Enum bắt đầu từ meaningful value"
  fix: "Luôn có _UNSPECIFIED = 0 (proto3 default)"

rpc_per_field:
  bad: "GetUserName(), GetUserEmail(), GetUserAge() — chatty"
  fix: "GetUser() trả full resource, client dùng field mask nếu cần"
```
