# Handover — {{TASK_ID}}

> Tài liệu bàn giao từ dev sang QC. Self-contained: QC đọc file này là đủ để test.

**Task:** {{TASK_TITLE}}  
**Service:** {{SERVICE}}  
**Owner agent:** {{OWNER_AGENT}}  
**Handover version:** v{{N}} ({{v1: first handover | v2+: after blocker fix}})  
**Created:** {{TIMESTAMP}}  
**Dev state transition:** dev-done → qc-ready

---

## 1. Task summary

{{1-2 câu mô tả task}}

**Scope:** {{service folder path}}  
**Type:** feature | bug-fix | refactor  
**Links:** task file `tasks/{{TASK_ID}}.md`

---

## 2. Changes

**Files changed:** ({{n}} files)

```
{{list from git diff --name-only, grouped by module}}

services/{{service}}/src/
  + new-file.ts
  M modified-file.ts
  D deleted-file.ts
```

**Summary:**
- {{1 bullet per logical change}}
- {{...}}

---

## 3. API Diff

### Endpoints added
- `POST /api/v1/...` — {{purpose}}
  - Request: `{ ... }`
  - Response 200: `{ ... }`
  - Errors: 400, 401, 404

### Endpoints changed
- `GET /api/v1/...` — {{what changed}}
  - **Breaking?** Yes/No
  - Migration note: {{if breaking}}

### Endpoints removed
- `DELETE /api/v1/legacy` — replaced by `POST /api/v1/...`

### Schema changes
- Table `{{table}}`:
  - `+ column_new (type, nullable=false, default=...)`
  - `M column_existing: type changed from X to Y`
- Event `{{event_name}}`:
  - new field `...`

**N/A** → nếu task không đụng API.

---

## 4. Test Evidence

### Unit tests (by coder)
- Files: `{{paths}}`
- Run: `{{command}}`
- Result: {{n}}/{{n}} PASS

### Integration / E2E tests (by tester)
- Files: `{{paths}}`
- Run: `{{command}}`
- Result: {{n}}/{{n}} PASS
- Coverage: {{%}}

### Manual smoke test (by coder before handover)
- [ ] Happy path verified
- [ ] Error case verified

### Review report
- Link: `tasks/{{TASK_ID}}.md` section `## Review report`
- Conclusion: PASS

---

## 5. Env & Keys

### New env vars required

| Var name | Purpose | Env | Source to request from |
|----------|---------|-----|------------------------|
| `STRIPE_KEY_LOCAL` | Stripe test API | local | Stripe test dashboard |
| `STRIPE_KEY_DEV` | Stripe test API | dev | user-provided |
| `STRIPE_KEY_SIT` | Stripe test API | sit | user-provided |

### Changed env vars

| Var name | Before | After | Note |
|----------|--------|-------|------|
| ... | ... | ... | ... |

### Infra dependency

- [ ] Database migration run: `{{command}}`
- [ ] Redis key seeded: {{if any}}
- [ ] Event topic created: {{if any}}

**Secret placeholder only — KHÔNG ghi giá trị thật.**

---

## 6. How to verify (step-by-step cho QC)

### Prerequisite
1. Pull branch / merge commit `{{sha}}`
2. Install: `{{install command}}`
3. Run migration: `{{migration command}}`
4. Start service: `{{start command}}`
5. Setup env: copy `.env.example` → `.env.<target-env>`, fill keys từ section 5

### Acceptance Criteria checklist

- [ ] **AC-1:** {{acceptance criteria 1}}
  - Step 1: {{action}}
  - Step 2: {{verify}}
  - Expected: {{result}}

- [ ] **AC-2:** {{acceptance criteria 2}}
  - Steps: ...
  - Expected: ...

{{...}}

### Edge cases to verify
- {{edge case 1}}
- {{edge case 2}}

### Negative test
- {{error case 1}}
- {{error case 2}}

---

## 7. Known limitations

- {{Limitation 1: edge case chưa handle, lý do}}
- {{Limitation 2: tech debt, plan fix sau}}
- {{Limitation 3: performance caveat}}

N/A → nếu không có.

---

## 8. Scope of retest

> Section này CHỈ ÁP DỤNG khi handover version ≥ v2 (sau khi fix blocker bug).

**For v1 (first handover):** Full feature scope — test tất cả AC + edge + negative.

**For v2+ (after blocker fix):**
- [ ] Chỉ retest: {{phần bị fix}}
- [ ] Related paths: {{API/module có dependency với fix}}
- [ ] Full regression: Yes / No
  - Yes nếu: fix đụng shared code / common utils / schema core
  - No nếu: fix isolated trong 1 handler/function

---

## Audit trail

| Version | Date | Reason | Dev |
|---------|------|--------|-----|
| v1 | {{date}} | First handover | {{agent}} |
| v2 | {{date}} | Fix BUG-B-... | {{agent}} |
