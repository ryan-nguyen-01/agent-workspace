# BLUEPRINT-003 — File Upload

**Goal**: Upload file an toàn + consistent (S3/R2/local), có validation, metadata, cleanup.

---

## When to use

- Avatar upload, documents, attachments, media

---

## Two patterns

### Pattern A — Direct upload (server proxy)

1) Client `POST /uploads` multipart  
2) Server validate → upload to storage → return URL/key

Pros: đơn giản  
Cons: tốn bandwidth server

### Pattern B — Presigned upload (recommended at scale)

1) Client `POST /uploads/presign` → server trả presigned URL + key  
2) Client `PUT` trực tiếp lên storage  
3) Client `POST /uploads/confirm` (key, metadata) → server persist reference

Pros: scale tốt  
Cons: nhiều bước hơn

---

## Validation checklist (minimum)

```yaml
validation:
  max_size_mb: 10
  allowed_mime:
    - image/jpeg
    - image/png
    - application/pdf
  filename:
    sanitize: true
    max_length: 120
  content_sniffing: recommended
  virus_scan: optional
```

---

## Storage conventions

Key pattern:

```
{tenantId}/{entityType}/{entityId}/{yyyy}/{mm}/{uuid}.{ext}
```

Store in DB:
- `storageProvider` (s3/r2/local)
- `key`
- `url` (optional derived)
- `mime`, `size`, `checksum`
- `createdBy`, `createdAt`

---

## API contract

- `POST /uploads` (direct)
- `POST /uploads/presign`
- `POST /uploads/confirm`
- `DELETE /uploads/{id}` (soft delete + retention)

---

## Processing (optional)

- Images: generate `thumb/medium/large`
- Documents: extract basic metadata
- Background jobs for processing/cleanup (queue)

---

## Security pitfalls

- Accepting arbitrary MIME/extensions
- Public buckets without auth controls
- Path traversal in filenames
- Serving uploads from same domain without correct headers (XSS)

