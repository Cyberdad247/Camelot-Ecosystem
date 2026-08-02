# 🕹️ Holotable — CAMELOT-OS Dashboard

> **STATUS:** Active · `v0.1.0` · Next.js 16

Holotable is the strategic command dashboard for CAMELOT-OS — a Next.js application featuring an interactive ReactFlow node graph (Oracle Canvas), a Genesis Designer for agent persona creation, a Knight roster viewer, a provenance ledger explorer, and a development hub. Twin-mode interface: Oracle Simulation and Genesis Forge.

## Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16 (App Router) |
| Graph | ReactFlow 11 |
| Styling | Tailwind CSS v4 |
| Icons | Lucide React |
| Compiler | babel-plugin-react-compiler |

## Components

| Component | Description |
|-----------|-------------|
| **Oracle Canvas** | Interactive ReactFlow node graph for system topology |
| **Genesis Designer** | Agent persona and workflow designer |
| **The Roster** | Active Knight listing and status |
| **The Ledger** | Provenance and event log viewer |
| **DevHub** | Development tools and quick actions |

## Setup

```bash
# From monorepo root (02_FORGE/)
pnpm install

cd holotable
pnpm dev
```

## Scripts

| Script | Description |
|--------|-------------|
| `pnpm dev` | Next.js dev server |
| `pnpm build` | Production build |
| `pnpm lint` | ESLint |
