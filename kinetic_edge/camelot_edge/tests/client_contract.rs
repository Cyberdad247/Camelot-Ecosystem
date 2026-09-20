use camelot_edge::{Action, SignedEnvelope, TailnetClient};
use ed25519_dalek::SigningKey;
use serde_json::json;

#[test]
fn refuses_a_non_tailnet_base_url() {
    assert!(TailnetClient::new("http://162.35.107.134:8095").is_err());
    assert!(TailnetClient::new("https://example.com:8095").is_err());
}

#[test]
fn accepts_a_tailnet_base_url() {
    assert!(TailnetClient::new("http://100.110.180.18:8095").is_ok());
}

#[test]
fn refuses_tls_that_the_native_minimal_transport_cannot_verify() {
    assert!(TailnetClient::new("https://100.110.180.18:8096").is_err());
}

#[test]
fn snapshot_request_carries_only_the_signed_envelope_header() {
    let client = TailnetClient::new("http://100.110.180.18:8096").unwrap();
    let envelope = SignedEnvelope::sign(
        "motorola-moto-g-power-5g---2024",
        Action::RefreshSnapshot,
        json!({}),
        1,
        2,
        "nonce-1",
        &SigningKey::from_bytes(&[3_u8; 32]),
    );

    let request = String::from_utf8(client.snapshot_request_bytes(&envelope).unwrap()).unwrap();

    assert!(request.starts_with("GET /v1/edge/snapshot HTTP/1.1\r\n"));
    assert!(request.contains("Host: 100.110.180.18:8096\r\n"));
    assert!(request.contains("X-Camelot-Edge-Envelope: "));
    assert!(request.ends_with("Connection: close\r\n\r\n"));
}
