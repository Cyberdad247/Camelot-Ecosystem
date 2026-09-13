// SPDX-License-Identifier: MIT
// Package contracts provides canonical Go struct bindings for Camelot-OS L2 Contracts (P0).
package contracts

type AuthorityVectorTuple [6]int

type Actor struct {
	SchemaVersion string `json:"schema_version"`
	ActorID       string `json:"actor_id"`
	Role          string `json:"role"`
	TrustBand     string `json:"trust_band"`
	PublicKeyID   string `json:"public_key_id"`
}

type Tenant struct {
	SchemaVersion      string                 `json:"schema_version"`
	TenantID           string                 `json:"tenant_id"`
	AgencyID           string                 `json:"agency_id,omitempty"`
	MaxRiskTierAllowed string                 `json:"max_risk_tier_allowed"`
	PolicyOverrides    map[string]interface{} `json:"policy_overrides,omitempty"`
}

type Workspace struct {
	SchemaVersion   string `json:"schema_version"`
	WorkspaceID     string `json:"workspace_id"`
	TenantID        string `json:"tenant_id"`
	NamespacePrefix string `json:"namespace_prefix"`
	QuotaBytes      int64  `json:"quota_bytes"`
}

type Task struct {
	SchemaVersion string `json:"schema_version"`
	TaskID        string `json:"task_id"`
	Status        string `json:"status"`
	ManifestID    string `json:"manifest_id"`
	LeaseID       string `json:"lease_id,omitempty"`
}

type EffectManifest struct {
	SchemaVersion     string            `json:"schema_version"`
	ManifestID        string            `json:"manifest_id"`
	EffectClass       string            `json:"effect_class"`
	DeclaredRiskTier  string            `json:"declared_risk_tier"`
	DeclarationHash   string            `json:"declaration_hash"`
	ImmutableInputs   map[string]string `json:"immutable_inputs"`
}

type PolicyDecision struct {
	SchemaVersion    string   `json:"schema_version"`
	DecisionID       string   `json:"decision_id"`
	TaskID           string   `json:"task_id"`
	ManifestHash     string   `json:"manifest_hash"`
	Decision         string   `json:"decision"`
	ComputedRiskTier string   `json:"computed_risk_tier"`
	Allowlist        []string `json:"allowlist"`
	PolicyBundleHash string   `json:"policy_bundle_hash"`
}

type ApprovalCertificate struct {
	SchemaVersion   string               `json:"schema_version"`
	CertificateID   string               `json:"certificate_id"`
	TaskID          string               `json:"task_id"`
	ManifestHash    string               `json:"manifest_hash"`
	Approver        string               `json:"approver"`
	DeviceID        string               `json:"device_id"`
	AuthorityVector AuthorityVectorTuple `json:"authority_vector"`
	Decision        string               `json:"decision"`
	Reason          string               `json:"reason,omitempty"`
	ValidUntil      string               `json:"valid_until"`
	Signature       struct {
		Algorithm  string `json:"algorithm"`
		PublicKeyID string `json:"public_key_id"`
		Value      string `json:"value"`
	} `json:"signature"`
}

type CapabilityLease struct {
	SchemaVersion    string                 `json:"schema_version"`
	LeaseID          string                 `json:"lease_id"`
	AuthorityEpoch   int                    `json:"authority_epoch,omitempty"`
	AuthorityVector  *AuthorityVectorTuple  `json:"authority_vector,omitempty"`
	ManifestHash     string                 `json:"manifest_hash"`
	TaskID           string                 `json:"task_id"`
	CorrelationID    string                 `json:"correlation_id"`
	TenantID         string                 `json:"tenant_id"`
	EffectClass      string                 `json:"effect_class"`
	DeclaredRiskTier string                 `json:"declared_risk_tier"`
	Subject          struct {
		ActorID       string `json:"actor_id"`
		NodeID        string `json:"node_id"`
		NodeTrustBand string `json:"node_trust_band"`
	} `json:"subject"`
	Permissions map[string]interface{} `json:"permissions"`
	Limits      map[string]interface{} `json:"limits"`
}

type VfsAttestation struct {
	SchemaVersion        string   `json:"schema_version"`
	AttestationID        string   `json:"attestation_id"`
	TaskID               string   `json:"task_id"`
	TenantID             string   `json:"tenant_id,omitempty"`
	WorkspaceRef         string   `json:"workspace_ref"`
	SourceClassification string   `json:"source_classification"`
	PinnedRevision       string   `json:"pinned_revision,omitempty"`
	Checks               []string `json:"checks"`
	AttestedAt           string   `json:"attested_at"`
	Signature            string   `json:"signature"`
}

type EvidenceEnvelope struct {
	SchemaVersion string                 `json:"schema_version"`
	EnvelopeID    string                 `json:"envelope_id"`
	Kind          string                 `json:"kind"`
	CorrelationID string                 `json:"correlation_id"`
	Integrity     string                 `json:"integrity"`
	ReceiptRef    string                 `json:"receipt_ref,omitempty"`
	ParentHash    string                 `json:"parent_hash,omitempty"`
	Payload       map[string]interface{} `json:"payload"`
}

type GideonVerdict struct {
	SchemaVersion                                string          `json:"schema_version"`
	VerdictID                                    string          `json:"verdict_id"`
	TaskID                                       string          `json:"task_id"`
	Verdict                                      string          `json:"verdict"`
	Score                                        float64         `json:"score"`
	Gates                                        map[string]bool `json:"gates"`
	DeclaredRiskTierMatchesObservableEffect      bool            `json:"declared_risk_tier_matches_observable_effect"`
}

type ArthurResolution struct {
	SchemaVersion   string               `json:"schema_version"`
	ResolutionID    string               `json:"resolution_id"`
	DirectiveType   string               `json:"directive_type"`
	TargetScope     string               `json:"target_scope"`
	Rationale       string               `json:"rationale"`
	AuthorityVector AuthorityVectorTuple `json:"authority_vector"`
	Timestamp       string               `json:"timestamp"`
	SovereignSeal   struct {
		KingID           string `json:"king_id"`
		SealType         string `json:"seal_type"`
		Ed25519Signature string `json:"ed25519_signature"`
	} `json:"sovereign_seal"`
}

type Receipt struct {
	SchemaVersion    string                `json:"schema_version"`
	ReceiptID        string                `json:"receipt_id"`
	ParentHash       string                `json:"parent_hash"`
	SelfHash         string                `json:"self_hash,omitempty"`
	ChainHeight      int64                 `json:"chain_height"`
	TenantID         string                `json:"tenant_id"`
	CorrelationID    string                `json:"correlation_id"`
	TaskID           string                `json:"task_id"`
	AuthorityEpoch   int                   `json:"authority_epoch,omitempty"`
	AuthorityVector  *AuthorityVectorTuple `json:"authority_vector,omitempty"`
	EffectClass      string                `json:"effect_class"`
	DeclaredRiskTier string                `json:"declared_risk_tier"`
	Timestamp        string                `json:"timestamp"`
	Actor            struct {
		ID        string `json:"id"`
		Role      string `json:"role"`
		NodeID    string `json:"node_id"`
		TrustBand string `json:"trust_band"`
	} `json:"actor"`
	Event string `json:"event"`
	Proof struct {
		HashAlgorithm      string `json:"hash_algorithm"`
		SignatureAlgorithm string `json:"signature_algorithm"`
		Signer             string `json:"signer"`
		Signature          string `json:"signature"`
	} `json:"proof"`
}

type AuthorityEpoch struct {
	SchemaVersion     string               `json:"schema_version"`
	EpochID           string               `json:"epoch_id"`
	AuthorityVector   AuthorityVectorTuple `json:"authority_vector"`
	FencedLeaderNode  *string              `json:"fenced_leader_node"`
	ActiveLeaderNode  string               `json:"active_leader_node"`
	PolicyBundleHash  string               `json:"policy_bundle_hash"`
	ContractsLockHash string               `json:"contracts_lock_hash"`
	IssuedAt          string               `json:"issued_at"`
	ExpiresAt         *string              `json:"expires_at,omitempty"`
	Signer            struct {
		ActorID            string `json:"actor_id"`
		TrustBand          string `json:"trust_band"`
		SignatureAlgorithm string `json:"signature_algorithm"`
		Signature          string `json:"signature"`
	} `json:"signer"`
}

type Promotion struct {
	SchemaVersion        string `json:"schema_version"`
	PromotionID          string `json:"promotion_id"`
	Mode                 string `json:"mode"`
	WitnessLockRef       string `json:"witness_lock_ref"`
	AttestedQuorumCount  int    `json:"attested_quorum_count"`
	FencedOldVPS         string `json:"fenced_old_vps"`
}

type WorkspaceEvent struct {
	SchemaVersion string  `json:"schema_version"`
	EventID       string  `json:"event_id"`
	WorkspaceID   string  `json:"workspace_id"`
	LeaseID       string  `json:"lease_id"`
	TaskID        string  `json:"task_id,omitempty"`
	MutationType  string  `json:"mutation_type"`
	Path          string  `json:"path"`
	PreHash       *string `json:"pre_hash"`
	PostHash      string  `json:"post_hash"`
	BytesDelta    int64   `json:"bytes_delta,omitempty"`
	Timestamp     string  `json:"timestamp"`
}
