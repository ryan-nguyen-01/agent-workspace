---
name: skill-arch-storage
description: Storage system design — object storage architecture, CDN integration, media processing pipelines, file upload strategies, backup & disaster recovery.
---

# Skill: Storage Architecture

## Storage Tiers

```
┌─────────────────────────────────────────────────────┐
│  HOT (frequent access, low latency)                 │
│  SSD, in-memory cache, CDN edge                     │
│  Use: active user avatars, recent uploads, static   │
├─────────────────────────────────────────────────────┤
│  WARM (moderate access)                             │
│  Standard S3, block storage                         │
│  Use: older files, documents, reports               │
├─────────────────────────────────────────────────────┤
│  COLD (rare access, high latency ok)                │
│  S3 Glacier, Archive storage                        │
│  Use: backups, compliance archives, old logs        │
└─────────────────────────────────────────────────────┘

lifecycle_policy:
  - "After 30 days: HOT → WARM (move to cheaper storage class)"
  - "After 90 days: WARM → COLD (archive)"
  - "After 7 years: COLD → DELETE (compliance retention met)"
```

---

## Object Storage Architecture

### S3-Compatible Storage

```yaml
path_convention: "{env}/{entity_type}/{entity_id}/{uuid}.{ext}"
examples:
  - "prod/avatars/user-123/a1b2c3d4.jpg"
  - "prod/documents/order-456/invoice.pdf"
  - "prod/media/post-789/video.mp4"

bucket_strategy:
  single_bucket:
    when: Small project, simple setup
    structure: "myapp-{env}/{entity_type}/..."

  multi_bucket:
    when: Different access patterns, security requirements
    buckets:
      myapp-public: "Avatars, product images (CDN-backed)"
      myapp-private: "Documents, invoices (authenticated access)"
      myapp-temp: "Upload staging, processing (auto-delete 24h)"
      myapp-backup: "Database dumps, logs (lifecycle → Glacier)"

access_control:
  public_read:
    what: "Product images, avatars, static assets"
    method: "Bucket policy: public read, CDN in front"
  private:
    what: "Documents, invoices, user uploads"
    method: "Presigned URLs (time-limited), IAM roles"
  internal:
    what: "Backups, logs, processing temp files"
    method: "IAM only, no public access ever"
```

### Upload Strategies

```yaml
direct_upload (presigned URL):
  flow: |
    1. Client → POST /api/upload/presign { fileName, contentType }
    2. Server validates → generates presigned PUT URL (5min TTL)
    3. Server returns { uploadUrl, fileKey }
    4. Client → PUT file directly to S3 via uploadUrl
    5. Client → POST /api/upload/confirm { fileKey }
    6. Server verifies file exists → save reference in DB
  pros: "No server bandwidth bottleneck, handles large files"
  implementation: |
    // Generate presigned URL
    const command = new PutObjectCommand({
      Bucket: 'myapp-uploads',
      Key: `temp/${uuid()}.${ext}`,
      ContentType: contentType,
    })
    const uploadUrl = await getSignedUrl(s3Client, command, { expiresIn: 300 })

server_proxy:
  flow: |
    1. Client → POST /api/upload (multipart/form-data)
    2. Server receives file → validates → uploads to S3
    3. Server returns { fileUrl, fileKey }
  pros: "Simple, server controls everything"
  cons: "Server bandwidth bottleneck, memory usage"
  when: "Small files (< 10MB), simple apps"

multipart_upload (large files):
  flow: |
    1. Client → POST /api/upload/init { fileName, fileSize }
    2. Server → S3 CreateMultipartUpload → returns uploadId
    3. Server → generate presigned URLs for each part (5MB chunks)
    4. Client uploads parts in parallel
    5. Client → POST /api/upload/complete { uploadId, parts }
    6. Server → S3 CompleteMultipartUpload
  when: "Files > 100MB (video, datasets)"
  benefit: "Resumable, parallel upload, progress tracking"

resumable_upload:
  protocol: "tus.io protocol"
  when: "Unreliable networks, mobile, very large files"
  benefit: "Resume from where it stopped on network failure"
```

### File Validation

```typescript
const ALLOWED_TYPES: Record<string, { mimes: string[]; maxSize: number }> = {
  image: {
    mimes: ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
    maxSize: 10 * 1024 * 1024, // 10MB
  },
  document: {
    mimes: ['application/pdf', 'application/msword', 'text/plain'],
    maxSize: 50 * 1024 * 1024, // 50MB
  },
  video: {
    mimes: ['video/mp4', 'video/webm'],
    maxSize: 500 * 1024 * 1024, // 500MB
  },
}

async function validateFile(file: UploadedFile, category: string): Promise<void> {
  const config = ALLOWED_TYPES[category]
  if (!config) throw new BadRequestError('Invalid file category')

  // Check MIME type (from file header, NOT extension)
  const fileType = await fileTypeFromBuffer(file.buffer)
  if (!fileType || !config.mimes.includes(fileType.mime)) {
    throw new BadRequestError(`File type ${fileType?.mime} not allowed`)
  }

  // Check size
  if (file.size > config.maxSize) {
    throw new BadRequestError(`File too large: ${file.size} > ${config.maxSize}`)
  }

  // Sanitize filename
  const safeName = file.originalname
    .replace(/[^a-zA-Z0-9._-]/g, '_')
    .substring(0, 255)
}
```

---

## Media Processing Pipeline

```yaml
architecture: |
  Upload → S3 (original) → Event trigger → Processing Queue
    → Worker:
      ├── Image: resize, compress, format convert
      ├── Video: transcode, thumbnail, HLS segments
      └── Document: extract text, generate preview

image_processing:
  tools: [Sharp (Node.js), Pillow (Python), ImageMagick]
  outputs:
    thumbnail: "150x150, crop center, WebP, quality 80"
    medium: "600x600, fit contain, WebP, quality 85"
    large: "1200x1200, fit contain, WebP, quality 90"
    original: "Keep original (backup)"
  implementation: |
    import sharp from 'sharp'

    async function processImage(inputBuffer: Buffer, key: string) {
      const variants = [
        { suffix: 'thumb', width: 150, height: 150, fit: 'cover' },
        { suffix: 'md', width: 600, height: 600, fit: 'inside' },
        { suffix: 'lg', width: 1200, height: 1200, fit: 'inside' },
      ]

      for (const v of variants) {
        const processed = await sharp(inputBuffer)
          .resize(v.width, v.height, { fit: v.fit as any })
          .webp({ quality: 85 })
          .toBuffer()

        await s3.putObject({
          Bucket: 'myapp-public',
          Key: key.replace('.', `_${v.suffix}.webp`),
          Body: processed,
          ContentType: 'image/webp',
          CacheControl: 'public, max-age=31536000, immutable',
        })
      }
    }

video_processing:
  tools: [FFmpeg, AWS MediaConvert, Mux]
  outputs:
    thumbnail: "Extract frame at 1s, JPEG"
    preview: "First 10s, compressed GIF/WebP"
    adaptive: "HLS segments (240p, 480p, 720p, 1080p)"
  when: "User-generated video, streaming platform"
```

---

## CDN Integration

```yaml
architecture: |
  Client → CDN Edge (closest PoP)
    → Cache HIT → return immediately
    → Cache MISS → Origin (S3 / App Server)
      → Store at edge → return to client

configuration:
  cloudfront:
    origins:
      - S3 bucket (static assets, user uploads)
      - API server (cacheable API responses)
    behaviors:
      "/static/*": "Cache 1 year, immutable"
      "/images/*": "Cache 30 days, stale-while-revalidate"
      "/api/products": "Cache 60s, vary by query params"
      "/api/user/*": "No cache (personalized)"

  cache_key:
    include: [path, query_string (selected params)]
    exclude: [cookies, authorization header]

  invalidation:
    on_deploy: "Invalidate /static/*"
    on_upload: "Invalidate specific file path"
    versioned_urls: "/assets/app.a1b2c3.js → no invalidation needed"

image_cdn:
  tools: [Cloudinary, imgix, Cloudflare Images]
  benefit: "On-the-fly resize, format conversion, optimization"
  example: |
    Original: https://cdn.myapp.com/images/photo.jpg
    Resized:  https://cdn.myapp.com/images/photo.jpg?w=300&h=300&fit=crop&format=webp
    // CDN caches each variant separately
```

---

## Backup & Disaster Recovery

```yaml
backup_strategy:
  database:
    full_backup: "Daily at 3am UTC"
    incremental: "Every 6 hours (WAL archiving for PostgreSQL)"
    retention: "30 days hot, 1 year cold (Glacier)"
    test_restore: "Monthly — verify backup actually works"

  file_storage:
    versioning: "S3 versioning enabled (recover overwritten/deleted files)"
    cross_region: "Replicate to another region (disaster recovery)"
    retention: "Same as DB: 30 days hot, 1 year cold"

  config:
    infrastructure_as_code: "Terraform/Pulumi state in versioned S3"
    secrets: "Vault snapshots, exported encrypted"

rpo_rto:
  rpo: "Recovery Point Objective — max data loss acceptable"
  rto: "Recovery Time Objective — max downtime acceptable"

  tiers:
    critical:
      rpo: "< 1 hour"
      rto: "< 15 minutes"
      strategy: "Multi-AZ, streaming replication, auto-failover"
      example: "Production database, payment data"
    important:
      rpo: "< 24 hours"
      rto: "< 4 hours"
      strategy: "Daily backups, manual failover"
      example: "User uploads, documents"
    standard:
      rpo: "< 7 days"
      rto: "< 24 hours"
      strategy: "Weekly backups"
      example: "Logs, analytics data"

disaster_recovery:
  pilot_light: "Minimal infra in DR region, scale up when needed"
  warm_standby: "Scaled-down copy in DR region, quick scale up"
  multi_region: "Active-active in multiple regions (expensive, complex)"
```

---

## Anti-patterns

```yaml
storing_files_in_db:
  bad: "Store images as BLOB in PostgreSQL"
  fix: "Object storage (S3) + store URL/key in DB"

no_file_validation:
  bad: "Accept any uploaded file without checking"
  fix: "Validate MIME type from header, check size, sanitize name"

serving_from_app_server:
  bad: "Express serves static files directly"
  fix: "CDN for static assets, presigned URLs for private files"

no_cleanup:
  bad: "Orphaned files accumulate (upload but never confirmed)"
  fix: "Temp bucket with 24h lifecycle, cleanup cron job"

single_region_storage:
  bad: "All data in 1 region, no backup"
  fix: "Cross-region replication, regular backup verification"
```
