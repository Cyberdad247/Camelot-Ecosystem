# SPDX-License-Identifier: MIT

import base64
import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from control_plane.dispatch.edge_protocol import canonical_envelope_bytes
from control_plane.dispatch.vps_mobile_mesh_bridge import (
    edge_request_authorized,
    is_mesh_request_authorized,
    is_tailnet_bind_host,
)


def test_mesh_bridge_rejects_missing_or_wrong_token(monkeypatch):
    monkeypatch.setenv("MESH_BRIDGE_TOKEN", "fixture-mesh-token")

    assert is_mesh_request_authorized({}) is False
    assert is_mesh_request_authorized({"x-camelot-token": "wrong"}) is False
    assert is_mesh_request_authorized({"x-camelot-token": "fixture-mesh-token"}) is True


def test_mesh_bridge_rejects_blank_environment_tokens(monkeypatch):
    for token in ("", " ", "\t"):
        monkeypatch.setenv("MESH_BRIDGE_TOKEN", token)
        assert is_mesh_request_authorized({"x-camelot-token": token}) is False

    monkeypatch.delenv("MESH_BRIDGE_TOKEN", raising=False)
    assert is_mesh_request_authorized({"x-camelot-token": "any-token"}) is False


def test_edge_endpoint_rejects_missing_signed_envelope(monkeypatch):
    monkeypatch.delenv("CAMELOT_EDGE_PUBLIC_KEYS_JSON", raising=False)

    assert edge_request_authorized({}, now=1_700_000_000).reason == "missing-edge-envelope"


def test_edge_endpoint_accepts_signed_envelope_without_mesh_token(monkeypatch):
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
        "nonce": "fixture-nonce",
    }
    envelope["signature"] = base64.b64encode(private_key.sign(canonical_envelope_bytes(envelope))).decode("ascii")
    headers = {
        "x-camelot-edge-envelope": base64.b64encode(json.dumps(envelope).encode("utf-8")).decode("ascii")
    }

    assert edge_request_authorized(headers, now=now).ok


def test_edge_listener_only_accepts_tailnet_bind_hosts():
    assert is_tailnet_bind_host("100.110.180.18")
    assert not is_tailnet_bind_host("0.0.0.0")
    assert not is_tailnet_bind_host("162.35.107.134")
