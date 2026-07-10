// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS - CONFIDENTIAL AND PROPRIETARY
use axum::{
    extract::{
        ConnectInfo, Query, Request, State,
        ws::{Message, WebSocketUpgrade},
    },
    http::{header, HeaderMap, HeaderValue, Method, StatusCode},
    middleware::{self, Next},
    response::{IntoResponse, Response},
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::net::{IpAddr, Ipv4Addr, SocketAddr};
use std::path::Path;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::SystemTime;
use tokio::sync::broadcast;
use tokio::time::{sleep, timeout, Duration};
use tower_http::cors::{Any, CorsLayer};

const TAILNET_CGNAT: Ipv4Addr = Ipv4Addr::new(100, 64, 0, 0);
const DEFAULT_TRUSTED_TAILNET_OWNERS: &str = "Cyberdad247@github,Cyberdad247@";
const DEFAULT_ALLOWED_SOVEREIGN_IDENTITIES: &str =
    "SIR_BORIS,SIR_CODEX,SIR_ALEX,SIR_FORGE,SIR_SENTINEL,SIR_DEBUG,LADY_APIS,MERLIN_OMEGA,SIR_HELIO";
const SOVEREIGN_TRACE_HEADER: &str = "x-sovereign-trace-id";
const SOVEREIGN_IDENTITY_HEADER: &str = "x-sovereign-identity";
static TRACE_COUNTER: AtomicU64 = AtomicU64::new(1);

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
    nervous_system_log: String,
    immune_response_log: String,
    metabolic_mailbox: String,
    sovereign_identity_required: bool,
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
    nervous_system_log_path: String,
    immune_response_log_path: String,
    metabolic_mailbox_path: String,
    staging_reclamation_dir: String,
    sovereign_identity_required: bool,
    allowed_sovereign_identities: Vec<String>,
    fatigue_threshold_ms: u128,
}

#[derive(Debug, Serialize)]
struct MutationStaging {
    knight_id: String,
    payload: String,
    timestamp_ms: u128,
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

fn env_u128(key: &str, default: u128) -> u128 {
    std::env::var(key)
        .ok()
        .and_then(|value| value.trim().parse::<u128>().ok())
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
    let bio_root = format!(
        r"{}\03_VAULT\runtime_state\bio_agentic_hive",
        camelot_root
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
        nervous_system_log_path: env_or(
            "BIFROST_NERVOUS_SYSTEM_LOG",
            &format!(r"{}\logs\nervous_system.jsonl", bio_root),
        ),
        immune_response_log_path: env_or(
            "BIFROST_IMMUNE_RESPONSE_LOG",
            &format!(r"{}\logs\immune_response.jsonl", bio_root),
        ),
        metabolic_mailbox_path: env_or(
            "BIFROST_METABOLIC_MAILBOX",
            &format!(r"{}\staging\reclamation\harness_queue.jsonl", bio_root),
        ),
        staging_reclamation_dir: env_or(
            "BIFROST_STAGING_RECLAMATION_DIR",
            &format!(r"{}\staging\reclamation", bio_root),
        ),
        sovereign_identity_required: env_flag("BIFROST_REQUIRE_SOVEREIGN_IDENTITY", false),
        allowed_sovereign_identities: env_csv(
            "BIFROST_ALLOWED_SOVEREIGN_IDENTITIES",
            DEFAULT_ALLOWED_SOVEREIGN_IDENTITIES,
        ),
        fatigue_threshold_ms: env_u128("BIFROST_FATIGUE_THRESHOLD_MS", 200),
    }
}

fn append_jsonl(path: &str, value: &serde_json::Value) -> std::io::Result<()> {
    if let Some(parent) = Path::new(path).parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut file = OpenOptions::new().create(true).append(true).open(path)?;
    writeln!(file, "{}", value)
}

fn generate_trace_id() -> String {
    let counter = TRACE_COUNTER.fetch_add(1, Ordering::Relaxed);
    format!("{:x}-{:x}-{:x}", now_ms(), std::process::id(), counter)
}

fn sovereign_identity(headers: &HeaderMap) -> Option<String> {
    headers
        .get(SOVEREIGN_IDENTITY_HEADER)
        .and_then(|value| value.to_str().ok())
        .map(str::trim)
        .filter(|value| !value.is_empty())
        .map(|value| value.to_ascii_uppercase())
}

fn sovereign_identity_allowed(identity: &str, gateway: &GatewayConfig) -> bool {
    gateway
        .allowed_sovereign_identities
        .iter()
        .any(|allowed| allowed.eq_ignore_ascii_case(identity))
}

fn stage_forage_mutation(
    gateway: &GatewayConfig,
    knight_id: &str,
    data: &str,
) -> std::io::Result<()> {
    std::fs::create_dir_all(&gateway.staging_reclamation_dir)?;
    let mutation = MutationStaging {
        knight_id: knight_id.to_ascii_uppercase(),
        payload: data.to_string(),
        timestamp_ms: now_ms(),
    };
    append_jsonl(
        &gateway.metabolic_mailbox_path,
        &serde_json::to_value(mutation)
            .unwrap_or_else(|_| serde_json::json!({ "error": "mutation serialization failed" })),
    )
}

fn should_stage_forage(payload: &DispatchRequest) -> bool {
    let intent = payload.intent.to_ascii_lowercase();
    payload.execution_target.eq_ignore_ascii_case("squire_foraging")
        || intent.contains("forage")
        || intent.contains("discover")
        || intent.contains("reclaim")
}

async fn nervous_system_middleware(
    State(state): State<Arc<AppState>>,
    request: Request,
    next: Next,
) -> Response {
    let trace_id = generate_trace_id();
    let method = request.method().clone();
    let path = request.uri().path().to_string();
    let request_start = std::time::Instant::now();
    let mut response = next.run(request).await;
    let latency_ms = request_start.elapsed().as_millis();
    let fatigue = latency_ms > state.gateway.fatigue_threshold_ms;

    if let Ok(value) = HeaderValue::from_str(&trace_id) {
        response.headers_mut().insert(SOVEREIGN_TRACE_HEADER, value);
    }

    let entry = serde_json::json!({
        "event": if fatigue { "system_fatigue" } else { "request_observed" },
        "trace_id": trace_id,
        "method": method.as_str(),
        "path": path,
        "status": response.status().as_u16(),
        "latency_ms": latency_ms,
        "threshold_ms": state.gateway.fatigue_threshold_ms,
        "timestamp_ms": now_ms(),
    });
    if let Err(error) = append_jsonl(&state.gateway.nervous_system_log_path, &entry) {
        eprintln!("[NERVOUS_SYSTEM]: log write failed: {}", error);
    }
    if fatigue {
        eprintln!(
            "[NERVOUS_SYSTEM]: System Fatigue trace={} latency={}ms threshold={}ms",
            entry["trace_id"], latency_ms, state.gateway.fatigue_threshold_ms
        );
    }

    response
}

async fn immune_shield(
    State(state): State<Arc<AppState>>,
    headers: HeaderMap,
    request: Request,
    next: Next,
) -> impl IntoResponse {
    if !state.gateway.sovereign_identity_required {
        return next.run(request).await.into_response();
    }

    let path = request.uri().path().to_string();
    let identity = sovereign_identity(&headers);
    if identity
        .as_deref()
        .is_some_and(|value| sovereign_identity_allowed(value, &state.gateway))
    {
        return next.run(request).await.into_response();
    }

    let entry = serde_json::json!({
        "event": "identity_rejected",
        "path": path,
        "identity": identity.unwrap_or_else(|| "missing".to_string()),
        "allowed": state.gateway.allowed_sovereign_identities,
        "timestamp_ms": now_ms(),
    });
    if let Err(error) = append_jsonl(&state.gateway.immune_response_log_path, &entry) {
        eprintln!("[IMMUNE_SYSTEM]: log write failed: {}", error);
    }

    (
        StatusCode::FORBIDDEN,
        Json(serde_json::json!({
            "error": "Bifrost immune shield closed",
            "detail": "sovereign identity is not authorized"
        })),
    )
        .into_response()
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
        Err(AuthFailure::Unauthorized(reason)) => {
            let entry = serde_json::json!({
                "event": "auth_rejected",
                "class": "unauthorized",
                "origin": addr.ip().to_string(),
                "detail": reason,
                "timestamp_ms": now_ms(),
            });
            if let Err(error) = append_jsonl(&state.gateway.immune_response_log_path, &entry) {
                eprintln!("[IMMUNE_SYSTEM]: log write failed: {}", error);
            }
            (
                StatusCode::UNAUTHORIZED,
                Json(serde_json::json!({ "error": "unauthorized", "detail": entry["detail"] })),
            )
                .into_response()
        }
        Err(AuthFailure::Forbidden(reason)) => {
            let entry = serde_json::json!({
                "event": "auth_rejected",
                "class": "forbidden",
                "origin": addr.ip().to_string(),
                "detail": reason,
                "timestamp_ms": now_ms(),
            });
            if let Err(error) = append_jsonl(&state.gateway.immune_response_log_path, &entry) {
                eprintln!("[IMMUNE_SYSTEM]: log write failed: {}", error);
            }
            (
                StatusCode::FORBIDDEN,
                Json(serde_json::json!({
                    "error": "Bifrost gate closed",
                    "detail": entry["detail"]
                })),
            )
                .into_response()
        }
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
        ))
        .route_layer(middleware::from_fn_with_state(
            state.clone(),
            immune_shield,
        ));

    let bind_addr = state.gateway.bind_addr;
    let app = Router::new()
        .route("/health", get(health))
        .route("/ping", get(ping))
        .route("/ws", get(ws_handler))
        .merge(protected_routes)
        .layer(middleware::from_fn_with_state(
            state.clone(),
            nervous_system_middleware,
        ))
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
        nervous_system_log: state.gateway.nervous_system_log_path.clone(),
        immune_response_log: state.gateway.immune_response_log_path.clone(),
        metabolic_mailbox: state.gateway.metabolic_mailbox_path.clone(),
        sovereign_identity_required: state.gateway.sovereign_identity_required,
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

    if should_stage_forage(&payload) {
        let knight_id = empty_as(&payload.preferred_knight, "SQUIRE_FORAGER");
        if let Err(error) = stage_forage_mutation(&state.gateway, knight_id, &payload.intent) {
            eprintln!("[METABOLIC_LOOP]: mutation staging failed: {}", error);
        }
    }

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
            nervous_system_log_path: r"C:\tmp\morgana_bridge\nervous_system.jsonl".to_string(),
            immune_response_log_path: r"C:\tmp\morgana_bridge\immune_response.jsonl".to_string(),
            metabolic_mailbox_path: r"C:\tmp\morgana_bridge\harness_queue.jsonl".to_string(),
            staging_reclamation_dir: r"C:\tmp\morgana_bridge".to_string(),
            sovereign_identity_required: false,
            allowed_sovereign_identities: vec![
                "SIR_BORIS".to_string(),
                "SIR_CODEX".to_string(),
            ],
            fatigue_threshold_ms: 200,
        }
    }

    fn test_dispatch(intent: &str, execution_target: &str) -> DispatchRequest {
        DispatchRequest {
            intent: intent.to_string(),
            target: String::new(),
            cartridge: String::new(),
            preferred_knight: "sir_codex".to_string(),
            execution_target: execution_target.to_string(),
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

    #[test]
    fn sovereign_identity_is_case_insensitive() {
        let cfg = test_gateway_config();
        assert!(sovereign_identity_allowed("sir_codex", &cfg));
        assert!(!sovereign_identity_allowed("SIR_UNKNOWN", &cfg));
    }

    #[test]
    fn forage_detection_catches_metabolic_intents() {
        assert!(should_stage_forage(&test_dispatch(
            "forage a new tool manifest",
            ""
        )));
        assert!(should_stage_forage(&test_dispatch(
            "normal request",
            "squire_foraging"
        )));
        assert!(!should_stage_forage(&test_dispatch("normal request", "")));
    }

    #[test]
    fn stage_forage_mutation_writes_jsonl_mailbox() {
        let unique = format!("morgana_bridge_test_{}", generate_trace_id());
        let root = std::env::temp_dir().join(unique);
        let mailbox = root.join("staging").join("reclamation").join("harness_queue.jsonl");
        let mut cfg = test_gateway_config();
        cfg.staging_reclamation_dir = root
            .join("staging")
            .join("reclamation")
            .to_string_lossy()
            .to_string();
        cfg.metabolic_mailbox_path = mailbox.to_string_lossy().to_string();

        stage_forage_mutation(&cfg, "sir_codex", "discover local tool")
            .expect("mutation staging succeeds");

        let content = std::fs::read_to_string(&cfg.metabolic_mailbox_path)
            .expect("mailbox was written");
        assert!(content.contains("\"knight_id\":\"SIR_CODEX\""));
        assert!(content.contains("\"payload\":\"discover local tool\""));

        let _ = std::fs::remove_dir_all(root);
    }
}
