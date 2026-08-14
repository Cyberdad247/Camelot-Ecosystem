// SPDX-License-Identifier: MIT

use sha2::{Digest, Sha256};
use std::collections::{HashMap, HashSet};

#[derive(Debug, Clone)]
pub struct TenantQuota {
    pub tenant_id: String,
    pub limit: u64,
    pub used: u64,
}

impl TenantQuota {
    pub fn new(tenant_id: impl Into<String>, limit: u64) -> Self {
        Self {
            tenant_id: tenant_id.into(),
            limit,
            used: 0,
        }
    }

    pub fn remaining(&self) -> u64 {
        self.limit.saturating_sub(self.used)
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AdmissionAudit {
    pub accepted: bool,
    pub reason: String,
    pub primary_hit: bool,
    pub secondary_hit: bool,
}

#[derive(Debug, Clone)]
pub struct SecureBloomRouter {
    salt: Vec<u8>,
    primary_bits: Vec<bool>,
    secondary_bits: Vec<bool>,
    quotas: HashMap<String, TenantQuota>,
    signatures: HashSet<String>,
}

impl SecureBloomRouter {
    pub fn new(salt: impl AsRef<[u8]>, capacity_bits: usize) -> Self {
        let size = capacity_bits.max(64);
        Self {
            salt: salt.as_ref().to_vec(),
            primary_bits: vec![false; size],
            secondary_bits: vec![false; size],
            quotas: HashMap::new(),
            signatures: HashSet::new(),
        }
    }

    pub fn set_quota(&mut self, quota: TenantQuota) {
        self.quotas.insert(quota.tenant_id.clone(), quota);
    }

    pub fn insert_signature(&mut self, tenant_id: &str, signature: &str) {
        let (primary, secondary) = self.indexes(tenant_id, signature);
        self.primary_bits[primary] = true;
        self.secondary_bits[secondary] = true;
        self.signatures
            .insert(Self::signature_key(tenant_id, signature));
    }

    pub fn audit_admission(&mut self, tenant_id: &str, signature: &str) -> AdmissionAudit {
        let Some(quota) = self.quotas.get(tenant_id) else {
            return AdmissionAudit {
                accepted: false,
                reason: "tenant_quota_missing".to_string(),
                primary_hit: false,
                secondary_hit: false,
            };
        };

        if quota.used >= quota.limit {
            return AdmissionAudit {
                accepted: false,
                reason: "tenant_quota_exhausted".to_string(),
                primary_hit: false,
                secondary_hit: false,
            };
        }

        let (primary, secondary) = self.indexes(tenant_id, signature);
        let primary_hit = self.primary_bits[primary];
        let secondary_hit = self.secondary_bits[secondary];
        let known_signature = self
            .signatures
            .contains(&Self::signature_key(tenant_id, signature));

        if primary_hit && secondary_hit && known_signature {
            if let Some(quota) = self.quotas.get_mut(tenant_id) {
                quota.used += 1;
            }
            return AdmissionAudit {
                accepted: true,
                reason: "admitted".to_string(),
                primary_hit,
                secondary_hit,
            };
        }

        AdmissionAudit {
            accepted: false,
            reason: "signature_not_admitted".to_string(),
            primary_hit,
            secondary_hit,
        }
    }

    fn indexes(&self, tenant_id: &str, signature: &str) -> (usize, usize) {
        let primary = calculate_salted_hash(&self.salt, tenant_id, signature, 0);
        let secondary = calculate_salted_hash(&self.salt, tenant_id, signature, 1);
        (
            (primary as usize) % self.primary_bits.len(),
            (secondary as usize) % self.secondary_bits.len(),
        )
    }

    fn signature_key(tenant_id: &str, signature: &str) -> String {
        format!("{tenant_id}:{signature}")
    }
}

pub fn calculate_salted_hash(
    salt: &[u8],
    tenant_id: &str,
    signature: &str,
    stage: u8,
) -> u64 {
    let mut hasher = Sha256::new();
    hasher.update(salt);
    hasher.update([stage]);
    hasher.update(tenant_id.as_bytes());
    hasher.update([0]);
    hasher.update(signature.as_bytes());
    let digest = hasher.finalize();
    u64::from_be_bytes(digest[0..8].try_into().expect("sha256 slice length"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn admits_inserted_signature_with_quota() {
        let mut router = SecureBloomRouter::new("tenant-salt", 128);
        router.set_quota(TenantQuota::new("tenant-a", 1));
        router.insert_signature("tenant-a", "tool:read");

        let audit = router.audit_admission("tenant-a", "tool:read");
        assert!(audit.accepted);
        assert_eq!(audit.reason, "admitted");

        let exhausted = router.audit_admission("tenant-a", "tool:read");
        assert!(!exhausted.accepted);
        assert_eq!(exhausted.reason, "tenant_quota_exhausted");
    }
}
