---
name: skill-qc-runner
description: Run QC from the handoff document, record test results, and stop immediately on blocker bugs.
---

# Skill: QC Runner

Use when a task is QC_READY.

## Flow

```text
Read QC handoff
Create test cases
Test local before higher environments unless instructed otherwise
Record each case result
On blocker, stop and create blocker bug
On non-blocker, create bug and continue unaffected cases
QC_DONE requires zero open blockers
After QC_DONE, write qc-delivery-report.md for user handover
```

## QC Delivery Report

After QC_DONE, write `qc-delivery-report.md` using the template:

```text
Include:
  - Tóm tắt: what was tested, overall verdict
  - Kết quả QC: stats (total/pass/fail/blocked/blocker count)
  - Những gì đã hoàn thành: completed features list
  - Files thay đổi: services and files
  - Test Results Summary: table by category
  - Known Limitations: deferred items with severity
  - Bugs mở: blockers and non-blockers
  - Hướng dẫn verify cho User: concrete steps user can run to verify
  - Đề xuất tiếp theo: recommendations for future work

Template: .claude/templates/qc-delivery-report.template.md
Target audience: the USER (not other agents)
```

## Rules

```text
QC does not fix code.
QC does not continue after blocker.
QC does not store real secrets.
After QC_DONE, always write delivery report before declaring done.
```
