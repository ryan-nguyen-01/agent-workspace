---
name: skill-arch-email-delivery
description: Email deliverability — DKIM/SPF/DMARC authentication, bounce handling, reputation management, warm-up strategy, transactional vs marketing, template design, và provider selection.
---

# Skill: Email Delivery

## Email Authentication (DNS Records)

```yaml
SPF (Sender Policy Framework):
  purpose: "Declare which servers are allowed to send email for your domain"
  dns_record: |
    TXT  myapp.com  "v=spf1 include:sendgrid.net include:amazonses.com ~all"
  rules:
    - "+all" → NEVER (allows anyone)
    - "~all" → soft fail (recommended during setup)
    - "-all" → hard fail (strict, recommended for production)

DKIM (DomainKeys Identified Mail):
  purpose: "Cryptographic signature proving email wasn't tampered"
  dns_record: |
    TXT  sg1._domainkey.myapp.com  "v=DKIM1; k=rsa; p=MIGfMA0GCSqG..."
  setup: "Provider generates key pair, you add public key to DNS"

DMARC (Domain-based Message Authentication):
  purpose: "Tell receivers what to do when SPF/DKIM fail"
  dns_record: |
    TXT  _dmarc.myapp.com  "v=DMARC1; p=quarantine; rua=mailto:dmarc@myapp.com; pct=100"
  policies:
    none: "Monitor only (start here)"
    quarantine: "Send to spam"
    reject: "Block entirely (goal)"
  rollout:
    week_1: "p=none (monitor)"
    week_4: "p=quarantine; pct=10 (quarantine 10%)"
    week_8: "p=quarantine; pct=100"
    week_12: "p=reject (full protection)"
```

---

## Bounce Handling

```yaml
bounce_types:
  hard_bounce:
    cause: "Invalid email, domain doesn't exist, mailbox full permanently"
    action: "Remove from list IMMEDIATELY. Never send again."
    threshold: "Hard bounce rate > 2% → sending reputation damaged"

  soft_bounce:
    cause: "Mailbox full temporarily, server down, message too large"
    action: "Retry 3 times over 72 hours. If still failing → treat as hard bounce."

  complaint:
    cause: "User clicked 'Report Spam'"
    action: "Unsubscribe IMMEDIATELY. Flag in DB."
    threshold: "Complaint rate > 0.1% → serious reputation risk"

implementation: |
  // Webhook handler for SendGrid events
  app.post('/webhooks/sendgrid', async (req, res) => {
    for (const event of req.body) {
      switch (event.event) {
        case 'bounce':
          await markEmailInvalid(event.email, event.reason)
          break
        case 'spamreport':
          await unsubscribeUser(event.email, 'spam_complaint')
          break
        case 'dropped':
          // Previously bounced/complained — SendGrid auto-suppressed
          break
        case 'delivered':
          await updateEmailStatus(event.email, 'delivered')
          break
        case 'open':
          await trackEmailOpen(event.sg_message_id)
          break
      }
    }
    res.sendStatus(200)
  })
```

---

## Sending Reputation

```yaml
reputation_factors:
  bounce_rate: "< 2% hard bounces"
  complaint_rate: "< 0.1% spam complaints"
  engagement: "Opens, clicks (positive signal)"
  list_hygiene: "Remove inactive, verify emails"
  volume_consistency: "Gradual increase, no sudden spikes"
  authentication: "SPF + DKIM + DMARC all passing"

warm_up_strategy:
  purpose: "New domain/IP has no reputation — must build gradually"
  schedule:
    day_1: "50 emails (to most engaged users)"
    day_3: "100 emails"
    day_7: "500 emails"
    day_14: "2,000 emails"
    day_21: "5,000 emails"
    day_30: "10,000+ emails"
  rules:
    - "Start with users who OPEN emails (most engaged)"
    - "Monitor bounce/complaint after each batch"
    - "If bounce > 5% → STOP, investigate list quality"
    - "Use dedicated IP (not shared) for > 50K emails/month"
```

---

## Transactional vs Marketing

```yaml
transactional:
  purpose: "Triggered by user action — receipt, password reset, OTP"
  rules:
    - "MUST send (user expects it)"
    - "No unsubscribe link needed (legally)"
    - "Send immediately (low latency)"
    - "Separate IP/subdomain from marketing"
  subdomain: "notify.myapp.com (separate from marketing.myapp.com)"

marketing:
  purpose: "Promotional — newsletter, offers, campaigns"
  rules:
    - "MUST have unsubscribe link (CAN-SPAM, GDPR)"
    - "Honor unsubscribe within 10 days (law) — ideally instant"
    - "Separate IP/subdomain from transactional"
    - "Consent required before sending (GDPR: explicit opt-in)"
  subdomain: "mail.myapp.com"

why_separate:
  - "Marketing emails get more complaints → damages reputation"
  - "Separate domain: marketing complaints don't affect transactional"
  - "Transactional emails (password reset) MUST reach inbox"
```

---

## Template Best Practices

```yaml
design:
  - "Max width 600px (email clients)"
  - "Inline CSS (many clients strip <style>)"
  - "Table-based layout (Outlook doesn't support flexbox/grid)"
  - "Include plain text version (multipart/alternative)"
  - "Images: host on CDN, include alt text, don't rely on images for key info"

tools:
  - "MJML → responsive email framework → compiles to HTML"
  - "React Email → React components → email HTML"
  - "Handlebars/Mustache → template engine with variables"

testing:
  - "Litmus / Email on Acid → preview in 90+ email clients"
  - "Send test to Gmail, Outlook, Apple Mail before production"
  - "Check spam score: mail-tester.com"

accessibility:
  - "Semantic HTML where possible"
  - "Color contrast ≥ 4.5:1"
  - "role='presentation' on layout tables"
  - "lang attribute on <html>"
```

---

## Provider Selection

```
┌──────────────┬────────────┬──────────┬─────────┬───────────────┐
│ Provider     │ Cost/email │ Free tier│ Best for│ Key feature   │
├──────────────┼────────────┼──────────┼─────────┼───────────────┤
│ SendGrid     │ ~$0.001    │ 100/day  │ Scale   │ Event webhooks│
│ AWS SES      │ ~$0.0001   │ 62K/mo*  │ Cost    │ Cheapest      │
│ Postmark     │ ~$0.001    │ 100/mo   │ Txn     │ Best delivery │
│ Resend       │ ~$0.001    │ 3K/mo    │ DX      │ React Email   │
│ Mailgun      │ ~$0.001    │ 100/day  │ API     │ Email parsing │
└──────────────┴────────────┴──────────┴─────────┴───────────────┘
* AWS SES free tier: from EC2 instances only
```

---

## Anti-patterns

```yaml
no_authentication:
  bad: "Send email without SPF/DKIM/DMARC → goes to spam"
  fix: "Setup all 3 DNS records before sending first email"

no_bounce_handling:
  bad: "Keep sending to invalid emails → reputation destroyed"
  fix: "Process bounce webhooks, remove hard bounces immediately"

same_domain_for_all:
  bad: "Marketing + transactional from same domain/IP"
  fix: "Separate subdomains: notify.myapp.com vs mail.myapp.com"

no_unsubscribe:
  bad: "Marketing email without unsubscribe link → legal violation"
  fix: "One-click unsubscribe header + visible unsubscribe link"

sudden_volume:
  bad: "New domain sends 50K emails day 1 → blocked by ISPs"
  fix: "Warm up gradually over 4-6 weeks"
```
