//! MicroVM Execution Lease & Authority Binding
//! ============================================

use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionLease {
    pub lease_id: String,
    pub target_knight: String,
    pub capabilities: Vec<String>,
    pub issued_at_epoch_sec: u64,
    pub ttl_seconds: u64,
}

impl ExecutionLease {
    pub fn new(
        lease_id: impl Into<String>,
        target_knight: impl Into<String>,
        capabilities: Vec<String>,
        ttl_seconds: u64,
    ) -> Self {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        Self {
            lease_id: lease_id.into(),
            target_knight: target_knight.into(),
            capabilities,
            issued_at_epoch_sec: now,
            ttl_seconds,
        }
    }

    pub fn is_active(&self) -> bool {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        now <= self.issued_at_epoch_sec + self.ttl_seconds
    }

    pub fn allows_action(&self, action: &str) -> bool {
        self.capabilities.iter().any(|c| c == action || c == "*")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lease_validity_and_permission() {
        let lease = ExecutionLease::new(
            "lease_codex_01",
            "SIR_CODEX",
            vec!["ast:write".into(), "kernel:boot".into()],
            3600,
        );

        assert!(lease.is_active());
        assert!(lease.allows_action("ast:write"));
        assert!(!lease.allows_action("root:kill"));
    }
}
