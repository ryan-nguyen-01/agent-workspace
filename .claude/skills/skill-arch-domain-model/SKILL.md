---
name: skill-arch-domain-model
description: Thiết kế domain model: xác định bounded contexts, core entities, relationships, business rules và viết ERD dạng text hoặc Mermaid.
---

# Skill: Domain Modeling

## Bounded Context Identification

```
Hỏi để xác định boundaries:
1. "Ai làm gì với hệ thống?" → Actors → Aggregates
2. "Dữ liệu nào thuộc nhau?" → Clusters → Contexts
3. "Đội nào owns phần nào?" → Team boundaries → Context boundaries
4. "Thay đổi ở A có bắt buộc thay đổi B không?" → Coupling → có thể cùng context
```

```markdown
### Bounded Contexts

| Context | Owns | Exposes |
|---------|------|---------|
| Identity | User, Credential, Session | UserId, UserProfile |
| Catalog | Product, Category, Price | ProductId, ProductSummary |
| Ordering | Order, OrderItem, Cart | OrderId, OrderStatus |
| Payment | Transaction, Invoice | PaymentStatus |
| Notification | Message, Template, Delivery | — |
```

## Entity Definition Format

```markdown
### [EntityName]
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, generated | |
| email | string | unique, not null | normalized lowercase |
| name | string | not null, max 100 | |
| role | enum | not null, default 'viewer' | admin/editor/viewer |
| passwordHash | string | not null | bcrypt, never expose |
| createdAt | datetime | not null, auto | UTC |
| updatedAt | datetime | not null, auto | UTC |
| deletedAt | datetime | nullable | soft delete |
```

## Relationships

```markdown
### ERD (Mermaid)

\`\`\`mermaid
erDiagram
    User {
        uuid id PK
        string email
        string name
        enum role
        datetime createdAt
    }

    Order {
        uuid id PK
        uuid userId FK
        enum status
        decimal total
        datetime createdAt
    }

    OrderItem {
        uuid id PK
        uuid orderId FK
        uuid productId FK
        int quantity
        decimal unitPrice
    }

    Product {
        uuid id PK
        string name
        decimal price
        int stock
    }

    User ||--o{ Order : "places"
    Order ||--|{ OrderItem : "contains"
    Product ||--o{ OrderItem : "included in"
\`\`\`
```

## Business Rules Capture

```markdown
### Business Rules

#### User
- BR-U01: Email phải unique và lowercase
- BR-U02: Password tối thiểu 8 ký tự, phải có chữ hoa và số
- BR-U03: User bị soft-delete vẫn giữ data nhưng không login được

#### Order
- BR-O01: Order chỉ cancel được khi status = 'pending'
- BR-O02: Order không thể sửa sau khi status = 'paid'
- BR-O03: total = sum(quantity × unitPrice) cho tất cả items
- BR-O04: Khi cancel order → hoàn lại stock cho từng product

#### Product
- BR-P01: stock không được âm
- BR-P02: Không xóa product nếu còn OrderItem reference (soft delete)
```

## Value Objects vs Entities

```markdown
### Entities (có identity, mutable)
- User, Order, Product, Payment

### Value Objects (không có identity, immutable)
- Address { street, city, country, zipCode }
- Money { amount, currency }
- DateRange { from, to }
- Email (validated, normalized)

### Aggregates (consistency boundary)
- Order Aggregate: Order (root) + OrderItems
  → Tất cả thay đổi OrderItem phải qua Order root
  → Order đảm bảo business rules về tổng tiền
```

## Database Schema Guidelines

```sql
-- ✅ UUID primary keys (portable, no sequence dependency)
id UUID PRIMARY KEY DEFAULT gen_random_uuid()

-- ✅ Timestamps trên mọi table
created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

-- ✅ Soft delete pattern
deleted_at TIMESTAMPTZ,  -- NULL = active

-- ✅ Enum as DB type (type-safe)
CREATE TYPE order_status AS ENUM ('pending', 'paid', 'shipped', 'cancelled');

-- ✅ Foreign key với explicit ON DELETE
user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,

-- ✅ Partial index cho soft delete
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
```

## Anti-patterns

```
❌ God object — 1 entity có 50+ fields và nhiều responsibilities
   → Split thành multiple entities / value objects

❌ Anemic domain model — chỉ có getters/setters, logic nằm hết trong service
   → Business rules nên nằm trong entity/aggregate

❌ Bỏ qua business rules trong model — chỉ design schema kỹ thuật
   → Business rules là phần quan trọng nhất của domain model

❌ Circular references giữa contexts
   → Contexts communicate qua events hoặc IDs, không phải object references
```
