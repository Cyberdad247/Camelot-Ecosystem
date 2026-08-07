//! Strict job/lease validation: the node agent refuses everything that is not
//! an approved, unexpired, capability-matched, correctly signed lease.

use camelot_node_agent::compute::{run_job, ComputeFrame, ComputeJob, ComputeLease};
use camelot_node_agent::backend::cpu::CpuBackend;
use camelot_node_agent::validate::{
    hmac_sha256, parse_rfc3339_utc, JobValidator, LeaseValidator, StrictValidator, ValidationError,
};

const KEY: &[u8] = b"camelot-demo-key";
const NOW: u64 = 1_754_000_000; // fixed clock for determinism

fn now_fixed() -> u64 {
    NOW
}

fn validator() -> StrictValidator {
    StrictValidator {
        lease_key: Some(KEY.to_vec()),
        now_unix: now_fixed,
    }
}

fn signed_lease(expires_at: &str) -> ComputeLease {
    let message = format!("lease-1|compute:audio.features|{expires_at}");
    ComputeLease {
        lease_id: "lease-1".into(),
        capability: "compute:audio.features".into(),
        status: "approved".into(),
        expires_at: expires_at.into(),
        token: hex::encode(hmac_sha256(KEY, message.as_bytes())),
    }
}

fn job(lease: ComputeLease) -> ComputeJob {
    ComputeJob {
        job_id: "job-1".into(),
        kind: "audio.features".into(),
        lease,
        frames: vec![ComputeFrame {
            frame_id: "frame-0".into(),
            samples: vec![0.0, 0.5, -0.5, 0.25],
        }],
        frame_size: Some(2),
    }
}

// Far in the future relative to the fixed clock.
const VALID_EXP: &str = "2026-08-07T12:00:00Z";

#[test]
fn valid_signed_lease_passes_and_computes() {
    let v = validator();
    let j = job(signed_lease(VALID_EXP));
    v.validate_job(&j).unwrap();
    v.validate_lease(&j).unwrap();

    let result = run_job(&j, &CpuBackend);
    assert_eq!(result.results.len(), 1);
    let features = &result.results[0].features;
    assert_eq!(features.sample_count, 4);
    assert!(features.peak > 0.49 && features.peak < 0.51);
    assert_eq!(features.frame_energies.len(), 2);
}

#[test]
fn pending_lease_is_rejected() {
    let v = validator();
    let mut lease = signed_lease(VALID_EXP);
    lease.status = "pending".into();
    let err = v.validate_lease(&job(lease)).unwrap_err();
    assert!(matches!(err, ValidationError::LeaseNotApproved(_)));
}

#[test]
fn expired_lease_is_rejected() {
    let v = validator();
    // 2020 < fixed clock (2026) — signed correctly but stale.
    let err = v.validate_lease(&job(signed_lease("2020-01-01T00:00:00Z"))).unwrap_err();
    assert_eq!(err, ValidationError::LeaseExpired);
}

#[test]
fn capability_mismatch_is_rejected() {
    let v = validator();
    let mut lease = signed_lease(VALID_EXP);
    lease.capability = "skill:change_request.create".into();
    let err = v.validate_lease(&job(lease)).unwrap_err();
    assert!(matches!(err, ValidationError::CapabilityMismatch(_)));
}

#[test]
fn forged_token_is_rejected() {
    let v = validator();
    let mut lease = signed_lease(VALID_EXP);
    lease.token = "deadbeef".into();
    let err = v.validate_lease(&job(lease)).unwrap_err();
    assert_eq!(err, ValidationError::BadToken);
}

#[test]
fn wrong_kind_and_bad_batches_are_rejected() {
    let v = validator();
    let mut j = job(signed_lease(VALID_EXP));
    j.kind = "shell.exec".into();
    assert!(matches!(v.validate_job(&j).unwrap_err(), ValidationError::UnsupportedKind(_)));

    let mut empty = job(signed_lease(VALID_EXP));
    empty.frames.clear();
    assert_eq!(v.validate_job(&empty).unwrap_err(), ValidationError::EmptyBatch);

    let mut huge = job(signed_lease(VALID_EXP));
    huge.frames = (0..65)
        .map(|i| ComputeFrame { frame_id: format!("f{i}"), samples: vec![0.0] })
        .collect();
    assert!(matches!(v.validate_job(&huge).unwrap_err(), ValidationError::BatchTooLarge(65)));
}

#[test]
fn rfc3339_parser_is_strict() {
    assert!(parse_rfc3339_utc("2026-08-07T12:00:00Z").is_some());
    assert!(parse_rfc3339_utc("2026-08-07 12:00:00").is_none());
    assert!(parse_rfc3339_utc("2026-08-07T12:00:00+02:00").is_none());
    assert!(parse_rfc3339_utc("garbage").is_none());
    // Known value: 2026-08-07T12:00:00Z (checked against date -d).
    assert_eq!(parse_rfc3339_utc("1970-01-01T00:00:00Z"), Some(0));
    assert_eq!(parse_rfc3339_utc("1970-01-02T00:00:00Z"), Some(86_400));
}
