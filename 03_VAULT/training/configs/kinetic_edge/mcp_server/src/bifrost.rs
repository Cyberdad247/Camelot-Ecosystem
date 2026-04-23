//! Bifrost — Kinetic Edge Sovereign Gate
//!
//! Warden: SIR_HEIMDALL (Watcher of the Bifrost)
//! Governance persona for all ingress to the Kinetic Edge MCP server.
//! Heimdall sees every caller, verifies their claim to the rainbow bridge,
//! and refuses any presence that is neither local flesh nor trusted tailnet peer.
//!
//! Three-layer gate mirrors `CAMELOT_OS/bin/bifrost.py`:
//!
//!   1. LOOPBACK          — caller is on 127.0.0.0/8 (trusted by OS ACL on socket bind)
//!   2. TAILNET + TOKEN   — caller is on 100.64.0.0/10 AND presents valid `X-Bifrost-Token`
//!   3. EVERYTHING ELSE   — refused with 403 Forbidden
//!
//! Token is read once at server startup from `~/.camelot/bifrost.token` and
//! compared in constant time (subtle::ConstantTimeEq — or manual fallback here
//! to avoid adding a dep; Heimdall audits this choice on every reforge).

use axum::{
    extract::{ConnectInfo, Request},
    http::StatusCode,
    middleware::Next,
    response::{IntoResponse, Response},
};
use std::net::{IpAddr, Ipv4Addr, SocketAddr};
use std::path::PathBuf;
use std::sync::OnceLock;

const BIFROST_HEADER: &str = "x-bifrost-token";
const TAILNET_CGNAT: Ipv4Addr = Ipv4Addr::new(100, 64, 0, 0);
const TAILNET_CGNAT_PREFIX: u8 = 10;
const WHOIS_TIMEOUT_MS: u64 = 2500;
const TRUSTED_TAILNET_OWNERS: &[&str] = &["Cyberdad247@github", "Cyberdad247@"];

static BIFROST_TOKEN: OnceLock<Option<String>> = OnceLock::new();

fn token_path() -> PathBuf {
    // Prefer CAMELOT_OS_HOME, then fall back to USERPROFILE/HOME
    if let Ok(cos_home) = std::env::var("CAMELOT_OS_HOME") {
        let p = PathBuf::from(&cos_home)
            .parent()
            .map(|h| h.join(".camelot").join("bifrost.token"))
            .unwrap_or_else(|| PathBuf::from(cos_home).join(".camelot").join("bifrost.token"));
        if p.exists() {
            return p;
        }
    }
    let home = std::env::var("USERPROFILE")
        .or_else(|_| std::env::var("HOME"))
        .unwrap_or_else(|_| ".".to_string());
    PathBuf::from(home).join(".camelot").join("bifrost.token")
}

fn load_token() -> Option<String> {
    std::fs::read_to_string(token_path())
        .ok()
        .map(|s| s.trim().to_string())
        .filter(|s| !s.is_empty())
}

/// Initialize Heimdall's token cache. Call once from main() before serving.
pub fn init() -> bool {
    let tok = load_token();
    let present = tok.is_some();
    let _ = BIFROST_TOKEN.set(tok);
    present
}

fn is_loopback(ip: IpAddr) -> bool {
    ip.is_loopback()
}

fn is_tailnet(ip: IpAddr) -> bool {
    match ip {
        IpAddr::V4(v4) => {
            let octets = v4.octets();
            let base = TAILNET_CGNAT.octets();
            // 100.64.0.0/10 → first 10 bits must match
            octets[0] == base[0] && (octets[1] & 0xC0) == (base[1] & 0xC0)
        }
        IpAddr::V6(_) => false,
    }
}

/// Constant-time byte comparison. Returns true only if both are equal length and content.
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

/// Call `tailscale whois <ip>` and extract the `Name:` line owner.
/// Returns None on timeout, non-zero exit, missing binary, or unparseable output.
async fn tailscale_whois(ip: IpAddr) -> Option<String> {
    let fut = tokio::process::Command::new("tailscale")
        .arg("whois")
        .arg(ip.to_string())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::null())
        .output();

    let out = tokio::time::timeout(
        std::time::Duration::from_millis(WHOIS_TIMEOUT_MS),
        fut,
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

fn is_trusted_owner(owner: &str) -> bool {
    TRUSTED_TAILNET_OWNERS.iter().any(|t| *t == owner)
}

fn verify_token(presented: Option<&str>) -> bool {
    let stored = match BIFROST_TOKEN.get().and_then(|o| o.as_ref()) {
        Some(t) => t,
        None => return false,
    };
    let Some(p) = presented else { return false };
    ct_eq(stored.as_bytes(), p.as_bytes())
}

/// Axum middleware: refuse unauthorized callers before they reach any tool handler.
pub async fn gate(
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    req: Request,
    next: Next,
) -> Result<Response, Response> {
    let ip = addr.ip();

    // Rule 1: loopback — socket is already bound to 127.0.0.1 and OS ACL protects it.
    if is_loopback(ip) {
        return Ok(next.run(req).await);
    }

    // Rule 2: tailnet peer with valid token AND trusted tailnet owner.
    if is_tailnet(ip) {
        let hdr = req
            .headers()
            .get(BIFROST_HEADER)
            .and_then(|v| v.to_str().ok())
            .map(|s| s.to_string());
        if !verify_token(hdr.as_deref()) {
            return Err((
                StatusCode::FORBIDDEN,
                format!("[HEIMDALL] tailnet peer {ip} presented no valid bifrost token"),
            )
                .into_response());
        }
        match tailscale_whois(ip).await {
            Some(owner) if is_trusted_owner(&owner) => {
                return Ok(next.run(req).await);
            }
            Some(owner) => {
                return Err((
                    StatusCode::FORBIDDEN,
                    format!("[HEIMDALL] tailnet peer {ip} owner {owner} not trusted"),
                )
                    .into_response());
            }
            None => {
                return Err((
                    StatusCode::FORBIDDEN,
                    format!("[HEIMDALL] tailnet whois failed for {ip}"),
                )
                    .into_response());
            }
        }
    }

    // Rule 3: refuse everything else.
    Err((
        StatusCode::FORBIDDEN,
        format!("[HEIMDALL] origin {ip} is not on the rainbow bridge"),
    )
        .into_response())
}
