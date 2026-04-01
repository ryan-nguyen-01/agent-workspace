---
name: skill-framework-strapi
description: Best practices Strapi v5 — content types, custom controllers, services, policies, middlewares, plugins, và headless CMS patterns.
---

# Skill: Strapi v5

## Project Structure

```
src/
├── api/                ← Content types + custom logic
│   └── article/
│       ├── content-types/article/schema.json
│       ├── controllers/article.ts
│       ├── services/article.ts
│       ├── routes/article.ts
│       └── policies/
├── components/         ← Reusable content components
│   └── shared/
│       └── seo.json
├── plugins/            ← Custom plugins
├── middlewares/        ← Custom middlewares
└── policies/          ← Global policies
config/
├── database.ts
├── server.ts
├── admin.ts
└── plugins.ts
```

## Content Type Schema

```json
// src/api/article/content-types/article/schema.json
{
  "kind": "collectionType",
  "collectionName": "articles",
  "info": {
    "singularName": "article",
    "pluralName": "articles",
    "displayName": "Article"
  },
  "options": { "draftAndPublish": true },
  "attributes": {
    "title": { "type": "string", "required": true },
    "slug": { "type": "uid", "targetField": "title" },
    "content": { "type": "richtext" },
    "cover": { "type": "media", "allowedTypes": ["images"] },
    "category": {
      "type": "relation",
      "relation": "manyToOne",
      "target": "api::category.category",
      "inversedBy": "articles"
    },
    "seo": { "type": "component", "component": "shared.seo" },
    "tags": { "type": "relation", "relation": "manyToMany", "target": "api::tag.tag" }
  }
}
```

## Custom Controller

```typescript
// src/api/article/controllers/article.ts
import { factories } from "@strapi/strapi"

export default factories.createCoreController(
  "api::article.article",
  ({ strapi }) => ({
    // Override find — add custom logic
    async find(ctx) {
      const { data, meta } = await super.find(ctx)
      // Add reading time
      const enhanced = data.map((article) => ({
        ...article,
        readingTime: Math.ceil(
          (article.attributes.content?.split(" ").length ?? 0) / 200
        ),
      }))
      return { data: enhanced, meta }
    },

    // Custom action
    async findBySlug(ctx) {
      const { slug } = ctx.params
      const entity = await strapi.db.query("api::article.article").findOne({
        where: { slug },
        populate: ["cover", "category", "seo"],
      })
      if (!entity) return ctx.notFound("Article not found")
      return this.transformResponse(entity)
    },
  })
)
```

## Custom Service

```typescript
// src/api/article/services/article.ts
import { factories } from "@strapi/strapi"

export default factories.createCoreService(
  "api::article.article",
  ({ strapi }) => ({
    async findPublished(filters = {}) {
      return strapi.entityService.findMany("api::article.article", {
        filters: { ...filters, publishedAt: { $notNull: true } },
        populate: ["cover", "category"],
        sort: { publishedAt: "desc" },
      })
    },

    async incrementViews(id: string) {
      const article = await strapi.entityService.findOne("api::article.article", id)
      return strapi.entityService.update("api::article.article", id, {
        data: { views: (article.views || 0) + 1 },
      })
    },
  })
)
```

## Custom Routes

```typescript
// src/api/article/routes/article.ts
import { factories } from "@strapi/strapi"

// Default CRUD routes
const defaultRouter = factories.createCoreRouter("api::article.article")

// Custom routes
const customRouter = {
  routes: [
    {
      method: "GET",
      path: "/articles/slug/:slug",
      handler: "article.findBySlug",
      config: { auth: false },
    },
  ],
}

export default [defaultRouter, customRouter]
```

## Policies & Middlewares

```typescript
// src/policies/is-owner.ts
export default (policyContext, config, { strapi }) => {
  const { id } = policyContext.params
  const userId = policyContext.state.user?.id
  if (!userId) return false
  // Check ownership logic
  return true
}

// src/middlewares/logger.ts
export default (config, { strapi }) => {
  return async (ctx, next) => {
    const start = Date.now()
    await next()
    const duration = Date.now() - start
    strapi.log.info(`${ctx.method} ${ctx.url} - ${duration}ms`)
  }
}
```

## Lifecycle Hooks

```typescript
// src/api/article/content-types/article/lifecycles.ts
export default {
  beforeCreate(event) {
    const { data } = event.params
    if (!data.slug && data.title) {
      data.slug = data.title.toLowerCase().replace(/\s+/g, "-")
    }
  },
  afterCreate(event) {
    const { result } = event
    // Send notification, invalidate cache, etc.
  },
}
```

## Config

```typescript
// config/database.ts
export default ({ env }) => ({
  connection: {
    client: "postgres",
    connection: {
      host: env("DATABASE_HOST", "localhost"),
      port: env.int("DATABASE_PORT", 5432),
      database: env("DATABASE_NAME", "strapi"),
      user: env("DATABASE_USERNAME", "strapi"),
      password: env("DATABASE_PASSWORD"),
      ssl: env.bool("DATABASE_SSL", false),
    },
    pool: { min: 2, max: 10 },
  },
})
```

## Anti-patterns

```
❌ KHÔNG query database trực tiếp, dùng Entity Service API
❌ KHÔNG hardcode populate, dùng query params hoặc default populate
❌ KHÔNG bỏ qua permissions — luôn config roles trong admin
❌ KHÔNG lưu secrets trong schema, dùng env variables
❌ KHÔNG override core routes khi custom route đủ dùng
```
