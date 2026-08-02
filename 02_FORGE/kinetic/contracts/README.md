# 📦 Contracts — MsgPack Wire-Format Boundary Structs

> **STATUS:** Active · Rust Library

Contracts defines the MsgPack-encoded wire-format boundary structs for communication between the WASM actor host, the Ouroboros engine, and the control plane. Provides strongly-typed request/response envelopes with pack/unpack serialization.

## Stack

| Layer | Technology |
|-------|-----------|
| Language | Rust (edition 2021) |
| Serialization | Serde + rmp-serde (MsgPack) |

## Key Types

- `TriageRequestV1` — Intent triage request from the control plane
- `CartridgeSwitchRequestV1` — Cartridge hot-swap request
- `pack()` / `unpack()` — MsgPack serialization helpers

## Usage

```rust
use contracts::{TriageRequestV1, pack};

let req = TriageRequestV1 { /* ... */ };
let bytes = pack(&req)?;
```
