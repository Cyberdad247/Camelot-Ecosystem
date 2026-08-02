// Scaffold only — every member is wired up in the Phase 1 cut window.
// Per-item `#[allow(dead_code)]` keeps the lint usable for future regressions
// that are NOT scaffolding artefacts.

use crate::Result;
use serde_json::Value;

/// Scaffolded MCP client. The Phase 1 cut window adds transport wiring so `call` round-trips
/// to the server over the chosen transport. Until then, callers should treat `call` as a
/// documented no-op that returns `Value::Null` for any method.
#[allow(dead_code)]
pub struct Client {
    #[allow(dead_code)]
    pub server_endpoint: String,
}

#[allow(dead_code)]
impl Client {
    #[allow(dead_code)]
    pub fn new(server_endpoint: impl Into<String>) -> Self {
        Self {
            server_endpoint: server_endpoint.into(),
        }
    }

    #[allow(dead_code)]
    pub async fn call(&self, method: &str, params: Value) -> Result<Value> {
        // Scaffolded; full transport is wired in the Phase 1 cut window.
        let _ = (method, params);
        Ok(Value::Null)
    }
}
