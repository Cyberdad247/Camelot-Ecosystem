# 🌌 PORTAL CORE — Sarda Engine

> **STATUS:** Active · `v1.0.1` · Vite + React 19

The PORTAL CORE (codenamed "Sarda Engine") is the main CAMELOT-OS portal interface — a Vite-powered React 19 application with Framer Motion animations, xterm.js terminal emulation, Zustand state management, and a React Router-driven multi-view layout.

## Stack

| Layer | Technology |
|-------|-----------|
| Build | Vite 6 |
| Framework | React 19.2 |
| Routing | React Router DOM 7 |
| State | Zustand 5 |
| Animation | Framer Motion 12 |
| Terminal | xterm.js 5 |
| Styling | Tailwind CSS v4 |
| Icons | Lucide React |
| Lint/Format | Biome |
| Scaffolding | Hygen |
| Testing | Bun test |

## Structure

```
PORTAL_CORE/
├── src/              # Application source
├── components/       # Shared React components
├── Anya_Dashboard/   # Anya-specific dashboard views
├── Modal/            # Modal cloud services
│   ├── kinetic_fortress.py
│   ├── rustdesk_server/
│   ├── excalibur-resonance/  # Quantum cinematic engine
│   ├── kinetic_fortress.py   # Kinetic fortress service
│   ├── tts_pipeline/
│   └── voice_pipeline/
├── public/           # Static assets
└── web/              # Web-specific assets
```

## Setup

```bash
# ⚠️ PORTAL_CORE is NOT in the pnpm workspace — `pnpm install` from
# 02_FORGE/ root will NOT install this project. Use npm directly below.
# From 02_FORGE/PORTAL_CORE/
cd PORTAL_CORE
npm install

# Dev server
npm run dev
```

## Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Vite dev server |
| `npm run build` | Production build |
| `npm run lint` | Biome check |
| `npm run test` | Bun test runner |
| `npm run generate` | Hygen component generator |
