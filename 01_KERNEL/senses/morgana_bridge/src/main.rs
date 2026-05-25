// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS - CONFIDENTIAL AND PROPRIETARY
use axum::{
    extract::{
        ConnectInfo, Query, State,
        ws::{Message, WebSocketUpgrade},
    },
    http::{header, HeaderMap, Method, StatusCode},
    middleware::{self, Next},
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::net::{IpAddr, Ipv4Addr, SocketAddr};
use std::sync::Arc;
use std::time::SystemTime;
use tokio::sync::broadcast;
use tokio::time::{sleep, timeout, Duration};
use tower_http::cors::{Any, CorsLayer};

const TAILNET_CGNAT: Ipv4Addr = Ipv4Addr::new(100, 64, 0, 0);
const DEFAULT_TRUSTED_TAILNET_OWNERS: &str = "Cyberdad247@github,Cyberdad247@";

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
    #[serde(default)]
    cartridge: String,
    #[serde(default)]
    preferred_knight: String,
    #[serde(default)]
    execution_target: String,
}

#[derive(Debug, Serialize)]
struct DispatchResponse {
    response: String,
    source: String,
    cost: String,
}

#[derive(Debug, Serialize, Clone)]
struct StreamEvent {
    event: String,
    intent: String,
    source: String,
    detail: String,
    timestamp_ms: u128,
}

#[derive(Debug, Deserialize)]
struct PulseRequest {
    ram_usage: Option<f32>,
    cpu_load: Option<f32>,
}

#[derive(Debug, Serialize)]
struct BifrostStatus {
    gate: String,
    owner: String,
    current_user: String,
    hostname: String,
    token_present: bool,
    bridge: String,
    dispatch_url: String,
    websocket_url: String,
    cartridges: Vec<String>,
    cognitive_helm: String,
    bridge_knight: String,
}

#[derive(Debug, Serialize)]
struct OpenVikingMap {
    name: String,
    path: String,
    bytes: u64,
    modified_ms: u128,
    line_count: usize,
    section_count: usize,
    directory_markers: usize,
    preview: String,
    content: String,
}

struct AppState {
    config: VideneptusConfig,
    gateway: GatewayConfig,
    client: reqwest::Client,
    tx: broadcast::Sender<StreamEvent>,
}

#[derive(Debug, Clone)]
struct GatewayConfig {
    bind_addr: SocketAddr,
    public_http_url: String,
    public_ws_url: String,
    owner: String,
    gateway_token: Option<String>,
    trusted_tailnet_owners: Vec<String>,
    tailscale_whois_timeout_ms: u64,
    allow_loopback_owner_without_token: bool,
    saltare_gateway_url: String,
    modal_cloud_brain_url: Option<String>,
    gradio_url: Option<String>,
    camelot_root: String,
    openviking_map_path: String,
    cors_origin: Option<String>,
}

fn now_ms() -> u128 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis()
}

fn empty_as<'a>(value: &'a str, fallback: &'a str) -> &'a str {
    if value.trim().is_empty() {
        fallback
    } else {
        value
    }
}

fn env_or(key: &str, fallback: &str) -> String {
    std::env::var(key)
        .ok()
        .map(|value| value.trim().to_string())
        .filter(|value| !value.is_empty())
        .unwrap_or_else(|| fallback.to_string())
}

fn env_opt(key: &str) -> Option<String> {
    std::env::var(key)
        .ok()
        .map(|value| value.trim().to_string())
        .filter(|value| !value.is_empty())
}

fn env_flag(key: &str, default: bool) -> bool {
    std::env::var(key)
        .ok()
        .map(|value| value.trim().to_ascii_lowercase())
        .map(|value| matches!(value.as_str(), "1" | "true" | "yes" | "on"))
        .unwrap_or(default)
}

fn env_csv(key: &str, default: &str) -> Vec<String> {
    let raw = std::env::var(key).unwrap_or_else(|_| default.to_string());
    let parsed: Vec<String> = raw
        .split(',')
        .map(str::trim)
        .filter(|value| !value.is_empty())
        .map(ToString::to_string)
        .collect();
    if parsed.is_empty() {
        default
            .split(',')
            .map(str::trim)
            .filter(|value| !value.is_empty())
            .map(ToString::to_string)
            .collect()
    } else {
        parsed
    }
}

fn env_u64(key: &str, default: u64) -> u64 {
    std::env::var(key)
        .ok()
        .and_then(|value| value.trim().parse::<u64>().ok())
        .unwrap_or(default)
}

fn load_gateway_config() -> GatewayConfig {
    let bind_raw = env_or("BIFROST_BIND_ADDR", "0.0.0.0:8001");
    let bind_addr = bind_raw
        .parse::<SocketAddr>()
        .unwrap_or_else(|_| "0.0.0.0:8001".parse().expect("valid default bind address"));
    let public_http_url = env_or("BIFROST_PUBLIC_HTTP_URL", "http://127.0.0.1:8001");
    let public_ws_url = env_or("BIFROST_PUBLIC_WS_URL", "ws://127.0.0.1:8001/ws");
    let camelot_root = env_or("CAMELOT_ROOT", r"C:\Users\vizio\CAMELOT_OS");
    let openviking_map_path = env_or(
        "OPENVIKING_MAP_PATH",
        &format!(r"{}\entiremap.md", camelot_root),
    );

    GatewayConfig {
        bind_addr,
        public_http_url,
        public_ws_url,
        owner: env_or("CAMELOT_OWNER", "vizio"),
        gateway_token: env_opt("CAMELOT_GATEWAY_TOKEN"),
        trusted_tailnet_owners: env_csv(
            "BIFROST_TRUSTED_TAILNET_OWNERS",
            DEFAULT_TRUSTED_TAILNET_OWNERS,
        ),
        tailscale_whois_timeout_ms: env_u64("BIFROST_TAILSCALE_WHOIS_TIMEOUT_MS", 2500),
        allow_loopback_owner_without_token: env_flag(
            "BIFROST_ALLOW_LOOPBACK_OWNER_WITHOUT_TOKEN",
            false,
        ),
        saltare_gateway_url: env_or("SALTARE_GATEWAY_URL", "http://localhost:8085"),
        modal_cloud_brain_url: env_opt("MODAL_CLOUD_BRAIN_URL"),
        gradio_url: env_opt("GRADIO_URL"),
        camelot_root,
        openviking_map_path,
        cors_origin: env_opt("BIFROST_CORS_ORIGIN"),
    }
}

/// Constant-time byte comparison to prevent timing attacks.
fn ct_eq(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }
    let mut diff: u8 = 0;
    for (x, y) in a.iter().zip(b.iter()) {
        diff |= x ^ y;
    }
    diff == 0
}

fn is_tailnet(ip: IpAddr) -> bool {
    match ip {
        IpAddr::V4(v4) => {
            let octets = v4.octets();
            let base = TAILNET_CGNAT.octets();
            // 100.64.0.0/10 check
            octets[0] == base[0] && (octets[1] & 0xC0) == (base[1] & 0xC0)
        }
        IpAddr::V6(_) => false,
    }
}

async fn tailscale_whois(ip: IpAddr, timeout_ms: u64) -> Option<String> {
    let out = timeout(
        Duration::from_millis(timeout_ms),
        tokio::process::Command::new("tailscale")
            .arg("whois")
            .arg(ip.to_string())
            .output(),
    )
    .await
    .ok()?
    .ok()?;

    if !out.status.success() {
        return None;
    }
    let text = String::from_utf8_lossy(&out.stdout);
    for line in text.lines() {
        let s = line.trim();
        if let Some(rest) = s.strip_prefix("Name:") {
            let owner = rest.trim().to_string();
            if owner.contains('@') {
                return Some(owner);
            }
        }
    }
    None
}

fn extract_token(headers: &HeaderMap) -> Option<&str> {
    headers
        .get(header::AUTHORIZATION)
        .and_then(|value| value.to_str().ok())
        .and_then(|value| value.strip_prefix("Bearer "))
        .or_else(|| {
            headers
                .get("x-camelot-token")
                .and_then(|value| value.to_str().ok())
        })
        .or_else(|| {
            headers
                .get("x-bifrost-token")
                .and_then(|value| value.to_str().ok())
        })
}

fn current_username() -> String {
    std::env::var("USERNAME")
        .or_else(|_| std::env::var("USER"))
        .unwrap_or_else(|_| "unknown".to_string())
}

fn owner_matches(owner: &str, current: &str) -> bool {
    owner.eq_ignore_ascii_case(current)
}

enum AuthFailure {
    Unauthorized(String),
    Forbidden(String),
}

async fn authorized(
    ip: IpAddr,
    headers: &HeaderMap,
    query_token: Option<&str>,
    gateway: &GatewayConfig,
) -> Result<(), AuthFailure> {
    let Some(expected) = gateway.gateway_token.as_deref() else {
        return Ok(());
    };

    // WebSocket loop-out: query param allowed for browser compatibility
    if let Some(token) = query_token {
        if ct_eq(token.as_bytes(), expected.as_bytes()) {
            return Ok(());
        }
        return Err(AuthFailure::Unauthorized("invalid websocket token".to_string()));
    }

    let presented = extract_token(headers);

    // Rule 1: Local Loopback
    if ip.is_loopback() {
        if let Some(token) = presented {
            if ct_eq(token.as_bytes(), expected.as_bytes()) {
                return Ok(());
            }
            return Err(AuthFailure::Unauthorized(
                "invalid or missing bifrost token".to_string(),
            ));
        }

        if gateway.allow_loopback_owner_without_token {
            let current_user = current_username();
            if owner_matches(&gateway.owner, &current_user) {
                return Ok(());
            }
            return Err(AuthFailure::Forbidden(format!(
                "local user {} is not configured owner {}",
                current_user, gateway.owner
            )));
        }

        return Err(AuthFailure::Unauthorized(
            "invalid or missing bifrost token".to_string(),
        ));
    }

    // Rule 2: Tailnet Peer + Token
    if is_tailnet(ip) {
        if presented.is_none() || !ct_eq(presented.unwrap().as_bytes(), expected.as_bytes()) {
            return Err(AuthFailure::Unauthorized(
                "invalid or missing bifrost token".to_string(),
            ));
        }

        match tailscale_whois(ip, gateway.tailscale_whois_timeout_ms).await {
            Some(owner) if gateway.trusted_tailnet_owners.iter().any(|trusted| trusted == &owner) => Ok(()),
            Some(owner) => Err(AuthFailure::Forbidden(format!(
                "tailnet peer owner {} not trusted",
                owner
            ))),
            None => Err(AuthFailure::Forbidden("tailscale whois failed".to_string())),
        }
    } else {
        Err(AuthFailure::Forbidden(format!(
            "origin {} is not on the rainbow bridge",
            ip
        )))
    }
}

async fn require_gateway_auth(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    headers: HeaderMap,
    request: axum::extract::Request,
    next: Next,
) -> impl IntoResponse {
    match authorized(addr.ip(), &headers, None, &state.gateway).await {
        Ok(()) => next.run(request).await,
        Err(AuthFailure::Unauthorized(reason)) => (
            StatusCode::UNAUTHORIZED,
            Json(serde_json::json!({ "error": "unauthorized", "detail": reason })),
        )
            .into_response(),
        Err(AuthFailure::Forbidden(reason)) => (
            StatusCode::FORBIDDEN,
            Json(serde_json::json!({ 
                "error": "Bifrost gate closed",
                "detail": reason 
            })),
        )
            .into_response(),
    }
}

#[tokio::main]
async fn main() {
    let config_path = env_or("VIDENEPTUS_CONFIG_PATH", r"C:\Users\vizio\CAMELOT_OS\01_KERNEL\config\videneptus_config.json");
    let config_data = std::fs::read_to_string(&config_path).unwrap_or_else(|_| "{}".to_string());
    let config: VideneptusConfig = serde_json::from_str(&config_data).unwrap_or(VideneptusConfig {
        trigger_threshold: 0.8,
        execution_loop: vec![],
    });

    let gateway = load_gateway_config();
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(30))
        .build()
        .expect("reqwest client");
    let (tx, _) = broadcast::channel(128);
    let state = Arc::new(AppState { config, gateway, client, tx });

    let cors = if let Some(origin) = &state.gateway.cors_origin {
        CorsLayer::new()
            .allow_origin(origin.parse::<header::HeaderValue>().expect("valid CORS origin"))
            .allow_methods([Method::GET, Method::POST, Method::OPTIONS])
            .allow_headers([header::AUTHORIZATION, header::CONTENT_TYPE, "x-camelot-token".parse().unwrap()])
    } else {
        CorsLayer::new()
            .allow_origin(Any)
            .allow_methods([Method::GET, Method::POST, Method::OPTIONS])
            .allow_headers(Any)
    };

    let protected_routes = Router::new()
        .route("/bifrost/status", get(bifrost_status))
        .route("/openviking/map", get(openviking_map))
        .route("/pulse", post(receive_pulse))
        .route("/agent/dispatch", post(dispatch))
        .route("/modal/cloud-brain", post(modal_cloud_brain))
        .route_layer(middleware::from_fn_with_state(
            state.clone(),
            require_gateway_auth,
        ));

    let bind_addr = state.gateway.bind_addr;
    let app = Router::new()
        .route("/health", get(health))
        .route("/ping", get(ping))
        .route("/ws", get(ws_handler))
        .merge(protected_routes)
        .layer(cors)
        .with_state(state);

    let listener = tokio::net::TcpListener::bind(bind_addr).await.unwrap();
    println!(
        "MORGANA BIFROST GATEWAY ONLINE. Listening on {}...",
        bind_addr
    );
    axum::serve(listener, app.into_make_service_with_connect_info::<SocketAddr>()).await.unwrap();
}

async fn health(State(state): State<Arc<AppState>>) -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "status": "healthy",
        "node": "MORGANA_BIFROST_GATEWAY_v0.3.0",
        "auth_required": state.gateway.gateway_token.is_some(),
        "gate_type": "HEIMDALL_SOVEREIGN",
        "public_http_url": state.gateway.public_http_url,
        "public_ws_url": state.gateway.public_ws_url,
        "modal_cloud_brain_configured": state.gateway.modal_cloud_brain_url.is_some(),
        "camelot_root": state.gateway.camelot_root,
    }))
}

async fn ping() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "status": "alive",
        "node": "MORGANA_BIFROST_GATEWAY_v0.3.0",
        "bifrost": "linked"
    }))
}

async fn bifrost_status(State(state): State<Arc<AppState>>) -> Json<BifrostStatus> {
    let owner = state.gateway.owner.clone();
    let current_user = std::env::var("USERNAME")
        .or_else(|_| std::env::var("USER"))
        .unwrap_or_else(|_| "unknown".to_string());
    let hostname = std::env::var("COMPUTERNAME")
        .or_else(|_| std::env::var("HOSTNAME"))
        .unwrap_or_else(|_| "localhost".to_string());
    let token_present = std::env::var("USERPROFILE")
        .map(|profile| {
            std::path::Path::new(&profile)
                .join(".camelot")
                .join("bifrost.token")
                .is_file()
        })
        .unwrap_or(false);

    Json(BifrostStatus {
        gate: if current_user == owner {
            "local-owner"
        } else {
            "local-user-mismatch"
        }
        .to_string(),
        owner,
        current_user,
        hostname,
        token_present,
        bridge: "MORGANA_BIFROST_GATEWAY_v0.3.0".to_string(),
        dispatch_url: format!("{}/agent/dispatch", state.gateway.public_http_url),
        websocket_url: state.gateway.public_ws_url.clone(),
        cartridges: vec![
            "COGNITIVE".to_string(),
            "RESEARCH".to_string(),
            "ENGINEER".to_string(),
            "CREATIVE".to_string(),
            "MARKETING".to_string(),
            "LEGAL".to_string(),
            "BRAINSTORM".to_string(),
            "CRITICAL_THINKING".to_string(),
        ],
        cognitive_helm: "sir_alex".to_string(),
        bridge_knight: "sir_link".to_string(),
    })
}

async fn openviking_map(State(state): State<Arc<AppState>>) -> (StatusCode, Json<serde_json::Value>) {
    let path = state.gateway.openviking_map_path.as_str();
    let map_path = std::path::Path::new(path);

    let Ok(content) = std::fs::read_to_string(map_path) else {
        return (
            StatusCode::NOT_FOUND,
            Json(serde_json::json!({
                "error": "entiremap.md not found",
                "path": path
            })),
        );
    };

    let metadata = std::fs::metadata(map_path).ok();
    let modified_ms = metadata
        .as_ref()
        .and_then(|meta| meta.modified().ok())
        .and_then(|time| time.duration_since(SystemTime::UNIX_EPOCH).ok())
        .map(|duration| duration.as_millis())
        .unwrap_or_default();
    let line_count = content.lines().count();
    let section_count = content
        .lines()
        .filter(|line| line.starts_with("## "))
        .count();
    let directory_markers = content.matches("CAMELOT_OS/").count()
        + content.matches("[CORE]").count()
        + content.matches("[ACTIVE]").count();
    let preview = content.lines().take(36).collect::<Vec<_>>().join("\n");

    (
        StatusCode::OK,
        Json(
            serde_json::to_value(OpenVikingMap {
                name: "OpenViking Local Brain Map".to_string(),
                path: path.to_string(),
                bytes: metadata
                    .map(|meta| meta.len())
                    .unwrap_or(content.len() as u64),
                modified_ms,
                line_count,
                section_count,
                directory_markers,
                preview,
                content,
            })
            .unwrap_or_else(|_| serde_json::json!({ "error": "serialization failed" })),
        ),
    )
}

async fn receive_pulse(Json(payload): Json<PulseRequest>) -> Json<serde_json::Value> {
    println!(
        "PULSE: Received Telemetry -> RAM: {:?} | CPU: {:?}%",
        payload.ram_usage, payload.cpu_load
    );
    Json(serde_json::json!({
        "status": "ACKNOWLEDGED",
        "timestamp": std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs()
    }))
}

async fn ws_handler(
    ws: WebSocketUpgrade,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    State(state): State<Arc<AppState>>,
    headers: HeaderMap,
    Query(query): Query<HashMap<String, String>>,
) -> impl IntoResponse {
    let auth_res = authorized(
        addr.ip(),
        &headers,
        query.get("token").map(String::as_str),
        &state.gateway,
    ).await;

    if auth_res.is_err() {
        return (
            StatusCode::UNAUTHORIZED,
            Json(serde_json::json!({
                "error": "websocket authentication required"
            })),
        )
            .into_response();
    }

    ws.on_upgrade(move |mut socket| async move {
        let mut rx = state.tx.subscribe();
        let welcome = serde_json::json!({
            "event": "bridge.ready",
            "source": "MORGANA_BIFROST_GATEWAY_v0.3.0",
            "detail": "Anya websocket uplink established",
            "timestamp_ms": now_ms(),
        });

        if socket
            .send(Message::Text(welcome.to_string()))
            .await
            .is_err()
        {
            return;
        }

        while let Ok(event) = rx.recv().await {
            let Ok(payload) = serde_json::to_string(&event) else {
                continue;
            };
            if socket.send(Message::Text(payload)).await.is_err() {
                break;
            }
        }
    })
}

async fn dispatch(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<DispatchRequest>,
) -> (StatusCode, Json<DispatchResponse>) {
    let query_lower = payload.intent.to_lowercase();
    let target_file = payload.target.clone();

    let _ = state.tx.send(StreamEvent {
        event: "dispatch.accepted".to_string(),
        intent: payload.intent.clone(),
        source: "MORGANA_BRIDGE".to_string(),
        detail: format!(
            "cartridge={} knight={} target={}",
            empty_as(&payload.cartridge, "AUTO"),
            empty_as(&payload.preferred_knight, "AUTO"),
            empty_as(&payload.execution_target, "local_dispatch")
        ),
        timestamp_ms: now_ms(),
    });

    println!(
        "MORGANA ROUTER (RUST): Processing Intent: [{}]",
        payload.intent
    );

    let (source, response, cost) = if query_lower.contains("audit") && query_lower.contains("trivy")
    {
        let target = if target_file.is_empty() {
            r"C:\Users\vizio\CAMELOT_OS\01_KERNEL"
        } else {
            &target_file
        };
        let output =
            execute_kinetic_tool("trivy", target, &state.gateway.saltare_gateway_url).await;
        (
            "KINETIC_GATEWAY".to_string(),
            format!("SENTINEL (Via Saltare): {}", output),
            "0.00".to_string(),
        )
    } else if query_lower.contains("fix") && query_lower.contains("biome") {
        let target = if target_file.is_empty() {
            r"C:\Users\vizio\CAMELOT_OS\02_FORGE\PORTAL_CORE\src\main.tsx"
        } else {
            &target_file
        };
        let output =
            execute_kinetic_tool("biome", target, &state.gateway.saltare_gateway_url).await;
        (
            "KINETIC_GATEWAY".to_string(),
            format!("SQUIRE (Via Saltare): {}", output),
            "0.00".to_string(),
        )
    } else if query_lower.contains("remote") || query_lower.contains("rustdesk") {
        let output = execute_kinetic_tool(
            "rustdesk",
            "START_SESSION",
            &state.gateway.saltare_gateway_url,
        )
        .await;
        (
            "KINETIC_GATEWAY".to_string(),
            format!("ANYA (Remote): {}", output),
            "0.00".to_string(),
        )
    } else {
        let complexity_score =
            if query_lower.contains("architect") || query_lower.contains("design") {
                0.9
            } else {
                0.2
            };

        if complexity_score > state.config.trigger_threshold {
            let result = execute_lac_protocol(&state.config).await;
            (
                "CLOUD".to_string(),
                format!("MERLIN (LaC): {}", result),
                "0.12".to_string(),
            )
        } else if query_lower.contains("research") || query_lower.contains("scrape") {
            (
                "CLOUD".to_string(),
                format!(
                    "MERLIN (Sky): Authorized Crusade for '{}'. [Modal A100]",
                    payload.intent
                ),
                "0.04".to_string(),
            )
        } else if query_lower.contains("key") || query_lower.contains("password") {
            (
                "LOCAL".to_string(),
                "MORGANA (Vault): Accessing Secure Storage.".to_string(),
                "0.00".to_string(),
            )
        } else {
            let context_node = format!("UKG_NODE_{}_V1", payload.intent.to_uppercase());
            (
                "LOCAL".to_string(),
                format!(
                    "MORGANA (Local): Processing '{}' with context [{}].",
                    payload.intent, context_node
                ),
                "0.00".to_string(),
            )
        }
    };

    let _ = state.tx.send(StreamEvent {
        event: "dispatch.completed".to_string(),
        intent: payload.intent.clone(),
        source: source.clone(),
        detail: response.clone(),
        timestamp_ms: now_ms(),
    });

    (
        StatusCode::OK,
        Json(DispatchResponse {
            response,
            source,
            cost,
        }),
    )
}

async fn modal_cloud_brain(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<serde_json::Value>,
) -> (StatusCode, Json<serde_json::Value>) {
    let Some(url) = &state.gateway.modal_cloud_brain_url else {
        return (
            StatusCode::SERVICE_UNAVAILABLE,
            Json(serde_json::json!({
                "error": "MODAL_CLOUD_BRAIN_URL is not configured"
            })),
        );
    };

    match state.client.post(url).json(&payload).send().await {
        Ok(response) => {
            let status = StatusCode::from_u16(response.status().as_u16())
                .unwrap_or(StatusCode::BAD_GATEWAY);
            match response.json::<serde_json::Value>().await {
                Ok(body) => (status, Json(body)),
                Err(error) => (
                    StatusCode::BAD_GATEWAY,
                    Json(serde_json::json!({
                        "error": "modal response decode failed",
                        "detail": error.to_string()
                    })),
                ),
            }
        }
        Err(error) => (
            StatusCode::BAD_GATEWAY,
            Json(serde_json::json!({
                "error": "modal cloud brain request failed",
                "detail": error.to_string()
            })),
        ),
    }
}

async fn execute_kinetic_tool(tool_name: &str, target: &str, gateway_url: &str) -> String {
    println!("KINETIC: Routing {} -> Saltare Gateway...", tool_name);
    let client = reqwest::Client::new();
    let body = serde_json::json!({
        "tool": tool_name,
        "args": { "target": target }
    });

    match client
        .post(format!("{}/mcp/execute", gateway_url))
        .json(&body)
        .timeout(Duration::from_secs(30))
        .send()
        .await
    {
        Ok(resp) => match resp.text().await {
            Ok(text) => text,
            Err(e) => format!("DECODE_ERROR: {}", e),
        },
        Err(e) => format!("SALTARE_LINK_FAILED: {}", e),
    }
}

async fn execute_lac_protocol(config: &VideneptusConfig) -> String {
    println!("VIDENEPTUS: High Entropy Task Detected. Engaging LaC Protocol...");
    let mut last_result = String::new();

    for phase in &config.execution_loop {
        println!(
            "   >> PHASE: {} [T={}] | {}",
            phase.phase, phase.temperature, phase.instruction
        );
        sleep(Duration::from_millis(200)).await;
        last_result = format!("{}_RESULT", phase.phase);
    }

    format!("LaC OPTIMIZED OUTPUT: {} (Converged)", last_result)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_gateway_config() -> GatewayConfig {
        GatewayConfig {
            bind_addr: "127.0.0.1:8001".parse().expect("socket addr"),
            public_http_url: "http://127.0.0.1:8001".to_string(),
            public_ws_url: "ws://127.0.0.1:8001/ws".to_string(),
            owner: "vizio".to_string(),
            gateway_token: Some("test-token".to_string()),
            trusted_tailnet_owners: vec!["Cyberdad247@github".to_string()],
            tailscale_whois_timeout_ms: 100,
            allow_loopback_owner_without_token: false,
            saltare_gateway_url: "http://localhost:8085".to_string(),
            modal_cloud_brain_url: None,
            gradio_url: None,
            camelot_root: r"C:\Users\vizio\CAMELOT_OS".to_string(),
            openviking_map_path: r"C:\Users\vizio\CAMELOT_OS\entiremap.md".to_string(),
            cors_origin: None,
        }
    }

    #[test]
    fn owner_match_is_case_insensitive() {
        assert!(owner_matches("vizio", "VIZIO"));
        assert!(!owner_matches("vizio", "alex"));
    }

    #[test]
    fn extract_token_supports_all_header_names() {
        let mut headers = HeaderMap::new();
        headers.insert(header::AUTHORIZATION, "Bearer a-token".parse().expect("header"));
        assert_eq!(extract_token(&headers), Some("a-token"));

        headers.clear();
        headers.insert("x-camelot-token", "b-token".parse().expect("header"));
        assert_eq!(extract_token(&headers), Some("b-token"));

        headers.clear();
        headers.insert("x-bifrost-token", "c-token".parse().expect("header"));
        assert_eq!(extract_token(&headers), Some("c-token"));
    }

    #[tokio::test]
    async fn loopback_requires_token_by_default() {
        let headers = HeaderMap::new();
        let cfg = test_gateway_config();
        let result = authorized(IpAddr::V4(Ipv4Addr::LOCALHOST), &headers, None, &cfg).await;
        assert!(matches!(result, Err(AuthFailure::Unauthorized(_))));
    }

    #[tokio::test]
    async fn loopback_accepts_valid_token() {
        let mut headers = HeaderMap::new();
        headers.insert(header::AUTHORIZATION, "Bearer test-token".parse().expect("header"));
        let cfg = test_gateway_config();
        let result = authorized(IpAddr::V4(Ipv4Addr::LOCALHOST), &headers, None, &cfg).await;
        assert!(result.is_ok());
    }
}
