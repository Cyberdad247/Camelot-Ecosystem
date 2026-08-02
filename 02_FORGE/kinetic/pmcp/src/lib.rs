/*
 * pmcp — pure-Rust MCP (Model Context Protocol) implementation.
 *
 * Phase 1 additive scaffold for HiveIDE_Apex_v1000 ExecutionDAG.
 * Reversible: this crate does NOT yet replace any Node.js surface.
 * The actual destructive cut is held under HUMAN_GATE in
 * `control_plane.soul_oversight.pre_execute` and requires
 * CAMELOT_DASHBOARD_OPERATOR_TOKEN.
 */

#![deny(unsafe_code)]
#![warn(rust_2018_idioms)]

pub mod types;
pub mod transport;
pub mod server;
pub mod client;

pub use types::{ErrorCode, JsonRpc, Notification, Request, Response};
pub use server::Server;
pub use client::Client;
pub use transport::{StdioTransport, Transport, TransportConfig, TransportKind};

/// MCP spec version this crate targets.
pub const PROTOCOL_VERSION: &str = "2024-11-05";

/// Additive default port — sits beside the existing Node.js edge on 3001
/// without colliding. Real cut-over happens in Phase 1 cut window.
pub const SOCKET_DEFAULT_PORT: u16 = 3002;

/// Crate-level error.
#[derive(Debug, thiserror::Error)]
pub enum PmcpError {
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
    #[error("serde error: {0}")]
    Serde(#[from] serde_json::Error),
    #[error("transport error: {0}")]
    Transport(String),
    #[error("protocol error: code={code:?} message={message}")]
    Protocol {
        code: crate::types::ErrorCode,
        message: String,
    },
}

pub type Result<T> = std::result::Result<T, PmcpError>;
