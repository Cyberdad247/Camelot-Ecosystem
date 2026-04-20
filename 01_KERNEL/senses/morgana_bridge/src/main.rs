// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
use axum::{
    extract::State,
    http::StatusCode,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tower_http::cors::CorsLayer;
use tokio::time::{sleep, Duration};

#[derive(Debug, Deserialize, Serialize, Clone)]
struct VideneptusPhase {
    phase: String,
    temperature: f32,
    instruction: String,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
struct VideneptusConfig {
    #[serde(default)]
    trigger_threshold: f32,
    #[serde(default)]
    execution_loop: Vec<VideneptusPhase>,
}

#[derive(Debug, Deserialize)]
struct DispatchRequest {
    intent: String,
    #[serde(default)]
    target: String,
}

#[derive(Debug, Serialize)]
struct DispatchResponse {
    response: String,
    source: String,
    cost: String,
}

#[derive(Debug, Deserialize)]
struct PulseRequest {
    ram_usage: Option<f32>,
    cpu_load: Option<f32>,
}

struct AppState {
    config: VideneptusConfig,
}

const SALTARE_GATEWAY: &str = "http://localhost:8085";

#[tokio::main]
async fn main() {
    let config_path = r"C:\Users\vizio\CAMELOT_OS\01_KERNEL\config\videneptus_config.json";
    let config_data = std::fs::read_to_string(config_path).unwrap_or_else(|_| "{}".to_string());
    let config: VideneptusConfig = serde_json::from_str(&config_data).unwrap_or(VideneptusConfig {
        trigger_threshold: 0.8,
        execution_loop: vec![],
    });

    let state = Arc::new(AppState { config });

    let app = Router::new()
        .route("/ping", get(ping))
        .route("/pulse", post(receive_pulse))
        .route("/agent/dispatch", post(dispatch))
        .layer(CorsLayer::permissive())
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8001").await.unwrap();
    println!("🌑 MORGANA BRIDGE (RUST) ONLINE (v0.1.0 Kinetic Sovereign). Listening on Port 8001...");
    axum::serve(listener, app).await.unwrap();
}

async fn ping() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "status": "alive",
        "node": "MORGANA_BRIDGE_RUST_v0.1.0"
    }))
}

async fn receive_pulse(Json(payload): Json<PulseRequest>) -> Json<serde_json::Value> {
    println!("🫀 PULSE: Received Telemetry -> RAM: {:?} | CPU: {:?}%", payload.ram_usage, payload.cpu_load);
    Json(serde_json::json!({
        "status": "ACKNOWLEDGED",
        "timestamp": std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs()
    }))
}

async fn dispatch(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<DispatchRequest>,
) -> (StatusCode, Json<DispatchResponse>) {
    let query_lower = payload.intent.to_lowercase();
    let target_file = payload.target.clone();

    println!("🌑 MORGANA ROUTER (RUST): Processing Intent: [{}]", payload.intent);

    // 1. KINETIC ROUTING
    if query_lower.contains("audit") && query_lower.contains("trivy") {
        let target = if target_file.is_empty() {
            r"C:\Users\vizio\CAMELOT_OS\01_KERNEL"
        } else {
            &target_file
        };
        let output = execute_kinetic_tool("trivy", target).await;
        return (StatusCode::OK, Json(DispatchResponse {
            response: format!("🛡️ SENTINEL (Via Saltare): {}", output),
            source: "KINETIC_GATEWAY".to_string(),
            cost: "0.00".to_string(),
        }));
    }

    if query_lower.contains("fix") && query_lower.contains("biome") {
        let target = if target_file.is_empty() {
            r"C:\Users\vizio\CAMELOT_OS\02_FORGE\PORTAL_CORE\src\main.tsx"
        } else {
            &target_file
        };
        let output = execute_kinetic_tool("biome", target).await;
        return (StatusCode::OK, Json(DispatchResponse {
            response: format!("🧹 SQUIRE (Via Saltare): {}", output),
            source: "KINETIC_GATEWAY".to_string(),
            cost: "0.00".to_string(),
        }));
    }

    if query_lower.contains("remote") || query_lower.contains("rustdesk") {
        let output = execute_kinetic_tool("rustdesk", "START_SESSION").await;
        return (StatusCode::OK, Json(DispatchResponse {
            response: format!("📱 ANYA (Remote): {}", output),
            source: "KINETIC_GATEWAY".to_string(),
            cost: "0.00".to_string(),
        }));
    }

    // 2. COMPLEXITY ROUTING (VIDENEPTUS LaC)
    let complexity_score = if query_lower.contains("architect") || query_lower.contains("design") {
        0.9
    } else {
        0.2
    };

    if complexity_score > state.config.trigger_threshold {
        let result = execute_lac_protocol(&state.config).await;
        // In a real app, we'd save to UKG here
        return (StatusCode::OK, Json(DispatchResponse {
            response: format!("🧙‍♂️ MERLIN (LaC): {}", result),
            source: "CLOUD".to_string(),
            cost: "0.12".to_string(),
        }));
    }

    // 3. OTHER ROUTING
    if query_lower.contains("research") || query_lower.contains("scrape") {
        return (StatusCode::OK, Json(DispatchResponse {
            response: format!("🧙‍♂️ MERLIN (Sky): Authorized Crusade for '{}'. [Modal A100]", payload.intent),
            source: "CLOUD".to_string(),
            cost: "0.04".to_string(),
        }));
    }

    if query_lower.contains("key") || query_lower.contains("password") {
        return (StatusCode::OK, Json(DispatchResponse {
            response: "🔒 MORGANA (Vault): Accessing Secure Storage.".to_string(),
            source: "LOCAL".to_string(),
            cost: "0.00".to_string(),
        }));
    }

    // 4. DEFAULT CHAT
    let context_node = format!("UKG_NODE_{}_V1", payload.intent.to_uppercase());
    (StatusCode::OK, Json(DispatchResponse {
        response: format!("⚡ MORGANA (Local): Processing '{}' with context [{}].", payload.intent, context_node),
        source: "LOCAL".to_string(),
        cost: "0.00".to_string(),
    }))
}

async fn execute_kinetic_tool(tool_name: &str, target: &str) -> String {
    println!("🔧 KINETIC: Routing {} -> Saltare Gateway...", tool_name);
    let client = reqwest::Client::new();
    let body = serde_json::json!({
        "tool": tool_name,
        "args": { "target": target }
    });

    match client.post(format!("{}/mcp/execute", SALTARE_GATEWAY))
        .json(&body)
        .timeout(Duration::from_secs(30))
        .send()
        .await {
        Ok(resp) => {
            match resp.text().await {
                Ok(text) => text,
                Err(e) => format!("DECODE_ERROR: {}", e),
            }
        },
        Err(e) => format!("SALTARE_LINK_FAILED: {}", e),
    }
}

async fn execute_lac_protocol(config: &VideneptusConfig) -> String {
    println!("⚛️ VIDENEPTUS: High Entropy Task Detected. Engaging LaC Protocol...");
    let mut last_result = String::new();

    for phase in &config.execution_loop {
        println!("   >> PHASE: {} [T={}] | {}", phase.phase, phase.temperature, phase.instruction);
        // Simulate processing time
        sleep(Duration::from_millis(200)).await;
        last_result = format!("{}_RESULT", phase.phase);
    }

    format!("LaC OPTIMIZED OUTPUT: {} (Converged)", last_result)
}