//! Phase 1 server entry point.
//!
//! Reads `CAMELOT_PMCP_PORT` (default `3002`), initializes the MCP server,
//! registers the `hello_world` tool, and (in the Phase 1 cut window)
//! installs the chosen transport. This binary is intentionally additive —
//! no existing Node.js MCP is unbound yet. The actual destructive cut is
//! held under HUMAN_GATE in `soul_oversight.pre_execute` and requires
//! `CAMELOT_DASHBOARD_OPERATOR_TOKEN`.

use pmcp::server::Server;

fn main() {
    let port: u16 = std::env::var("CAMELOT_PMCP_PORT")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(3002);

    let mut server = Server::new("pmcp-server", "0.1.0");
    server.register_tool("hello_world", |params| {
        Ok(serde_json::json!({
            "hello": "camelot",
            "params": params,
        }))
    });

    eprintln!(
        "[pmcp-server] scaffolded at port {port} — stdio ready; tcp/unix pending Phase 1 cut"
    );
    eprintln!("[pmcp-server] registered tools: {:?}", server.list_tools());

    // Phase 1 cut window replaces this with a real transport loop.
}
