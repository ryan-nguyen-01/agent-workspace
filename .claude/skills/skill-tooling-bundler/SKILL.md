---
name: skill-tooling-bundler
description: Best practices dùng Vite, esbuild và Rollup cho frontend/library bundling: config, code splitting, optimization và build performance.
---

# Skill: Bundlers (Vite / esbuild / Rollup)

## Chọn Bundler

```
Vite      ← Default cho web app (React, Vue, Svelte)
  + Dev server cực nhanh (native ESM + esbuild)
  + HMR instant
  + Rollup cho production build (tree-shaking tốt)
  + Plugin ecosystem phong phú

esbuild   ← Cho tooling, scripts, libraries đơn giản
  + Nhanh nhất (Go-based)
  + Dùng làm transform engine trong Vite/Remix
  - Không có HMR, thiếu một số Rollup features

Rollup    ← Cho libraries (npm packages)
  + Tree-shaking tốt nhất
  + Output formats: ESM, CJS, UMD
  - Dev server không tốt bằng Vite

Webpack   ← Legacy, chỉ dùng khi project cũ
  - Chậm, config phức tạp
  → Migrate sang Vite nếu có thể
```

## Vite — Web App Config

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'  // SWC nhanh hơn Babel
import tsconfigPaths from 'vite-tsconfig-paths'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
    tsconfigPaths(),  // ✅ Support TypeScript path aliases
    mode === 'analyze' && visualizer({
      open: true,
      gzipSize: true,
    }),
  ],

  build: {
    target: 'es2020',
    sourcemap: mode !== 'production',

    rollupOptions: {
      output: {
        // ✅ Manual chunks — tách vendor khỏi app code
        manualChunks: {
          'vendor-react': ['react', 'react-dom'],
          'vendor-ui': ['@mui/material', '@emotion/react'],
          'vendor-query': ['@tanstack/react-query'],
        },
      },
    },

    // ✅ Warn nếu chunk > 500KB
    chunkSizeWarningLimit: 500,
  },

  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:4000',
        changeOrigin: true,
      },
    },
  },

  // ✅ Path aliases
  resolve: {
    alias: {
      '@': '/src',
    },
  },

  // ✅ Env variables — chỉ expose VITE_ prefix
  // VITE_API_URL=... → import.meta.env.VITE_API_URL
}))
```

## Vite — Library Mode (npm package)

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import dts from 'vite-plugin-dts'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    dts({ insertTypesEntry: true }),  // ✅ Generate .d.ts files
  ],
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      name: 'MyLib',
      formats: ['es', 'cjs'],
      fileName: (format) => `my-lib.${format}.js`,
    },
    rollupOptions: {
      // ✅ Externalize peer deps — không bundle vào output
      external: ['react', 'react-dom'],
      output: {
        globals: {
          react: 'React',
          'react-dom': 'ReactDOM',
        },
      },
    },
  },
})
```

## esbuild — Script / CLI Tool

```typescript
// build.ts
import { build } from 'esbuild'

await build({
  entryPoints: ['src/index.ts'],
  bundle: true,
  platform: 'node',
  target: 'node20',
  format: 'esm',
  outfile: 'dist/index.js',
  external: ['express', 'pg'],  // ✅ Externalize node_modules
  sourcemap: true,
  minify: process.env.NODE_ENV === 'production',
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
  },
})
```

## Optimization Techniques

```typescript
// ✅ Lazy loading routes (React)
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Settings = lazy(() => import('./pages/Settings'))

// ✅ Dynamic imports cho heavy libraries
const { Chart } = await import('chart.js')

// ✅ Preload critical chunks
// <link rel="modulepreload" href="/assets/vendor-react.js">
// Vite tự generate nếu dùng <script type="module">
```

```bash
# Phân tích bundle size
VITE_ANALYZE=true pnpm build
# Hoặc
pnpm add -D rollup-plugin-visualizer
# Xem dist/stats.html
```

## Anti-patterns

```
❌ Import toàn bộ library khi chỉ cần 1 function
import _ from 'lodash'           // ❌ Bundle toàn bộ lodash
import { debounce } from 'lodash' // ✅ Tree-shakable

❌ Không chia chunk vendor → app code thay đổi → cache miss toàn bộ
→ manualChunks tách vendor khỏi app

❌ Bundle node_modules vào server-side code
→ esbuild: external: ['express', ...]

❌ Source maps trong production → expose source code
→ sourcemap: false trong production (hoặc dùng hidden source maps)

❌ Không check bundle size → bloat không nhận ra
→ Dùng visualizer, set chunkSizeWarningLimit
```
