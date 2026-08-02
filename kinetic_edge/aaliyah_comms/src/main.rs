//! Aaliyah communications WASM pill.
//!
//! This Preview-1 WASI artifact is intentionally side-effect free. It accepts a
//! compact command, emits a draft envelope, and leaves email dispatch to a
//! separate HITL-approved host capability.

use std::env;

const VERSION: &str = "v9000.95";

fn render_draft(intent: &str) -> String {
    format!(
        "{{\"pill\":\"aaliyah_comms\",\"version\":\"{}\",\"status\":\"pending_hitl_approval\",\"intent\":\"{}\",\"next\":\"approve_via_dashboard_before_dispatch\"}}",
        VERSION,
        escape_json(intent)
    )
}

fn escape_json(value: &str) -> String {
    value
        .chars()
        .flat_map(|ch| match ch {
            '"' => "\\\"".chars().collect::<Vec<_>>(),
            '\\' => "\\\\".chars().collect::<Vec<_>>(),
            '\n' => "\\n".chars().collect::<Vec<_>>(),
            '\r' => "\\r".chars().collect::<Vec<_>>(),
            '\t' => "\\t".chars().collect::<Vec<_>>(),
            _ => vec![ch],
        })
        .collect()
}

fn main() {
    let intent = env::args().skip(1).collect::<Vec<_>>().join(" ");
    let intent = if intent.trim().is_empty() {
        "draft welcome campaign for new contacts"
    } else {
        intent.trim()
    };

    println!("{}", render_draft(intent));
}
