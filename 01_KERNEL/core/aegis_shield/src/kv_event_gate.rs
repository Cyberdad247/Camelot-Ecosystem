// SPDX-License-Identifier: MIT

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum KVEventType {
    Put,
    Delete,
    LeaseRenew,
    TrustUpdate,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct KVEvent {
    pub sequence: u64,
    pub tenant_id: String,
    pub event_type: KVEventType,
    pub key: String,
    pub value_hash: String,
    pub previous_hash: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EventAudit {
    pub accepted: bool,
    pub reason: String,
    pub cumulative_hash: String,
}

#[derive(Debug, Clone)]
pub struct RouterTrustGate {
    last_sequence: u64,
    last_hash: String,
}

impl Default for RouterTrustGate {
    fn default() -> Self {
        Self {
            last_sequence: 0,
            last_hash: "genesis".to_string(),
        }
    }
}

impl RouterTrustGate {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn audit_event(&mut self, event: &KVEvent) -> EventAudit {
        if event.sequence <= self.last_sequence {
            return EventAudit {
                accepted: false,
                reason: "non_monotonic_sequence".to_string(),
                cumulative_hash: self.last_hash.clone(),
            };
        }

        if event.previous_hash != self.last_hash {
            return EventAudit {
                accepted: false,
                reason: "previous_hash_mismatch".to_string(),
                cumulative_hash: self.last_hash.clone(),
            };
        }

        let cumulative_hash = calculate_cumulative_hash(event);
        self.last_sequence = event.sequence;
        self.last_hash = cumulative_hash.clone();

        EventAudit {
            accepted: true,
            reason: "accepted".to_string(),
            cumulative_hash,
        }
    }

    pub fn last_hash(&self) -> &str {
        &self.last_hash
    }
}

pub fn audit_event(gate: &mut RouterTrustGate, event: &KVEvent) -> EventAudit {
    gate.audit_event(event)
}

pub fn calculate_cumulative_hash(event: &KVEvent) -> String {
    let canonical = serde_json::to_vec(event).expect("KVEvent serialization is infallible");
    let mut hasher = Sha256::new();
    hasher.update(canonical);
    hex::encode(hasher.finalize())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_out_of_order_events() {
        let mut gate = RouterTrustGate::new();
        let first = KVEvent {
            sequence: 1,
            tenant_id: "tenant-a".to_string(),
            event_type: KVEventType::Put,
            key: "alpha".to_string(),
            value_hash: "v1".to_string(),
            previous_hash: "genesis".to_string(),
        };

        assert!(gate.audit_event(&first).accepted);
        assert!(!gate.audit_event(&first).accepted);
    }
}

