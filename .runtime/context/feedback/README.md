# Feedback Hub

Muc tieu: ghi nhan feedback ve cac truong hop AI lam sai, lam thieu, hoac khong dung convention de lan sau khong lap lai.

## Files

- `inbox.md`: feedback tho tu user/team (input ban dau)
- `patterns.md`: cac pattern da duoc xac nhan nen ap dung lai
- `anti-patterns.md`: cac loi lap lai can tranh

## Workflow

1. Them feedback moi vao `inbox.md` theo template.
2. Trong buoc `/sync-memory`, Memory Update triage feedback:
   - Neu feedback lap lai/co tinh ben vung -> promote sang `anti-patterns.md`.
   - Neu cach sua da on dinh -> promote sang `patterns.md`.
3. Ghi ro `source_artifact` va `confidence` trong memory updates.

## Notes

- Khong luu secret/token/log dai.
- Chi luu feedback co gia tri tai su dung.
