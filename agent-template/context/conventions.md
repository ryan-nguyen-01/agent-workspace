# Conventions

> Auto-detected từ code thực tế. **Không đoán, không ép style.** Mỗi entry có EVIDENCE (file path).

## Naming

- **Files:** TBD — evidence: `{{file path}}`
- **Functions:** TBD — evidence: `{{file path}}`
- **Classes:** TBD
- **Constants:** TBD
- **Interfaces / Types:** TBD

## Imports

- **Style:** absolute | relative | alias (`@/...`) — evidence: `{{file path}}`
- **Order:** external → internal → types — evidence: `{{file path}}`

## Code style

- **Indent:** 2 spaces | 4 spaces | tabs
- **Quotes:** single | double
- **Semicolons:** yes / no
- **Trailing comma:** yes / no
- **Config source:** `.prettierrc` | `.eslintrc` | `editorconfig`

## Error handling

- **Pattern:** throw Error | custom class | Result object | error codes
- **Evidence:** `{{file path}}`

## Validation

- **Library:** zod | joi | class-validator | manual | none
- **Evidence:** `{{file path}}`

## Logging

- **Library:** console | winston | pino | structured-json
- **Level:** debug/info/warn/error
- **Evidence:** `{{file path}}`

## Response format (API)

- **Success shape:** TBD (VD `{ data: ..., meta: ... }`)
- **Error shape:** TBD (VD `{ error: { code, message } }`)
- **Status codes used:** TBD

## Tests

- **Framework:** jest | vitest | pytest | junit | playwright | cypress | none
- **Location:** colocated | `__tests__/` | `tests/`
- **Naming:** `*.spec.*` | `*.test.*` | `test_*.py`
- **Style:** describe-it | test() | class-based

## Git conventions

- **Commit style:** conventional (feat:/fix:/chore:) | freeform
- **Branch naming:** `feature/...` | `feat/...` | free

## Project-specific patterns

- {{pattern 1 — evidence}}
- {{pattern 2 — evidence}}

---

_Auto-detected. Thêm mới khi context-keeper phát hiện pattern lặp ≥2 lần._
