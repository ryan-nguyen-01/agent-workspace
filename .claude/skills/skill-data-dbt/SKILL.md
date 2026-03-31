---
name: skill-data-dbt
description: Best practices dbt — modeling (staging/marts), tests, seeds, snapshots, sources, incremental models, docs, CI, và deployment.
---

# Skill: dbt

## Khi nào dùng

- Analytics engineering / warehouse transforms (ELT)
- Muốn chuẩn hóa data models + tests + lineage docs

---

## Project layout (recommended)

```
models/
  staging/
  marts/
  intermediate/
seeds/
snapshots/
tests/
macros/
```

---

## Modeling conventions

- `stg_*`: raw → cleaned
- `int_*`: join/reusable logic
- `fct_*`, `dim_*`: marts

---

## Tests

- Schema tests: `not_null`, `unique`, accepted values
- Relationship tests for FKs
- Custom tests for business invariants

---

## Incremental models

- Use `unique_key`
- Handle late arriving data
- Backfill strategy documented

---

## Docs

- `dbt docs generate` + publish
- Describe sources/columns with owners

---

## CI

- `dbt build --select state:modified+` for PRs (if state artifacts available)
- Fail fast on tests

