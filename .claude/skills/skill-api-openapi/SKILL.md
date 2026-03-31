---
name: skill-api-openapi
description: Best practices OpenAPI/Swagger — contract-first design, schema definition, code generation, documentation UI, versioning, và CI validation.
---

# Skill: OpenAPI / Swagger

## Contract-First vs Code-First

```yaml
contract_first:
  approach: "Write OpenAPI spec FIRST → generate code from spec"
  pros: "FE/mobile/partner can start before BE is done, single source of truth"
  cons: "More upfront work, spec can drift from code"
  best_for: "Multi-team, public APIs, B2B integrations"

code_first:
  approach: "Write code with decorators → auto-generate OpenAPI spec"
  pros: "Spec always matches code, faster for small teams"
  cons: "Code is source of truth — spec is derived"
  best_for: "Single team, internal APIs, rapid prototyping"

recommendation: "Code-first for NestJS/FastAPI/Spring (great decorator support)"
```

---

## Code-First: NestJS + Swagger

```typescript
// main.ts — setup Swagger UI
import { NestFactory } from '@nestjs/core'
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger'

async function bootstrap() {
  const app = await NestFactory.create(AppModule)

  const config = new DocumentBuilder()
    .setTitle('MyApp API')
    .setDescription('REST API documentation')
    .setVersion('1.0')
    .addBearerAuth()
    .addTag('users', 'User management')
    .addTag('orders', 'Order operations')
    .build()

  const document = SwaggerModule.createDocument(app, config)
  SwaggerModule.setup('docs', app, document) // available at /docs

  await app.listen(3000)
}

// DTOs with Swagger decorators
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger'

class CreateOrderDto {
  @ApiProperty({
    description: 'List of items to order',
    type: [OrderItemDto],
    minItems: 1,
    maxItems: 50,
  })
  @IsArray()
  @ValidateNested({ each: true })
  items: OrderItemDto[]

  @ApiPropertyOptional({ description: 'Coupon code', example: 'SAVE20' })
  @IsString()
  @IsOptional()
  couponCode?: string
}

class OrderItemDto {
  @ApiProperty({ description: 'Product UUID', format: 'uuid', example: '550e8400-e29b-41d4-a716-446655440000' })
  @IsUUID()
  productId: string

  @ApiProperty({ description: 'Quantity', minimum: 1, maximum: 100, example: 2 })
  @IsInt()
  @Min(1)
  @Max(100)
  quantity: number
}

// Controller with API decorators
@ApiTags('orders')
@ApiBearerAuth()
@Controller('orders')
export class OrderController {
  @Post()
  @ApiOperation({ summary: 'Create a new order' })
  @ApiResponse({ status: 201, description: 'Order created', type: OrderResponseDto })
  @ApiResponse({ status: 400, description: 'Validation error' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  async create(@Body() dto: CreateOrderDto): Promise<OrderResponseDto> { /* ... */ }

  @Get()
  @ApiOperation({ summary: 'List orders with pagination' })
  @ApiQuery({ name: 'page', required: false, type: Number, example: 1 })
  @ApiQuery({ name: 'limit', required: false, type: Number, example: 20 })
  @ApiResponse({ status: 200, description: 'Paginated order list', type: PaginatedOrdersDto })
  async findAll(@Query() query: ListOrdersQuery): Promise<PaginatedOrdersDto> { /* ... */ }

  @Get(':id')
  @ApiOperation({ summary: 'Get order by ID' })
  @ApiParam({ name: 'id', format: 'uuid' })
  @ApiResponse({ status: 200, type: OrderResponseDto })
  @ApiResponse({ status: 404, description: 'Order not found' })
  async findOne(@Param('id', ParseUUIDPipe) id: string): Promise<OrderResponseDto> { /* ... */ }
}

// Response DTO
class OrderResponseDto {
  @ApiProperty({ format: 'uuid' })
  id: string

  @ApiProperty({ enum: ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled'] })
  status: string

  @ApiProperty({ type: Number, example: 59.99 })
  totalAmount: number

  @ApiProperty({ type: [OrderItemResponseDto] })
  items: OrderItemResponseDto[]

  @ApiProperty({ format: 'date-time' })
  createdAt: string
}
```

---

## Code-First: FastAPI (Python)

```python
from fastapi import FastAPI, Query, Path, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

app = FastAPI(
    title="MyApp API",
    description="REST API documentation",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc alternative
)

class OrderItemCreate(BaseModel):
    product_id: UUID = Field(..., description="Product UUID")
    quantity: int = Field(..., ge=1, le=100, description="Quantity")

class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(..., min_length=1, max_length=50)
    coupon_code: str | None = Field(None, max_length=20, example="SAVE20")

class OrderResponse(BaseModel):
    id: UUID
    status: str
    total_amount: float
    created_at: datetime

    model_config = {"from_attributes": True}

@app.post("/orders", response_model=OrderResponse, status_code=201, tags=["orders"])
async def create_order(dto: OrderCreate, user=Depends(get_current_user)):
    """Create a new order."""
    return await order_service.create(dto, user.id)

@app.get("/orders", response_model=PaginatedResponse[OrderResponse], tags=["orders"])
async def list_orders(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    user=Depends(get_current_user),
):
    """List orders with pagination."""
    return await order_service.list(user.id, page, limit)
```

---

## Contract-First: OpenAPI Spec

```yaml
# openapi.yaml
openapi: 3.1.0
info:
  title: MyApp API
  version: 1.0.0
  description: REST API for MyApp

servers:
  - url: https://api.myapp.com/v1
    description: Production
  - url: https://api-staging.myapp.com/v1
    description: Staging

paths:
  /orders:
    post:
      tags: [orders]
      summary: Create order
      operationId: createOrder
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateOrder'
      responses:
        '201':
          description: Order created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Order'
        '400':
          $ref: '#/components/responses/ValidationError'
        '401':
          $ref: '#/components/responses/Unauthorized'

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    CreateOrder:
      type: object
      required: [items]
      properties:
        items:
          type: array
          minItems: 1
          maxItems: 50
          items:
            $ref: '#/components/schemas/OrderItem'
        couponCode:
          type: string
          maxLength: 20

    Order:
      type: object
      properties:
        id:
          type: string
          format: uuid
        status:
          type: string
          enum: [pending, confirmed, shipped, delivered, cancelled]
        totalAmount:
          type: number
          format: decimal
        createdAt:
          type: string
          format: date-time

  responses:
    ValidationError:
      description: Validation error
      content:
        application/json:
          schema:
            type: object
            properties:
              statusCode:
                type: integer
                example: 400
              message:
                type: array
                items:
                  type: string
              error:
                type: string
                example: Bad Request
```

---

## Client SDK Generation

```yaml
tools:
  openapi_generator: "openapi-generator-cli"
  orval: "TypeScript client from OpenAPI (React Query hooks)"
  swagger_codegen: "Official Swagger tool"

typescript_client:
  command: |
    npx openapi-generator-cli generate \
      -i https://api.myapp.com/docs-json \
      -g typescript-axios \
      -o src/api/generated

  orval: |
    # orval.config.ts — generates React Query hooks
    export default {
      myapp: {
        input: 'https://api.myapp.com/docs-json',
        output: {
          target: 'src/api/generated.ts',
          client: 'react-query',
          mode: 'tags-split',
        },
      },
    }

mobile_client:
  dart: "openapi-generator -g dart-dio"
  kotlin: "openapi-generator -g kotlin"
  swift: "openapi-generator -g swift5"
```

---

## CI Validation

```yaml
# Validate spec doesn't break
- name: Lint OpenAPI spec
  run: npx @redocly/cli lint openapi.yaml

# Detect breaking changes
- name: Check breaking changes
  run: npx oasdiff breaking openapi-main.yaml openapi-pr.yaml

# Export spec from running app
- name: Export OpenAPI spec
  run: |
    curl -o openapi.json http://localhost:3000/docs-json
    npx @redocly/cli lint openapi.json
```

---

## Anti-patterns

```yaml
no_examples:
  bad: "Schema without example values — consumers guess format"
  fix: "Add example to every property"

generic_responses:
  bad: "All endpoints return { data: any }"
  fix: "Specific response schema per endpoint"

undocumented_errors:
  bad: "Only document 200 — consumer doesn't know about 400, 401, 404"
  fix: "Document ALL possible response codes"

spec_drift:
  bad: "OpenAPI spec says X, actual API returns Y"
  fix: "CI: generate spec from code → validate against committed spec"
```
