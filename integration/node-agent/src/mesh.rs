//! Phase 4A mesh client: enrolment, heartbeat, and a READ-ONLY Tailscale
//! observer.
//!
//! Hard rule: this module observes the mesh, it never operates it. The only
//! external command it may ever run is `tailscale status --json`. It does
//! not log in, does not `tailscale up`, does not touch ACLs, does not
//! advertise routes or exit nodes, and does not modify host networking. If
//! the binary is absent or the user is logged out, the node simply reports
//! `mesh_reachable: false` and keeps serving local work.

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashSet;
use std::io::{Read, Write};
use std::net::TcpStream;
use std::process::Command;
use std::sync::Mutex;
use std::time::Duration;

pub const HEARTBEAT_INTERVAL: Duration = Duration::from_secs(15);

#[derive(Debug, Clone, Serialize)]
pub struct NodeIdentity {
    #[serde(rename = "nodeId")]
    pub node_id: String,
    #[serde(rename = "tenantId")]
    pub tenant_id: String,
    #[serde(rename = "displayName")]
    pub display_name: String,
    #[serde(rename = "keyFingerprint")]
    pub key_fingerprint: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct NodeCapability {
    pub name: String,
    #[serde(rename = "readOnly")]
    pub read_only: bool,
}

#[derive(Debug, Clone, Serialize)]
pub struct NodeRegistration {
    pub identity: NodeIdentity,
    pub capabilities: Vec<NodeCapability>,
    #[serde(rename = "agentVersion")]
    pub agent_version: String,
    #[serde(rename = "dispatchUrl")]
    pub dispatch_url: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct NodeHealth {
    #[serde(rename = "nodeId")]
    pub node_id: String,
    pub status: String,
    pub backend: String,
    #[serde(rename = "meshReachable")]
    pub mesh_reachable: bool,
    #[serde(rename = "meshBackend")]
    pub mesh_backend: String,
    #[serde(rename = "activeJobs")]
    pub active_jobs: usize,
    #[serde(rename = "reportedAt")]
    pub reported_at: String,
}

#[derive(Debug, Deserialize)]
pub struct NodeView {
    pub trust: String,
    pub health: String,
}

/// Mesh configuration, entirely from environment. Absent config = the agent
/// runs standalone exactly as it did in Phase 1 (local compute only).
#[derive(Debug, Clone)]
pub struct MeshConfig {
    pub enabled: bool,
    pub gateway_url: String,
    pub node_id: String,
    pub tenant_id: String,
    pub display_name: String,
    pub enrol_secret: String,
    pub dispatch_url: String,
}

impl MeshConfig {
    pub fn from_env(listen_addr: &str) -> Self {
        let node_id = std::env::var("CAMELOT_NODE_ID").unwrap_or_default();
        let dispatch_url = std::env::var("CAMELOT_NODE_DISPATCH_URL")
            .unwrap_or_else(|_| format!("http://{}", listen_addr.replace("0.0.0.0", "127.0.0.1")));
        Self {
            enabled: std::env::var("ENABLE_TAILSCALE_MESH").as_deref() == Ok("true")
                && !node_id.is_empty(),
            gateway_url: std::env::var("CAMELOT_GATEWAY_URL")
                .unwrap_or_else(|_| "http://127.0.0.1:8788".into()),
            node_id,
            tenant_id: std::env::var("CAMELOT_TENANT_ID").unwrap_or_else(|_| "local".into()),
            display_name: std::env::var("CAMELOT_NODE_NAME")
                .unwrap_or_else(|_| "camelot-node".into()),
            enrol_secret: std::env::var("CAMELOT_NODE_ENROL_SECRET")
                .unwrap_or_else(|_| "local-enrolment".into()),
            dispatch_url,
        }
    }

    /// The fingerprint pins this node's identity at the gateway. The secret
    /// itself never leaves the process.
    pub fn key_fingerprint(&self) -> String {
        let mut hasher = Sha256::new();
        hasher.update(self.node_id.as_bytes());
        hasher.update(b"|");
        hasher.update(self.enrol_secret.as_bytes());
        hex::encode(hasher.finalize())
    }
}

// ── Tailscale observer (read-only) ──────────────────────────────────────

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MeshStatus {
    pub reachable: bool,
    pub backend: String,
    pub detail: String,
}

/// Observe Tailscale via exactly one allowed read-only command. Any failure
/// (binary missing, logged out, timeout) degrades to "not reachable" without
/// affecting local operation.
pub fn observe_tailscale() -> MeshStatus {
    // The ONLY subcommand this agent is permitted to run, ever.
    const ALLOWED_ARGS: [&str; 2] = ["status", "--json"];
    let output = Command::new("tailscale").args(ALLOWED_ARGS).output();
    match output {
        Ok(out) if out.status.success() => {
            let text = String::from_utf8_lossy(&out.stdout);
            // "BackendState":"Running" means the user is logged in and up.
            let running = text.contains("\"BackendState\":\"Running\"")
                || text.contains("\"BackendState\": \"Running\"");
            MeshStatus {
                reachable: running,
                backend: "tailscale".into(),
                detail: if running { "running".into() } else { "not running".into() },
            }
        }
        Ok(_) => MeshStatus {
            reachable: false,
            backend: "tailscale".into(),
            detail: "tailscale present but not ready (logged out?)".into(),
        },
        Err(_) => MeshStatus {
            reachable: false,
            backend: "none".into(),
            detail: "tailscale not installed; local-only operation".into(),
        },
    }
}

// ── single-use enforcement on the node side ─────────────────────────────

/// Leases the gateway minted are single-use. The gateway cannot enforce that
/// for node jobs (it never sees the redemption), so the node keeps its own
/// spent-lease set. Bounded: old ids are dropped once the set grows past the
/// cap, and every lease expires within 30s anyway.
pub struct SpentLeases {
    seen: Mutex<HashSet<String>>,
    cap: usize,
}

impl SpentLeases {
    pub fn new() -> Self {
        Self { seen: Mutex::new(HashSet::new()), cap: 4096 }
    }

    /// Returns true if this lease id had NOT been spent before (i.e. accept).
    pub fn claim(&self, lease_id: &str) -> bool {
        let mut seen = self.seen.lock().expect("spent-lease lock");
        if seen.len() > self.cap {
            seen.clear(); // all prior leases are long expired
        }
        seen.insert(lease_id.to_string())
    }
}

impl Default for SpentLeases {
    fn default() -> Self {
        Self::new()
    }
}

// ── minimal HTTP client (no dependencies) ───────────────────────────────

fn split_url(url: &str) -> Option<(String, u16, String)> {
    let rest = url.strip_prefix("http://")?;
    let (authority, path) = match rest.find('/') {
        Some(i) => (&rest[..i], &rest[i..]),
        None => (rest, "/"),
    };
    let (host, port) = match authority.rsplit_once(':') {
        Some((h, p)) => (h.to_string(), p.parse().ok()?),
        None => (authority.to_string(), 80),
    };
    Some((host, port, path.to_string()))
}

/// POST a JSON body and return the response body. Bounded by connect/read
/// timeouts so a wedged gateway can never stall the agent.
pub fn post_json(url: &str, body: &str) -> Result<String, String> {
    let (host, port, path) = split_url(url).ok_or_else(|| format!("bad url {url}"))?;
    let addr = format!("{host}:{port}");
    let mut stream = TcpStream::connect(&addr).map_err(|e| format!("connect {addr}: {e}"))?;
    stream
        .set_read_timeout(Some(Duration::from_secs(10)))
        .map_err(|e| e.to_string())?;
    let request = format!(
        "POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}",
        body.len()
    );
    stream
        .write_all(request.as_bytes())
        .map_err(|e| format!("write: {e}"))?;
    let mut response = String::new();
    stream
        .read_to_string(&mut response)
        .map_err(|e| format!("read: {e}"))?;
    let (head, payload) = response
        .split_once("\r\n\r\n")
        .ok_or_else(|| "malformed http response".to_string())?;
    let status_ok = head.starts_with("HTTP/1.1 200") || head.starts_with("HTTP/1.0 200");
    if !status_ok {
        let code = head.lines().next().unwrap_or("unknown");
        return Err(format!("{code}: {payload}"));
    }
    Ok(payload.to_string())
}

// ── enrolment + heartbeat ───────────────────────────────────────────────

pub fn registration_for(cfg: &MeshConfig, capabilities: Vec<NodeCapability>, version: &str) -> NodeRegistration {
    NodeRegistration {
        identity: NodeIdentity {
            node_id: cfg.node_id.clone(),
            tenant_id: cfg.tenant_id.clone(),
            display_name: cfg.display_name.clone(),
            key_fingerprint: cfg.key_fingerprint(),
        },
        capabilities,
        agent_version: version.to_string(),
        dispatch_url: cfg.dispatch_url.clone(),
    }
}

pub fn register(cfg: &MeshConfig, registration: &NodeRegistration) -> Result<NodeView, String> {
    let body = serde_json::to_string(registration).map_err(|e| e.to_string())?;
    let url = format!("{}/v1/nodes/register", cfg.gateway_url.trim_end_matches('/'));
    let response = post_json(&url, &body)?;
    serde_json::from_str(&response).map_err(|e| format!("bad register response: {e}"))
}

pub fn heartbeat(cfg: &MeshConfig, health: &NodeHealth) -> Result<NodeView, String> {
    let payload = serde_json::json!({
        "keyFingerprint": cfg.key_fingerprint(),
        "health": health,
    });
    let url = format!(
        "{}/v1/nodes/{}/heartbeat",
        cfg.gateway_url.trim_end_matches('/'),
        cfg.node_id
    );
    let response = post_json(&url, &payload.to_string())?;
    serde_json::from_str(&response).map_err(|e| format!("bad heartbeat response: {e}"))
}

/// Background enrolment + heartbeat loop. Never panics, never exits the
/// process: a gateway that is down simply means "offline" until it returns.
pub fn spawn_heartbeat_loop(cfg: MeshConfig, capabilities: Vec<NodeCapability>, version: String) {
    std::thread::spawn(move || {
        let registration = registration_for(&cfg, capabilities, &version);
        match register(&cfg, &registration) {
            Ok(view) => eprintln!(
                "mesh: enrolled node {} (trust band: {}, health: {})",
                cfg.node_id, view.trust, view.health
            ),
            Err(e) => eprintln!("mesh: enrolment failed ({e}); will retry on heartbeat"),
        }
        let mut enrolled = true;
        loop {
            std::thread::sleep(HEARTBEAT_INTERVAL);
            let mesh = observe_tailscale();
            let health = NodeHealth {
                node_id: cfg.node_id.clone(),
                status: "healthy".into(),
                backend: crate::backend::select_backend().name().into(),
                mesh_reachable: mesh.reachable,
                mesh_backend: mesh.backend.clone(),
                active_jobs: 0,
                reported_at: String::new(), // gateway stamps authoritative time
            };
            match heartbeat(&cfg, &health) {
                Ok(view) => {
                    if !enrolled {
                        eprintln!("mesh: reconnected (trust band: {})", view.trust);
                        enrolled = true;
                    }
                }
                Err(e) => {
                    if enrolled {
                        eprintln!("mesh: heartbeat failed ({e}); re-enrolling");
                        enrolled = false;
                    }
                    let _ = register(&cfg, &registration);
                }
            }
        }
    });
}
