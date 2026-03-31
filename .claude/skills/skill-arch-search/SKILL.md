---
name: skill-arch-search
description: Search system design — search architecture, indexing pipeline, full-text search, relevance tuning, autocomplete, faceted search, và search infrastructure.
---

# Skill: Search Architecture

## Search Architecture Overview

```
Data Sources → Indexing Pipeline → Search Index → Search API → Client
  (DB, files,     (ETL, sync,        (ES, Typesense,   (query, filter,   (search bar,
   events)         transform)          Meilisearch)      rank)             autocomplete)
```

---

## Indexing Pipeline

### Sync Strategies

```yaml
database_trigger:
  description: DB trigger fires on change → queue → indexer
  latency: Near real-time (seconds)
  complexity: Medium
  cons: DB-coupled, trigger maintenance

change_data_capture (CDC):
  description: Read DB transaction log → stream changes
  tools: [Debezium, Maxwell, DynamoDB Streams]
  latency: Real-time (sub-second)
  complexity: High
  best_for: Production systems, zero-impact on DB performance
  implementation: |
    Debezium → Kafka → Consumer → Elasticsearch
    // Consumer transforms DB row → search document

event_driven:
  description: Application emits events → consumer indexes
  latency: Near real-time
  complexity: Low
  best_for: Microservices (events already exist)
  implementation: |
    // On product update
    await productRepo.save(product)
    await eventBus.publish('product.updated', { product })
    // Search consumer
    @OnEvent('product.updated')
    async handleProductUpdated(event) {
      await searchIndex.upsert(event.product.id, toSearchDoc(event.product))
    }

batch_reindex:
  description: Periodic full reindex (nightly)
  when: Initial setup, schema change, data correction
  implementation: |
    // Alias-based zero-downtime reindex
    1. Create new index: products_v2
    2. Bulk index all documents into products_v2
    3. Switch alias: products → products_v2
    4. Delete old index: products_v1
```

### Document Design

```typescript
// ✅ Flatten nested data for search efficiency
interface ProductSearchDoc {
  id: string
  name: string
  description: string
  category: string[]          // ["Electronics", "Phones", "Smartphones"]
  brand: string
  price: number
  currency: string
  rating: number
  reviewCount: number
  inStock: boolean
  tags: string[]
  attributes: Record<string, string>  // { color: "black", storage: "128GB" }
  createdAt: string
  updatedAt: string

  // Derived fields for search
  nameKeyword: string         // exact match (not analyzed)
  searchableText: string      // concatenated: name + description + brand + tags
  priceRange: string          // "100-500" for faceted filtering
  popularity: number          // computed score for ranking
}
```

---

## Full-Text Search

### Elasticsearch Implementation

```typescript
// Index settings with custom analyzer
const indexSettings = {
  settings: {
    analysis: {
      analyzer: {
        custom_analyzer: {
          type: 'custom',
          tokenizer: 'standard',
          filter: ['lowercase', 'asciifolding', 'synonym_filter', 'stemmer'],
        },
        autocomplete_analyzer: {
          type: 'custom',
          tokenizer: 'edge_ngram_tokenizer',
          filter: ['lowercase'],
        },
      },
      tokenizer: {
        edge_ngram_tokenizer: {
          type: 'edge_ngram',
          min_gram: 2,
          max_gram: 15,
          token_chars: ['letter', 'digit'],
        },
      },
      filter: {
        synonym_filter: {
          type: 'synonym',
          synonyms: ['phone, smartphone, mobile', 'laptop, notebook'],
        },
      },
    },
  },
  mappings: {
    properties: {
      name: {
        type: 'text',
        analyzer: 'custom_analyzer',
        fields: {
          keyword: { type: 'keyword' },       // exact match
          autocomplete: { type: 'text', analyzer: 'autocomplete_analyzer' },
        },
      },
      description: { type: 'text', analyzer: 'custom_analyzer' },
      category: { type: 'keyword' },          // facet filter
      brand: { type: 'keyword' },             // facet filter
      price: { type: 'float' },               // range filter
      rating: { type: 'float' },
      inStock: { type: 'boolean' },
      tags: { type: 'keyword' },
      createdAt: { type: 'date' },
      popularity: { type: 'float' },          // ranking signal
    },
  },
}
```

### Search Query Construction

```typescript
// Multi-purpose search query
function buildSearchQuery(params: SearchParams) {
  const { query, filters, sort, page, pageSize } = params

  return {
    from: (page - 1) * pageSize,
    size: pageSize,

    query: {
      bool: {
        must: query ? [{
          multi_match: {
            query,
            fields: [
              'name^3',           // name weighted 3x
              'brand^2',          // brand weighted 2x
              'description',
              'tags',
            ],
            type: 'best_fields',
            fuzziness: 'AUTO',   // typo tolerance
          },
        }] : [{ match_all: {} }],

        filter: [
          ...(filters.category ? [{ terms: { category: filters.category } }] : []),
          ...(filters.brand ? [{ terms: { brand: filters.brand } }] : []),
          ...(filters.priceMin || filters.priceMax ? [{
            range: {
              price: {
                ...(filters.priceMin && { gte: filters.priceMin }),
                ...(filters.priceMax && { lte: filters.priceMax }),
              },
            },
          }] : []),
          ...(filters.inStock !== undefined ? [{ term: { inStock: filters.inStock } }] : []),
          ...(filters.minRating ? [{ range: { rating: { gte: filters.minRating } } }] : []),
        ],
      },
    },

    // Faceted aggregations
    aggs: {
      categories: { terms: { field: 'category', size: 20 } },
      brands: { terms: { field: 'brand', size: 20 } },
      price_ranges: {
        range: {
          field: 'price',
          ranges: [
            { key: 'Under $50', to: 50 },
            { key: '$50-$200', from: 50, to: 200 },
            { key: '$200-$500', from: 200, to: 500 },
            { key: 'Over $500', from: 500 },
          ],
        },
      },
      avg_rating: { avg: { field: 'rating' } },
    },

    // Sorting
    sort: sort === 'price_asc' ? [{ price: 'asc' }]
         : sort === 'price_desc' ? [{ price: 'desc' }]
         : sort === 'newest' ? [{ createdAt: 'desc' }]
         : sort === 'rating' ? [{ rating: 'desc' }, { reviewCount: 'desc' }]
         : [{ _score: 'desc' }, { popularity: 'desc' }], // default: relevance

    // Highlighting
    highlight: {
      fields: {
        name: { number_of_fragments: 0 },
        description: { fragment_size: 150, number_of_fragments: 2 },
      },
      pre_tags: ['<mark>'],
      post_tags: ['</mark>'],
    },
  }
}
```

---

## Autocomplete

```yaml
strategies:
  prefix_search:
    description: Match từ đầu (edge ngram)
    latency: "<50ms"
    implementation: |
      // Query
      { match: { "name.autocomplete": { query: userInput } } }
    best_for: Product names, usernames

  completion_suggester:
    description: ES completion suggester (FST-based, fastest)
    latency: "<10ms"
    implementation: |
      // Mapping
      { suggest: { type: 'completion', analyzer: 'simple' } }
      // Query
      { suggest: { product_suggest: { prefix: userInput, completion: { field: 'suggest', size: 5 } } } }
    best_for: Very fast autocomplete

  search_as_you_type:
    description: ES search_as_you_type field type
    latency: "<30ms"
    best_for: Multi-word autocomplete with partial matching

ux_patterns:
  debounce: "300ms — don't query on every keystroke"
  min_chars: "2-3 characters before querying"
  cache: "Cache recent queries client-side (LRU)"
  highlight: "Bold matching portion in suggestions"
  recent_searches: "Show user's recent searches first"
  popular_searches: "Show trending searches when input empty"
```

---

## Relevance Tuning

```yaml
signals:
  text_relevance: "TF-IDF / BM25 score (default ES scoring)"
  field_boost: "name^3, brand^2, description^1"
  recency: "Newer products score higher (decay function)"
  popularity: "Products with more views/sales score higher"
  personalization: "User's past behavior, preferences"

function_score:
  implementation: |
    {
      query: {
        function_score: {
          query: { multi_match: { query: 'phone', fields: ['name^3', 'description'] } },
          functions: [
            { field_value_factor: { field: 'popularity', modifier: 'log1p', factor: 2 } },
            { gauss: { createdAt: { origin: 'now', scale: '30d', decay: 0.5 } } },
            { filter: { term: { inStock: true } }, weight: 5 },
          ],
          score_mode: 'sum',
          boost_mode: 'multiply',
        }
      }
    }

a_b_testing:
  description: "Test different ranking strategies"
  approach: |
    // 50% users get algorithm A, 50% get algorithm B
    // Measure: click-through rate, conversion, time to find
    // Keep winner
```

---

## Search API Design

```yaml
endpoint: "GET /api/search"

request:
  query_params:
    q: "search query (optional — empty = browse)"
    category: "filter by category (multi-value)"
    brand: "filter by brand (multi-value)"
    price_min: "min price"
    price_max: "max price"
    rating: "min rating"
    in_stock: "true/false"
    sort: "relevance | price_asc | price_desc | newest | rating"
    page: "page number (1-based)"
    page_size: "results per page (max 100)"

response: |
  {
    "data": [
      {
        "id": "prod-123",
        "name": "iPhone 15 Pro",
        "description": "...",
        "price": 999,
        "rating": 4.8,
        "highlight": {
          "name": ["<mark>iPhone</mark> 15 Pro"],
          "description": ["The latest <mark>iPhone</mark> with..."]
        }
      }
    ],
    "facets": {
      "categories": [
        { "key": "Smartphones", "count": 42 },
        { "key": "Accessories", "count": 15 }
      ],
      "brands": [
        { "key": "Apple", "count": 28 },
        { "key": "Samsung", "count": 20 }
      ],
      "price_ranges": [
        { "key": "Under $50", "count": 5 },
        { "key": "$50-$200", "count": 12 }
      ]
    },
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 142,
      "totalPages": 8
    },
    "meta": {
      "took_ms": 23,
      "query": "iphone"
    }
  }
```

---

## Anti-patterns

```yaml
search_in_sql:
  bad: "SELECT * FROM products WHERE name LIKE '%phone%'"
  fix: "Use search engine (ES, Typesense) for full-text search"

no_pagination:
  bad: "Return all 100K results"
  fix: "Always paginate, max 100 per page"

reindex_on_every_write:
  bad: "Full reindex after each product update"
  fix: "Incremental index: upsert single document on change"

no_synonyms:
  bad: "Search 'phone' doesn't find 'smartphone'"
  fix: "Configure synonym filter in analyzer"

ignoring_zero_results:
  bad: "Show empty page, user leaves"
  fix: "Did you mean? suggestions, related products, broaden filters"
```
