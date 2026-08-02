# 02_FORGE: The Kinetic Workshop (L2)

[![02_FORGE CI](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml/badge.svg)](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml)

## 🛡️ CI STATUS

| Workspace Checks | Subsystem Builds |
|------------------|------------------|
| [![Forge Lint](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml/badge.svg?job=Forge%20Lint)](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml) | [![Cartridge Tests](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml/badge.svg?job=Cartridge%20Tests)](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml) |
| [![Forge Typecheck](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml/badge.svg?job=Forge%20Typecheck)](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml) | [![Pocket Squire Build](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml/badge.svg?job=Pocket%20Squire%20Build)](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml) |
| [![Forge Test](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml/badge.svg?job=Forge%20Test)](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml) | [![Kinetic Build & Test](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml/badge.svg?job=Kinetic%20Build%20%26%20Test)](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml) |
| | [![Holotable Build](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml/badge.svg?job=Holotable%20Build)](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml) |
| | [![PORTAL_CORE Build](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml/badge.svg?job=PORTAL_CORE%20Build)](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml) |
| | [![Invoice Generator Build](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml/badge.svg?job=Invoice%20Generator%20Build)](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml) |
| | [![I2L Phygital Build](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml/badge.svg?job=I2L%20Phygital%20Build)](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/forge-ci.yml) |

## ⚒️ OVERVIEW

The **Forge Realm** contains the executable tools, applications, and binaries of CAMELOT-OS. It is the "Hands" (Lukas) and "Builders" (Kai) — the layer where neural intent from the Kernel (`01_KERNEL`) is transmuted into executable code, user interfaces, and operational tooling.

## 📂 STRUCTURE

| Directory | Purpose | Status |
|-----------|---------|--------|
| [`apps/`](apps/) | User-facing applications (4 apps) | Active |
| [`packages/`](packages/) | Shared libraries (4 packages) | Active |
| [`kinetic/`](kinetic/) | High-performance Rust binaries (8 crates) | Active |
| [`kinetic_sovereign/`](kinetic_sovereign/) | Go omni-modal TUI | Active |
| [`cartridge/`](cartridge/) | Cryptographic packaging & verification system | Production |
| [`cartridges/`](cartridges/) | Cartridge distribution packages | Active |
| [`holotable/`](holotable/) | Next.js strategic command dashboard | Active |
| [`PORTAL_CORE/`](PORTAL_CORE/) | Vite/React Sarda Engine portal | Active |
| [`excalibur-dev/`](excalibur-dev/) | EXCALIBUR v1000 Rust workspace | Research |
| [`dyad-apps/`](dyad-apps/) | Paired application projects (Happy Owl, Invoice Gen) | Active |
| [`assimilation/`](assimilation/) | Voice Assistant Omega (Python) | Development |
| [`hive_api/`](hive_api/) | Agno agent orchestration core | Active |
| [`hooks/`](hooks/) | Shared React hooks | Active |
| [`tools/`](tools/) | Developer utilities (Pi coding agent) | Active |
| [`vizion-telemetry/`](vizion-telemetry/) | System telemetry binary (Go) | Active |
| [`_templates/`](_templates/) | Project scaffolding templates | Meta |
| [`KINETIC_ARMORY/`](KINETIC_ARMORY/) | Vendored third-party tools (Goose, LiveKit, SpacetimeDB) | Vendored |
| [`scrcpy/`](scrcpy/) | Vendored scrcpy (Android screen mirroring) | Vendored |

## 🚀 APPS

| App | Path | Stack | Description |
|-----|------|-------|-------------|
| **PWA Cockpit** | [`apps/pwa-cockpit/`](apps/pwa-cockpit/) | Next.js 16 | Sovereign control PWA with WebAuthn, 3D avatars |
| **Anya Lyte** | [`apps/anya-lyte/`](apps/anya-lyte/) | Expo SDK 50 | Mobile voice interface |
| **Lux11 Router** | [`apps/lux11/`](apps/lux11/) | Vite + Express | Voice, persona, and input compiler layer (Anya_Ω) |
| **Omni-Eye Dashboard** | [`apps/omni-eye-dashboard/`](apps/omni-eye-dashboard/) | Next.js 16 | Monitoring and visualization dashboard |
| **HeadArtworks** | [`apps/headartworks/`](apps/headartworks/) | Shopify Liquid | E-commerce storefront theme |
| **I2L Phygital** | [`apps/i2l-phygital/`](apps/i2l-phygital/) | Web App | Physical-digital bridge application |

## 🖥️ DASHBOARDS & PORTALS

| Project | Path | Stack | Description |
|---------|------|-------|-------------|
| **Holotable** | [`holotable/`](holotable/) | Next.js 16 | Strategic command dashboard with ReactFlow |
| **PORTAL CORE** | [`PORTAL_CORE/`](PORTAL_CORE/) | Vite + React 19 | Sarda Engine portal with xterm.js (⚠️ separate npm install, not in pnpm workspace) |

## 📦 PACKAGES

| Package | Path | Description |
|---------|------|-------------|
| **Anya Domain** | [`packages/anya-domain/`](packages/anya-domain/) | Shared Zod domain models (workspace: `@camelot/anya-domain`) |
| **Anya Lyte Pkg** | [`packages/anya-lyte/`](packages/anya-lyte/) | Shared Expo mobile components |
| **Pocket Squire** | [`packages/pocket-squire/`](packages/pocket-squire/) | PWA component library with kernel bridge |
| **Voice-First Runtime** | [`packages/voice-first-runtime/`](packages/voice-first-runtime/) | Voice interaction runtime types |

## ⚙️ KINETIC RUST

| Crate | Path | Description |
|-------|------|-------------|
| **Cribo** | [`kinetic/cribo/`](kinetic/cribo/) | Dead-code analyzer & tree-shaker |
| **Rotel** | [`kinetic/rotel/`](kinetic/rotel/) | High-performance telemetry collector |
| **Hephaestus** | [`kinetic/hephaestus/`](kinetic/hephaestus/) | WASM deterministic engineering runtime |
| **PMCP** | [`kinetic/pmcp/`](kinetic/pmcp/) | Protocol multiplexing control plane |
| **Actor** | [`kinetic/actor/`](kinetic/actor/) | WASM actor host runtime |
| **Contracts** | [`kinetic/contracts/`](kinetic/contracts/) | MsgPack wire-format boundary structs |
| **Omni Nexus IDE** | [`kinetic/omni_nexus_ide/`](kinetic/omni_nexus_ide/) | IDE stub |

## 🏗️ BUILD COMMANDS

```bash
# Monorepo — Turborepo orchestrated (covers apps/ and packages/ workspaces)
pnpm install        # Install all workspace dependencies
pnpm build          # Build all JS/TS packages (topological order)
pnpm dev            # Dev servers (persistent)
pnpm lint           # Lint all packages
pnpm test           # Test all packages
pnpm typecheck      # Typecheck all packages

# Projects outside the pnpm workspace — install separately
cd PORTAL_CORE && npm install
cd dyad-apps/invoice-generator && npm install

# Rust crates
npx turbo run cargo:build --filter=@camelot/kinetic
cargo build -p cribo -p rotel -p hephaestus

# Go
npx turbo run go:build --filter=@camelot/kinetic-sovereign

# Cartridge
python -m cartridge.cartridge_cli verify <archive>
```

## 🔑 KEY ARCHITECTURE

- **L2 (Lukas Kinetic):** Rust binaries in `kinetic/` — execution, telemetry, WASM
- **L7 (Anya Ethereal):** TypeScript apps in `apps/` — voice, UI, dashboards
- **Cartridge Trust:** Ed25519 cryptographic verification chain for all deployable artifacts
- **Bifrost Bridge:** RustDesk + Tailscale encrypted P2P remote access
- **Turborepo:** Monorepo build orchestration with caching and parallel execution

## ☁️ TURBOREPO REMOTE CACHE

The forge-ci.yml workflow uses Vercel Remote Cache to share Turborepo
cache artifacts across CI runs. Setup steps:

```bash
# 1. Install the Vercel CLI (one-time)
npm i -g vercel

# 2. Authenticate Turborepo with your Vercel account
cd 02_FORGE
npx turbo login          # opens browser → sign in to Vercel

# 3. Link this monorepo to your Vercel team
npx turbo link           # creates .turbo/config.json (gitignored)
```

**GitHub Secrets required** (add in Settings → Secrets and variables → Actions):

| Secret | Where to get it |
|--------|----------------|
| `TURBO_TEAM` | Your Vercel team slug (visible after `turbo link`, or at vercel.com/account) |
| `TURBO_TOKEN` | Create a token at vercel.com/account/tokens with "Turbo" scope |

Once secrets are set, `turbo run lint` and `turbo run build` in CI will
hit the remote cache. A cache hit skips the task entirely — a lint job
that took 30s on first run takes <1s on subsequent runs with no source changes.
