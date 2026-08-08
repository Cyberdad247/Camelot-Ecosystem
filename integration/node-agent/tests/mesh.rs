//! Phase 4A: node/tenant lease binding, single-use redemption, and the
//! read-only Tailscale observer.

use camelot_node_agent::compute::{ComputeFrame, ComputeJob, ComputeLease};
use camelot_node_agent::mesh::{observe_tailscale, MeshConfig, SpentLeases};
use camelot_node_agent::validate::{hmac_sha256, LeaseValidator, StrictValidator, ValidationError};

const KEY: &[u8] = b"camelot-demo-key";
const EXP: &str = "2026-08-07T12:00:00Z";

fn now_fixed() -> u64 {
    1_754_000_000
}

fn enrolled_validator(node: &str, tenant: &str) -> StrictValidator {
    StrictValidator {
        lease_key: Some(KEY.to_vec()),
        now_unix: now_fixed,
        node_id: node.into(),
        tenant_id: tenant.into(),
    }
}

fn node_lease(node_id: &str, tenant_id: &str) -> ComputeLease {
    let message = format!("nlease-1|compute:audio.features|{EXP}|{node_id}|{tenant_id}");
    ComputeLease {
        lease_id: "nlease-1".into(),
        capability: "compute:audio.features".into(),
        status: "approved".into(),
        expires_at: EXP.into(),
        token: hex::encode(hmac_sha256(KEY, message.as_bytes())),
        node_id: node_id.into(),
        tenant_id: tenant_id.into(),
    }
}

fn job(lease: ComputeLease) -> ComputeJob {
    ComputeJob {
        job_id: "job-1".into(),
        kind: "audio.features".into(),
        lease,
        frames: vec![ComputeFrame { frame_id: "f0".into(), samples: vec![0.0, 0.5] }],
        frame_size: Some(2),
    }
}

#[test]
fn correctly_bound_node_lease_is_accepted() {
    let v = enrolled_validator("node-a", "tenant-1");
    v.validate_lease(&job(node_lease("node-a", "tenant-1"))).unwrap();
}

#[test]
fn lease_for_another_node_is_rejected_even_though_it_is_validly_signed() {
    let v = enrolled_validator("node-a", "tenant-1");
    // Genuinely signed by the gateway — but minted for node-b.
    let err = v.validate_lease(&job(node_lease("node-b", "tenant-1"))).unwrap_err();
    assert!(matches!(err, ValidationError::NodeMismatch(n) if n == "node-b"));
}

#[test]
fn lease_for_another_tenant_is_rejected() {
    let v = enrolled_validator("node-a", "tenant-1");
    let err = v.validate_lease(&job(node_lease("node-a", "tenant-2"))).unwrap_err();
    assert!(matches!(err, ValidationError::TenantMismatch(t) if t == "tenant-2"));
}

#[test]
fn node_and_tenant_cannot_be_edited_in_flight() {
    let v = enrolled_validator("node-a", "tenant-1");
    // Take a lease minted for node-b and rewrite the fields to point here.
    // The signature covers both, so the forgery fails on the token check.
    let mut forged = node_lease("node-b", "tenant-1");
    forged.node_id = "node-a".into();
    let err = v.validate_lease(&job(forged)).unwrap_err();
    assert_eq!(err, ValidationError::BadToken);
}

#[test]
fn standalone_agent_still_accepts_unbound_leases() {
    // No CAMELOT_NODE_ID configured: the Phase 1-3 direct compute path.
    let v = StrictValidator {
        lease_key: Some(KEY.to_vec()),
        now_unix: now_fixed,
        node_id: String::new(),
        tenant_id: String::new(),
    };
    let message = format!("lease-1|compute:audio.features|{EXP}||");
    let lease = ComputeLease {
        lease_id: "lease-1".into(),
        capability: "compute:audio.features".into(),
        status: "approved".into(),
        expires_at: EXP.into(),
        token: hex::encode(hmac_sha256(KEY, message.as_bytes())),
        node_id: String::new(),
        tenant_id: String::new(),
    };
    v.validate_lease(&job(lease)).unwrap();
}

#[test]
fn leases_are_single_use_at_the_node() {
    let spent = SpentLeases::new();
    assert!(spent.claim("nlease-1"), "first redemption accepted");
    assert!(!spent.claim("nlease-1"), "replay refused");
    assert!(spent.claim("nlease-2"), "a different lease is unaffected");
}

#[test]
fn tailscale_observer_never_fails_and_never_operates() {
    // Whether or not tailscale is installed, observing must be total and
    // must leave local operation intact.
    let status = observe_tailscale();
    assert!(!status.backend.is_empty());
    assert!(!status.detail.is_empty());
    if status.backend == "none" {
        assert!(!status.reachable);
    }
}

#[test]
fn mesh_is_disabled_without_explicit_configuration() {
    // Default environment: no ENABLE_TAILSCALE_MESH, no node id.
    let cfg = MeshConfig::from_env("0.0.0.0:8789");
    if std::env::var("ENABLE_TAILSCALE_MESH").is_err() {
        assert!(!cfg.enabled, "mesh must be opt-in");
    }
    // Fingerprint is stable and never contains the raw secret.
    let a = cfg.key_fingerprint();
    assert_eq!(a, cfg.key_fingerprint());
    assert!(!a.contains(&cfg.enrol_secret));
}
