//! Sovereign Security Policy & Z3 Invariant Enforcement
//! =====================================================

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KernelPolicy {
    pub max_memory_mb: usize,
    pub max_boot_time_ms: u64,
    pub require_ed25519: bool,
    pub allow_unauthenticated_mesh: bool,
}

impl Default for KernelPolicy {
    fn default() -> Self {
        Self {
            max_memory_mb: 4096, // Global Law 03 Node Ceiling
            max_boot_time_ms: 80, // 80ms boot threshold
            require_ed25519: true,
            allow_unauthenticated_mesh: false,
        }
    }
}

impl KernelPolicy {
    pub fn validate_boot_time(&self, boot_ms: u64) -> bool {
        boot_ms <= self.max_boot_time_ms
    }

    pub fn validate_memory(&self, requested_mb: usize) -> bool {
        requested_mb <= self.max_memory_mb
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn policy_defaults_enforce_law_03() {
        let policy = KernelPolicy::default();
        assert_eq!(policy.max_memory_mb, 4096);
        assert!(policy.validate_boot_time(75));
        assert!(!policy.validate_boot_time(100));
        assert!(policy.validate_memory(4096));
        assert!(!policy.validate_memory(4097));
    }
}
