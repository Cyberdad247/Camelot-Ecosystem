# ⚙️ Kinetic — High-Performance Rust Binaries

> **STATUS:** Active · Rust Workspace

The `kinetic/` directory contains Camelot-OS's high-performance Rust binaries and libraries — the "L2 Kinetic" execution layer. Each subdirectory is an independent Cargo crate.

## Crates

| Crate | Description | Status |
|-------|-------------|--------|
| [`cribo/`](cribo/) | Dead-code analyzer & tree-shaker | Active |
| [`rotel/`](rotel/) | High-performance telemetry collector | Active |
| [`hephaestus/`](hephaestus/) | WASM deterministic engineering runtime | Active |
| [`pmcp/`](pmcp/) | Protocol multiplexing control plane | Active |
| [`actor/`](actor/) | WASM actor host runtime | Active |
| [`contracts/`](contracts/) | MsgPack wire-format boundary structs | Active |
| [`omni_nexus_ide/`](omni_nexus_ide/) | IDE stub (pending forge_nexus.sh) | Stub |
| [`rustdesk-server/`](rustdesk-server/) | Vendored RustDesk remote access server | Vendored |

## Build

```bash
# Build all kinetic crates
cd 02_FORGE/kinetic
cargo build

# Build a specific crate
cargo build -p cribo
cargo build -p rotel

# Run tests
cargo test

# Lint
cargo clippy -- -D warnings
```

## Turborepo

Kinetic crates are wired into the monorepo via `cargo:build`, `cargo:test`, and `cargo:lint` tasks. See the root `turbo.json`.

```bash
# From 02_FORGE/
npx turbo run cargo:build --filter=@camelot/kinetic
npx turbo run cargo:test --filter=@camelot/kinetic
```
