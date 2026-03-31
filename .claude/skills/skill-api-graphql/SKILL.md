---
name: skill-api-graphql
description: Best practices thiết kế GraphQL APIs: schema design, resolvers, DataLoader, authentication, error handling và performance.
---

# Skill: GraphQL API Design

## Schema Design

```graphql
# ✅ Schema-first approach
type User {
  id: ID!
  email: String!
  name: String!
  posts(first: Int = 10, after: String): PostConnection!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String
  author: User!
  status: PostStatus!
  publishedAt: DateTime
}

enum PostStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}

# ✅ Connection pattern cho pagination
type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PostEdge {
  node: Post!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

# ✅ Mutations rõ ràng với input types
input CreateUserInput {
  email: String!
  name: String!
  password: String!
}

type CreateUserPayload {
  user: User
  errors: [UserError!]!
}

type UserError {
  field: String
  message: String!
  code: String!
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
  deleteUser(id: ID!): DeletePayload!
}
```

## Resolvers

```typescript
// resolvers/user.resolver.ts
const userResolvers = {
  Query: {
    user: async (_: unknown, { id }: { id: string }, ctx: Context) => {
      return ctx.loaders.user.load(id)  // ✅ DataLoader
    },
    users: async (_: unknown, { first, after }: PaginationArgs, ctx: Context) => {
      return ctx.services.user.findPaginated({ first, after })
    },
  },

  Mutation: {
    createUser: async (_: unknown, { input }: { input: CreateUserInput }, ctx: Context) => {
      try {
        const user = await ctx.services.user.create(input)
        return { user, errors: [] }
      } catch (err) {
        if (err instanceof ValidationError) {
          return {
            user: null,
            errors: err.fields.map(f => ({ field: f.name, message: f.message, code: 'VALIDATION_ERROR' })),
          }
        }
        throw err
      }
    },
  },

  User: {
    posts: async (user: User, { first, after }: PaginationArgs, ctx: Context) => {
      return ctx.services.post.findByUserId(user.id, { first, after })
    },
  },
}
```

## DataLoader — N+1 Prevention

```typescript
import DataLoader from 'dataloader'

// ✅ Batch load users
function createUserLoader(db: Database) {
  return new DataLoader<string, User | null>(async (ids) => {
    const users = await db.users.findMany({
      where: { id: { in: ids as string[] } },
    })

    const userMap = new Map(users.map(u => [u.id, u]))
    return ids.map(id => userMap.get(id) ?? null)  // Maintain order!
  })
}

// ✅ Context với loaders
interface Context {
  user: AuthUser | null
  services: Services
  loaders: {
    user: DataLoader<string, User | null>
    post: DataLoader<string, Post | null>
  }
}

// Create fresh loaders per request
function createContext(req: Request): Context {
  return {
    user: req.user ?? null,
    services: createServices(),
    loaders: {
      user: createUserLoader(db),
      post: createPostLoader(db),
    },
  }
}
```

## Authentication & Authorization

```typescript
// ✅ Auth trong context
const server = new ApolloServer({
  schema,
  context: async ({ req }): Promise<Context> => {
    const token = req.headers.authorization?.replace('Bearer ', '')
    const user = token ? await verifyToken(token) : null
    return createContext(req, user)
  },
})

// ✅ Field-level auth với directives
const typeDefs = gql`
  directive @authenticated on FIELD_DEFINITION | OBJECT
  directive @hasRole(roles: [String!]!) on FIELD_DEFINITION

  type Query {
    me: User @authenticated
    adminStats: Stats @hasRole(roles: ["admin"])
  }
`

// ✅ Resolver-level auth check
Query: {
  adminStats: async (_: unknown, __: unknown, ctx: Context) => {
    if (!ctx.user) throw new AuthenticationError('Must be logged in')
    if (!ctx.user.roles.includes('admin')) throw new ForbiddenError('Requires admin role')
    return ctx.services.stats.getAdminStats()
  },
},
```

## Error Handling

```typescript
import { GraphQLError } from 'graphql'
import { ApolloServerErrorCode } from '@apollo/server/errors'

// ✅ Typed GraphQL errors
function throwNotFound(resource: string, id: string): never {
  throw new GraphQLError(`${resource} '${id}' not found`, {
    extensions: {
      code: 'NOT_FOUND',
      http: { status: 404 },
    },
  })
}

// ✅ Error formatting — không expose internal errors
const server = new ApolloServer({
  formatError: (formattedError, error) => {
    // Log internal errors
    if (!formattedError.extensions?.code ||
        formattedError.extensions.code === ApolloServerErrorCode.INTERNAL_SERVER_ERROR) {
      console.error('GraphQL error:', error)
      return {
        message: 'Internal server error',
        extensions: { code: 'INTERNAL_SERVER_ERROR' },
      }
    }
    return formattedError
  },
})
```

## Query Complexity & Depth Limiting

```typescript
import depthLimit from 'graphql-depth-limit'
import { createComplexityLimitRule } from 'graphql-validation-complexity'

const server = new ApolloServer({
  validationRules: [
    depthLimit(7),  // ✅ Prevent deeply nested queries
    createComplexityLimitRule(1000, {
      onCost: (cost) => console.log('Query complexity:', cost),
    }),
  ],
})
```

## Anti-patterns

```graphql
# ❌ Over-fetching — không expose tất cả fields
type User {
  password: String  # ❌ Never!
  internalNotes: String  # ❌ Sensitive
}

# ❌ Mutations trả về raw types thay vì payload
type Mutation {
  createUser(input: CreateUserInput!): User  # ❌ Không handle errors
  createUser(input: CreateUserInput!): CreateUserPayload!  # ✅
}

# ❌ N+1 không dùng DataLoader
User: {
  posts: async (user) => {
    return db.posts.find({ authorId: user.id })  # N queries!
  }
}

# ❌ Không giới hạn query depth/complexity
# Attacker có thể gửi deeply nested query gây OOM
```
