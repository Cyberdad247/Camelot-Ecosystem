# 🧬 Anya Domain

> **STATUS:** Active · `v1.0.0` · Shared TypeScript Library

`@camelot/anya-domain` is the shared domain model library for CAMELOT-OS TypeScript projects. Provides Zod-validated schemas, type definitions, and domain logic shared across Anya Lyte (mobile) and other TypeScript consumers.

## Stack

| Layer | Technology |
|-------|-----------|
| Language | TypeScript 5.9 |
| Validation | Zod 3.25 |
| Build | tsup (CJS + ESM + DTS) |

## Setup

```bash
# From monorepo root (02_FORGE/)
pnpm install

# Build the library
cd packages/anya-domain
pnpm build
```

## Scripts

| Script | Description |
|--------|-------------|
| `pnpm build` | `tsup` — dual CJS/ESM output with declarations |
| `pnpm dev` | Watch mode build |
| `pnpm lint` | ESLint |

## Consumers

- `apps/anya-lyte` — Expo mobile application
- `packages/anya-lyte` — Shared mobile component package

## Output

```
dist/
├── index.js   (CJS)
├── index.mjs  (ESM)
└── index.d.ts (TypeScript declarations)
```
