use regex::Regex;
use sha2::{Digest, Sha256};

// AEGIS SHIELD: PII Redaction & Telemetry Hashing
fn sanitize_and_hash(input: &str) -> (String, String) {
    let email_regex = Regex::new(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}").unwrap();
    let sanitized = email_regex.replace_all(input, "[REDACTED_BY_AEGIS]").into_owned();

    let mut hasher = Sha256::new();
    hasher.update(sanitized.as_bytes());
    let hash = format!("{:x}", hasher.finalize());

    (sanitized, hash)
}

// RL-CONDUCTOR: Dynamic Routing
struct Agent { id: &'static str, success_rate: f32, latency_ms: u32 }

fn route_task(agents: &[Agent]) -> &Agent {
    agents.iter().max_by(|a, b| {
        let score_a = a.success_rate / (a.latency_ms as f32 + 1.0);
        let score_b = b.success_rate / (b.latency_ms as f32 + 1.0);
        score_a.partial_cmp(&score_b).unwrap()
    }).unwrap()
}

fn main() {
    println!("[PULSE] Cosmic Ecosystem v1000.0 Test Harness Active");

    // 1. Test RL-Conductor Routing
    let swarm = vec![
        Agent { id: "NODE_01_S26", success_rate: 0.99, latency_ms: 12 },
        Agent { id: "NODE_02_CLOUD", success_rate: 0.95, latency_ms: 105 },
    ];

    let selected = route_task(&swarm);
    println!("[RL_CONDUCTOR] Task routed to optimal agent: {} (Latency: {}ms)", selected.id, selected.latency_ms);

    // 2. Test Aegis Shield Compliance
    let raw_intent = "Deploy scraping swarm targeting admin@targetcorp.com immediately.";
    let (clean_intent, telemetry_hash) = sanitize_and_hash(raw_intent);

    println!("[AEGIS_SHIELD] Raw Intent: {}", raw_intent);
    println!("[AEGIS_SHIELD] Sanitized: {}", clean_intent);
    println!("[AEGIS_SHIELD] Telemetry Hash: {}", telemetry_hash);
    println!("[STATUS] V1000.0 KINETIC TEST COMPLETE.");
}
