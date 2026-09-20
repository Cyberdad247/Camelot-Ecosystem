// SPDX-License-Identifier: MIT
/**
 * Canonical TypeScript contract interfaces for Camelot-OS L2 Contracts (P0).
 * Generated from packages/contracts/ Draft 2020-12 schemas.
 */

export type AuthorityVectorTuple = [number, number, number, number, number, number];

export interface Actor {
  schema_version: "camelot-actor/1";
  actor_id: string;
  role: "operator" | "knight" | "node" | "provider" | "service";
  trust_band: "sovereign" | "attested" | "witness" | "untrusted";
  public_key_id: string;
}

export interface Tenant {
  schema_version: "camelot-tenant/1";
  tenant_id: string;
  agency_id?: string;
  max_risk_tier_allowed: "T0" | "T1" | "T2" | "T3" | "T4";
  policy_overrides?: Record<string, unknown>;
}

export interface Workspace {
  schema_version: "camelot-workspace/1";
  workspace_id: string;
  tenant_id: string;
  namespace_prefix: string;
  quota_bytes: number;
}

export interface Task {
  schema_version: "camelot-task/1";
  task_id: string;
  status: "pending" | "evaluating" | "approved" | "executing" | "completed" | "failed";
  manifest_id: string;
  lease_id?: string;
}

export interface EffectManifest {
  schema_version: "camelot-effect-manifest/1";
  manifest_id: string;
  effect_class: string;
  declared_risk_tier: "T0" | "T1" | "T2" | "T3" | "T4";
  declaration_hash: string;
  immutable_inputs: Record<string, string>;
}

export interface PolicyDecision {
  schema_version: "camelot-policy-decision/1";
  decision_id: string;
  task_id: string;
  manifest_hash: string;
  decision: "ALLOW" | "DENY" | "APPROVAL_REQUIRED";
  computed_risk_tier: "T0" | "T1" | "T2" | "T3" | "T4";
  allowlist: string[];
  policy_bundle_hash: string;
}

export interface ApprovalCertificate {
  schema_version: "camelot-approval-certificate/1";
  certificate_id: string;
  task_id: string;
  manifest_hash: string;
  approver: string;
  device_id: string;
  authority_vector: AuthorityVectorTuple;
  decision: "APPROVED" | "REJECTED" | "QUORUM_PARTIAL";
  reason?: string;
  valid_until: string;
  signature: {
    algorithm: "ed25519" | "webauthn_p256";
    public_key_id: string;
    value: string;
  };
}

export interface CapabilityLease {
  schema_version: "camelot-lease/1";
  lease_id: string;
  authority_epoch?: number;
  authority_vector?: AuthorityVectorTuple;
  manifest_hash: string;
  task_id: string;
  correlation_id: string;
  tenant_id: string;
  effect_class: string;
  declared_risk_tier: "T0" | "T1" | "T2" | "T3" | "T4";
  subject: {
    actor_id: string;
    node_id: string;
    node_trust_band: string;
  };
  permissions: Record<string, unknown>;
  limits: Record<string, unknown>;
}

export interface VfsAttestation {
  schema_version: "camelot-vfs-attestation/1" | "camelot-vfs-attestation/2";
  attestation_id: string;
  task_id: string;
  tenant_id?: string;
  workspace_ref: string;
  source_classification: "tier0" | "tier1" | "tier2" | "tier3" | "tier4";
  pinned_revision?: string;
  checks: string[];
  attested_at: string;
  signature: string;
}

export interface EvidenceEnvelope {
  schema_version: "operator-evidence/1";
  envelope_id: string;
  kind: string;
  correlation_id: string;
  integrity: string;
  receipt_ref?: string;
  parent_hash?: string;
  payload: Record<string, unknown>;
}

export interface GideonVerdict {
  schema_version: "camelot-gideon-verdict/1";
  verdict_id: string;
  task_id: string;
  verdict: "PASS" | "BLOCK";
  score: number;
  gates: Record<string, boolean>;
  declared_risk_tier_matches_observable_effect: boolean;
}

export interface ArthurResolution {
  schema_version: "camelot-arthur-resolution/1";
  resolution_id: string;
  directive_type: "SOVEREIGN_OVERRIDE" | "EMERGENCY_REZERO" | "ETHICAL_COMPASS_VETO" | "CONSENSUS_RATIFICATION" | "PROMOTION_AUTHORIZATION";
  target_scope: string;
  rationale: string;
  authority_vector: AuthorityVectorTuple;
  timestamp: string;
  sovereign_seal: {
    king_id: "ARTHUR_OMEGA";
    seal_type: "SOVEREIGN_GOLDEN_SEAL" | "EMERGENCY_HALT_SEAL";
    ed25519_signature: string;
  };
}

export interface Receipt {
  schema_version: "camelot-receipt/1" | "camelot-receipt/2";
  receipt_id: string;
  parent_hash: string;
  self_hash?: string;
  chain_height: number;
  tenant_id: string;
  correlation_id: string;
  task_id: string;
  authority_epoch?: number;
  authority_vector?: AuthorityVectorTuple;
  effect_class: string;
  declared_risk_tier: "T0" | "T1" | "T2" | "T3" | "T4";
  timestamp: string;
  actor: {
    id: string;
    role: string;
    node_id: string;
    trust_band: string;
  };
  event: string;
  proof: {
    hash_algorithm: string;
    signature_algorithm: string;
    signer: string;
    signature: string;
  };
}

export interface AuthorityEpoch {
  schema_version: "camelot-authority-epoch/1";
  epoch_id: string;
  authority_vector: AuthorityVectorTuple;
  fenced_leader_node: string | null;
  active_leader_node: string;
  policy_bundle_hash: string;
  contracts_lock_hash: string;
  issued_at: string;
  expires_at?: string | null;
  signer: {
    actor_id: string;
    trust_band: "sovereign" | "attested" | "witness";
    signature_algorithm: "ed25519" | "p256";
    signature: string;
  };
}

export interface Promotion {
  schema_version: "camelot-promotion/1";
  promotion_id: string;
  mode: "auto_failover" | "operator_promoted";
  witness_lock_ref: string;
  attested_quorum_count: number;
  fenced_old_vps: string;
}

export interface WorkspaceEvent {
  schema_version: "camelot-workspace-event/1";
  event_id: string;
  workspace_id: string;
  lease_id: string;
  task_id?: string;
  mutation_type: "CREATE" | "UPDATE" | "DELETE" | "PATCH" | "COMPENDIUM_MUTATE";
  path: string;
  pre_hash: string | null;
  post_hash: string;
  bytes_delta?: number;
  timestamp: string;
}
