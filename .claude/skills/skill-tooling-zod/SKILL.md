---
name: skill-tooling-zod
description: Best practices Zod — schema validation TypeScript-first, z.infer, parse vs safeParse, transforms, refinements, integration với react-hook-form/tRPC/Hono.
---

# Skill: Zod

## Khi nào dùng

- Validate input ở runtime với full TypeScript inference
- Schema cho API request/response, form data, env vars, config
- Integration với tRPC, React Hook Form, Hono, NestJS

---

## Primitives

```typescript
import { z } from "zod";

// Primitives
const nameSchema = z.string().min(1).max(100).trim();
const ageSchema = z.number().int().min(0).max(150);
const activeSchema = z.boolean();
const idSchema = z.string().uuid();
const emailSchema = z.string().email().toLowerCase();
const urlSchema = z.string().url();
const dateSchema = z.coerce.date();

// Optional & nullable
const optionalName = z.string().optional(); // string | undefined
const nullableName = z.string().nullable(); // string | null
const nullishName = z.string().nullish(); // string | null | undefined
```

---

## Objects

```typescript
const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(1).max(100),
  role: z.enum(["user", "admin", "moderator"]).default("user"),
  age: z.number().int().min(18).optional(),
  createdAt: z.coerce.date(),
});

// ✅ Infer TypeScript type từ schema
type User = z.infer<typeof UserSchema>;

// Partial & strict
const UpdateUserSchema = UserSchema.partial().omit({
  id: true,
  createdAt: true,
});
const StrictSchema = UserSchema.strict(); // reject unknown keys

// Extend
const AdminSchema = UserSchema.extend({
  permissions: z.array(z.string()),
});
```

---

## Arrays & Sets

```typescript
const TagsSchema = z.array(z.string().min(1)).min(1).max(10);
const UniqueTagsSchema = z.set(z.string());

// Tuple
const PointSchema = z.tuple([z.number(), z.number()]);
```

---

## Discriminated unions & union

```typescript
// ✅ Discriminated union — type-narrowing tốt hơn
const ResponseSchema = z.discriminatedUnion("type", [
  z.object({ type: z.literal("success"), data: z.any() }),
  z.object({ type: z.literal("error"), message: z.string() }),
]);

// Regular union
const IdSchema = z.union([z.string(), z.number()]);
```

---

## Parse vs safeParse

```typescript
// .parse() — throws ZodError nếu invalid
try {
  const user = UserSchema.parse(rawData);
} catch (e) {
  if (e instanceof z.ZodError) {
    console.log(e.errors); // ZodIssue[]
  }
}

// ✅ .safeParse() — không throw, prefer này
const result = UserSchema.safeParse(rawData);
if (!result.success) {
  // result.error.errors — mảng issues có path + message
  const formatted = result.error.format();
  // { email: { _errors: ["Invalid email"] }, name: { _errors: [] } }
} else {
  const user = result.data; // typed User
}

// Async parse (nếu có .refine async)
const result = await UserSchema.safeParseAsync(rawData);
```

---

## Transforms & preprocess

```typescript
// Transform — chuyển đổi sau khi validate
const TrimmedStringSchema = z.string().transform((s) => s.trim());
const NumberFromStringSchema = z.string().pipe(z.coerce.number());

// preprocess — chuyển đổi TRƯỚC khi validate
const BooleanLikeSchema = z.preprocess(
  (val) => (val === "true" ? true : val === "false" ? false : val),
  z.boolean(),
);

// Từ form data (strings) sang number
const PaginationSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
});
```

---

## Refinements

```typescript
// .refine() — custom validation logic
const PasswordSchema = z
  .string()
  .min(8, "At least 8 characters")
  .refine((val) => /[A-Z]/.test(val), "Must contain uppercase")
  .refine((val) => /[0-9]/.test(val), "Must contain a number");

// Cross-field validation với superRefine
const SignupSchema = z
  .object({
    password: z.string().min(8),
    confirmPassword: z.string(),
  })
  .superRefine(({ password, confirmPassword }, ctx) => {
    if (password !== confirmPassword) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["confirmPassword"],
        message: "Passwords don't match",
      });
    }
  });
```

---

## Env vars validation

```typescript
// lib/env.ts
import { z } from "zod";

const envSchema = z.object({
  NODE_ENV: z
    .enum(["development", "test", "production"])
    .default("development"),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  REDIS_URL: z.string().url().optional(),
});

// Validate at startup — throw if invalid
export const env = envSchema.parse(process.env);

// Access with full types
env.PORT; // number
env.DATABASE_URL; // string
```

---

## React Hook Form integration

```typescript
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"

const LoginSchema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string().min(6, "Min 6 characters"),
})
type LoginForm = z.infer<typeof LoginSchema>

function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(LoginSchema),
  })

  return (
    <form onSubmit={handleSubmit((data) => login(data))}>
      <input {...register("email")} />
      {errors.email && <p>{errors.email.message}</p>}
    </form>
  )
}
```

---

## tRPC / Hono integration

```typescript
// tRPC
import { z } from "zod";

router.query("getUser", {
  input: z.object({ id: z.string().uuid() }),
  resolve: ({ input }) => db.user.findUnique({ where: { id: input.id } }),
});

// Hono
import { zValidator } from "@hono/zod-validator";

app.post("/users", zValidator("json", CreateUserSchema), async (c) => {
  const body = c.req.valid("json"); // fully typed
  const user = await createUser(body);
  return c.json(user, 201);
});
```

---

## Error formatting

```typescript
// Format errors cho API response
function formatZodError(error: z.ZodError) {
  return error.errors.reduce(
    (acc, err) => {
      const path = err.path.join(".");
      acc[path] = err.message;
      return acc;
    },
    {} as Record<string, string>,
  );
}

// { "email": "Invalid email", "password": "Min 8 characters" }
```

---

## Checklist

- ✅ Dùng `z.infer<typeof Schema>` thay vì định nghĩa type riêng
- ✅ `.safeParse()` ở API boundaries — không để ZodError leak
- ✅ `z.coerce.*` để xử lý form data (string to number/date)
- ✅ Validate env vars lúc startup với `envSchema.parse(process.env)`
- ✅ `.superRefine()` cho cross-field validations
- ✅ Reuse schemas — extend, merge, omit, pick thay vì viết mới
