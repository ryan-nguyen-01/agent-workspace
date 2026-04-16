# Environments

> File này lưu config cho mỗi env. **KHÔNG bao giờ ghi giá trị secret** — chỉ placeholder/tên var.

## Env list

### local
- **base_url:** `http://localhost:3000`
- **db:** `postgres://localhost:5432/app_local`
- **key file:** `.env.local` (gitignored)
- **setup command:** `docker-compose up -d && npm run migrate && npm run dev`
- **health check:** `curl http://localhost:3000/health`
- **required keys:**
  - `DATABASE_URL`
  - `JWT_SECRET` (dev-safe random)
  - `STRIPE_KEY_LOCAL` (Stripe test key — user lấy từ Stripe dashboard)

### dev
- **base_url:** `https://dev.yourapp.com`
- **db:** managed (dev cluster)
- **key file:** `.env.dev` (gitignored)
- **access:** VPN required? SSH tunnel?
- **health check:** `curl https://dev.yourapp.com/health`
- **required keys:**
  - `STRIPE_KEY_DEV` — xin user
  - `SENDGRID_KEY_DEV` — xin user
  - `REDIS_URL_DEV` — xin user

### sit
- **base_url:** `https://sit.yourapp.com`
- **db:** managed (sit cluster)
- **key file:** `.env.sit` (gitignored)
- **access:** VPN required
- **health check:** `curl https://sit.yourapp.com/health`
- **required keys:**
  - `STRIPE_KEY_SIT` — xin user
  - `SENDGRID_KEY_SIT` — xin user

### (prod — reference only, không dùng cho QC)
- Không test trên prod tự động.
- User phải trigger manual cho smoke test.

---

## Domain config

Cách inject base_url vào test:

```bash
# Test framework env (vitest/jest):
ENV=local npm test
ENV=sit npm test
```

Test config đọc `process.env.ENV` → map sang `base_url` ở trên.

---

## Key handling rules

1. **Không ghi key thật vào `.agent/`** — chỉ placeholder ở file này
2. **Key file `.env.<env>` phải gitignored**
3. **qc-runner thiếu key** → HỎI USER (exception của rule autonomy):
   ```
   Cần: <KEY_NAME> cho env <ENV>.
   Options:
   [1] Paste key → ghi vào .env.<env>
   [2] Skip env này
   [3] Abort QC
   ```
4. **Không log key** trong test output hay bug report — mask `***`

---

## Setup hướng dẫn (cho dev lần đầu)

```bash
# local env
cp .env.example .env.local
# mở .env.local, fill các key dev-safe

# dev env (nếu có access)
cp .env.example .env.dev
# xin key từ team / vault

# sit env
cp .env.example .env.sit
# xin key từ team / vault
```
