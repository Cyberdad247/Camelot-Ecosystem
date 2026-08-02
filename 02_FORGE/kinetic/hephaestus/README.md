# 🔥 Hephaestus — Deterministic Engineering Runtime

> **STATUS:** Active · `v1.0.0` · Rust

Cartridge_Hephaestus is the deterministic WebAssembly engineering runtime for CAMELOT-OS. It executes WASM payloads inside a sandboxed Wasmtime environment with tree-sitter-based code parsing, SHA-256 content hashing, and optimized release builds (LTO, single codegen unit).

## Stack

| Layer | Technology |
|-------|-----------|
| Language | Rust (edition 2021) |
| WASM Runtime | Wasmtime 14 |
| Parsing | tree-sitter 0.20 |
| Serialization | Serde + serde_json |
| Hashing | SHA-2 (sha2 crate) |
| Time | Chrono |

## Install

```bash
cargo build -p hephaestus --release
```

## Architecture

- **Sandboxed Execution:** All WASM payloads run in isolated Wasmtime instances
- **AST Analysis:** tree-sitter parses source code for engineering tasks
- **Content Integrity:** SHA-256 hashing of all executed payloads
- **Release Profile:** LTO + single codegen unit for maximum performance

## Usage

```bash
hephaestus --payload ./task.wasm --manifest ./manifest.json
```
