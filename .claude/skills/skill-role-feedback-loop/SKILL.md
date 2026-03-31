---
name: skill-role-feedback-loop
description: Skill quản lý feedback loop — thu thập patterns tốt và anti-patterns từ review/test results, lưu vào .agent/context/feedback/, giúp agents học từ lịch sử.
---

# Skill: Feedback Loop

## Mục đích
Hệ thống "bộ nhớ dài hạn" cho agents. Mỗi khi reviewer/tester/security phát hiện issue hoặc pattern tốt, feedback được ghi lại để agents sau đó không lặp lại sai lầm và áp dụng patterns tốt.

---

## Khi nào dùng

```yaml
triggers:
  review_complete:
    from: agent-reviewer
    capture: praise entries → patterns.md, major/critical issues → anti-patterns.md

  review_round_2:
    from: agent-reviewer
    capture: coder đã fix tốt? → patterns.md (good fix pattern)
             coder fix sai? → anti-patterns.md (common fix mistakes)

  test_failure_resolved:
    from: agent-tester
    capture: root cause → anti-patterns.md, fix approach → patterns.md

  security_finding_resolved:
    from: agent-security
    capture: vulnerability pattern → anti-patterns.md, remediation → patterns.md

  migration_complete:
    from: agent-migrator
    capture: migration strategy → patterns.md, pitfalls found → anti-patterns.md
```

---

## File Structure

```
.agent/context/feedback/
├── patterns.md          ← Patterns tốt, cần theo
├── anti-patterns.md     ← Sai lầm, cần tránh
└── stats.md             ← Thống kê: top issues, trends
```

---

## Format: patterns.md

```markdown
# Good Patterns

## Pattern Library

### PAT-001: {Tên pattern ngắn gọn}
- **Category:** {convention | architecture | performance | testing | security}
- **Module:** {module liên quan | global}
- **Description:** {1-2 câu mô tả}
- **Example:**
  ```
  {code snippet minh họa — max 10 lines}
  ```
- **Why good:** {giải thích ngắn tại sao pattern này tốt}
- **Source:** {agent-reviewer | agent-tester | agent-security}
- **Detected:** {timestamp}
- **Frequency:** {số lần pattern này xuất hiện — tăng mỗi lần thấy lại}

---

### PAT-002: ...
```

### Ví dụ entries:

```markdown
### PAT-001: Early return for guard clauses
- **Category:** quality
- **Module:** global
- **Description:** Dùng early return thay vì nested if-else cho validation/guard logic
- **Example:**
  ```typescript
  async findUser(id: string) {
    if (!id) throw new BadRequestException('ID required');
    const user = await this.repo.findOne(id);
    if (!user) throw new NotFoundException('User not found');
    return user;
  }
  ```
- **Why good:** Giảm nesting, dễ đọc, clear error path
- **Source:** agent-reviewer (praise)
- **Detected:** 2025-01-15
- **Frequency:** 5

### PAT-002: Centralized error handling via exception filter
- **Category:** architecture
- **Module:** core
- **Description:** Dùng global exception filter thay vì try-catch ở mỗi controller
- **Example:**
  ```typescript
  @Catch()
  export class AllExceptionsFilter implements ExceptionFilter {
    catch(exception: unknown, host: ArgumentsHost) { ... }
  }
  ```
- **Why good:** DRY, consistent error response format, dễ maintain
- **Source:** agent-reviewer (praise)
- **Detected:** 2025-01-15
- **Frequency:** 3
```

---

## Format: anti-patterns.md

```markdown
# Anti-Patterns — Mistakes to Avoid

## Anti-Pattern Library

### ANTI-001: {Tên anti-pattern ngắn gọn}
- **Category:** {convention | correctness | performance | security | testing}
- **Severity:** {critical | high | medium}
- **Module:** {module liên quan | global}
- **Description:** {vấn đề là gì}
- **Bad example:**
  ```
  {code sai — max 10 lines}
  ```
- **Good alternative:**
  ```
  {code đúng — max 10 lines}
  ```
- **Why bad:** {hậu quả cụ thể}
- **Source:** {agent nào phát hiện}
- **First detected:** {timestamp}
- **Occurrences:** {số lần bị lặp lại — đây là metric quan trọng}
- **Last seen:** {timestamp}

---

### ANTI-002: ...
```

### Ví dụ entries:

```markdown
### ANTI-001: Catching errors without handling
- **Category:** correctness
- **Severity:** high
- **Module:** global
- **Description:** Try-catch mà catch block chỉ console.log, không throw hoặc handle properly
- **Bad example:**
  ```typescript
  try {
    await createOrder(data);
  } catch (error) {
    console.log(error); // swallowed!
  }
  ```
- **Good alternative:**
  ```typescript
  try {
    await createOrder(data);
  } catch (error) {
    this.logger.error('Failed to create order', { error, data });
    throw new InternalServerErrorException('Order creation failed');
  }
  ```
- **Why bad:** Error bị nuốt, caller không biết fail, data corruption risk
- **Source:** agent-reviewer (critical issue)
- **First detected:** 2025-01-10
- **Occurrences:** 3
- **Last seen:** 2025-01-18

### ANTI-002: N+1 queries in loop
- **Category:** performance
- **Severity:** high
- **Module:** global
- **Description:** Gọi DB query trong for loop thay vì batch query
- **Bad example:**
  ```typescript
  for (const order of orders) {
    order.user = await this.userRepo.findOne(order.userId);
  }
  ```
- **Good alternative:**
  ```typescript
  const userIds = orders.map(o => o.userId);
  const users = await this.userRepo.findByIds(userIds);
  const userMap = new Map(users.map(u => [u.id, u]));
  orders.forEach(o => o.user = userMap.get(o.userId));
  ```
- **Why bad:** 100 orders = 100 queries thay vì 1. O(n) vs O(1) DB calls
- **Source:** agent-reviewer (major issue)
- **First detected:** 2025-01-12
- **Occurrences:** 2
- **Last seen:** 2025-01-15
```

---

## Format: stats.md

```markdown
# Feedback Stats

## Overview
- Total patterns: {n}
- Total anti-patterns: {n}
- Last updated: {timestamp}

## Top Anti-Patterns (by occurrences)
| Rank | ID | Name | Occurrences | Severity |
|------|----|------|-------------|----------|
| 1 | ANTI-001 | Catching errors without handling | 3 | high |
| 2 | ANTI-002 | N+1 queries | 2 | high |

## Top Patterns (by frequency)
| Rank | ID | Name | Frequency |
|------|----|------|-----------|
| 1 | PAT-001 | Early return guards | 5 |
| 2 | PAT-002 | Centralized error handling | 3 |

## Trends
- This week: {n} new anti-patterns, {n} new patterns
- Recurring issues: {list anti-patterns with occurrences > 2}
- Improvement areas: {list anti-patterns with decreasing occurrences}
```

---

## Quy trình thu thập feedback

### Từ agent-reviewer:

```
1. Review result có praise entries?
   → Extract: tạo PAT-xxx entry, ghi vào patterns.md

2. Review result có critical/major issues?
   → Kiểm tra: issue này đã có trong anti-patterns.md chưa?
   → Nếu có: tăng occurrences + update last_seen
   → Nếu chưa: tạo ANTI-xxx entry mới

3. Round 2 — coder fix tốt?
   → Extract fix pattern → ghi vào patterns.md
   Round 2 — coder fix sai (thêm issue mới)?
   → Ghi vào anti-patterns.md
```

### Từ agent-tester:

```
1. Test phát hiện code bug?
   → Root cause → anti-patterns.md

2. Test pass với edge case tốt?
   → Test pattern → patterns.md
```

### Từ agent-security:

```
1. Critical finding?
   → Security anti-pattern → anti-patterns.md (severity: critical)

2. Good security practice detected?
   → Security pattern → patterns.md
```

---

## Quy trình sử dụng feedback

### Agent-reviewer đọc trước khi review:

```
1. Đọc anti-patterns.md → top 5 relevant (filter by module + global)
2. Đọc patterns.md → top 5 relevant
3. Check diff against anti-patterns → flag ngay nếu match
4. Check diff against patterns → praise nếu match
```

### Agent-coder đọc trước khi code (tuỳ chọn):

```
1. Đọc anti-patterns.md → filter by module đang code
2. Chủ động tránh anti-patterns đã biết
3. Follow patterns.md cho module đó
```

### Orchestrator đọc khi phân tích:

```
1. Đọc stats.md → biết areas cần attention
2. Nếu anti-pattern có occurrences > 5 → suggest refactor task
3. Include relevant feedback trong context inject cho agents
```

---

## ID Generation

```
Patterns: PAT-{3 digits} — auto-increment
Anti-patterns: ANTI-{3 digits} — auto-increment
Tracking: đọc last ID từ file → increment
```

---

## Retention & Cleanup

```yaml
rules:
  max_patterns: 50
  max_anti_patterns: 50

  cleanup:
    pattern_stale: >90 days không thấy lại → archive
    anti_pattern_resolved: occurrences giảm về 0 trong 30 days → mark resolved
    stats_refresh: rebuild stats.md mỗi tuần

  archive:
    Patterns/Anti-patterns cũ → move to feedback/archive.md
    Giữ stats summary
```

---

## Nguyên tắc

- **Automated collection** — agents tự ghi feedback, không cần user
- **Dedup** — check trước khi thêm, tăng counter nếu đã có
- **Relevant only** — mỗi agent chỉ đọc feedback liên quan (filter by module + category)
- **Actionable** — mỗi entry phải có example code cụ thể
- **Metric-driven** — occurrences/frequency cho biết severity thực tế
- **Low overhead** — thu thập trong quá trình review, không cần agent riêng
