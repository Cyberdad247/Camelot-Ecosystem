//! camelot-node-agent — local compute plane of the Kickbox voice slice.
//! See docs/adr/001-kickbox-camelot-boundaries.md for the trust model:
//! this process validates leases, it never issues them.
//!
//! Phase 4A: when ENABLE_TAILSCALE_MESH=true and CAMELOT_NODE_ID is set, the
//! agent also enrols with the gateway and heartbeats. Enrolment grants it
//! nothing — the gateway decides the trust band, and every job still carries
//! a lease this agent re-validates from scratch.

use camelot_node_agent::mesh::{self, MeshConfig, NodeCapability};
use camelot_node_agent::{backend, compute, http, validate};
use std::sync::atomic::Ordering;

const AGENT_VERSION: &str = "0.2.0";

extern "C" fn on_signal(_sig: libc::c_int) {
    // Async-signal-safe: only flip the atomic; the accept loop does the rest.
    http::SHUTDOWN.store(true, Ordering::SeqCst);
}

fn install_signal_handlers() {
    unsafe {
        libc::signal(libc::SIGINT, on_signal as libc::sighandler_t);
        libc::signal(libc::SIGTERM, on_signal as libc::sighandler_t);
    }
}

/// What this agent offers the mesh. Audio features are read-only: they
/// compute over a buffer and change nothing, so a limited-trust node may
/// still serve them.
fn capabilities() -> Vec<NodeCapability> {
    vec![NodeCapability {
        name: compute::CAPABILITY_AUDIO_FEATURES.to_string(),
        read_only: true,
    }]
}

fn main() {
    install_signal_handlers();
    let addr = std::env::var("NODE_AGENT_ADDR").unwrap_or_else(|_| "0.0.0.0:8789".into());

    let mesh_cfg = MeshConfig::from_env(&addr);
    if mesh_cfg.enabled {
        let status = mesh::observe_tailscale();
        eprintln!(
            "mesh: enabled as node {} (tenant {}); tailscale: {}",
            mesh_cfg.node_id, mesh_cfg.tenant_id, status.detail
        );
        mesh::spawn_heartbeat_loop(mesh_cfg.clone(), capabilities(), AGENT_VERSION.into());
    } else {
        eprintln!("mesh: disabled (local-only operation)");
    }

    let agent = http::Agent::new(backend::select_backend(), validate::StrictValidator::from_env());
    if let Err(e) = http::serve(&addr, agent) {
        eprintln!("fatal: {e}");
        std::process::exit(1);
    }
}
