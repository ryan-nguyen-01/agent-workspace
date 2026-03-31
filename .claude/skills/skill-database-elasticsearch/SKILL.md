---
name: skill-database-elasticsearch
description: Best practices dùng Elasticsearch 8+: index design, mappings, search queries, aggregations, relevance tuning và Node.js client patterns.
---

# Skill: Elasticsearch 8+

## Index Design & Mappings

```typescript
import { Client } from '@elastic/elasticsearch'

const es = new Client({
  node: process.env.ELASTICSEARCH_URL,
  auth: {
    apiKey: process.env.ELASTICSEARCH_API_KEY!,
  },
  tls: { rejectUnauthorized: process.env.NODE_ENV === 'production' },
})

// ✅ Explicit mapping — không để dynamic mapping trong production
await es.indices.create({
  index: 'products',
  body: {
    settings: {
      number_of_shards: 3,
      number_of_replicas: 1,
      analysis: {
        analyzer: {
          vietnamese_analyzer: {
            type: 'custom',
            tokenizer: 'standard',
            filter: ['lowercase', 'asciifolding'],
          },
        },
      },
    },
    mappings: {
      properties: {
        id:          { type: 'keyword' },
        name:        { type: 'text', analyzer: 'vietnamese_analyzer', fields: { keyword: { type: 'keyword' } } },
        description: { type: 'text', analyzer: 'vietnamese_analyzer' },
        price:       { type: 'scaled_float', scaling_factor: 100 },
        category:    { type: 'keyword' },
        tags:        { type: 'keyword' },
        inStock:     { type: 'boolean' },
        rating:      { type: 'half_float' },
        createdAt:   { type: 'date' },
        location:    { type: 'geo_point' },
      },
    },
  },
})
```

## Indexing Documents

```typescript
// ✅ Index single document
await es.index({
  index: 'products',
  id: product.id,
  document: {
    id: product.id,
    name: product.name,
    description: product.description,
    price: product.price,
    category: product.category,
    tags: product.tags,
    inStock: product.stock > 0,
    createdAt: product.createdAt,
  },
  refresh: 'wait_for',  // ✅ Wait for indexing (only in tests/critical writes)
})

// ✅ Bulk indexing (production preferred)
const operations = products.flatMap(product => [
  { index: { _index: 'products', _id: product.id } },
  {
    id: product.id,
    name: product.name,
    price: product.price,
    category: product.category,
    inStock: product.stock > 0,
    createdAt: product.createdAt,
  },
])

const { errors, items } = await es.bulk({ operations, refresh: false })
if (errors) {
  const failed = items.filter(item => item.index?.error)
  console.error('Bulk indexing errors:', failed)
}
```

## Search Queries

```typescript
// ✅ Full-text search với scoring
async function searchProducts(query: string, filters: {
  category?: string
  minPrice?: number
  maxPrice?: number
  inStock?: boolean
  page?: number
  size?: number
}) {
  const { page = 1, size = 20 } = filters

  const response = await es.search({
    index: 'products',
    from: (page - 1) * size,
    size,
    body: {
      query: {
        bool: {
          must: query ? [{
            multi_match: {
              query,
              fields: ['name^3', 'description', 'tags^2'],  // ✅ Boost name & tags
              type: 'best_fields',
              fuzziness: 'AUTO',
            },
          }] : [{ match_all: {} }],
          filter: [
            ...(filters.category ? [{ term: { category: filters.category } }] : []),
            ...(filters.inStock !== undefined ? [{ term: { inStock: filters.inStock } }] : []),
            ...(filters.minPrice !== undefined || filters.maxPrice !== undefined ? [{
              range: {
                price: {
                  ...(filters.minPrice !== undefined ? { gte: filters.minPrice } : {}),
                  ...(filters.maxPrice !== undefined ? { lte: filters.maxPrice } : {}),
                },
              },
            }] : []),
          ],
        },
      },
      highlight: {
        fields: {
          name: { pre_tags: ['<mark>'], post_tags: ['</mark>'] },
          description: { number_of_fragments: 2, fragment_size: 150 },
        },
      },
      sort: query ? ['_score'] : [{ createdAt: { order: 'desc' } }],
    },
  })

  return {
    items: response.hits.hits.map(hit => ({
      ...hit._source,
      _score: hit._score,
      _highlight: hit.highlight,
    })),
    total: typeof response.hits.total === 'number'
      ? response.hits.total
      : response.hits.total?.value ?? 0,
    page,
    size,
  }
}
```

## Aggregations

```typescript
// ✅ Faceted search aggregations
const response = await es.search({
  index: 'products',
  size: 0,  // ✅ Only aggregations, no hits
  body: {
    query: { term: { inStock: true } },
    aggs: {
      categories: {
        terms: { field: 'category', size: 20 },
        aggs: {
          avg_price: { avg: { field: 'price' } },
        },
      },
      price_ranges: {
        range: {
          field: 'price',
          ranges: [
            { key: 'under_100', to: 100 },
            { key: '100_500', from: 100, to: 500 },
            { key: 'over_500', from: 500 },
          ],
        },
      },
      avg_rating: { avg: { field: 'rating' } },
      top_tags: { terms: { field: 'tags', size: 10 } },
    },
  },
})

const { categories, price_ranges, avg_rating, top_tags } = response.aggregations!
```

## Index Alias & Zero-Downtime Reindex

```typescript
// ✅ Blue-green reindex pattern
async function reindex(): Promise<void> {
  const newIndex = `products_${Date.now()}`

  // 1. Create new index with updated mapping
  await es.indices.create({ index: newIndex, body: newMapping })

  // 2. Reindex data
  await es.reindex({
    body: {
      source: { index: 'products' },
      dest: { index: newIndex },
    },
    wait_for_completion: true,
  })

  // 3. Swap alias atomically
  await es.indices.updateAliases({
    body: {
      actions: [
        { remove: { index: '*', alias: 'products' } },
        { add: { index: newIndex, alias: 'products' } },
      ],
    },
  })

  // 4. Delete old index
  const { indices } = await es.cat.indices({ h: ['index'], format: 'json' })
  // Delete old products_* indices
}
```

## Anti-patterns

```typescript
// ❌ Dynamic mapping trong production (auto-creates uncontrolled field types)
// ✅ explicit_mapping: true hoặc strict mode
{ mappings: { dynamic: 'strict' } }

// ❌ Deep pagination với from/size (>10k hits)
{ from: 50000, size: 20 }  // Very expensive!
// ✅ Search After pagination
{
  sort: [{ createdAt: 'desc' }, { _id: 'asc' }],
  search_after: [lastCreatedAt, lastId],
  size: 20,
}

// ❌ Wildcard query ở đầu (full index scan)
{ query: { wildcard: { name: '*phone*' } } }  // ❌
// ✅ Match query với analyzer

// ❌ Không dùng alias (hard to reindex without downtime)
es.index({ index: 'products_v1', ... })
// ✅ index: 'products' (alias → actual index)
```
