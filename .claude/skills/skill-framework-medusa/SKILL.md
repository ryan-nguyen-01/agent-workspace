---
name: skill-framework-medusa
description: Best practices MedusaJS v2 — modules, workflows, API routes, subscribers, links, admin customization, và e-commerce patterns.
---

# Skill: MedusaJS v2

## Project Structure chuẩn

```
src/
├── modules/           ← Custom modules (business logic)
│   └── brand/
│       ├── models/
│       │   └── brand.ts
│       ├── service.ts
│       ├── migrations/
│       └── index.ts
├── workflows/         ← Multi-step business flows
│   └── create-brand.ts
├── api/               ← Custom API routes
│   ├── store/
│   │   └── brands/route.ts
│   └── admin/
│       └── brands/route.ts
├── subscribers/       ← Event listeners
│   └── order-placed.ts
├── links/             ← Module links (relations across modules)
│   └── brand-product.ts
├── admin/             ← Admin UI customizations
│   └── widgets/
└── jobs/              ← Scheduled jobs
```

## Custom Module

```typescript
// src/modules/brand/models/brand.ts
import { model } from "@medusajs/framework/utils"

const Brand = model.define("brand", {
  id: model.id().primaryKey(),
  name: model.text(),
  handle: model.text().unique(),
  description: model.text().nullable(),
  logo_url: model.text().nullable(),
  products: model.hasMany(() => "product"),
})

export default Brand
```

```typescript
// src/modules/brand/service.ts
import { MedusaService } from "@medusajs/framework/utils"
import Brand from "./models/brand"

class BrandModuleService extends MedusaService({ Brand }) {
  // MedusaService tự generate CRUD methods:
  // createBrands, retrieveBrand, listBrands, updateBrands, deleteBrands
  
  // Chỉ thêm custom methods khi cần
  async getBrandByHandle(handle: string) {
    const [brand] = await this.listBrands({ handle })
    return brand
  }
}

export default BrandModuleService
```

```typescript
// src/modules/brand/index.ts
import { Module } from "@medusajs/framework/utils"
import BrandModuleService from "./service"

export const BRAND_MODULE = "brandModuleService"

export default Module(BRAND_MODULE, { service: BrandModuleService })
```

## Workflows — Multi-step Operations

```typescript
// src/workflows/create-brand-with-products.ts
import {
  createWorkflow,
  createStep,
  StepResponse,
  WorkflowResponse,
} from "@medusajs/framework/workflows-sdk"
import { BRAND_MODULE } from "../modules/brand"

const createBrandStep = createStep(
  "create-brand",
  async (input: { name: string; handle: string }, { container }) => {
    const brandService = container.resolve(BRAND_MODULE)
    const brand = await brandService.createBrands(input)
    return new StepResponse(brand, brand.id)
  },
  // Compensation (rollback)
  async (brandId, { container }) => {
    const brandService = container.resolve(BRAND_MODULE)
    await brandService.deleteBrands([brandId])
  }
)

export const createBrandWorkflow = createWorkflow(
  "create-brand-workflow",
  (input: { name: string; handle: string }) => {
    const brand = createBrandStep(input)
    return new WorkflowResponse(brand)
  }
)
```

## API Routes

```typescript
// src/api/store/brands/route.ts
import type { MedusaRequest, MedusaResponse } from "@medusajs/framework/http"
import { BRAND_MODULE } from "../../../modules/brand"

export const GET = async (req: MedusaRequest, res: MedusaResponse) => {
  const brandService = req.scope.resolve(BRAND_MODULE)
  const [brands, count] = await brandService.listAndCountBrands(
    req.filterableFields,
    { skip: req.listConfig.skip, take: req.listConfig.take }
  )
  res.json({ brands, count })
}

export const POST = async (req: MedusaRequest, res: MedusaResponse) => {
  const brandService = req.scope.resolve(BRAND_MODULE)
  const brand = await brandService.createBrands(req.body)
  res.status(201).json({ brand })
}
```

```typescript
// src/api/store/brands/[id]/route.ts
import type { MedusaRequest, MedusaResponse } from "@medusajs/framework/http"

export const GET = async (req: MedusaRequest, res: MedusaResponse) => {
  const brandService = req.scope.resolve("brandModuleService")
  const brand = await brandService.retrieveBrand(req.params.id)
  res.json({ brand })
}
```

## Input Validation với Zod

```typescript
// src/api/store/brands/validators.ts
import { z } from "zod"

export const CreateBrandSchema = z.object({
  name: z.string().min(1),
  handle: z.string().min(1).regex(/^[a-z0-9-]+$/),
  description: z.string().optional(),
})

// Trong route.ts
import { CreateBrandSchema } from "./validators"

export const POST = async (req: MedusaRequest, res: MedusaResponse) => {
  const validated = CreateBrandSchema.parse(req.body)
  // ...
}
```

## Subscribers — Event Handling

```typescript
// src/subscribers/order-placed.ts
import type { SubscriberConfig, SubscriberArgs } from "@medusajs/framework"

export default async function orderPlacedHandler({
  event,
  container,
}: SubscriberArgs<{ id: string }>) {
  const orderId = event.data.id
  const logger = container.resolve("logger")
  logger.info(`Order placed: ${orderId}`)
  // Send notification, update inventory, etc.
}

export const config: SubscriberConfig = {
  event: "order.placed",
}
```

## Module Links — Cross-module Relations

```typescript
// src/links/brand-product.ts
import { defineLink } from "@medusajs/framework/utils"
import BrandModule from "../modules/brand"
import ProductModule from "@medusajs/medusa/product"

export default defineLink(BrandModule.linkable.brand, ProductModule.linkable.product)
```

## Scheduled Jobs

```typescript
// src/jobs/sync-inventory.ts
import type { IScheduledJobConfig } from "@medusajs/framework"

export default async function syncInventoryJob(container) {
  const logger = container.resolve("logger")
  logger.info("Running inventory sync...")
}

export const config: IScheduledJobConfig = {
  name: "sync-inventory",
  schedule: "0 */6 * * *", // Every 6 hours
}
```

## medusa-config.ts

```typescript
import { defineConfig, loadEnv } from "@medusajs/framework/utils"
loadEnv(process.env.NODE_ENV, process.cwd())

export default defineConfig({
  projectConfig: {
    databaseUrl: process.env.DATABASE_URL,
    redisUrl: process.env.REDIS_URL,
    http: {
      storeCors: process.env.STORE_CORS,
      adminCors: process.env.ADMIN_CORS,
      authCors: process.env.AUTH_CORS,
    },
  },
  modules: [
    { resolve: "./src/modules/brand" },
  ],
})
```

## Anti-patterns

```
❌ KHÔNG modify core Medusa modules trực tiếp
❌ KHÔNG dùng direct DB queries, dùng Module Service
❌ KHÔNG bỏ qua compensation trong workflows
❌ KHÔNG hardcode IDs, dùng links để relate modules
❌ KHÔNG viết business logic trong API routes, đặt trong workflows
```
