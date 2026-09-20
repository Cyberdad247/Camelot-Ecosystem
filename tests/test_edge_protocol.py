import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from control_plane.dispatch.edge_protocol import EdgeProtocol, canonical_envelope_bytes


NOW = 1_700_000_000
MOTO = "motorola-moto-g-power-5g---2024"


def signed_envelope(key: Ed25519PrivateKey, *, nonce: str = "nonce-1", action: str = "health_probe") -> dict:
    envelope = {
        "device_id": MOTO,
        "action": action,
        "payload": {"battery_percent": 84},
        "issued_at": NOW - 60,
        "expires_at": NOW + 600,
        "nonce": nonce,
    }
    envelope["signature"] = base64.b64encode(key.sign(canonical_envelope_bytes(envelope))).decode("ascii")
    return envelope


def edge_protocol() -> tuple[EdgeProtocol, Ed25519PrivateKey]:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return EdgeProtocol({MOTO: public_key}), private_key


def test_envelope_canonicalization_uses_the_cross_runtime_field_order():
    envelope = {
        "device_id": MOTO,
        "action": "refresh_snapshot",
        "payload": {},
        "issued_at": NOW - 60,
        "expires_at": NOW + 600,
        "nonce": "nonce-1",
    }

    assert canonical_envelope_bytes(envelope) == (
        b'{"device_id":"motorola-moto-g-power-5g---2024",'
        b'"action":"refresh_snapshot","payload":{},'
        b'"issued_at":1699999940,"expires_at":1700000600,"nonce":"nonce-1"}'
    )


def test_valid_edge_envelope_is_accepted_once():
    protocol, private_key = edge_protocol()
    envelope = signed_envelope(private_key)

    assert protocol.validate_envelope(envelope, now=NOW).ok
    assert protocol.validate_envelope(envelope, now=NOW).reason == "replayed-nonce"


def test_unregistered_device_key_is_rejected():
    protocol, private_key = edge_protocol()
    envelope = signed_envelope(private_key)
    envelope["device_id"] = "unknown-device"

    assert protocol.validate_envelope(envelope, now=NOW).reason == "unregistered-device"


def test_invalid_action_is_rejected_even_when_signed():
    protocol, private_key = edge_protocol()

    assert protocol.validate_envelope(signed_envelope(private_key, action="execute_shell"), now=NOW).reason == "forbidden-action"


def test_expired_or_tampered_envelope_is_rejected():
    protocol, private_key = edge_protocol()
    expired = signed_envelope(private_key, nonce="expired")
    expired["expires_at"] = NOW - 1
    assert protocol.validate_envelope(expired, now=NOW).reason == "expired-envelope"

    tampered = signed_envelope(private_key, nonce="tampered")
    tampered["action"] = "notify"
    assert protocol.validate_envelope(tampered, now=NOW).reason == "invalid-signature"
