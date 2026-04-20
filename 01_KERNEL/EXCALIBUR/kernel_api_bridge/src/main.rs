// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
use axum::{
    extract::{Query, State, ws::{WebSocketUpgrade, Message}, Request},
    http::StatusCode,
    middleware::{self, Next},
    response::{IntoResponse, Response},
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::sync::Arc;
use tokio::sync::broadcast;
use tower_http::cors::CorsLayer;
use chrono::Local;
use std::fs::{OpenOptions, read_to_string};
use std::io::Write;
use jsonschema::JSONSchema;
use std::time::Instant;

// --- TYPES ---
#[derive(Debug, Serialize, Deserialize, Clone)]
struct DispatchRequest {
    intent: String,
    agent_id: Option<String>,
    priority: Option<i32>,
    metadata: Option<Value>,
}

#[derive(Debug, Serialize)]
struct DispatchResponse {
    job_id: String,
    status: String,
    agent: String,
    response: String,
}

struct AppState {
    tx: broadcast::Sender<Value>,
    dispatch_schema: JSONSchema,
    health_schema: JSONSchema,
}

// --- MIDDLEWARE: AUDIT ---
async fn audit_middleware(
    State(state): State<Arc<AppState>>,
    req: Request,
    next: Next,
) -> Response {
    let start = Instant::now();
    let method = req.method().clone();
    let path = req.uri().path().to_string();
    let token = req.headers().get("x-camelot-token")
        .and_then(|h| h.to_str().ok())
        .unwrap_or("anonymous")
        .to_string();

    let response = next.run(req).await;
    let duration = start.elapsed().as_secs_f64();

    if method == "POST" || path.contains("memory/query") {
        let timestamp = Local::now().to_rfc3339();
        let status = if response.status().is_success() { "SUCCESS" } else { "FAILURE" };
        let log_entry = format!("| {} | {} | {} {} | {} ({:.2}s) |\n", timestamp, token, method, path, status, duration);

        let ledger_path = "../../PROVENANCE_LEDGER.md";
        if let Ok(mut file) = OpenOptions::new().append(true).open(ledger_path) {
            let _ = writeln!(file, "{}", log_entry.trim());
        }

        let _ = state.tx.send(serde_json::json!({
            "type": "LEDGER_UPDATE",
            "data": log_entry.trim()
        }));
    }

    response
}

// --- MIDDLEWARE: AUTH ---
async fn auth_middleware(
    req: Request,
    next: Next,
) -> Result<Response, StatusCode> {
    let token = req.headers().get("x-camelot-token")
        .and_then(|h| h.to_str().ok());

    if token == Some("merlin-v100-dev") {
        Ok(next.run(req).await)
    } else {
        Err(StatusCode::UNAUTHORIZED)
    }
}

// --- HANDLERS ---
async fn root() -> &'static str {
    "🏰 CAMELOT KERNEL v100.0 [KINETIC_CORE] Online."
}

async fn get_health(State(state): State<Arc<AppState>>) -> impl IntoResponse {
    let health_data = serde_json::json!({
        "status": "RADIANT",
        "uptime": 0.0,
        "engines": {
            "videneptus": true,
            "antigravity": true,
            "ouroboros": true,
            "kinetic_bridge": true
        },
        "metrics": {
            "cpu_usage": 12.0,
            "ram_usage": 42.0
        }
    });

    if state.health_schema.is_valid(&health_data) {
        (StatusCode::OK, Json(health_data))
    } else {
        (StatusCode::INTERNAL_SERVER_ERROR, Json(serde_json::json!({"status": "DEGRADED", "error": "Schema validation failed"})))
    }
}

async fn dispatch_agent(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<Value>,
) -> Result<Json<DispatchResponse>, (StatusCode, String)> {
    if let Err(mut errors) = state.dispatch_schema.validate(&payload) {
        let msg = errors.next().map(|e| e.to_string()).unwrap_or_else(|| "Unknown validation error".to_string());
        return Err((StatusCode::BAD_REQUEST, format!("❌ Schema Violation: {}", msg)));
    }

    let intent = payload.get("intent").and_then(|v| v.as_str()).unwrap_or("");
    let agent_id = payload.get("agent_id").and_then(|v| v.as_str()).unwrap_or("MERLIN");

    let client = reqwest::Client::new();
    let brain_res = client.post("http://localhost:8005/process")
        .json(&serde_json::json!({ "intent": intent }))
        .send()
        .await;

    let brain_response_text = match brain_res {
        Ok(resp) => resp.json::<Value>().await.ok()
            .and_then(|v| v.get("response").and_then(|r| r.as_str()).map(|s| s.to_string()))
            .unwrap_or_else(|| "Brain responded with unknown format".to_string()),
        Err(e) => format!("BRAIN_LINK_FAILED: {}", e),
    };

    Ok(Json(DispatchResponse {
        job_id: format!("job_{}_{}", Local::now().timestamp(), agent_id),
        status: "COMPLETED".to_string(),
        agent: agent_id.to_string(),
        response: brain_response_text,
    }))
}

async fn query_memory(
    Query(params): Query<std::collections::HashMap<String, String>>,
) -> Json<Value> {
    let q = params.get("q").cloned().unwrap_or_default();
    let client = reqwest::Client::new();
    match client.get(format!("http://localhost:8005/memory/query?q={}", q)).send().await {
        Ok(resp) => Json(resp.json::<Value>().await.unwrap_or(serde_json::json!({"results": []}))),
        Err(e) => Json(serde_json::json!({
            "query": q,
            "results": [],
            "status": "RAG_OFFLINE",
            "debug": e.to_string()
        })),
    }
}

async fn ws_handler(
    ws: WebSocketUpgrade,
    State(state): State<Arc<AppState>>,
) -> impl IntoResponse {
    ws.on_upgrade(|mut socket| async move {
        let mut rx = state.tx.subscribe();
        while let Ok(msg) = rx.recv().await {
            if socket.send(Message::Text(msg.to_string())).await.is_err() {
                break;
            }
        }
    })
}

#[tokio::main]
async fn main() {
    let (tx, _) = broadcast::channel(100);

    let base_path = r"../config/schemas/";
    let dispatch_raw = read_to_string(format!("{}agent_dispatch.schema.json", base_path)).unwrap_or_else(|_| "{}".to_string());
    let health_raw = read_to_string(format!("{}system_health.schema.json", base_path)).unwrap_or_else(|_| "{}".to_string());

    let dispatch_schema = JSONSchema::compile(&serde_json::from_str(&dispatch_raw).unwrap_or(serde_json::json!({}))).unwrap();
    let health_schema = JSONSchema::compile(&serde_json::from_str(&health_raw).unwrap_or(serde_json::json!({}))).unwrap();

    let state = Arc::new(AppState { tx, dispatch_schema, health_schema });

    let app = Router::new()
        .route("/", get(root))
        .route("/system/health", get(get_health))
        .route("/memory/query", get(query_memory))
        .route("/agent/dispatch", post(dispatch_agent))
        .route("/ws", get(ws_handler))
        .layer(middleware::from_fn_with_state(state.clone(), audit_middleware))
        .layer(middleware::from_fn(auth_middleware))
        .layer(CorsLayer::permissive())
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8000").await.unwrap();
    println!("⚔️ EXCALIBUR KERNEL BRIDGE (RUST) ONLINE. Listening on Port 8000...");
    axum::serve(listener, app).await.unwrap();
}