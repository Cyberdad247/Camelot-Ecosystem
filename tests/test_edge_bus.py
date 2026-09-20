import base64
import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from control_plane.dispatch.edge_protocol import canonical_envelope_bytes
from control_plane.dispatch.edge_bus import edge_request_authorized, is_tailnet_bind_host


def test_edge_bus_rejects_missing_signed_envelope(monkeypatch):
    monkeypatch.delenv("CAMELOT_EDGE_PUBLIC_KEYS_JSON", raising=False)

    assert edge_request_authorized({}, now=1_700_000_000).reason == "missing-edge-envelope"


def test_edge_bus_accepts_enrolled_device_envelope(monkeypatch):
    now = 1_700_000_000
    device_id = "motorola-moto-g-power-5g---2024"
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    monkeypatch.setenv(
        "CAMELOT_EDGE_PUBLIC_KEYS_JSON",
        json.dumps({device_id: base64.b64encode(public_key).decode("ascii")}),
    )
    envelope = {
        "device_id": device_id,
        "action": "refresh_snapshot",
        "payload": {},
        "issued_at": now - 1,
        "expires_at": now + 60,
        "nonce": "edge-bus-test-nonce",
    }
    envelope["signature"] = base64.b64encode(private_key.sign(canonical_envelope_bytes(envelope))).decode("ascii")
    headers = {"x-camelot-edge-envelope": base64.b64encode(json.dumps(envelope).encode()).decode()}

    assert edge_request_authorized(headers, now=now).ok


def test_edge_bus_loads_enrollment_registry_from_a_file(monkeypatch, tmp_path):
    registry_path = tmp_path / "edge-public-keys.json"
    registry_path.write_text(json.dumps({"motorola-moto-g-power-5g---2024": base64.b64encode(b"x" * 32).decode()}))
    monkeypatch.delenv("CAMELOT_EDGE_PUBLIC_KEYS_JSON", raising=False)
    monkeypatch.setenv("CAMELOT_EDGE_PUBLIC_KEYS_FILE", str(registry_path))

    # A registry file avoids JSON quoting ambiguity in systemd EnvironmentFile.
    assert edge_request_authorized({"x-camelot-edge-envelope": "not-a-valid-envelope"}, now=1_700_000_000).reason == "malformed-edge-envelope"


def test_edge_bus_only_binds_a_tailnet_address():
    assert is_tailnet_bind_host("100.110.180.18")
    assert not is_tailnet_bind_host("0.0.0.0")
