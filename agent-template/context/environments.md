# Environments

> **KHÔNG ghi secret value.** Chỉ placeholder + tên var.  
> Fill initial bởi `agent-onboarding`, user bổ sung dev/sit keys.

## Envs

### local

- **base_url:** TBD (VD `http://localhost:3000`)
- **db:** TBD
- **key file:** `.env.local` (gitignored)
- **setup:** TBD (VD `docker-compose up -d && npm run dev`)
- **health check:** TBD (VD `curl http://localhost:3000/health`)
- **required keys:**
  - TBD

### dev

- **base_url:** TBD
- **key file:** `.env.dev` (gitignored)
- **access:** TBD (VPN / SSH tunnel / public)
- **required keys:**
  - TBD — xin từ user

### sit

- **base_url:** TBD
- **key file:** `.env.sit` (gitignored)
- **access:** TBD
- **required keys:**
  - TBD — xin từ user

---

## Key handling rules

1. Key THẬT chỉ nằm trong `.env.<env>` (gitignored), KHÔNG bao giờ commit vào `.agent/`
2. `qc-runner` thiếu key → HỎI USER (exception của rule autonomy):
   - `[1] Paste key` → ghi vào `.env.<env>`
   - `[2] Skip env này`
   - `[3] Abort QC`
3. Log/bug report → mask key bằng `***`

---

## Domain routing cho test

Test framework đọc `ENV` var → inject đúng `base_url`:

```bash
ENV=local npm test
ENV=sit npm test
```

---

_Fill đầy đủ trước khi qc-runner test env đó lần đầu._
