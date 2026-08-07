//! camelot-node-agent — local compute plane of the Kickbox voice slice.
//! See docs/adr/001-kickbox-camelot-boundaries.md for the trust model:
//! this process validates leases, it never issues them.

use camelot_node_agent::{backend, http, validate};
use std::sync::atomic::Ordering;

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

fn main() {
    install_signal_handlers();
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
