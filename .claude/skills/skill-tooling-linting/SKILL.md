---
name: skill-tooling-linting
description: Best practices cấu hình ESLint, Prettier và Biome cho TypeScript/JavaScript projects: setup, rules quan trọng, tích hợp với editor và CI/CD.
---

# Skill: Linting & Formatting

## Chọn Tool

```
Biome  ← Recommend cho project mới (2024+)
  + 1 tool thay cả ESLint + Prettier
  + Cực nhanh (Rust-based)
  + Zero config để bắt đầu
  - Rules ít hơn ESLint ecosystem

ESLint + Prettier ← Cho project cần rules phức tạp / ecosystem lớn
  + Ecosystem plugin phong phú (React, NestJS, import order, ...)
  + Customizable cao
  - Config phức tạp hơn, chậm hơn Biome
```

## Biome Setup

```bash
pnpm add -D @biomejs/biome
npx @biomejs/biome init
```

```json
// biome.json
{
  "$schema": "https://biomejs.dev/schemas/1.8.0/schema.json",
  "organizeImports": { "enabled": true },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "correctness": {
        "noUnusedVariables": "error",
        "noUnusedImports": "error"
      },
      "suspicious": {
        "noExplicitAny": "warn"
      },
      "style": {
        "noNonNullAssertion": "warn"
      }
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "trailingCommas": "es5",
      "semicolons": "always"
    }
  },
  "files": {
    "ignore": ["node_modules", "dist", "build", "coverage"]
  }
}
```

```json
// package.json scripts
{
  "scripts": {
    "lint": "biome check src",
    "lint:fix": "biome check --write src",
    "format": "biome format --write src"
  }
}
```

## ESLint + Prettier Setup (TypeScript)

```bash
pnpm add -D eslint @typescript-eslint/eslint-plugin @typescript-eslint/parser
pnpm add -D eslint-config-prettier prettier
pnpm add -D eslint-plugin-import eslint-import-resolver-typescript
```

```js
// eslint.config.js (flat config — ESLint v9+)
import tseslint from 'typescript-eslint'
import importPlugin from 'eslint-plugin-import'
import prettier from 'eslint-config-prettier'

export default tseslint.config(
  ...tseslint.configs.recommended,
  {
    plugins: { import: importPlugin },
    rules: {
      // TypeScript
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/no-non-null-assertion': 'warn',

      // Imports
      'import/order': ['error', {
        groups: ['builtin', 'external', 'internal', 'parent', 'sibling'],
        'newlines-between': 'always',
        alphabetize: { order: 'asc' },
      }],
      'import/no-duplicates': 'error',

      // General
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'prefer-const': 'error',
    },
    settings: {
      'import/resolver': { typescript: true },
    },
  },
  prettier, // ✅ Phải để cuối để override conflicting rules
  {
    ignores: ['dist/', 'build/', 'node_modules/', 'coverage/'],
  },
)
```

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "always"
}
```

## ESLint cho NestJS

```bash
pnpm add -D @darraghor/eslint-plugin-nestjs-typed
```

```js
// Thêm vào eslint.config.js
import nestjsTyped from '@darraghor/eslint-plugin-nestjs-typed'

export default [
  ...nestjsTyped.configs.flatRecommended,
  // ... rest of config
]
```

## ESLint cho React

```bash
pnpm add -D eslint-plugin-react eslint-plugin-react-hooks eslint-plugin-jsx-a11y
```

```js
// Thêm rules
{
  'react-hooks/rules-of-hooks': 'error',
  'react-hooks/exhaustive-deps': 'warn',
  'jsx-a11y/alt-text': 'error',
  'jsx-a11y/anchor-is-valid': 'error',
}
```

## VS Code Integration

```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "biomejs.biome",  // hoặc "esbenp.prettier-vscode"
  "editor.codeActionsOnSave": {
    "quickfix.biome": "explicit",              // hoặc "source.fixAll.eslint"
    "source.organizeImports": "never"          // để Biome/ESLint handle
  },
  "[typescript]": {
    "editor.defaultFormatter": "biomejs.biome"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "biomejs.biome"
  }
}
```

## CI Integration

```yaml
# GitHub Actions
- name: Lint
  run: pnpm lint

- name: Format check
  run: pnpm biome format --check src  # exit 1 nếu có file chưa format
```

## Anti-patterns

```
❌ Disable toàn bộ rule cho 1 file: /* eslint-disable */
→ Disable rule cụ thể với comment lý do:
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- legacy API response

❌ any ở khắp nơi → mất type safety
→ Dùng unknown và narrow type, hoặc tạo proper types

❌ Prettier và ESLint conflict → formatting wars khi save
→ Luôn dùng eslint-config-prettier để tắt ESLint formatting rules

❌ Không chạy lint trong CI → code tệ được merge
→ Lint phải là required check trong PR
```
