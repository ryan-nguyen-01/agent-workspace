# inputs/

Folder để user cung cấp **tài liệu project-level** cho agents đọc khi onboard và phân tích task. Khác với `services/` (chứa source code clone) và `.runtime/tasks/<id>/task-input.md` (input per-task).

## Khi nào dùng

Drop tài liệu vào đây khi:
- Bắt đầu project mới và muốn agent hiểu business context trước khi đọc code
- Có PRD/HLD/LLD/ADR không nằm trong repo source
- Cung cấp API contract, OpenAPI spec, domain glossary
- Share runbooks, ops playbooks, post-mortem reference
- Đính kèm diagram (PNG/SVG/PDF) hoặc exported Figma

Agent onboarding sẽ **scan toàn bộ** thư mục này và cite source path vào `.runtime/context/project-brain.yaml` + service brains.

## Cấu trúc

```text
inputs/
├── README.md            ← file này
├── product/             PRD, business specs, user stories, market analysis
├── architecture/        HLD, LLD, ADRs, system diagrams, infrastructure docs
├── api/                 OpenAPI/Swagger specs, Postman collections, API contracts
├── domain/              Domain models, glossary, business rules, data dictionary
├── runbooks/            Ops playbooks, incident response, deployment guides
└── misc/                Files chưa phân loại
```

User không bắt buộc dùng đủ subdir — để trống cũng được. Nếu file không khớp category nào, đặt vào `misc/`.

## Định dạng được hỗ trợ

| Định dạng | Xử lý |
|---|---|
| `.md`, `.txt` | Đọc trực tiếp, parse heading + content |
| `.yaml`, `.yml`, `.json` | Parse structured |
| `.html` | Strip tags, lấy text |
| `.pdf` | Đọc qua Read tool (giới hạn 20 trang/request) |
| `.png`, `.jpg`, `.svg` | Đọc visual (multimodal) |
| `.csv`, `.tsv` | Sample header + first rows |
| Binary khác | Ghi metadata only (filename, size, mtime) |

## Cách agent dùng

**Onboarding agent** (run khi `/onboard`):
1. Scan `inputs/` recursively (skip `.gitkeep`, hidden files)
2. Mỗi file → tạo entry trong `.runtime/context/inputs-index.yaml` với `path`, `category`, `summary`, `last_modified`, `confidence`
3. Trích key facts (architecture decisions, API contracts, business rules) vào `project-brain.yaml` với `source: inputs/<path>`
4. Trích service-specific facts (vd. orders API spec) vào service brains

**Task-analysis agent**: đọc `inputs-index.yaml` trước, chỉ mở file relevant theo task intent.

**Service coders**: chỉ đọc file trong `inputs/api/` và `inputs/domain/` nếu task contract change.

## Confidence ranking

Agent dùng heuristic:

```text
high      file mtime <= 90 days, format có cấu trúc (yaml/json/openapi)
medium    file mtime <= 365 days, markdown có heading rõ
low       file mtime > 365 days, không có metadata, hoặc misc/
```

Memory entries inferred từ `inputs/` luôn cite source. Nếu sau này code/code-review mâu thuẫn với `inputs/`, code thắng và agent flag cho user review.

## Bảo mật

- **KHÔNG commit credentials, secrets, raw tokens** dưới bất kỳ hình thức nào. R-013 áp dụng cho cả `inputs/`.
- Tài liệu confidential (vd. contract NDA, internal-only specs) → thêm vào `.gitignore` thủ công:
  ```text
  inputs/product/confidential-*.md
  inputs/misc/legal-*
  ```
- Khi commit lên public repo, audit `inputs/` trước.

## Quan hệ với các folder khác

```text
inputs/                    Tài liệu user cung cấp (project-level reference, persistent)
services/<repo>/           Source code clone (gitignored, persistent)
.runtime/tasks/<id>/        Artifact per-task (auto-generated, includes task-input.md per task)
.runtime/context/           Memory được agent generate sau khi đọc các nguồn trên
```

Quy tắc:
- `inputs/` là **source of truth của user-provided knowledge**.
- `.runtime/context/` là **distilled brain agent** — không thay thế `inputs/`, chỉ cite nó.
- Khi `inputs/` thay đổi, chạy `/sync-memory --refresh-index` để agent re-scan.
