---
name: skill-security-graphql
description: GraphQL-specific security — query depth limiting, complexity analysis, introspection control, batch attack prevention, persisted queries, rate limiting per operation, và N+1 prevention.
---

# Skill: GraphQL Security

## Attack Vectors

```yaml
query_depth_attack:
  attack: "Deeply nested query → exponential DB joins → server crash"
  example: |
    {
      user {
        posts {
          comments {
            author {
              posts {
                comments {
                  author { ... }  # infinite nesting
                }
              }
            }
          }
        }
      }
    }

complexity_attack:
  attack: "Query requests huge dataset → OOM or slow response"
  example: |
    { users(first: 10000) { posts(first: 10000) { comments(first: 10000) { body } } } }

batch_attack:
  attack: "Single request with 1000 aliased queries → amplification"
  example: |
    {
      a1: user(id: "1") { email }
      a2: user(id: "2") { email }
      ...
      a1000: user(id: "1000") { email }
    }

introspection_leak:
  attack: "Query __schema to discover hidden fields/mutations"
  example: |
    { __schema { types { name fields { name } } } }
```

---

## Query Depth Limiting

```typescript
import depthLimit from 'graphql-depth-limit'

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [
    depthLimit(7),  // max 7 levels deep
  ],
})

// Custom depth limit with field-specific rules
import { createComplexityRule } from 'graphql-query-complexity'

const depthRule = depthLimit(7, {
  ignore: ['__schema', '__type'], // allow introspection (dev only)
})
```

---

## Query Complexity Analysis

```typescript
import { createComplexityLimitRule } from 'graphql-validation-complexity'

const complexityRule = createComplexityLimitRule(1000, {
  scalarCost: 1,
  objectCost: 2,
  listFactor: 10,     // multiply by list size
  introspectionListFactor: 2,
  formatErrorMessage: (cost) =>
    `Query too complex: cost ${cost} exceeds maximum 1000`,
})

// Per-field complexity (Apollo)
const typeDefs = gql`
  type Query {
    users(first: Int = 20): [User!]! @complexity(value: 5, multipliers: ["first"])
    user(id: ID!): User @complexity(value: 1)
  }

  type User {
    id: ID!
    email: String!
    posts(first: Int = 10): [Post!]! @complexity(value: 3, multipliers: ["first"])
  }
`

// Implementation with graphql-query-complexity
import { getComplexity, simpleEstimator, fieldExtensionsEstimator } from 'graphql-query-complexity'

const server = new ApolloServer({
  plugins: [{
    requestDidStart: () => ({
      didResolveOperation({ request, document }) {
        const complexity = getComplexity({
          schema,
          operationName: request.operationName,
          query: document,
          variables: request.variables,
          estimators: [
            fieldExtensionsEstimator(),
            simpleEstimator({ defaultComplexity: 1 }),
          ],
        })

        if (complexity > 1000) {
          throw new GraphQLError(
            `Query complexity ${complexity} exceeds maximum 1000`
          )
        }
      },
    }),
  }],
})
```

---

## Introspection Control

```typescript
// ✅ Disable introspection in production
import { ApolloServerPluginLandingPageDisabled } from '@apollo/server/plugin/disabled'

const server = new ApolloServer({
  typeDefs,
  resolvers,
  introspection: process.env.NODE_ENV !== 'production',
  plugins: [
    process.env.NODE_ENV === 'production'
      ? ApolloServerPluginLandingPageDisabled()
      : ApolloServerPluginLandingPageLocalDefault(),
  ],
})

// ✅ Alternative: allow introspection only for authenticated admin
const server = new ApolloServer({
  introspection: false,
  plugins: [{
    requestDidStart: ({ request, contextValue }) => {
      if (request.query?.includes('__schema') || request.query?.includes('__type')) {
        if (!contextValue.user?.roles.includes('admin')) {
          throw new GraphQLError('Introspection not allowed')
        }
      }
    },
  }],
})
```

---

## Batch & Alias Attack Prevention

```typescript
// Limit number of aliases per query
function aliasLimitRule(maxAliases: number) {
  return (context: ValidationContext) => ({
    Field(node: FieldNode) {
      // Count aliases in document
      const aliases = new Set<string>()
      visit(context.getDocument(), {
        Field(node) {
          if (node.alias) aliases.add(node.alias.value)
        },
      })
      if (aliases.size > maxAliases) {
        context.reportError(
          new GraphQLError(`Too many aliases: ${aliases.size} (max: ${maxAliases})`)
        )
      }
    },
  })
}

// Limit batch queries (Apollo)
const server = new ApolloServer({
  allowBatchedHttpRequests: false, // ✅ disable batched queries
})

// Or limit batch size
app.use('/graphql', express.json({ limit: '100kb' })) // limit request size
```

---

## Persisted Queries (Allowlist)

```yaml
concept: "Only allow pre-registered queries — reject arbitrary queries"
benefit: "Eliminates ALL query-based attacks (depth, complexity, injection)"
tradeoff: "FE must register queries at build time"
```

```typescript
// Automatic Persisted Queries (APQ) — Apollo
// Client sends hash first, server checks cache
// If miss → client sends full query → server caches

const server = new ApolloServer({
  persistedQueries: {
    cache: new KeyValueCache(), // Redis recommended
    ttl: 900, // 15 minutes
  },
})

// Strict mode: ONLY allow persisted queries (whitelist)
const allowedQueries = new Map<string, string>() // hash → query

const server = new ApolloServer({
  plugins: [{
    requestDidStart: ({ request }) => {
      const hash = request.extensions?.persistedQuery?.sha256Hash
      if (!hash || !allowedQueries.has(hash)) {
        throw new GraphQLError('Only persisted queries allowed in production')
      }
    },
  }],
})
```

---

## Rate Limiting per Operation

```typescript
import { RateLimiterRedis } from 'rate-limiter-flexible'

const rateLimiter = new RateLimiterRedis({
  storeClient: redis,
  keyPrefix: 'gql_rate',
  points: 100,     // 100 operations
  duration: 60,    // per 60 seconds
})

// Per-operation cost
const operationCosts: Record<string, number> = {
  'users': 1,
  'createOrder': 5,      // mutations cost more
  'deleteAccount': 10,   // destructive = expensive
  'exportData': 20,      // heavy operations
}

const server = new ApolloServer({
  plugins: [{
    requestDidStart: ({ contextValue }) => ({
      async didResolveOperation({ request }) {
        const userId = contextValue.user?.id ?? contextValue.ip
        const operationName = request.operationName ?? 'anonymous'
        const cost = operationCosts[operationName] ?? 1

        try {
          await rateLimiter.consume(userId, cost)
        } catch {
          throw new GraphQLError('Rate limit exceeded', {
            extensions: { code: 'RATE_LIMITED', retryAfter: 60 },
          })
        }
      },
    }),
  }],
})
```

---

## N+1 Prevention (DataLoader)

```typescript
import DataLoader from 'dataloader'

// Without DataLoader: N+1 queries
// Query { users { posts { ... } } }
// → 1 query for users + N queries for posts (one per user)

// With DataLoader: 2 queries total
const postLoader = new DataLoader(async (userIds: readonly string[]) => {
  const posts = await prisma.post.findMany({
    where: { authorId: { in: [...userIds] } },
  })
  // Return in same order as input keys
  return userIds.map(id => posts.filter(p => p.authorId === id))
})

const resolvers = {
  User: {
    posts: (user: User) => postLoader.load(user.id),
  },
}

// Create new DataLoader per request (avoid cross-request caching)
function createLoaders() {
  return {
    postLoader: new DataLoader(batchPosts),
    commentLoader: new DataLoader(batchComments),
  }
}
```

---

## Anti-patterns

```yaml
no_depth_limit:
  bad: "Accept any query depth → recursive query crashes server"
  fix: "depthLimit(7) minimum"

introspection_in_prod:
  bad: "__schema query reveals all types, fields, mutations"
  fix: "Disable introspection in production"

no_complexity_limit:
  bad: "{ users(first: 99999) { ... } } returns entire DB"
  fix: "Query complexity analysis with per-field cost estimation"

resolver_auth_skip:
  bad: "Auth check only on top-level query, not nested resolvers"
  fix: "Auth check at resolver level OR use schema directives"
```
