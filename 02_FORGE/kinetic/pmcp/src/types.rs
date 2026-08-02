use serde::{Deserialize, Serialize};

/// JSON-RPC 2.0 error codes plus the MCP-defined extensions.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ErrorCode {
    ParseError,
    InvalidRequest,
    MethodNotFound,
    InvalidParams,
    InternalError,
}

/// JSON-RPC 2.0 envelope used both for requests and responses.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JsonRpc<T> {
    pub jsonrpc: String, // always "2.0"
    #[serde(skip_serializing_if = "Option::is_none")]
    pub id: Option<u64>,
    #[serde(flatten)]
    pub body: T,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Request {
    pub method: String,
    #[serde(default)]
    pub params: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Response {
    pub result: serde_json::Value,
}

/// Server- or client-originated notification (no `id`), per JSON-RPC 2.0.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Notification {
    pub method: String,
    #[serde(default)]
    pub params: serde_json::Value,
}
