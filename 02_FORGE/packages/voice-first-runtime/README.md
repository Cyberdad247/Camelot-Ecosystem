# 🎙️ Voice-First Runtime

> **STATUS:** Early Development · `v0.1.0` · TypeScript Library

`@camelot/voice-first-runtime` is the voice interaction runtime library for CAMELOT-OS. Provides the foundational TypeScript types and interfaces for voice-first cartridge and agent interactions.

## Stack

| Layer | Technology |
|-------|-----------|
| Language | TypeScript |
| Module | ESM (`"type": "module"`) |
| Entry | `./src/index.ts` |

## Setup

```bash
# From monorepo root (02_FORGE/)
pnpm install

# Typecheck
cd packages/voice-first-runtime
pnpm build
```

## Scripts

| Script | Description |
|--------|-------------|
| `pnpm build` | `tsc --noEmit` typecheck |
| `pnpm lint` | `tsc --noEmit` typecheck |
| `pnpm typecheck` | `tsc --noEmit` typecheck |
| `pnpm clean` | Remove dist |
