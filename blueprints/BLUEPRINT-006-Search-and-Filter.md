# BLUEPRINT-006 — Search & Filter

**Goal**: Search API có filter/sort/pagination, hỗ trợ full-text (optional) + autocomplete.

---

## When to use

- List pages có filter/sort
- Search across entities (courses, lessons, products)

---

## Two levels

### Level 1 — Database search (default)

- LIKE/ILIKE (PostgreSQL)
- trigram index (optional)
- structured filters via indexed columns

### Level 2 — Search engine (Elasticsearch)

- Full-text relevance
- autocomplete suggestions
- facets

---

## API contract (recommended)

`GET /search`

Query:
- `q` (string)
- `filters` (key/value)
- `sort` (field)
- `order` (asc|desc)
- `page`, `limit` (or cursor)

Response:
- `data`
- `meta`

---

## Indexing pipeline (if Elasticsearch)

- Source of truth: DB
- Sync options:
  - event-driven (Outbox → consumer)
  - CDC
  - scheduled reindex

---

## Pitfalls

- Unbounded queries (limit cap)
- Sorting by non-indexed fields
- N+1 loading for results

