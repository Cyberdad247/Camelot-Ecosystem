//! Sovereign Authority & Lease Management
//! ======================================

use chrono::{DateTime, Duration, Utc};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use uuid::Uuid;

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub enum AuthorityLevel {
    Drone = 0,
    Squire = 1,
    Knight = 2,
    OmegaKnight = 3,
    King = 4,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Lease {
    pub lease_id: String,
    pub holder_id: String,
    pub level: AuthorityLevel,
    pub capabilities: Vec<String>,
    pub issued_at: DateTime<Utc>,
    pub expires_at: DateTime<Utc>,
    pub token_hash: String,
}

impl Lease {
    pub fn is_valid(&self, at: DateTime<Utc>) -> bool {
        at >= self.issued_at && at <= self.expires_at
    }

    pub fn has_capability(&self, cap: &str) -> bool {
        self.capabilities.iter().any(|c| c == cap || c == "*")
    }
}

pub struct SovereignAuthority {
    secret_salt: String,
}

impl SovereignAuthority {
    pub fn new(secret_salt: impl Into<String>) -> Self {
        Self {
            secret_salt: secret_salt.into(),
        }
    }

    pub fn issue_lease(
        &self,
        holder_id: &str,
        level: AuthorityLevel,
        capabilities: Vec<String>,
        ttl_seconds: i64,
    ) -> Lease {
        let now = Utc::now();
        let expires = now + Duration::seconds(ttl_seconds);
        let lease_id = format!("lease_{}", Uuid::new_v4());

        let mut hasher = Sha256::new();
        hasher.update(lease_id.as_bytes());
        hasher.update(holder_id.as_bytes());
        hasher.update(self.secret_salt.as_bytes());
        let token_hash = hex::encode(hasher.finalize());

        Lease {
            lease_id,
            holder_id: holder_id.to_string(),
            level,
            capabilities,
            issued_at: now,
            expires_at: expires,
            token_hash,
        }
    }

    pub fn verify_token(&self, lease: &Lease) -> bool {
        let mut hasher = Sha256::new();
        hasher.update(lease.lease_id.as_bytes());
        hasher.update(lease.holder_id.as_bytes());
        hasher.update(self.secret_salt.as_bytes());
        let expected = hex::encode(hasher.finalize());
        lease.token_hash == expected
    }
}

// Minimal hex encoder for self-contained portability
mod hex {
    pub fn encode(data: impl AsRef<[u8]>) -> String {
        data.as_ref()
            .iter()
            .map(|b| format!("{:02x}", b))
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lease_lifecycle_and_verification() {
        let auth = SovereignAuthority::new("sovereign_lattice_salt");
        let lease = auth.issue_lease(
            "SIR_HELIOS",
            AuthorityLevel::OmegaKnight,
            vec!["telemetry:read".into(), "vfs:crystal_write".into()],
            60,
        );

        assert!(lease.is_valid(Utc::now()));
        assert!(lease.has_capability("telemetry:read"));
        assert!(!lease.has_capability("host:bare_metal_exec"));
        assert!(auth.verify_token(&lease));
    }

    #[test]
    fn tampered_lease_fails_verification() {
        let auth = SovereignAuthority::new("salt_a");
        let mut lease = auth.issue_lease("SIR_BORIS", AuthorityLevel::Knight, vec!["*".into()], 30);
        lease.holder_id = "MALICIOUS_ACTOR".to_string();
        assert!(!auth.verify_token(&lease));
    }
}
