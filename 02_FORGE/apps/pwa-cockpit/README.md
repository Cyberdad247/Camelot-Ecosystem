# 🛡️ PWA Cockpit

> **STATUS:** Production · `v1.0.0` · Next.js 16

The PWA Cockpit is the sovereign control interface for CAMELOT-OS — a progressive web application with WebAuthn biometric authentication, 3D VRM avatar rendering (Three.js), Voice Worklet streaming, and cartridge-verified secure operations.

## Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16 (App Router) |
| 3D Rendering | Three.js 0.185, @pixiv/three-vrm |
| Computer Vision | @mediapipe/tasks-vision |
| Auth | WebAuthn (passkeys) via @simplewebauthn |
| Crypto | @noble/ed25519, @noble/hashes (cartridge verification) |
| Styling | Tailwind CSS v4 |
| Icons | Lucide React |

## Setup

```bash
# From monorepo root (02_FORGE/)
pnpm install

# Build voice worklet + icons + service worker, then dev
cd apps/pwa-cockpit
pnpm prebuild
pnpm dev          # → http://localhost:3005
```

## Scripts

| Script | Description |
|--------|-------------|
| `pnpm dev` | Next.js dev server on port 3005 |
| `pnpm build` | Production build |
| `pnpm prebuild` | Generate voice worklet, icons, service worker |
| `pnpm icons` | Generate PWA icon set |
| `pnpm voice-worklet` | Sync voice processing worklet |
| `pnpm service-worker` | Generate service worker |
| `pnpm test` | Node test runner (`tests/*.test.mjs`) |
| `pnpm typecheck` | TypeScript check (`tsc --noEmit`) |
| `pnpm verify` | Full CI check (SW + test + typecheck + build) |
| `pnpm host:install` | Install as Windows PWA host |
| `pnpm host:run` | Launch Windows PWA host |

## Architecture

- **Cartridge Platform:** Client-side cryptographic verification of `.cartridge` archives using Ed25519
- **Voice Pipeline:** Custom AudioWorklet for real-time voice processing
- **Auth Flow:** Passkey-based WebAuthn with server-side verification
- **3D Avatars:** VRM model loading and rendering for immersive agent presence

## Sub-READMEs

- [`public/models/README.md`](public/models/README.md) — 3D model assets
- [`native/desktop-bridge/README.md`](native/desktop-bridge/README.md) — Windows desktop bridge
