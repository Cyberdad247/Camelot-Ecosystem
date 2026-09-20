# SPDX-License-Identifier: MIT
"""
Tests for Phase 1 Excalibur Gate (Bio-Auth, QR Device Binding, Tenant Carousel).
"""

from control_plane.security.excalibur_gate import ExcaliburGateService


def test_qr_binding_challenge():
    gate = ExcaliburGateService()
    challenge = gate.generate_qr_binding_challenge("vashawns-s26-ultra")
    assert challenge["device_id"] == "vashawns-s26-ultra"
    assert challenge["challenge_id"].startswith("qr_")
    assert "nonce" in challenge
    assert "sha256" in challenge
    assert "camelot://auth/device-bind" in challenge["qr_payload"]


def test_bio_auth_verification_success():
    gate = ExcaliburGateService()
    packet = {
        "face_vector_hash": "sha256:face_vector_mock_d92837",
        "voice_vad_hash": "sha256:voice_vad_mock_394821",
        "qr_signature": "ed25519:sig_mock_qr_challenge_9921",
        "device_id": "vashawns-s26-ultra",
    }
    result = gate.verify_bio_auth_packet(packet)
    assert result["authenticated"] is True
    assert result["carousel_unlocked"] is True
    assert result["sla_conformance_800ms"] is True
    assert len(result["tenants"]) >= 2
    for tenant in result["tenants"]:
        assert tenant["status"] == "UNLOCKED"


def test_bio_auth_verification_failure():
    gate = ExcaliburGateService()
    packet = {
        "face_vector_hash": "sha256:face_only",
    }
    result = gate.verify_bio_auth_packet(packet)
    assert result["authenticated"] is False
    assert result["carousel_unlocked"] is False
