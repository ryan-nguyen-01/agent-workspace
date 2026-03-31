---
name: skill-arch-distributed-systems
description: Distributed systems fundamentals — CAP theorem, consistency models, distributed locks, consensus algorithms, clock synchronization, failure modes, và partition tolerance.
---

# Skill: Distributed Systems

## CAP Theorem

```yaml
definition: |
  Trong distributed system, chỉ có thể đảm bảo 2 trong 3:
  - Consistency: Mọi read nhận data mới nhất
  - Availability: Mọi request nhận response (không timeout)
  - Partition Tolerance: System tiếp tục hoạt động khi network partition

reality: |
  Network partition LUÔN có thể xảy ra → phải chọn giữa C và A
  CP: Consistency + Partition Tolerance (sacrifice Availability)
  AP: Availability + Partition Tolerance (sacrifice Consistency)

systems:
  CP:
    examples: [PostgreSQL, MongoDB (default), Redis Cluster, ZooKeeper, etcd]
    behavior: "Khi partition → reject writes để giữ consistency"
    when: "Financial transactions, inventory count, leader election"

  AP:
    examples: [Cassandra, DynamoDB, CouchDB, DNS]
    behavior: "Khi partition → accept writes, resolve conflicts later"
    when: "Social media feeds, shopping cart, user activity logs"

  choosing:
    questions:
      - "Stale data có acceptable không? (AP = yes, CP = no)"
      - "Downtime có acceptable không? (CP = yes cho writes, AP = no)"
      - "Conflicts có resolve được không? (AP = phải resolve)"
```

---

## Consistency Models

```yaml
strong_consistency:
  description: Read luôn trả data mới nhất sau write
  implementation: Synchronous replication, single leader
  cost: High latency, lower availability
  when: Bank balances, inventory stock, seat booking
  example: |
    User A: write balance = $100
    User B: read balance → ALWAYS $100 (never stale)

eventual_consistency:
  description: Read CÓ THỂ trả stale data, nhưng eventually converge
  implementation: Async replication, multi-leader, conflict resolution
  cost: Low latency, high availability
  when: Social media likes, view counts, recommendations
  window: Typically 100ms - few seconds
  example: |
    User A: post photo
    User B (different region): may not see photo for 1-2 seconds

causal_consistency:
  description: Causally related events seen in order, concurrent events may differ
  implementation: Vector clocks, causal ordering
  when: Chat messages, comment threads
  example: |
    Reply ALWAYS appears after original message
    But 2 unrelated messages may appear in different order for different users

read_your_writes:
  description: User always sees their own writes
  implementation: Read from primary after write, or session-based routing
  when: User updates profile → must see updated profile immediately
  example: |
    User A: update name to "John"
    User A: read profile → ALWAYS "John"
    User B: read User A → may see old name briefly

monotonic_reads:
  description: Once you see a value, you never see an older value
  implementation: Pin client to same replica
  when: Prevent confusing UX (data appearing then disappearing)
```

---

## Distributed Locks

### When Needed

```yaml
use_cases:
  - Prevent double processing (payment, email send)
  - Mutual exclusion on shared resource (file, DB row)
  - Leader election
  - Rate limiting per-user across instances
  - Scheduled job: only 1 instance executes
```

### Redis-based Lock (Redlock)

```typescript
class DistributedLock {
  constructor(
    private redis: RedisClient,
    private lockTTL: number = 10_000, // 10 seconds
  ) {}

  async acquire(resource: string, timeout: number = 5000): Promise<string | null> {
    const lockId = crypto.randomUUID()
    const deadline = Date.now() + timeout

    while (Date.now() < deadline) {
      // SET NX: chỉ set nếu key chưa tồn tại
      const acquired = await this.redis.set(
        `lock:${resource}`,
        lockId,
        'PX', this.lockTTL,
        'NX'
      )

      if (acquired === 'OK') return lockId

      // Wait before retry
      await sleep(50 + Math.random() * 50)
    }

    return null // Failed to acquire
  }

  async release(resource: string, lockId: string): Promise<boolean> {
    // Atomic: chỉ release nếu đúng owner (tránh release lock của người khác)
    const script = `
      if redis.call('get', KEYS[1]) == ARGV[1] then
        return redis.call('del', KEYS[1])
      end
      return 0
    `
    const result = await this.redis.eval(script, 1, `lock:${resource}`, lockId)
    return result === 1
  }

  async withLock<T>(resource: string, fn: () => Promise<T>): Promise<T> {
    const lockId = await this.acquire(resource)
    if (!lockId) throw new Error(`Failed to acquire lock on ${resource}`)

    try {
      return await fn()
    } finally {
      await this.release(resource, lockId)
    }
  }
}

// Usage
await lock.withLock(`order:${orderId}`, async () => {
  const order = await orderRepo.findById(orderId)
  if (order.status !== 'pending') throw new Error('Already processed')
  await processPayment(order)
  await orderRepo.update(orderId, { status: 'paid' })
})
```

### Lock Considerations

```yaml
fencing_tokens:
  problem: "Lock expires while holder still processing → 2 holders"
  solution: |
    Lock includes monotonically increasing token
    Resource checks: reject operations with old tokens
    token = await lock.acquire('resource')  // returns 34
    await storage.write(data, { fencingToken: 34 })
    // Storage rejects writes with token < 34

lock_renewal:
  problem: "Processing takes longer than TTL → lock expires"
  solution: |
    Heartbeat: renew lock every TTL/3
    const interval = setInterval(() => lock.extend(resource, lockId, ttl), ttl / 3)
    try { await process() } finally { clearInterval(interval) }

deadlock_prevention:
  - Always acquire locks in same order
  - Use timeouts (never wait forever)
  - Lock hierarchy: fine-grained → coarse-grained
```

---

## Consensus & Leader Election

### Raft (Simplified)

```yaml
concept: |
  Nodes elect a leader. Leader handles all writes.
  If leader dies → new election.

roles:
  leader: Receives writes, replicates to followers
  follower: Replicates from leader, forwards writes to leader
  candidate: Trying to become leader (during election)

election:
  1. Follower timeout (no heartbeat from leader)
  2. Becomes candidate, votes for self
  3. Requests votes from other nodes
  4. Majority votes → becomes leader
  5. Sends heartbeats to maintain leadership

log_replication:
  1. Client sends write to leader
  2. Leader appends to local log
  3. Leader sends AppendEntries to followers
  4. Majority acknowledges → leader commits
  5. Leader responds to client

tools: [etcd, Consul, ZooKeeper]
managed: [AWS ElastiCache (Redis Cluster), CockroachDB]
```

### Leader Election with Redis

```typescript
class LeaderElection {
  private isLeader = false
  private renewInterval: NodeJS.Timer | null = null

  constructor(
    private redis: RedisClient,
    private nodeId: string,
    private electionKey: string = 'leader',
    private ttl: number = 15_000,
  ) {}

  async start(): Promise<void> {
    await this.tryBecomeLeader()
    setInterval(() => this.tryBecomeLeader(), this.ttl / 2)
  }

  private async tryBecomeLeader(): Promise<void> {
    const acquired = await this.redis.set(
      this.electionKey, this.nodeId,
      'PX', this.ttl, 'NX'
    )

    if (acquired === 'OK') {
      this.isLeader = true
      this.startRenewing()
    } else {
      const currentLeader = await this.redis.get(this.electionKey)
      this.isLeader = currentLeader === this.nodeId
      if (this.isLeader) {
        await this.redis.pexpire(this.electionKey, this.ttl)
      }
    }
  }
}
```

---

## Clock & Ordering

### Problem

```yaml
issue: |
  Máy khác nhau có clock khác nhau (clock drift)
  → Không dùng wall clock để order events across machines

solutions:
  logical_clocks:
    lamport_clock:
      description: "Counter tăng dần — only partial ordering"
      rule: "On send: counter++. On receive: counter = max(local, received) + 1"

    vector_clock:
      description: "Array of counters (1 per node) — detect concurrent events"
      example: |
        Node A: [2, 0, 0]
        Node B: [1, 3, 0]
        → Concurrent! (A không biết về B's events 2,3 và ngược lại)

  hybrid_logical_clock (HLC):
    description: "Wall clock + logical counter — best of both"
    used_by: [CockroachDB, YugabyteDB]
    benefit: "Causal ordering + human-readable timestamps"

  ntp_sync:
    description: "Sync clocks via NTP (Network Time Protocol)"
    accuracy: "~1-10ms between servers in same datacenter"
    limitation: "Not sufficient for strict ordering — use logical clocks"
```

### Snowflake ID

```typescript
// Twitter Snowflake: 64-bit unique, time-ordered, distributed
// [1 bit unused][41 bits timestamp][10 bits machine ID][12 bits sequence]
class SnowflakeGenerator {
  private sequence = 0
  private lastTimestamp = -1
  private readonly epoch = 1609459200000 // 2021-01-01

  constructor(private machineId: number) {
    if (machineId < 0 || machineId > 1023) throw new Error('Machine ID: 0-1023')
  }

  generate(): bigint {
    let timestamp = Date.now() - this.epoch

    if (timestamp === this.lastTimestamp) {
      this.sequence = (this.sequence + 1) & 0xfff // 4096 per ms
      if (this.sequence === 0) {
        while (timestamp <= this.lastTimestamp) {
          timestamp = Date.now() - this.epoch
        }
      }
    } else {
      this.sequence = 0
    }

    this.lastTimestamp = timestamp
    return (BigInt(timestamp) << 22n) | (BigInt(this.machineId) << 12n) | BigInt(this.sequence)
  }
}
```

---

## Failure Modes

```yaml
fail_stop:
  description: Node crashes, stops responding
  detection: Heartbeat timeout
  handling: Replace node, reroute traffic
  example: Process killed, server power off

fail_slow:
  description: Node responds slowly (degraded, not dead)
  detection: Latency monitoring, P99 spike
  handling: Circuit breaker, timeout, remove from LB
  danger: Worst failure type — can cascade

byzantine_failure:
  description: Node behaves incorrectly (sends wrong data)
  detection: Very hard — need consensus (BFT algorithms)
  handling: Voting (2f+1 nodes to tolerate f failures)
  when: Blockchain, untrusted environments

network_partition:
  description: Network split — some nodes can't talk to others
  detection: Heartbeat failures in both directions
  handling: CAP choice — CP (reject writes) or AP (accept, resolve later)

split_brain:
  description: 2 nodes both think they're leader
  prevention: Fencing tokens, quorum-based election
  danger: Data corruption if both write

cascading_failure:
  description: One service failure causes others to fail
  prevention: Circuit breaker, bulkhead, timeout, graceful degradation
  example: |
    DB slow → App threads exhausted → Health check fails
    → LB removes instance → remaining instances overloaded → total outage
```

### Designing for Failure

```yaml
principles:
  assume_failure: "Everything fails — design for it"
  blast_radius: "Minimize impact of any single failure"
  graceful_degradation: "Reduce functionality rather than total outage"
  fail_fast: "Detect problems early, fail quickly, recover quickly"

patterns:
  retry_with_backoff: "Transient failures → retry with exponential delay"
  circuit_breaker: "Repeated failures → stop calling, fallback"
  bulkhead: "Isolate resources — failure in A doesn't affect B"
  timeout: "Never wait forever — set deadline on every call"
  fallback: "If primary fails → use cached data / default / degraded response"
  health_check: "Proactive detection before users notice"
  chaos_engineering: "Inject failures in production to find weaknesses"
```

---

## Idempotency

```yaml
why: "In distributed systems, retries are inevitable → operations MUST be idempotent"

definition: "f(x) = f(f(x)) — running operation multiple times = same result as once"

naturally_idempotent:
  - GET requests
  - DELETE by ID (delete same ID twice → same result)
  - SET value (set x = 5 twice → x = 5)

NOT_idempotent:
  - INCREMENT counter
  - INSERT (creates duplicate)
  - Transfer money (double charge)

making_idempotent:
  idempotency_key:
    description: "Client generates unique key per operation"
    implementation: |
      1. Client sends: POST /payments { amount: 100, idempotencyKey: "abc-123" }
      2. Server checks: does "abc-123" exist in processed_requests?
      3. If YES → return cached response (no re-processing)
      4. If NO → process, store result with key "abc-123", return response
    storage: "Redis with TTL (24h) or DB table"

  optimistic_locking:
    description: "Version check before update"
    implementation: |
      UPDATE orders
      SET status = 'confirmed', version = version + 1
      WHERE id = $1 AND version = $2
      -- If version mismatch → 0 rows affected → concurrent modification detected
```

---

## Anti-patterns

```yaml
trusting_network:
  bad: "Assume network always works"
  fix: "Timeout, retry, circuit breaker on every external call"

trusting_clocks:
  bad: "Use wall clock for ordering events across machines"
  fix: "Logical clocks, vector clocks, or HLC"

ignoring_partial_failure:
  bad: "Treat distributed operation as all-or-nothing"
  fix: "Saga pattern, compensating transactions, idempotency"

shared_mutable_state:
  bad: "Multiple services write same DB table"
  fix: "Database per service, communicate via events"

synchronous_everything:
  bad: "Chain of synchronous calls across 5 services"
  fix: "Async events for non-critical paths, CQRS for reads"

no_backpressure:
  bad: "Producer pushes unlimited messages, consumer overwhelmed"
  fix: "Queue with limits, consumer pull, rate limiting"
```
