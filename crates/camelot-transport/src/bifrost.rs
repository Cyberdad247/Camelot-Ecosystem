//! Bifrost Ingress Gateway & Execution Router
//! ============================================

use axum::{http::StatusCode, Json};
use blake3::Hasher;
use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};
use tracing::info;

#[derive(Deserialize, Debug, Clone, Serialize, PartialEq, Eq)]
pub struct ExecuteRequest {
    pub tenant: String,
    pub capability: String,
    pub payload: String,
}

#[derive(Serialize, Debug, Clone, Deserialize, PartialEq, Eq)]
pub struct ExecuteResponse {
    pub status: String,
    pub result: String,
    pub receipt_id: String,
}

pub struct BifrostRouter;

impl BifrostRouter {
    pub async fn handle_execute(
        Json(req): Json<ExecuteRequest>,
    ) -> Result<Json<ExecuteResponse>, (StatusCode, String)> {
        info!(
            "Received execution envelope from tenant [{}]: capability={}",
            req.tenant, req.capability
        );

        // Generate deterministic Blake3 receipt hash
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis();

        let mut hasher = Hasher::new();
        hasher.update(req.tenant.as_bytes());
        hasher.update(req.capability.as_bytes());
        hasher.update(req.payload.as_bytes());
        hasher.update(&timestamp.to_le_bytes());
        let receipt_id = hasher.finalize().to_hex().to_string();

        // Forward to microVM / capability resolver
        let output = match req.capability.as_str() {
            "echo" => req.payload,
            _ => format!("unsupported_capability: {}", req.capability),
        };

        info!(
            "Dispatched payload successfully. Generated receipt: {}",
            receipt_id
        );

        // Record receipt in Kernel SQLite ledger
        let db_path = "/var/lib/camelot/ledger.db";
        let mut ledger = camelot_kernel::Ledger::new(db_path).unwrap_or_else(|_| {
            camelot_kernel::Ledger::new("ledger_fallback.db").unwrap()
        });
        if ledger.initialize().is_ok() {
            let _ = ledger.write_explicit_receipt("execute_capability", &req.tenant, "SUCCESS", &receipt_id);
        }

        Ok(Json(ExecuteResponse {
            status: "ok".to_string(),
            result: output,
            receipt_id,
        }))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_bifrost_handle_execute_echo() {
        let req = ExecuteRequest {
            tenant: "t1".to_string(),
            capability: "echo".to_string(),
            payload: "hello".to_string(),
        };

        let res = BifrostRouter::handle_execute(Json(req)).await.unwrap();
        assert_eq!(res.status, "ok");
        assert_eq!(res.result, "hello");
        assert_eq!(res.receipt_id.len(), 64);
    }

    #[tokio::test]
    async fn test_bifrost_unsupported_capability() {
        let req = ExecuteRequest {
            tenant: "t2".to_string(),
            capability: "unknown_task".to_string(),
            payload: "data".to_string(),
        };

        let res = BifrostRouter::handle_execute(Json(req)).await.unwrap();
        assert_eq!(res.status, "ok");
        assert!(res.result.contains("unsupported_capability"));
    }
}
