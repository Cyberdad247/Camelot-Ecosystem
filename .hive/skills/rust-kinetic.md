# SKILL BIBLE — Rust Kinetic Toolchain
# Knight: Lukas_Omega | Layer: L2_KINETIC | v400.1.0
# LOAD: KINETIC_STACK — instilled on any Rust/Go/binary task

## TITANIUM LAW #1 — KINETIC PURITY
Never write Python where a compiled Rust/Go binary exists. Violations block merge.

## LIVE BINARIES (bin/)
| Binary | Tech | Port | Status |
|---|---|---|---|
| camelot-mcp-edge.exe | Rust Axum 0.7 + Tokio | 3001 | LIVE |
| saltare.exe | Go MCP Gateway | 8085 | configured |
| cribo | Rust bundler | CLI | source-only |
| rotel | Rust OpenTelemetry | CLI | source-only |

## CONVENTIONS
- Stable toolchain only — no nightly features in production paths
- No `unwrap()` — use `?` operator or explicit match at boundaries
- Tokio for all async runtime — no blocking I/O inside async contexts
- Axum for HTTP/MCP servers (already wired in kinetic_edge)
- Serde + serde_json for all serialization
- tower-http for CORS and middleware
- `cargo clippy -- -D warnings` must pass before any commit
- `cargo check` before any PR — 0 errors mandatory

## CODE PATTERNS
```rust
// Correct async handler — non-blocking
async fn handle(State(state): State<AppState>) -> Result<Json<Response>, AppError> {
    let result = state.service.process().await?;
    Ok(Json(result))
}

// Correct error type — never panic in handlers
#[derive(Debug, thiserror::Error)]
pub enum AppError {
    #[error("not found: {0}")] NotFound(String),
    #[error("internal: {0}")] Internal(#[from] anyhow::Error),
}
```

## ANTI-PATTERNS (Sir Gideon will STING)
- Python scripts where `bin/` binary exists → KINETIC_PURITY violation → REZERO
- Exposing local ports to public internet → Split-Brain violation
- Blocking calls (`std::thread::sleep`, sync I/O) inside `async fn`
- `unsafe` blocks without justification comment
- Failing `cargo clippy`
- `unwrap()` or `expect()` in non-test code

## FORGE PATH
1. `cargo check` — structural validity
2. `cargo clippy -- -D warnings` — zero warnings
3. `cargo build --release` — output to `bin/`
4. Copy binary: `cp target/release/<name>.exe bin/`
5. Log to PROVENANCE_LEDGER: `[Omega_EVOLVE]` tag
