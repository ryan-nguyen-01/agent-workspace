# Feedback Hub

Muc tieu: ghi nhan feedback ve cac truong hop AI lam sai, lam thieu, hoac khong dung convention de lan sau khong lap lai.

## Files

- `inbox.md`: feedback tho tu user/team (input ban dau)
- `patterns.md`: cac pattern da duoc xac nhan nen ap dung lai
- `anti-patterns.md`: cac loi lap lai can tranh

## Workflow

1. Them feedback moi vao `inbox.md` theo template.
2. Neu feedback den tu bug/err khi coding, bat buoc ghi `root_cause`, `prevention_rule`, `regression_check`, va `recurrence_key`.
3. Trong buoc `/sync-memory`, Memory Update triage feedback:
   - Neu feedback lap lai/co tinh ben vung -> promote sang `anti-patterns.md`.
   - Neu cach sua da on dinh -> promote sang `patterns.md`.
4. Ghi ro `source_artifact` va `confidence` trong memory updates.

## Coding Error Loop

Khi user/manual test hoac Dev Verification phat hien agent coding sai:

1. Ghi defect canonical vao `.runtime/bugs/blockers/` hoac `.runtime/bugs/non-blockers/`.
2. Link defect vao `.runtime/tasks/<task-id>/bugs.yaml`.
3. Them feedback raw vao `inbox.md` voi `issue_type: coding-error|regression|verification-miss`.
4. Sau khi fix/retest, promote durable prevention sang `anti-patterns.md` hoac `patterns.md`.
5. Task Analysis/Coder Leader phai dua pattern lien quan vao context pack de coder khong lap lai loi.

## Notes

- Khong luu secret/token/log dai.
- Chi luu feedback co gia tri tai su dung.
