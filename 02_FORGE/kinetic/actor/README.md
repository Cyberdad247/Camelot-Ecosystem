# 🎭 Actor — WASM Actor Host

> **STATUS:** Active · Rust Library

Actor is the WASM actor host runtime for CAMELOT-OS. It provides the host-side infrastructure for executing WebAssembly guest components, targeting `wasm32-wasip1` and `wasm32-wasip2` (WASI Preview 2).

## Stack

| Layer | Technology |
|-------|-----------|
| Language | Rust (edition 2021) |
| WASM Runtime | Wasmtime |
| Error Handling | anyhow |
| Target | wasm32-wasip1, wasm32-wasip2 |

## Architecture

- **Host/guest separation:** This crate is the *host* side; guest components are separate WASM binaries
- **WASI Preview 2:** Supports the next-generation WASI interface for component model
- **Type-safe boundaries:** Integrates with `contracts/` crate for MsgPack serialization
