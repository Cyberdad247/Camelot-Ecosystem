# 📱 Anya Lyte Package

> **STATUS:** Active Development · `v0.1.0` · Expo Shared Package

`anya-lyte-pkg` is the shared component and logic package for the Anya Lyte mobile ecosystem. Built with Expo SDK 50, Tamagui for cross-platform UI, and Drizzle ORM for local SQLite persistence.

## Stack

| Layer | Technology |
|-------|-----------|
| Framework | Expo SDK 50, React Native 0.73 |
| UI System | Tamagui v2 + Lucide React Native |
| Database | expo-sqlite + Drizzle ORM |
| Domain | `@camelot/anya-domain` (workspace) |

## Setup

```bash
# From monorepo root (02_FORGE/)
pnpm install

# Start Expo
cd packages/anya-lyte
npx expo start
```

## Scripts

| Script | Description |
|--------|-------------|
| `pnpm start` | Expo dev server |
| `pnpm build` | TypeScript check (`tsc --noEmit`) |
| `pnpm lint` | TypeScript check |
| `pnpm clean` | Remove dist |

## Dependencies

- **Workspace:** `@camelot/anya-domain` — shared domain models
- Tamagui, Drizzle ORM, expo-sqlite, Lucide React Native
