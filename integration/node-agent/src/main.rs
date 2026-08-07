//! camelot-node-agent — local compute plane of the Kickbox voice slice.
//! See docs/adr/001-kickbox-camelot-boundaries.md for the trust model:
//! this process validates leases, it never issues them.

use camelot_node_agent::{backend, http, validate};

fn main() {
    let addr = std::env::var("NODE_AGENT_ADDR").unwrap_or_else(|_| "0.0.0.0:8789".into());
    let agent = http::Agent {
        backend: backend::select_backend(),
        validator: validate::StrictValidator::from_env(),
    };
    if let Err(e) = http::serve(&addr, agent) {
        eprintln!("fatal: {e}");
        std::process::exit(1);
    }
}
