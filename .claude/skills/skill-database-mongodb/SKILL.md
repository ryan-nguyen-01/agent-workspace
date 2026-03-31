---
name: skill-database-mongodb
description: Best practices dùng MongoDB: schema design, indexes, aggregation pipeline, transactions và Mongoose ODM patterns.
---

# Skill: MongoDB

## Schema Design với Mongoose

```typescript
import { Schema, model, Document, Types } from 'mongoose'

// ✅ Interface cho type safety
interface IUser extends Document {
  _id: Types.ObjectId
  email: string
  name: string
  password: string
  isActive: boolean
  createdAt: Date
  updatedAt: Date
}

const userSchema = new Schema<IUser>(
  {
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
      match: [/^\S+@\S+\.\S+$/, 'Invalid email format'],
    },
    name: {
      type: String,
      required: true,
      minlength: 2,
      maxlength: 100,
      trim: true,
    },
    password: {
      type: String,
      required: true,
      select: false,  // ✅ Không trả về password mặc định
    },
    isActive: { type: Boolean, default: true },
  },
  {
    timestamps: true,  // ✅ Tự thêm createdAt, updatedAt
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
  }
)

// ✅ Indexes
userSchema.index({ email: 1 }, { unique: true })
userSchema.index({ createdAt: -1 })
userSchema.index({ name: 'text' })  // Full-text search

// ✅ Pre-save hook
userSchema.pre('save', async function(next) {
  if (this.isModified('password')) {
    this.password = await bcrypt.hash(this.password, 12)
  }
  next()
})

// ✅ Instance method
userSchema.methods.comparePassword = async function(candidate: string): Promise<boolean> {
  return bcrypt.compare(candidate, this.password)
}

// ✅ Static method
userSchema.statics.findByEmail = function(email: string) {
  return this.findOne({ email: email.toLowerCase() })
}

export const User = model<IUser>('User', userSchema)
```

## Query Patterns

```typescript
// ✅ Projection — chỉ lấy fields cần thiết
const user = await User.findById(id).select('email name createdAt').lean()

// ✅ lean() cho read-only queries (nhanh hơn 3-5x)
const users = await User.find({ isActive: true })
  .select('email name')
  .sort({ createdAt: -1 })
  .skip((page - 1) * limit)
  .limit(limit)
  .lean()

// ✅ Populate với projection
const post = await Post.findById(id)
  .populate('author', 'name email')  // Chỉ lấy name, email của author
  .lean()

// ✅ findOneAndUpdate với returnDocument
const updated = await User.findByIdAndUpdate(
  id,
  { $set: { name }, $currentDate: { updatedAt: true } },
  { new: true, runValidators: true }
).select('-password').lean()
```

## Aggregation Pipeline

```typescript
// ✅ Aggregation cho complex queries
const stats = await Post.aggregate([
  // Stage 1: Match
  { $match: { status: 'published', publishedAt: { $gte: startDate } } },

  // Stage 2: Lookup (JOIN)
  {
    $lookup: {
      from: 'users',
      localField: 'author',
      foreignField: '_id',
      as: 'authorData',
      pipeline: [{ $project: { name: 1, email: 1 } }],  // ✅ Filter trong lookup
    },
  },
  { $unwind: '$authorData' },

  // Stage 3: Group
  {
    $group: {
      _id: '$authorData._id',
      authorName: { $first: '$authorData.name' },
      postCount: { $sum: 1 },
      avgViews: { $avg: '$views' },
    },
  },

  // Stage 4: Sort + Limit
  { $sort: { postCount: -1 } },
  { $limit: 10 },
])
```

## Transactions

```typescript
// ✅ Session-based transactions
import mongoose from 'mongoose'

async function transferFunds(fromId: string, toId: string, amount: number) {
  const session = await mongoose.startSession()

  try {
    await session.withTransaction(async () => {
      const from = await Account.findById(fromId).session(session)
      if (!from || from.balance < amount) {
        throw new Error('Insufficient balance')
      }

      await Account.findByIdAndUpdate(fromId,
        { $inc: { balance: -amount } },
        { session }
      )
      await Account.findByIdAndUpdate(toId,
        { $inc: { balance: amount } },
        { session }
      )
    })
  } finally {
    await session.endSession()
  }
}
```

## Connection Setup

```typescript
import mongoose from 'mongoose'

export async function connectDB(): Promise<void> {
  mongoose.set('strictQuery', true)

  await mongoose.connect(process.env.MONGODB_URI!, {
    maxPoolSize: 10,
    serverSelectionTimeoutMS: 5000,
    socketTimeoutMS: 45000,
  })

  mongoose.connection.on('error', err => {
    console.error('MongoDB connection error:', err)
  })
}
```

## Anti-patterns

```typescript
// ❌ Không dùng lean() khi không cần Mongoose methods
const users = await User.find({})  // Heavy Mongoose documents
// ✅
const users = await User.find({}).lean()

// ❌ N+1 queries (populate trong loop)
for (const post of posts) {
  post.author = await User.findById(post.authorId)  // N+1!
}
// ✅ Dùng populate hoặc aggregation $lookup

// ❌ Lưu arrays lớn và vô hạn trong document
{ comments: [/* có thể grow vô hạn */] }
// ✅ Separate collection với reference

// ❌ Không có indexes trên query fields
User.find({ email: 'test@test.com' })  // Collection scan nếu không có index!

// ❌ Bỏ qua validation với { strict: false }
new User(data, { strict: false })  // Cho phép unknown fields
```
