# ⚡ Anya Lyte

> **STATUS:** Active Development · `v1.0.6` · Expo SDK 50

Anya Lyte is the primary mobile interface for CAMELOT-OS — a React Native application built with Expo, Tamagui, and the Anya Domain shared library. Features voice interaction, secure storage, notifications, and gesture-driven navigation.

## Stack

| Layer | Technology |
|-------|-----------|
| Framework | Expo SDK 50, React Native 0.73 |
| Navigation | React Navigation (native stack) |
| UI System | Tamagui v2 + Lucide React Native |
| State / Domain | `@camelot/anya-domain` (workspace) |
| Media | expo-av (audio), expo-notifications |
| Security | expo-secure-store |
| Types | TypeScript 5.9 |

## Setup

```bash
# From monorepo root (02_FORGE/)
pnpm install

# Start the Expo dev server
cd apps/anya-lyte
npx expo start

# Platform targets
npx expo start --android
npx expo start --ios
```

## Scripts

| Script | Description |
|--------|-------------|
| `pnpm build` | `expo export` (production bundle; add `--platform ios\|android`) |
| `pnpm lint` | `tsc --noEmit` typecheck |
| `pnpm test` | Jest test runner |
| `pnpm clean` | Remove dist and .expo caches |

## Dependencies

- **Workspace:** `@camelot/anya-domain` — shared domain models and validation schemas (Zod)
- React Navigation, Tamagui, expo-av, expo-notifications, expo-secure-store
