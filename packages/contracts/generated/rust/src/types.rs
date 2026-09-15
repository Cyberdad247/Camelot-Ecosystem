// SPDX-License-Identifier: MIT
//! Canonical Rust serde struct bindings for Camelot-OS L2 Contracts (P0).
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

pub type AuthorityVectorTuple = [u64; 6];

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Actor {
    pub schema_version: String,
    pub actor_id: String,
    pub role: String,
    pub trust_band: String,
    pub public_key_id: String,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Tenant {
    pub schema_version: String,
    pub tenant_id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub agency_id: Option<String>,
    pub max_risk_tier_allowed: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub policy_overrides: Option<HashMap<String, serde_json::Value>>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Workspace {
    pub schema_version: String,
    pub workspace_id: String,
    pub tenant_id: String,
    pub namespace_prefix: String,
    pub quota_bytes: u64,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Task {
    pub schema_version: String,
    pub task_id: String,
    pub status: String,
    pub manifest_id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub lease_id: Option<String>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct EffectManifest {
    pub schema_version: String,
    pub manifest_id: String,
    pub effect_class: String,
    pub declared_risk_tier: String,
    pub declaration_hash: String,
    pub immutable_inputs: HashMap<String, String>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct PolicyDecision {
    pub schema_version: String,
    pub decision_id: String,
    pub task_id: String,
    pub manifest_hash: String,
    pub decision: String,
    pub computed_risk_tier: String,
    pub allowlist: Vec<String>,
    pub policy_bundle_hash: String,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ApprovalCertificateSignature {
    pub algorithm: String,
    pub public_key_id: String,
    pub value: String,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ApprovalCertificate {
    pub schema_version: String,
    pub certificate_id: String,
    pub task_id: String,
    pub manifest_hash: String,
    pub approver: String,
    pub device_id: String,
    pub authority_vector: AuthorityVectorTuple,
    pub decision: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub reason: Option<String>,
    pub valid_until: String,
    pub signature: ApprovalCertificateSignature,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct CapabilityLeaseSubject {
    pub actor_id: String,
    pub node_id: String,
    pub node_trust_band: String,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct CapabilityLease {
    pub schema_version: String,
    pub lease_id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub authority_epoch: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub authority_vector: Option<AuthorityVectorTuple>,
    pub manifest_hash: String,
    pub task_id: String,
    pub correlation_id: String,
    pub tenant_id: String,
    pub effect_class: String,
    pub declared_risk_tier: String,
    pub subject: CapabilityLeaseSubject,
    pub permissions: HashMap<String, serde_json::Value>,
    pub limits: HashMap<String, serde_json::Value>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct VfsAttestation {
    pub schema_version: String,
    pub attestation_id: String,
    pub task_id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tenant_id: Option<String>,
    pub workspace_ref: String,
    pub source_classification: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub pinned_revision: Option<String>,
    pub checks: Vec<String>,
    pub attested_at: String,
    pub signature: String,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct EvidenceEnvelope {
    pub schema_version: String,
    pub envelope_id: String,
    pub kind: String,
    pub correlation_id: String,
    pub integrity: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub receipt_ref: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parent_hash: Option<String>,
    pub payload: HashMap<String, serde_json::Value>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct GideonVerdict {
    pub schema_version: String,
    pub verdict_id: String,
    pub task_id: String,
    pub verdict: String,
    pub score: f64,
    pub gates: HashMap<String, bool>,
    pub declared_risk_tier_matches_observable_effect: bool,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ArthurResolutionSeal {
    pub king_id: String,
    pub seal_type: String,
    pub ed25519_signature: String,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ArthurResolution {
    pub schema_version: String,
    pub resolution_id: String,
    pub directive_type: String,
    pub target_scope: String,
    pub rationale: String,
    pub authority_vector: AuthorityVectorTuple,
    pub timestamp: String,
    pub sovereign_seal: ArthurResolutionSeal,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ReceiptActor {
    pub id: String,
    pub role: String,
    pub node_id: String,
    pub trust_band: String,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ReceiptProof {
    pub hash_algorithm: String,
    pub signature_algorithm: String,
    pub signer: String,
    pub signature: String,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Receipt {
    pub schema_version: String,
    pub receipt_id: String,
    pub parent_hash: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub self_hash: Option<String>,
    pub chain_height: u64,
    pub tenant_id: String,
    pub correlation_id: String,
    pub task_id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub authority_epoch: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub authority_vector: Option<AuthorityVectorTuple>,
    pub effect_class: String,
    pub declared_risk_tier: String,
    pub timestamp: String,
    pub actor: ReceiptActor,
    pub event: String,
    pub proof: ReceiptProof,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct AuthorityEpochSigner {
    pub actor_id: String,
    pub trust_band: String,
    pub signature_algorithm: String,
    pub signature: String,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct AuthorityEpoch {
    pub schema_version: String,
    pub epoch_id: String,
    pub authority_vector: AuthorityVectorTuple,
    pub fenced_leader_node: Option<String>,
    pub active_leader_node: String,
    pub policy_bundle_hash: String,
    pub contracts_lock_hash: String,
    pub issued_at: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub expires_at: Option<String>,
    pub signer: AuthorityEpochSigner,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Promotion {
    pub schema_version: String,
    pub promotion_id: String,
    pub mode: String,
    pub witness_lock_ref: String,
    pub attested_quorum_count: u32,
    pub fenced_old_vps: String,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct WorkspaceEvent {
    pub schema_version: String,
    pub event_id: String,
    pub workspace_id: String,
    pub lease_id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub task_id: Option<String>,
    pub mutation_type: String,
    pub path: String,
    pub pre_hash: Option<String>,
    pub post_hash: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bytes_delta: Option<i64>,
    pub timestamp: String,
}
