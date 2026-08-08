//! Strict job/lease validation. The node agent trusts NOTHING it receives:
//! every compute job must carry an approved, unexpired lease for the exact
//! capability, signed by the control plane (ADR-001: node authorization is
//! Camelot-owned; the node agent only verifies).

use crate::compute::{ComputeJob, CAPABILITY_AUDIO_FEATURES};
use sha2::{Digest, Sha256};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, PartialEq, Eq)]
pub enum ValidationError {
    UnsupportedKind(String),
    EmptyBatch,
    BatchTooLarge(usize),
    LeaseNotApproved(String),
    LeaseExpired,
    CapabilityMismatch(String),
    BadToken,
    MalformedExpiry,
    /// Phase 4A: the lease was minted for a different node or tenant. The
    /// agent refuses even a perfectly signed lease that is not ITS lease.
    NodeMismatch(String),
    TenantMismatch(String),
}

impl std::fmt::Display for ValidationError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::UnsupportedKind(k) => write!(f, "unsupported job kind {k:?}"),
            Self::EmptyBatch => write!(f, "job carries no frames"),
            Self::BatchTooLarge(n) => write!(f, "batch of {n} frames exceeds the limit"),
            Self::LeaseNotApproved(s) => write!(f, "lease status {s:?} is not \"approved\""),
            Self::LeaseExpired => write!(f, "lease expired"),
            Self::CapabilityMismatch(c) => write!(f, "lease capability {c:?} does not cover this job"),
            Self::BadToken => write!(f, "lease token signature invalid"),
            Self::MalformedExpiry => write!(f, "lease expiresAt is not RFC3339 UTC"),
            Self::NodeMismatch(n) => write!(f, "lease was issued for node {n:?}, not this node"),
            Self::TenantMismatch(t) => write!(f, "lease was issued for tenant {t:?}, not this tenant"),
        }
    }
}

pub const MAX_BATCH_FRAMES: usize = 64;

/// Interface for job-level checks (shape, kind, batching limits).
pub trait JobValidator {
    fn validate_job(&self, job: &ComputeJob) -> Result<(), ValidationError>;
}

/// Interface for lease-level checks (status, expiry, capability, signature).
pub trait LeaseValidator {
    fn validate_lease(&self, job: &ComputeJob) -> Result<(), ValidationError>;
}

/// The strict production validator: both interfaces, no bypasses.
pub struct StrictValidator {
    /// HMAC key shared with the control plane (hex, via CAMELOT_NODE_LEASE_KEY).
    /// None = demo mode: signature check requires a non-empty token but cannot
    /// verify provenance; health reports "lease_key": "unset" so this is loud.
    pub lease_key: Option<Vec<u8>>,
    pub now_unix: fn() -> u64,
    /// Phase 4A: when this agent is enrolled in a mesh, every lease it accepts
    /// must name THIS node and THIS tenant. Empty = standalone local agent.
    pub node_id: String,
    pub tenant_id: String,
}

pub fn system_now_unix() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

impl StrictValidator {
    pub fn from_env() -> Self {
        let lease_key = std::env::var("CAMELOT_NODE_LEASE_KEY")
            .ok()
            .filter(|k| !k.is_empty())
            .map(|k| k.into_bytes());
        Self {
            lease_key,
            now_unix: system_now_unix,
            node_id: std::env::var("CAMELOT_NODE_ID").unwrap_or_default(),
            tenant_id: std::env::var("CAMELOT_TENANT_ID").unwrap_or_default(),
        }
    }
}

impl JobValidator for StrictValidator {
    fn validate_job(&self, job: &ComputeJob) -> Result<(), ValidationError> {
        if job.kind != "audio.features" {
            return Err(ValidationError::UnsupportedKind(job.kind.clone()));
        }
        if job.frames.is_empty() {
            return Err(ValidationError::EmptyBatch);
        }
        if job.frames.len() > MAX_BATCH_FRAMES {
            return Err(ValidationError::BatchTooLarge(job.frames.len()));
        }
        Ok(())
    }
}

impl LeaseValidator for StrictValidator {
    fn validate_lease(&self, job: &ComputeJob) -> Result<(), ValidationError> {
        let lease = &job.lease;
        if lease.status != "approved" {
            return Err(ValidationError::LeaseNotApproved(lease.status.clone()));
        }
        if lease.capability != CAPABILITY_AUDIO_FEATURES {
            return Err(ValidationError::CapabilityMismatch(lease.capability.clone()));
        }
        let expires = parse_rfc3339_utc(&lease.expires_at).ok_or(ValidationError::MalformedExpiry)?;
        if (self.now_unix)() > expires {
            return Err(ValidationError::LeaseExpired);
        }
        // Node/tenant binding: an enrolled agent accepts only leases minted
        // for itself. A perfectly signed lease for another node is refused —
        // reachability is not authorization (Phase 4A rule).
        if !self.node_id.is_empty() && lease.node_id != self.node_id {
            return Err(ValidationError::NodeMismatch(lease.node_id.clone()));
        }
        if !self.tenant_id.is_empty() && lease.tenant_id != self.tenant_id {
            return Err(ValidationError::TenantMismatch(lease.tenant_id.clone()));
        }
        match &self.lease_key {
            Some(key) => {
                // Signature covers node and tenant too, so those fields
                // cannot be edited in flight.
                let message = format!(
                    "{}|{}|{}|{}|{}",
                    lease.lease_id, lease.capability, lease.expires_at, lease.node_id, lease.tenant_id
                );
                let expected = hex::encode(hmac_sha256(key, message.as_bytes()));
                if !constant_time_eq(expected.as_bytes(), lease.token.as_bytes()) {
                    return Err(ValidationError::BadToken);
                }
            }
            None => {
                if lease.token.is_empty() {
                    return Err(ValidationError::BadToken);
                }
            }
        }
        Ok(())
    }
}

/// HMAC-SHA256 (RFC 2104) over sha2 — avoids an extra dependency.
pub fn hmac_sha256(key: &[u8], message: &[u8]) -> [u8; 32] {
    const BLOCK: usize = 64;
    let mut key_block = [0u8; BLOCK];
    if key.len() > BLOCK {
        key_block[..32].copy_from_slice(&Sha256::digest(key));
    } else {
        key_block[..key.len()].copy_from_slice(key);
    }
    let mut inner = Sha256::new();
    inner.update(key_block.map(|b| b ^ 0x36));
    inner.update(message);
    let inner_hash = inner.finalize();

    let mut outer = Sha256::new();
    outer.update(key_block.map(|b| b ^ 0x5c));
    outer.update(inner_hash);
    outer.finalize().into()
}

fn constant_time_eq(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }
    a.iter().zip(b).fold(0u8, |acc, (x, y)| acc | (x ^ y)) == 0
}

/// Parse "YYYY-MM-DDTHH:MM:SSZ" (the exact shape both the Go gateway and the
/// TS contracts emit) into unix seconds. Returns None for anything else.
pub fn parse_rfc3339_utc(s: &str) -> Option<u64> {
    let bytes = s.as_bytes();
    if bytes.len() != 20 || bytes[4] != b'-' || bytes[7] != b'-' || bytes[10] != b'T'
        || bytes[13] != b':' || bytes[16] != b':' || bytes[19] != b'Z'
    {
        return None;
    }
    let num = |range: std::ops::Range<usize>| -> Option<u64> { s.get(range)?.parse().ok() };
    let (year, month, day) = (num(0..4)?, num(5..7)?, num(8..10)?);
    let (hour, minute, second) = (num(11..13)?, num(14..16)?, num(17..19)?);
    if !(1970..=9999).contains(&year) || !(1..=12).contains(&month) || !(1..=31).contains(&day)
        || hour > 23 || minute > 59 || second > 60
    {
        return None;
    }
    // Days since epoch (civil-from-days inverse, Howard Hinnant's algorithm).
    let y = if month <= 2 { year - 1 } else { year } as i64;
    let era = y / 400;
    let yoe = y - era * 400;
    let m = month as i64;
    let d = day as i64;
    let doy = (153 * (if m > 2 { m - 3 } else { m + 9 }) + 2) / 5 + d - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    let days = era * 146_097 + doe - 719_468;
    Some((days as u64) * 86_400 + hour * 3_600 + minute * 60 + second)
}
