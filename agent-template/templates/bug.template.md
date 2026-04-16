# Bug: {{BUG_ID}}

> Format ID:  
> Blocker: `BUG-B-YYYYMMDD-<slug>`  
> Non-blocker: `BUG-N-YYYYMMDD-<slug>`

## Metadata

- **ID:** {{BUG_ID}}
- **Severity:** blocker | high | medium | low | cosmetic
- **Classification:** blocker | non-blocker
- **Found in task:** {{TASK_ID}}
- **Found by:** agent-qc-runner
- **Found at:** {{timestamp}}
- **Env:** local | dev | sit
- **Status:** open | fixing | resolved | wontfix

## Blocker rationale (chỉ cho blocker)

Thỏa điều kiện nào trong section 7.1 workflow.md?

- [ ] Happy path FAIL
- [ ] Crash / 500 error trên core endpoint
- [ ] Data corruption / data loss
- [ ] Security vuln (auth bypass, injection, ...)
- [ ] Block downstream test khác

## Description

{{1-2 câu mô tả vấn đề gặp phải}}

## Reproduction steps

1. {{step 1}}
2. {{step 2}}
3. {{step 3}}

## Expected vs Actual

**Expected:** {{behavior đúng theo AC}}

**Actual:** {{behavior sai quan sát được}}

## Impact

- **User-facing:** {{ai bị ảnh hưởng, mức độ}}
- **Data:** {{có corrupt/loss data không}}
- **Blocks:** {{AC/endpoint/feature nào bị block}}

## Evidence

- Screenshot: {{link or path}}
- Log snippet:
  ```
  {{log}}
  ```
- Request/response nếu là API bug:
  ```
  {{curl + response}}
  ```

**Không ghi secret — mask `***`.**

## Environment details

- Env: {{local/dev/sit}}
- URL: {{base_url — không ghi key}}
- Service version: {{commit sha}}
- Browser/Client: {{if FE}}

## Root cause (fill sau khi dev phân tích)

{{Dev điền sau khi phân tích xong, trước khi fix}}

## Fix summary (fill sau khi resolved)

- **Fixed in:** handover-v{{N}}
- **Commit:** {{sha}}
- **Fix approach:** {{summary}}

## Retest

- **Scope of retest:** {{từ handover-v{{N}} section 8}}
- **Retested at:** {{timestamp}}
- **Result:** PASS | FAIL (→ tạo bug mới)

---

## History

| Timestamp | Actor | Action |
|-----------|-------|--------|
| {{ts}} | agent-qc-runner | Created |
| {{ts}} | agent-orchestrator | Assigned to {{coder}} |
| {{ts}} | agent-coder-... | Started fix |
| {{ts}} | agent-coder-... | Fix done |
| {{ts}} | agent-qc-runner | Retest PASS → resolved |
