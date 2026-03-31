---
name: skill-fe-i18n
description: Best practices internationalization (i18n) và localization (l10n) — i18next (React), vue-i18n, Angular i18n, RTL support, date/number/currency formatting, backend translations, và translation workflow.
---

# Skill: Internationalization (i18n)

## Khi nào cần i18n

```yaml
LUÔN setup i18n từ đầu nếu:
  - Target audience đa quốc gia
  - Product có plan mở rộng sang thị trường khác
  - Có yêu cầu compliance (GDPR → phải hiện nội dung bằng ngôn ngữ local)

Setup i18n SAU cũng OK nếu:
  - MVP chỉ target 1 thị trường
  - Nhưng KHÔNG hardcode strings — dùng constants file để dễ migrate sau
```

---

## React + i18next (Recommended)

### Setup

```typescript
// i18n/config.ts
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import Backend from 'i18next-http-backend'

i18n
  .use(Backend)              // lazy load translations
  .use(LanguageDetector)     // detect user language
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    supportedLngs: ['en', 'vi', 'ja', 'ko'],
    defaultNS: 'common',
    ns: ['common', 'auth', 'dashboard', 'errors'],

    interpolation: {
      escapeValue: false, // React already escapes
    },

    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },

    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
  })

export default i18n
```

### Translation Files

```
public/locales/
├── en/
│   ├── common.json
│   ├── auth.json
│   ├── dashboard.json
│   └── errors.json
├── vi/
│   ├── common.json
│   ├── auth.json
│   ├── dashboard.json
│   └── errors.json
└── ja/
    └── ...
```

```json
// en/common.json
{
  "app_name": "MyApp",
  "nav": {
    "home": "Home",
    "dashboard": "Dashboard",
    "settings": "Settings"
  },
  "actions": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "confirm": "Are you sure?"
  },
  "pagination": {
    "showing": "Showing {{from}}-{{to}} of {{total}}",
    "next": "Next",
    "previous": "Previous"
  }
}

// en/auth.json
{
  "login": {
    "title": "Sign in to your account",
    "email": "Email address",
    "password": "Password",
    "submit": "Sign in",
    "forgot": "Forgot password?",
    "no_account": "Don't have an account? <1>Sign up</1>"
  },
  "errors": {
    "invalid_credentials": "Invalid email or password",
    "account_locked": "Account locked. Try again in {{minutes}} minutes."
  }
}
```

```json
// vi/auth.json
{
  "login": {
    "title": "Đăng nhập tài khoản",
    "email": "Địa chỉ email",
    "password": "Mật khẩu",
    "submit": "Đăng nhập",
    "forgot": "Quên mật khẩu?",
    "no_account": "Chưa có tài khoản? <1>Đăng ký</1>"
  },
  "errors": {
    "invalid_credentials": "Email hoặc mật khẩu không đúng",
    "account_locked": "Tài khoản bị khoá. Thử lại sau {{minutes}} phút."
  }
}
```

### Usage in Components

```tsx
import { useTranslation, Trans } from 'react-i18next'

function LoginPage() {
  const { t } = useTranslation('auth')

  return (
    <div>
      <h1>{t('login.title')}</h1>

      <form>
        <label>{t('login.email')}</label>
        <input type="email" placeholder={t('login.email')} />

        <label>{t('login.password')}</label>
        <input type="password" />

        <button type="submit">{t('login.submit')}</button>
      </form>

      {/* Interpolation */}
      {error && <p>{t('errors.account_locked', { minutes: 15 })}</p>}

      {/* Rich text with components */}
      <p>
        <Trans i18nKey="login.no_account" t={t}>
          Don't have an account? <Link to="/register">Sign up</Link>
        </Trans>
      </p>
    </div>
  )
}

// Pluralization
// en: { "items": "{{count}} item", "items_other": "{{count}} items" }
// vi: { "items": "{{count}} mục" }  (Vietnamese has no plural form)
<p>{t('items', { count: cart.length })}</p>

// Language switcher
function LanguageSwitcher() {
  const { i18n } = useTranslation()

  return (
    <select
      value={i18n.language}
      onChange={(e) => i18n.changeLanguage(e.target.value)}
    >
      <option value="en">English</option>
      <option value="vi">Tiếng Việt</option>
      <option value="ja">日本語</option>
    </select>
  )
}
```

---

## Vue 3 + vue-i18n

```typescript
// i18n/index.ts
import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import vi from './locales/vi.json'

export const i18n = createI18n({
  locale: localStorage.getItem('lang') || 'en',
  fallbackLocale: 'en',
  messages: { en, vi },
})

// Usage in template
// <template>
//   <h1>{{ $t('login.title') }}</h1>
//   <p>{{ $t('pagination.showing', { from: 1, to: 10, total: 100 }) }}</p>
// </template>

// Usage in Composition API
// const { t, locale } = useI18n()
// locale.value = 'vi' // switch language
```

---

## Date, Number, Currency Formatting

```typescript
// ✅ Use Intl API (built into browsers, Node.js)
// NEVER format dates/numbers manually

// Date formatting
function formatDate(date: Date, locale: string): string {
  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date)
}
// formatDate(new Date(), 'en-US') → "March 30, 2026"
// formatDate(new Date(), 'vi-VN') → "30 tháng 3, 2026"
// formatDate(new Date(), 'ja-JP') → "2026年3月30日"

// Relative time
function formatRelativeTime(date: Date, locale: string): string {
  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' })
  const diffMs = date.getTime() - Date.now()
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24))

  if (Math.abs(diffDays) < 1) {
    const diffHours = Math.round(diffMs / (1000 * 60 * 60))
    return rtf.format(diffHours, 'hour')
  }
  return rtf.format(diffDays, 'day')
}
// "2 hours ago", "yesterday", "in 3 days"
// "2 giờ trước", "hôm qua", "trong 3 ngày"

// Number formatting
function formatNumber(num: number, locale: string): string {
  return new Intl.NumberFormat(locale).format(num)
}
// formatNumber(1234567, 'en-US') → "1,234,567"
// formatNumber(1234567, 'de-DE') → "1.234.567"
// formatNumber(1234567, 'vi-VN') → "1.234.567"

// Currency
function formatCurrency(amount: number, currency: string, locale: string): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
  }).format(amount)
}
// formatCurrency(42.5, 'USD', 'en-US') → "$42.50"
// formatCurrency(42.5, 'VND', 'vi-VN') → "42 ₫"
// formatCurrency(42.5, 'JPY', 'ja-JP') → "￥43" (no decimals for JPY)
```

---

## RTL (Right-to-Left) Support

```yaml
rtl_languages: [ar, he, fa, ur]

approach:
  1_html_dir: '<html dir="rtl" lang="ar">'
  2_css_logical: "Use logical properties instead of physical"
  3_component_flip: "Mirror layout for RTL"
```

```css
/* ✅ CSS Logical Properties — works for both LTR and RTL */
.card {
  margin-inline-start: 1rem;   /* LTR: margin-left, RTL: margin-right */
  margin-inline-end: 2rem;
  padding-inline: 1rem;        /* both sides */
  border-inline-start: 3px solid blue;
  text-align: start;           /* LTR: left, RTL: right */
}

/* ✅ Tailwind v3+ RTL utilities */
/* <div class="ms-4 me-2 ps-4 pe-2"> */
/* ms = margin-inline-start, me = margin-inline-end */

/* ❌ Avoid physical properties for layout */
.card {
  margin-left: 1rem;  /* breaks in RTL */
  text-align: left;   /* breaks in RTL */
}
```

```typescript
// Direction-aware component
function Sidebar() {
  const { i18n } = useTranslation()
  const isRTL = ['ar', 'he', 'fa'].includes(i18n.language)

  useEffect(() => {
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr'
    document.documentElement.lang = i18n.language
  }, [i18n.language, isRTL])

  return <aside className="fixed inset-inline-start-0 w-64">{/* ... */}</aside>
}
```

---

## Backend Translations

```yaml
what_to_translate_on_backend:
  - "Error messages returned in API responses"
  - "Email/notification templates"
  - "PDF/export content"
  - "Push notification messages"

what_NOT_to_translate:
  - "Log messages (always English for debugging)"
  - "Internal error codes"
  - "Database values (unless explicitly multilingual)"
```

```typescript
// API error messages — accept-language header
@Catch()
export class I18nExceptionFilter implements ExceptionFilter {
  catch(exception: HttpException, host: ArgumentsHost) {
    const ctx = host.switchToHttp()
    const req = ctx.getRequest()
    const locale = req.headers['accept-language']?.split(',')[0] || 'en'

    const errorKey = exception.getResponse()['errorKey']
    const message = this.i18n.translate(errorKey, { lang: locale })

    ctx.getResponse().status(exception.getStatus()).json({
      statusCode: exception.getStatus(),
      message,
      errorKey,
    })
  }
}

// Email templates — per-locale
// templates/
//   en/welcome.hbs
//   vi/welcome.hbs
async function sendWelcomeEmail(user: User) {
  const locale = user.preferredLanguage || 'en'
  const template = await loadTemplate(`${locale}/welcome.hbs`)
  await mailer.send({
    to: user.email,
    subject: t('email.welcome.subject', { lng: locale }),
    html: template({ name: user.name }),
  })
}
```

---

## Translation Workflow

```yaml
dev_workflow:
  1: "Dev adds new key in English (source language)"
  2: "Commit → CI extracts new keys (i18next-parser)"
  3: "New keys pushed to translation platform (Crowdin, Lokalise, Phrase)"
  4: "Translators translate"
  5: "Translated files auto-committed back via PR"
  6: "Review + merge"

tools:
  extraction: "i18next-parser, babel-plugin-i18next-extract"
  platforms: "Crowdin, Lokalise, Phrase, Transifex"
  ci: "GitHub Action to sync keys"

key_naming:
  pattern: "{page}.{section}.{element}"
  examples:
    - "auth.login.title"
    - "dashboard.stats.total_users"
    - "errors.not_found"
    - "common.actions.save"
  rules:
    - "Lowercase, dot-separated"
    - "English value as fallback (not the key)"
    - "Group by feature/page, not by UI element type"
```

---

## Anti-patterns

```yaml
hardcoded_strings:
  bad: '<button>Save</button>'
  fix: '<button>{t("actions.save")}</button>'

concatenation:
  bad: 't("hello") + " " + name + "!"'
  fix: 't("hello", { name })  // "Hello, {{name}}!"'

date_manual_format:
  bad: '`${date.getMonth()+1}/${date.getDate()}/${date.getFullYear()}`'
  fix: 'new Intl.DateTimeFormat(locale).format(date)'

images_with_text:
  bad: "Banner image with English text baked in"
  fix: "Use CSS overlay text or locale-specific images"

no_pluralization:
  bad: '`${count} item(s)`'
  fix: 't("items", { count })  // handles plural rules per language'

english_only_errors:
  bad: "API returns 'Invalid email format' in English always"
  fix: "API returns error key, frontend translates"
```
