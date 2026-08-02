# 🛡️ Pocket Squire

> **STATUS:** Active · `v0.1.0` · PWA Component Library

`pocket-squire` is the shared Next.js PWA component library for CAMELOT-OS. Provides the kernel bridge, service worker infrastructure, React Query data fetching layer, Zustand state management, and Camelot design tokens consumed by the PWA Cockpit and other Next.js surfaces.

## Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16 (App Router) |
| Data Fetching | TanStack React Query 5 |
| State | Zustand 5 |
| Animation | Framer Motion 12 |
| PWA | next-pwa |
| Styling | Tailwind CSS v4 |
| Icons | Lucide React |

## Setup

```bash
# From monorepo root (02_FORGE/)
pnpm install

# Dev server
cd packages/pocket-squire
pnpm dev
```

## Scripts

| Script | Description |
|--------|-------------|
| `pnpm dev` | Next.js dev server |
| `pnpm build` | Production build |
| `pnpm lint` | ESLint |

## Key Features

- **Kernel Bridge:** Type-safe communication with CAMELOT-OS kernel
- **PWA Manifest:** Service worker and offline support
- **Design Tokens:** Camelot-branded Tailwind theme (Luxora Gold `#D4AF37`)
- **React Compiler:** babel-plugin-react-compiler enabled
