---
name: skill-framework-express
description: Best practices xây dựng Express.js applications: routing, middleware, validation, error handling và project structure chuẩn.
---

# Skill: Express.js

## Project Structure

```
src/
├── app.ts              # Express app setup (no listen)
├── server.ts           # HTTP server, port binding
├── routes/
│   └── v1/
│       ├── index.ts    # Aggregate routers
│       ├── users.ts
│       └── auth.ts
├── controllers/        # Request handlers — thin
├── services/           # Business logic
├── repositories/       # Data access
├── models/             # DB models (Mongoose/Prisma)
├── middlewares/        # Custom middleware
├── validators/         # Request validation schemas
├── types/              # TypeScript interfaces/types
└── config/             # App configuration
```

## App Setup

```typescript
// app.ts
import express from 'express'
import helmet from 'helmet'
import cors from 'cors'
import { errorHandler } from './middlewares/error-handler'
import { requestLogger } from './middlewares/request-logger'
import v1Router from './routes/v1'

const app = express()

// Security
app.use(helmet())
app.use(cors({ origin: process.env.CORS_ORIGINS?.split(',') }))

// Body parsing
app.use(express.json({ limit: '10mb' }))
app.use(express.urlencoded({ extended: true }))

// Logging
app.use(requestLogger)

// Routes
app.use('/api/v1', v1Router)

// 404
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found', path: req.path })
})

// Error handler — MUST be last
app.use(errorHandler)

export default app
```

## Router — Thin

```typescript
// routes/v1/users.ts
import { Router } from 'express'
import { UserController } from '../../controllers/user.controller'
import { authenticate } from '../../middlewares/authenticate'
import { validate } from '../../middlewares/validate'
import { createUserSchema, getUserSchema } from '../../validators/user.validator'

const router = Router()
const controller = new UserController()

router.get('/:id', authenticate, validate(getUserSchema), controller.findById)
router.post('/', validate(createUserSchema), controller.create)
router.delete('/:id', authenticate, controller.delete)

export default router
```

## Controller

```typescript
// controllers/user.controller.ts
import { Request, Response, NextFunction } from 'express'
import { UserService } from '../services/user.service'

export class UserController {
  private service = new UserService()

  findById = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const user = await this.service.findById(req.params.id)
      res.json(user)
    } catch (err) {
      next(err)  // ✅ Always pass to error handler
    }
  }

  create = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const user = await this.service.create(req.body)
      res.status(201).json(user)
    } catch (err) {
      next(err)
    }
  }

  delete = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      await this.service.delete(req.params.id)
      res.status(204).send()
    } catch (err) {
      next(err)
    }
  }
}
```

## Validation với Zod

```typescript
// validators/user.validator.ts
import { z } from 'zod'

export const createUserSchema = z.object({
  body: z.object({
    email: z.string().email(),
    name: z.string().min(2).max(100),
    password: z.string().min(8),
  }),
})

export const getUserSchema = z.object({
  params: z.object({
    id: z.string().uuid(),
  }),
})

// middlewares/validate.ts
import { Request, Response, NextFunction } from 'express'
import { ZodSchema } from 'zod'

export const validate = (schema: ZodSchema) =>
  (req: Request, res: Response, next: NextFunction): void => {
    const result = schema.safeParse({
      body: req.body,
      params: req.params,
      query: req.query,
    })
    if (!result.success) {
      res.status(400).json({
        error: 'Validation failed',
        details: result.error.flatten(),
      })
      return
    }
    next()
  }
```

## Error Handler

```typescript
// middlewares/error-handler.ts
import { Request, Response, NextFunction } from 'express'

export class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number = 500,
    public code?: string,
  ) {
    super(message)
    this.name = 'AppError'
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} '${id}' not found`, 404, 'NOT_FOUND')
  }
}

// ✅ Must have 4 parameters for Express to recognize as error handler
export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  _next: NextFunction,
): void => {
  if (err instanceof AppError) {
    res.status(err.statusCode).json({ error: err.message, code: err.code })
    return
  }

  console.error('Unhandled error:', err)
  res.status(500).json({ error: 'Internal server error' })
}
```

## Async Middleware Helper

```typescript
// ✅ Wrap async handlers để catch errors
export const asyncHandler = (
  fn: (req: Request, res: Response, next: NextFunction) => Promise<void>
) => (req: Request, res: Response, next: NextFunction): void => {
  fn(req, res, next).catch(next)
}

// Usage
router.get('/:id', asyncHandler(async (req, res) => {
  const user = await userService.findById(req.params.id)
  res.json(user)
}))
```

## Anti-patterns

```typescript
// ❌ Blocking event loop
app.get('/data', (req, res) => {
  const data = fs.readFileSync('big-file.json')  // Blocks!
  res.json(JSON.parse(data))
})

// ✅ Async IO
app.get('/data', async (req, res, next) => {
  try {
    const data = await fs.promises.readFile('big-file.json')
    res.json(JSON.parse(data.toString()))
  } catch (err) { next(err) }
})

// ❌ Error handler với 3 params (không được nhận diện)
app.use((err, req, res) => { ... })  // Sai!

// ❌ Không gọi next(err) trong async controller
app.get('/user', async (req, res) => {
  const user = await service.find()  // nếu throw, Express không bắt được
  res.json(user)
})
```
