//! Camelot Kinetic Edge — MCP Server + AgentArmor PDG
//!
//! Exposes safe filesystem tools via HTTP for the Control Plane.
//! Enforces Kinetic Purity: all heavy I/O lives here, not in Python.
//! AgentArmor PDG: Program Dependency Graph taint analysis on every request.

mod ap2_settlement;
mod bifrost;
mod turboquant;
mod wasi_nn;

use axum::{
    extract::Json,
    http::StatusCode,
    middleware::{self, Next},
    response::{IntoResponse, Response},
    routing::post,
    Router,
};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::fs;
use std::net::SocketAddr;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

// ---------------------------------------------------------------------------
// AgentArmor PDG — Program Dependency Graph Security Layer
// ---------------------------------------------------------------------------

/// Taint labels for data flow analysis.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
enum TaintLabel {
    /// Data from an untrusted external source (user input, web)
    UntrustedSource,
    /// Data from a trusted internal source (kernel, config)
    TrustedInternal,
    /// Data that has been sanitized
    Sanitized,
}

/// Security classification for tool sinks.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum SinkType {
    /// Read-only filesystem access
    ReadOnly,
    /// Write to filesystem
    WriteFS,
    /// Execute a subprocess (ALWAYS BLOCKED for untrusted)
    ShellExec,
    /// Network egress
    NetworkOut,
}

/// PDG verdict for a given request.
#[derive(Debug, Serialize)]
struct PDGVerdict {
    allowed: bool,
    tool: String,
    taint: TaintLabel,
    sink: String,
    reason: String,
}

/// Blocked path patterns — files that must never be read or written.
static BLOCKED_PATHS: LazyLock<Vec<&str>> = LazyLock::new(|| {
    vec![
        ".env",
        ".git-credentials",
        ".modal.toml",
        "secrets.json",
        "credentials",
        ".ssh/",
        "id_rsa",
        "id_ed25519",
    ]
});

/// Allowed root directories — sandbox boundary.
static ALLOWED_ROOTS: LazyLock<Vec<PathBuf>> = LazyLock::new(|| {
    vec![
        PathBuf::from("C:/Users/vizio/CAMELOT_OS"),
        PathBuf::from("C:/Users/vizio/.camelot"),
    ]
});

/// Core PDG engine: evaluates whether a data flow is safe.
fn pdg_evaluate(tool_name: &str, taint: TaintLabel, path: Option<&str>) -> PDGVerdict {
    let sink = match tool_name {
        "list_directory" | "read_file" | "stat_file" => SinkType::ReadOnly,
        "write_file" | "patch_file" => SinkType::WriteFS,
        "exec" | "shell" | "subprocess" => SinkType::ShellExec,
        "http_request" | "fetch" => SinkType::NetworkOut,
        _ => SinkType::ReadOnly,
    };

    // Rule 1: NEVER allow untrusted data to reach shell execution
    if taint == TaintLabel::UntrustedSource && sink == SinkType::ShellExec {
        return PDGVerdict {
            allowed: false,
            tool: tool_name.into(),
            taint,
            sink: format!("{sink:?}"),
            reason: "PDG BLOCK: Untrusted source -> Shell sink. Command injection risk.".into(),
        };
    }

    // Rule 2: NEVER allow untrusted data to reach network egress
    if taint == TaintLabel::UntrustedSource && sink == SinkType::NetworkOut {
        return PDGVerdict {
            allowed: false,
            tool: tool_name.into(),
            taint,
            sink: format!("{sink:?}"),
            reason: "PDG BLOCK: Untrusted source -> Network sink. Data exfiltration risk.".into(),
        };
    }

    // Rule 3: Block writes from untrusted sources
    if taint == TaintLabel::UntrustedSource && sink == SinkType::WriteFS {
        return PDGVerdict {
            allowed: false,
            tool: tool_name.into(),
            taint,
            sink: format!("{sink:?}"),
            reason: "PDG BLOCK: Untrusted source -> Write sink. Requires sanitization.".into(),
        };
    }

    // Rule 3b: Block settlement from untrusted sources
    if taint == TaintLabel::UntrustedSource && tool_name == "settle_compute" {
        return PDGVerdict {
            allowed: false,
            tool: tool_name.into(),
            taint,
            sink: "Settlement".into(),
            reason: "PDG BLOCK: Untrusted source -> Settlement sink. Only trusted agents may settle compute.".into(),
        };
    }

    // Rule 4: Path-based restrictions
    if let Some(p) = path {
        // Block path traversal
        if p.contains("..") {
            return PDGVerdict {
                allowed: false,
                tool: tool_name.into(),
                taint,
                sink: format!("{sink:?}"),
                reason: "PDG BLOCK: Path traversal (..) detected.".into(),
            };
        }

        // Block sensitive file patterns
        let lower = p.to_lowercase();
        for blocked in BLOCKED_PATHS.iter() {
            if lower.contains(blocked) {
                return PDGVerdict {
                    allowed: false,
                    tool: tool_name.into(),
                    taint,
                    sink: format!("{sink:?}"),
                    reason: format!("PDG BLOCK: Access to sensitive path pattern '{blocked}'."),
                };
            }
        }

        // Sandbox: ensure path is within allowed roots
        // Use canonicalize for existing paths; for non-existent paths (writes),
        // resolve the parent directory to prevent sandbox bypass.
        let canonical = fs::canonicalize(p).or_else(|_| {
            // Path doesn't exist yet — canonicalize parent to validate sandbox
            std::path::Path::new(p)
                .parent()
                .and_then(|parent| fs::canonicalize(parent).ok())
                .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "no parent"))
        });
        match canonical {
            Ok(resolved) => {
                if !ALLOWED_ROOTS.iter().any(|root| resolved.starts_with(root)) {
                    return PDGVerdict {
                        allowed: false,
                        tool: tool_name.into(),
                        taint,
                        sink: format!("{sink:?}"),
                        reason: "PDG BLOCK: Path outside sandbox boundary.".into(),
                    };
                }
            }
            Err(_) => {
                // Cannot resolve path at all — block for safety
                return PDGVerdict {
                    allowed: false,
                    tool: tool_name.into(),
                    taint,
                    sink: format!("{sink:?}"),
                    reason: "PDG BLOCK: Cannot resolve path — parent directory does not exist.".into(),
                };
            }
        }
    }

    PDGVerdict {
        allowed: true,
        tool: tool_name.into(),
        taint,
        sink: format!("{sink:?}"),
        reason: "ALLOWED".into(),
    }
}

// ---------------------------------------------------------------------------
// A2A Message types (mirrors control_plane schema)
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
struct A2AMessage {
    id: String,
    #[serde(rename = "type")]
    msg_type: String,
    source: String,
    #[allow(dead_code)]
    target: String,
    payload: ToolRequestPayload,
    correlation_id: Option<String>,
}

#[derive(Debug, Deserialize)]
struct ToolRequestPayload {
    tool_name: String,
    #[serde(default)]
    arguments: serde_json::Value,
}

#[derive(Debug, Serialize)]
struct ToolResult {
    tool_name: String,
    success: bool,
    result: serde_json::Value,
    #[serde(skip_serializing_if = "Option::is_none")]
    error: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pdg_verdict: Option<PDGVerdict>,
}

// ---------------------------------------------------------------------------
// Tool: list_directory
// ---------------------------------------------------------------------------

#[derive(Debug, Serialize)]
struct DirEntry {
    name: String,
    is_dir: bool,
    size: u64,
}

fn list_directory(path: &str) -> Result<Vec<DirEntry>, String> {
    let entries = fs::read_dir(path)
        .map_err(|e| format!("Failed to read directory: {e}"))?;

    let mut result = Vec::new();
    for entry in entries.flatten() {
        let meta = entry.metadata().ok();
        // Filter out sensitive files from listings
        let name = entry.file_name().to_string_lossy().into_owned();
        let lower = name.to_lowercase();
        if BLOCKED_PATHS.iter().any(|b| lower.contains(b)) {
            continue;
        }
        result.push(DirEntry {
            name,
            is_dir: meta.as_ref().map_or(false, |m| m.is_dir()),
            size: meta.as_ref().map_or(0, |m| m.len()),
        });
    }
    result.sort_by(|a, b| a.name.cmp(&b.name));
    Ok(result)
}

// ---------------------------------------------------------------------------
// Tool: read_file (with Iron Gate size limit)
// ---------------------------------------------------------------------------

const MAX_READ_BYTES: u64 = 1_048_576; // 1 MB

fn read_file(path: &str) -> Result<FileContent, String> {
    let meta = fs::metadata(path)
        .map_err(|e| format!("Cannot stat file: {e}"))?;

    if meta.len() > MAX_READ_BYTES {
        return Err(format!(
            "Iron Gate: file too large ({} bytes > {} limit)",
            meta.len(),
            MAX_READ_BYTES
        ));
    }

    let content = fs::read_to_string(path)
        .map_err(|e| format!("Failed to read file: {e}"))?;

    Ok(FileContent {
        path: path.into(),
        size: meta.len(),
        lines: content.lines().count(),
        content,
    })
}

#[derive(Debug, Serialize)]
struct FileContent {
    path: String,
    size: u64,
    lines: usize,
    content: String,
}

// ---------------------------------------------------------------------------
// Tool: stat_file
// ---------------------------------------------------------------------------

fn stat_file(path: &str) -> Result<FileStat, String> {
    let meta = fs::metadata(path)
        .map_err(|e| format!("Cannot stat: {e}"))?;

    Ok(FileStat {
        path: path.into(),
        exists: true,
        is_dir: meta.is_dir(),
        is_file: meta.is_file(),
        size: meta.len(),
        readonly: meta.permissions().readonly(),
    })
}

#[derive(Debug, Serialize)]
struct FileStat {
    path: String,
    exists: bool,
    is_dir: bool,
    is_file: bool,
    size: u64,
    readonly: bool,
}

// ---------------------------------------------------------------------------
// HTTP Handlers — each one runs PDG before executing
// ---------------------------------------------------------------------------

fn classify_taint(source: &str) -> TaintLabel {
    match source {
        "control_plane" | "kernel" | "merlin" => TaintLabel::TrustedInternal,
        _ => TaintLabel::UntrustedSource,
    }
}

fn extract_path(args: &serde_json::Value) -> Option<&str> {
    args.get("path").and_then(|v| v.as_str())
}

async fn handle_tool(Json(msg): Json<A2AMessage>) -> impl IntoResponse {
    let tool = &msg.payload.tool_name;
    let taint = classify_taint(&msg.source);
    let path = extract_path(&msg.payload.arguments);

    // PDG gate
    let verdict = pdg_evaluate(tool, taint, path);
    if !verdict.allowed {
        let reason = verdict.reason.clone();
        return (
            StatusCode::FORBIDDEN,
            Json(ToolResult {
                tool_name: tool.clone(),
                success: false,
                result: serde_json::Value::Null,
                error: Some(reason),
                pdg_verdict: Some(verdict),
            }),
        );
    }

    let p = path.unwrap_or(".");

    let result = match tool.as_str() {
        "list_directory" => match list_directory(p) {
            Ok(entries) => ToolResult {
                tool_name: tool.clone(),
                success: true,
                result: serde_json::to_value(entries).unwrap_or_default(),
                error: None,
                pdg_verdict: Some(verdict),
            },
            Err(e) => ToolResult {
                tool_name: tool.clone(),
                success: false,
                result: serde_json::Value::Null,
                error: Some(e),
                pdg_verdict: Some(verdict),
            },
        },
        "read_file" => match read_file(p) {
            Ok(content) => ToolResult {
                tool_name: tool.clone(),
                success: true,
                result: serde_json::to_value(content).unwrap_or_default(),
                error: None,
                pdg_verdict: Some(verdict),
            },
            Err(e) => ToolResult {
                tool_name: tool.clone(),
                success: false,
                result: serde_json::Value::Null,
                error: Some(e),
                pdg_verdict: Some(verdict),
            },
        },
        "stat_file" => match stat_file(p) {
            Ok(stat) => ToolResult {
                tool_name: tool.clone(),
                success: true,
                result: serde_json::to_value(stat).unwrap_or_default(),
                error: None,
                pdg_verdict: Some(verdict),
            },
            Err(e) => ToolResult {
                tool_name: tool.clone(),
                success: false,
                result: serde_json::Value::Null,
                error: Some(e),
                pdg_verdict: Some(verdict),
            },
        },
        "settle_compute" => {
            let args = &msg.payload.arguments;
            let source_agent = args.get("source_agent").and_then(|v| v.as_str()).unwrap_or("unknown");
            let target_agent = args.get("target_agent").and_then(|v| v.as_str()).unwrap_or("unknown");
            let units = args.get("compute_units").and_then(|v| v.as_u64()).unwrap_or(0);
            let desc = args.get("description").and_then(|v| v.as_str()).unwrap_or("");

            // Load persistent identity from vault; fall back to ephemeral if not found
            let identity = ap2_settlement::load_vault_identity()
                .unwrap_or_else(|| ap2_settlement::AgentIdentity::generate());
            let tx = ap2_settlement::Transaction {
                tx_id: format!("tx_{}", uuid::Uuid::new_v4().simple()),
                source_agent: source_agent.into(),
                target_agent: target_agent.into(),
                compute_units: units,
                timestamp: chrono::Utc::now().to_rfc3339(),
                artifact_hash: "".into(), // Should be passed in
                description: desc.into(),
            };

            let settlement = identity.sign_transaction(tx);
            ToolResult {
                tool_name: tool.clone(),
                success: true,
                result: serde_json::to_value(settlement).unwrap_or_default(),
                error: None,
                pdg_verdict: Some(verdict),
            }
        },
        _ => ToolResult {
            tool_name: tool.clone(),
            success: false,
            result: serde_json::Value::Null,
            error: Some(format!("Unknown tool: {tool}")),
            pdg_verdict: Some(verdict),
        },
    };

    (StatusCode::OK, Json(result))
}

// Backward-compatible route handler for /tool/list_directory
async fn handle_list_directory(json: Json<A2AMessage>) -> impl IntoResponse {
    handle_tool(json).await
}

// ---------------------------------------------------------------------------
// Server bootstrap
// ---------------------------------------------------------------------------

#[tokio::main]
async fn main() {
    let token_present = bifrost::init();
    println!("[HEIMDALL] Bifrost gate armed | token_present={token_present}");

    let app = Router::new()
        // Unified tool dispatcher
        .route("/tool/{tool_name}", post(handle_tool))
        // Legacy route for backward compatibility
        .route("/tool/list_directory", post(handle_list_directory))
        // Sir Heimdall watches every ingress
        .layer(middleware::from_fn(bifrost::gate));

    let addr = SocketAddr::from(([127, 0, 0, 1], 3001));
    println!("[KINETIC_EDGE] MCP server with AgentArmor PDG listening on {addr}");
    println!("[AGENT_ARMOR] PDG rules: 4 active | Sandbox: CAMELOT_OS + .camelot");
    println!("[AGENT_ARMOR] Blocked patterns: {} | Allowed roots: {}",
        BLOCKED_PATHS.len(), ALLOWED_ROOTS.len());

    let listener = tokio::net::TcpListener::bind(addr)
        .await
        .expect("Failed to bind");

    axum::serve(
        listener,
        app.into_make_service_with_connect_info::<SocketAddr>(),
    )
        .await
        .expect("Server error");
}
