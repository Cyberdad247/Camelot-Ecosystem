from __future__ import annotations

import base64
import hashlib
import hmac
import json

import pytest

from control_plane.core import approval_grants


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _grant(command: str, *, issued_at: int = 1_000, expires_at: int = 1_090) -> str:
    claims = {
        "version": 1,
        "grantId": "12345678-1234-1234-1234-123456789abc",
        "approvalId": "appr-test-001",
        "commandDigest": hashlib.sha256(command.encode("utf-8")).hexdigest(),
        "issuedAt": issued_at,
        "expiresAt": expires_at,
    }
    payload = _encode(json.dumps(claims, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(
        b"test-cockpit-token-32-bytes-long",
        approval_grants.GRANT_CONTEXT + payload.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{payload}.{_encode(signature)}"


def _grant_v2(command: str, digest: str, *, issued_at: int = 1_000, expires_at: int = 1_090) -> str:
    claims = {
        "version": 2,
        "grantId": "12345678-1234-1234-1234-123456789abc",
        "approvalId": "appr-test-002",
        "commandDigest": hashlib.sha256(command.encode("utf-8")).hexdigest(),
        "cartridgeDigest": digest,
        "targetRoot": ".",
        "issuedAt": issued_at,
        "expiresAt": expires_at,
    }
    payload = _encode(json.dumps(claims, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(
        b"test-cockpit-token-32-bytes-long",
        approval_grants.GRANT_CONTEXT_V2 + payload.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{payload}.{_encode(signature)}"


@pytest.fixture(autouse=True)
def signing_key(monkeypatch):
    monkeypatch.setenv("CAMELOT_COCKPIT_TOKEN", "test-cockpit-token-32-bytes-long")


def test_grant_is_command_bound_and_consumed_once(tmp_path):
    grant = _grant("//PLAN build cockpit")
    claims = approval_grants.verify_and_consume(
        grant, "//PLAN build cockpit", now=1_010, consumed_dir=tmp_path
    )
    assert claims["approval_id"] == "appr-test-001"
    assert (tmp_path / claims["grant_id"]).exists()

    with pytest.raises(approval_grants.ApprovalGrantError, match="already been consumed"):
        approval_grants.verify_and_consume(
            grant, "//PLAN build cockpit", now=1_011, consumed_dir=tmp_path
        )


def test_grant_rejects_command_substitution(tmp_path):
    with pytest.raises(approval_grants.ApprovalGrantError, match="does not match"):
        approval_grants.verify_and_consume(
            _grant("//PLAN safe"), "//FORGE unsafe", now=1_010, consumed_dir=tmp_path
        )


def test_grant_rejects_expiry_and_tampering(tmp_path):
    grant = _grant("//PLAN build cockpit")
    with pytest.raises(approval_grants.ApprovalGrantError, match="not currently valid"):
        approval_grants.verify_and_consume(
            grant, "//PLAN build cockpit", now=1_091, consumed_dir=tmp_path
        )

    payload, signature = grant.split(".")
    damaged = f"{payload[:-1]}A.{signature}"
    with pytest.raises(approval_grants.ApprovalGrantError, match="signature is invalid"):
        approval_grants.verify_and_consume(
            damaged, "//PLAN build cockpit", now=1_010, consumed_dir=tmp_path
        )


def test_v2_grant_binds_cartridge_digest_and_target(tmp_path):
    digest = "a" * 64
    claims = approval_grants.verify_and_consume(
        _grant_v2("//EXECUTE_PROMPT forge-0123456789abcdef", digest),
        "//EXECUTE_PROMPT forge-0123456789abcdef",
        now=1_010,
        consumed_dir=tmp_path,
    )
    assert claims["version"] == 2
    assert claims["cartridge_digest"] == digest
    assert claims["target_root"] == "."


def test_cockpit_requires_grant_before_queueing(monkeypatch, tmp_path):
    from control_plane.infra import cockpit, harness
    from control_plane.runes import runic_router

    monkeypatch.setenv("CAMELOT_COCKPIT_REQUIRE_APPROVAL_GRANT", "true")
    monkeypatch.setattr(approval_grants, "_CONSUMED_DIR", tmp_path / "consumed")
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "queue.jsonl")

    monkeypatch.setenv("CAMELOT_COCKPIT_APPROVAL_GRANT", "invalid")
    rejected = cockpit.cockpit_exec("//PLAN build cockpit")
    assert rejected["status"] == "APPROVAL_REJECTED"
    assert not (tmp_path / "queue.jsonl").exists()

    monkeypatch.setenv(
        "CAMELOT_COCKPIT_APPROVAL_GRANT",
        _grant("//PLAN build cockpit", issued_at=2_000, expires_at=2_090),
    )
    monkeypatch.setattr(approval_grants.time, "time", lambda: 2_010)
    accepted = cockpit.cockpit_exec("//PLAN build cockpit")
    assert accepted["status"] == "ROUTED"
    queued = json.loads((tmp_path / "queue.jsonl").read_text(encoding="utf-8"))
    assert queued["approval_grant"]["approval_id"] == "appr-test-001"
    assert queued["approval_grant"]["task_id"] == queued["id"]
    assert "CAMELOT_COCKPIT_TOKEN" not in json.dumps(queued)

    monkeypatch.setattr(harness, "QUEUE_FILE", tmp_path / "queue.jsonl")
    parsed = harness.SovereignHarness()._read_queue(set())
    assert parsed[0].approval_grant == queued["approval_grant"]
