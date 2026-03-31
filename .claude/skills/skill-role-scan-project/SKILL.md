---
name: skill-role-scan-project
description: Quét toàn bộ cấu trúc project để hiểu tổ chức code, modules, entry points mà không đọc từng file chi tiết.
---

# Skill: Scan Project Structure

## Mục đích
Hiểu nhanh cấu trúc tổng thể của project: có những modules nào, entry points ở đâu, tổ chức code theo pattern gì. Không đọc nội dung chi tiết từng file.

## Nguyên tắc
- Breadth first: hiểu toàn cảnh trước khi đi sâu
- Dừng ở 2-3 levels depth — đủ để hiểu structure
- Ưu tiên đọc index files, barrel files, main files
- Phân biệt production code với test/config/build files

## Quy trình quét

### Bước 1 — Root level scan
```
Đọc:
- README.md (tối đa 100 dòng đầu)
- package.json / pyproject.toml / pom.xml / go.mod (phần scripts + dependencies)
- .env.example (chỉ variable names)
- Folder list ở root level
```

### Bước 2 — Source folder scan
```
Xác định source root: src/ | app/ | lib/ | internal/ | packages/
Liệt kê tất cả folders ở level 1 trong source root
Đây là danh sách modules sơ bộ
```

### Bước 3 — Module classification
Với mỗi folder trong source root, phân loại:

```yaml
module_types:
  controller:     # API endpoints, route handlers
    patterns: ["controller", "handler", "router", "route", "api"]
  service:        # Business logic
    patterns: ["service", "usecase", "domain", "business"]
  repository:     # Data access
    patterns: ["repository", "repo", "store", "dao", "database", "db"]
  middleware:     # Request/response interceptors
    patterns: ["middleware", "interceptor", "guard", "filter", "pipe"]
  util:           # Shared utilities
    patterns: ["util", "helper", "common", "shared", "lib"]
  config:         # Configuration
    patterns: ["config", "setting", "env", "constant"]
  model:          # Data models/schemas
    patterns: ["model", "schema", "entity", "dto", "type", "interface"]
  test:           # Tests (exclude from module list)
    patterns: ["test", "spec", "__test__", "e2e"]
```

### Bước 4 — Entry points detection
```
Tìm entry points theo thứ tự:
Backend:  main.ts | main.py | main.go | Application.java | index.js
Frontend: main.tsx | App.tsx | pages/_app.tsx | index.html
Library:  index.ts | index.js | mod.rs | lib.rs
```

### Bước 5 — Dependency graph (sơ bộ)
```
Với mỗi module, đọc nhanh file index/barrel:
- Import gì từ module khác? → depends_on
- Export gì ra ngoài? → exports (tên, không cần chi tiết)
Chỉ cần level 1 dependency, không cần đệ quy
```

## Output format

```yaml
scan_result:
  source_root: src/
  entry_points:
    - main.ts
  modules:
    - name: auth
      path: src/auth/
      type: service
      index_file: src/auth/index.ts
      estimated_exports: [AuthService, AuthGuard, JwtStrategy]
      depends_on: [user, config]

    - name: user
      path: src/user/
      type: service
      index_file: src/user/index.ts
      estimated_exports: [UserService, UserRepository]
      depends_on: [database]

    - name: database
      path: src/database/
      type: repository
      index_file: src/database/index.ts
      estimated_exports: [DatabaseModule, DatabaseService]
      depends_on: []

  excluded:
    - path: src/__tests__/
      reason: test files
    - path: src/types/
      reason: type definitions only
```

## Các dấu hiệu nhận biết pattern

### Monorepo
```
Có: packages/ | apps/ | libs/ | workspace.json | nx.json | turbo.json
→ Scan từng package riêng biệt
→ Xác định shared packages
```

### Feature-based structure
```
src/features/<feature-name>/
└── components/ services/ hooks/ types/
→ Module = feature, không phải layer
```

### Layer-based structure
```
src/
├── controllers/
├── services/
├── repositories/
└── models/
→ Module = domain entity
```
