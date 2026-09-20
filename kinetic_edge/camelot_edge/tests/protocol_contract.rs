use camelot_edge::{signing_key_from_pkcs8_pem, Action, PolicySnapshot, SignedEnvelope, SignedPolicySnapshot};
use base64::{engine::general_purpose::STANDARD, Engine as _};
use serde_json::json;
use ed25519_dalek::SigningKey;

const MOTO_ID: &str = "motorola-moto-g-power-5g---2024";
const NOW: i64 = 1_700_000_000;

fn signed_snapshot(device_id: &str) -> SignedPolicySnapshot {
    let snapshot = PolicySnapshot {
        version: 1,
        device_id: device_id.to_owned(),
        issued_at: NOW - 60,
        expires_at: NOW + 600,
        allowed_actions: vec![Action::HealthProbe],
        route: "tailnet_only".to_owned(),
    };
    SignedPolicySnapshot::sign(snapshot, &SigningKey::from_bytes(&[7_u8; 32]))
}

#[test]
fn rejects_snapshot_for_a_different_device() {
    let snapshot = signed_snapshot("other-device");

    assert!(snapshot.verify_for(MOTO_ID, NOW).is_err());
}

#[test]
fn rejects_tampered_snapshot_signature() {
    let mut snapshot = signed_snapshot(MOTO_ID);
    snapshot.snapshot.allowed_actions.push(Action::Notify);

    assert!(snapshot.verify_for(MOTO_ID, NOW).is_err());
}

#[test]
fn rejects_expired_snapshot() {
    let mut snapshot = signed_snapshot(MOTO_ID);
    snapshot.snapshot.expires_at = NOW - 1;

    assert!(snapshot.verify_for(MOTO_ID, NOW).is_err());
}

#[test]
fn rejects_action_outside_allowlist() {
    assert!(Action::parse_allowlisted("execute_shell").is_err());
}

#[test]
fn rejects_snapshot_signed_by_an_untrusted_hub_key() {
    let snapshot = signed_snapshot(MOTO_ID);
    let different_hub = SigningKey::from_bytes(&[8_u8; 32]);

    assert!(snapshot
        .verify_for_with_trusted_key(MOTO_ID, NOW, &different_hub.verifying_key().to_bytes())
        .is_err());
}

#[test]
fn signed_request_envelope_round_trips_with_the_enrolled_device_key() {
    let device_key = SigningKey::from_bytes(&[9_u8; 32]);
    let envelope = SignedEnvelope::sign(
        MOTO_ID,
        Action::RefreshSnapshot,
        json!({}),
        NOW - 10,
        NOW + 60,
        "nonce-1",
        &device_key,
    );

    assert!(envelope
        .verify_with(&device_key.verifying_key().to_bytes())
        .is_ok());
}

#[test]
fn signed_request_envelope_rejects_payload_tampering() {
    let device_key = SigningKey::from_bytes(&[9_u8; 32]);
    let mut envelope = SignedEnvelope::sign(
        MOTO_ID,
        Action::RefreshSnapshot,
        json!({}),
        NOW - 10,
        NOW + 60,
        "nonce-1",
        &device_key,
    );
    envelope.payload = json!({"unexpected": true});

    assert!(envelope
        .verify_with(&device_key.verifying_key().to_bytes())
        .is_err());
}

#[test]
fn loads_the_ed25519_seed_from_a_private_pkcs8_pem() {
    let mut der = vec![0_u8; 16];
    der.extend_from_slice(&[5_u8; 32]);
    let pem = format!(
        "-----BEGIN PRIVATE KEY-----\n{}\n-----END PRIVATE KEY-----\n",
        STANDARD.encode(der)
    );

    assert_eq!(signing_key_from_pkcs8_pem(pem.as_bytes()).unwrap().to_bytes(), [5_u8; 32]);
}
