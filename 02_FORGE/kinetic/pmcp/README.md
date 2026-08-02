# pmcp — Pure-Rust MCP bindings (Phase 1 additive scaffold)

> **Status**: additive. The Phase 1 cut window for HiveIDE_Apex_v1000 is held
> under HUMAN_GATE per `control_plane.soul_oversight.pre_execute`.
> No existing Node.js MCP surface is replaced until `CAMELOT_DASHBOARD_OPERATOR_TOKEN`
> is set and a printed `[y/N]` confirm is signed.

## What this crate is

A pure-Rust implementation of the Model Context Protocol (MCP) envelope —
JSON-RPC 2.0 framing, tool registration, transport trait, and a stdio scaffold.
This is the **additive** replacement target for the Node.js MCP surface that
`02_FORGE/cartridge/rustclaw/src/main.rs` currently spawns via `camelot-mcp-edge.exe`.

## What this crate is NOT yet

- It does **not** unbind `camelot-mcp-edge.exe`. The actual cut happens in a
  separate user action with operator token + `git revert <cut-sha>` rollback path.
- TCP and Unix transports are wired at Phase 1 cut window; today only stdio works.
- See `03_VAULT/runtime_state/node_mcp_cutlist.json` for the inventory.

## Build

```sh
$ cargo build -p pmcp
$ cargo test -p pmcp
```

## Run (scaffold)

```sh
$ cargo run -p pmcp --bin pmcp-server
[pmcp-server] scaffolded at port 3002 — stdio ready; tcp/unix pending Phase 1 cut
[pmcp-server] registered tools: ["hello_world"]
```

## Conformance to scope review

See `docs/architecture/scope-review-cybertron-ascension-2026-06-25.md` for
the Iron Gate v2 scope review governing Phase 1.
