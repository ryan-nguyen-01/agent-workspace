---
name: skill-storage-s3
description: Best practices dùng AWS S3 / MinIO: upload/download, presigned URLs, multipart upload, access control và lifecycle policies.
---

# Skill: AWS S3 / MinIO

## Client Setup

```typescript
import { S3Client, GetObjectCommand, PutObjectCommand, DeleteObjectCommand } from '@aws-sdk/client-s3'
import { getSignedUrl } from '@aws-sdk/s3-request-presigner'

// ✅ Works với cả AWS S3 và MinIO (self-hosted)
const s3 = new S3Client({
  region: process.env.AWS_REGION || 'us-east-1',
  // MinIO config
  endpoint: process.env.S3_ENDPOINT,  // 'http://localhost:9000' for MinIO
  forcePathStyle: !!process.env.S3_ENDPOINT,  // Required for MinIO
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
})

const BUCKET = process.env.S3_BUCKET!
```

## Upload Patterns

```typescript
// ✅ Direct upload (small files < 5MB)
async function uploadFile(
  key: string,
  file: Buffer | Readable,
  options: { contentType: string; isPublic?: boolean }
): Promise<string> {
  await s3.send(new PutObjectCommand({
    Bucket: BUCKET,
    Key: key,
    Body: file,
    ContentType: options.contentType,
    // ✅ ACL chỉ dùng nếu bucket không block public access
    ACL: options.isPublic ? 'public-read' : 'private',
    // ✅ Server-side encryption
    ServerSideEncryption: 'AES256',
    // ✅ Cache control
    CacheControl: options.isPublic ? 'public, max-age=31536000, immutable' : 'private',
    // ✅ Metadata
    Metadata: {
      uploadedAt: new Date().toISOString(),
    },
  }))

  return key
}

// ✅ Generate a unique, collision-resistant key
function generateObjectKey(userId: string, filename: string): string {
  const ext = path.extname(filename).toLowerCase()
  const hash = crypto.randomBytes(8).toString('hex')
  const date = format(new Date(), 'yyyy/MM/dd')
  return `uploads/${userId}/${date}/${hash}${ext}`
  // e.g. uploads/user-123/2024/01/15/abc12345.jpg
}
```

## Presigned URLs (Preferred for Frontend Uploads)

```typescript
// ✅ Presigned PUT — frontend uploads directly to S3 (no backend bandwidth)
async function getUploadUrl(key: string, contentType: string): Promise<{
  uploadUrl: string
  objectKey: string
}> {
  const command = new PutObjectCommand({
    Bucket: BUCKET,
    Key: key,
    ContentType: contentType,
    ServerSideEncryption: 'AES256',
  })

  const uploadUrl = await getSignedUrl(s3, command, {
    expiresIn: 300,  // 5 minutes
  })

  return { uploadUrl, objectKey: key }
}

// ✅ Presigned GET — temporary access to private files
async function getDownloadUrl(key: string, expiresIn = 3600): Promise<string> {
  const command = new GetObjectCommand({
    Bucket: BUCKET,
    Key: key,
    ResponseContentDisposition: `attachment; filename="${path.basename(key)}"`,
  })

  return getSignedUrl(s3, command, { expiresIn })
}

// ✅ Frontend upload flow
// 1. Client requests upload URL from API
// 2. API returns presigned PUT URL + objectKey
// 3. Client PUT directly to S3 with file
// 4. Client notifies API with objectKey after upload
// 5. API verifies object exists, saves reference to DB
```

## Multipart Upload (Large Files > 5MB)

```typescript
import { CreateMultipartUploadCommand, UploadPartCommand, CompleteMultipartUploadCommand, AbortMultipartUploadCommand } from '@aws-sdk/client-s3'

async function multipartUpload(key: string, fileBuffer: Buffer, contentType: string): Promise<void> {
  const PART_SIZE = 10 * 1024 * 1024  // 10MB parts

  const { UploadId } = await s3.send(new CreateMultipartUploadCommand({
    Bucket: BUCKET,
    Key: key,
    ContentType: contentType,
    ServerSideEncryption: 'AES256',
  }))

  const parts: { ETag: string; PartNumber: number }[] = []

  try {
    const totalParts = Math.ceil(fileBuffer.length / PART_SIZE)

    for (let i = 0; i < totalParts; i++) {
      const start = i * PART_SIZE
      const end = Math.min(start + PART_SIZE, fileBuffer.length)
      const chunk = fileBuffer.slice(start, end)

      const { ETag } = await s3.send(new UploadPartCommand({
        Bucket: BUCKET,
        Key: key,
        UploadId,
        PartNumber: i + 1,
        Body: chunk,
      }))

      parts.push({ ETag: ETag!, PartNumber: i + 1 })
    }

    await s3.send(new CompleteMultipartUploadCommand({
      Bucket: BUCKET,
      Key: key,
      UploadId,
      MultipartUpload: { Parts: parts },
    }))
  } catch (err) {
    // ✅ Always abort on error to clean up incomplete uploads
    await s3.send(new AbortMultipartUploadCommand({ Bucket: BUCKET, Key: key, UploadId }))
    throw err
  }
}
```

## File Validation

```typescript
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
const MAX_IMAGE_SIZE = 10 * 1024 * 1024  // 10MB

function validateFile(file: Express.Multer.File, allowedTypes: string[], maxSize: number): void {
  // ✅ Validate by content type AND magic bytes (not just extension)
  if (!allowedTypes.includes(file.mimetype)) {
    throw new ValidationError(`File type not allowed: ${file.mimetype}`)
  }

  if (file.size > maxSize) {
    throw new ValidationError(`File too large: ${file.size} bytes (max: ${maxSize})`)
  }

  // ✅ Check magic bytes for images
  if (file.mimetype.startsWith('image/')) {
    const header = file.buffer.slice(0, 8)
    if (!isValidImageHeader(header)) {
      throw new ValidationError('Invalid file content')
    }
  }
}
```

## Anti-patterns

```typescript
// ❌ Store files locally in containerized apps (ephemeral filesystem)
fs.writeFileSync('/uploads/image.jpg', buffer)  // Lost when container restarts!

// ❌ Public bucket with private data
// ✅ Private bucket + presigned URLs for access

// ❌ Predictable object keys (enumeration attack)
`uploads/1.jpg`, `uploads/2.jpg`  // ❌ Users can guess others' files
// ✅ Random keys: `uploads/abc12345ef.jpg`

// ❌ Không validate file content (just extension)
if (!filename.endsWith('.jpg')) throw new Error()  // ❌ Rename trick!
// ✅ Validate MIME type + magic bytes

// ❌ Download file to server then re-upload
const response = await fetch(externalUrl)
const buffer = await response.buffer()
await s3.upload(buffer)  // ❌ Unnecessary bandwidth
// ✅ Copy/redirect directly

// ❌ Không có lifecycle policy → storage costs grow indefinitely
// ✅ Set lifecycle rules: delete temp uploads after 24h, archive old files
```
