"""CAMELOT_OS/tests/control_plane/test_viking_block_protocol.py.

PR #6A test suite — verify the viking_block_protocol module.

Run with: pytest CAMELOT_OS/tests/control_plane/test_viking_block_protocol.py
(uses the portable Python interpreter from CAMELOT_OS/.venv)
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest

from control_plane.viking_block_protocol import (
    DEFAULT_MAX_SKEW_SECONDS,
    DEFAULT_SECRET_KEY_ENV,
    VIKING_SCHEME,
    VikingBlock,
    VikingProtocolError,
    from_json,
    parse_viking_uri,
    sign_block,
    to_canonical_bytes,
    to_json,
    verify_block,
)

# ── Test fixtures ──────────────────────────────────────────────────────────────
@pytest.fixture()
def signed_block() -> VikingBlock:
    """A canonical VikingBlock signed with a sandbox test secret."""
    block = VikingBlock(
        id="mem-2026-07-14-001",
        type="mnemosyne_block",
        content="Lady Mnemosyne memory spine entry: PR #6A landed.",
        source_agent="sir_boris",
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    return sign_block(block, secret="test-secret-32bytes-padding-12345")


# ── 1. Constants ───────────────────────────────────────────────────────────────
def test_constants_are_stable():
    assert VIKING_SCHEME == "viking"
    assert DEFAULT_SECRET_KEY_ENV == "VIKING_BLOCK_HMAC_KEY"
    assert DEFAULT_MAX_SKEW_SECONDS == 300


# ── 2. URI Parsing — Appwrite destination ─────────────────────────────────────
def test_parse_viking_uri_appwrite_destination():
    uri = "viking://appwrite.databases/camelot_db/collections/memory_spine/documents/mem-001"
    parsed = parse_viking_uri(uri)
    assert parsed is not None
    assert parsed["domain"] == "appwrite.databases"
    assert parsed["path_segments"] == ["camelot_db", "collections", "memory_spine", "documents", "mem-001"]
    assert parsed["sub_path"] is None
    assert parsed["query_hmac"] is None


# ── 3. URI Parsing — Memory block reference ───────────────────────────────────
def test_parse_viking_uri_memory_block_abstract():
    uri = "viking://memory.block/mem-001"
    parsed = parse_viking_uri(uri)
    assert parsed is not None
    assert parsed["domain"] == "memory.block"
    assert parsed["path_segments"] == ["mem-001"]
    assert parsed["sub_path"] is None


# ── 4. URI Parsing — Memory block sub-path discovery ───────────────────────────
def test_parse_viking_uri_memory_block_sub_path():
    uri = "viking://memory.block/mem-001/type"
    parsed = parse_viking_uri(uri)
    assert parsed is not None
    assert parsed["sub_path"] == "type"
    assert parsed["path_segments"] == ["mem-001"]

    parsed_c = parse_viking_uri("viking://memory.block/mem-001/content")
    assert parsed_c is not None and parsed_c["sub_path"] == "content"


# ── 5. URI Parsing — Signed envelope query param ──────────────────────────────
def test_parse_viking_uri_signed_envelope():
    uri = "viking://memory.block/mem-001?hmac=deadbeefcafe"
    parsed = parse_viking_uri(uri)
    assert parsed is not None
    assert parsed["query_hmac"] == "deadbeefcafe"
    assert parsed["path_segments"] == ["mem-001"]


# ── 6. URI Parsing — Malformed / wrong scheme ─────────────────────────────────
def test_parse_viking_uri_rejects_malformed():
    assert parse_viking_uri("") is None
    assert parse_viking_uri("not-a-uri") is None
    assert parse_viking_uri("http://memory.block/mem-001") is None
    assert parse_viking_uri("viking://unknown.domain/x") is None
    assert parse_viking_uri(None) is None  # type: ignore[arg-type]
    assert parse_viking_uri(42) is None  # type: ignore[arg-type]


# ── 7. HMAC round-trip ─────────────────────────────────────────────────────────
def test_hmac_round_trip(signed_block):
    assert verify_block(signed_block, secret="test-secret-32bytes-padding-12345") is True


# ── 8. HMAC tamper detection (mutate any signed field) ──────────────────────────
def test_hmac_tamper_detection(signed_block):
    # Mutate content
    tampered = VikingBlock(
        id=signed_block.id,
        type=signed_block.type,
        content="TAMPERED CONTENT (should fail HMAC)",
        source_agent=signed_block.source_agent,
        timestamp=signed_block.timestamp,
        hmac=signed_block.hmac,
    )
    secret = "test-secret-32bytes-padding-12345"
    assert verify_block(tampered, secret=secret) is False
    # Resign with different content confirms the integrity
    legitimate_resign = sign_block(tampered, secret=secret)
    assert verify_block(legitimate_resign, secret=secret) is True


# ── 9. HMAC missing → reject ──────────────────────────────────────────────────
def test_hmac_missing_rejects():
    block = VikingBlock(
        id="mem-001",
        type="mnemosyne_block",
        content="unsigned",
        source_agent="sir_boris",
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        hmac="",  # empty
    )
    assert verify_block(block, secret="anything") is False


# ── 10. HMAC skew rejection (future-stamped block) ────────────────────────────
def test_skew_rejection_old_timestamp():
    """A block whose timestamp is older than max_skew_seconds must fail."""
    ancient = datetime.now(timezone.utc) - timedelta(seconds=DEFAULT_MAX_SKEW_SECONDS + 60)
    block = VikingBlock(
        id="mem-ancient",
        type="mnemosyne_block",
        content="stale",
        source_agent="sir_boris",
        timestamp=ancient.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    signed = sign_block(block, secret="secret")
    assert verify_block(signed, secret="secret", max_skew_seconds=DEFAULT_MAX_SKEW_SECONDS) is False


def test_skew_accepts_fresh_timestamp():
    """A block whose timestamp is within the window must pass."""
    fresh = datetime.now(timezone.utc) - timedelta(seconds=10)
    block = VikingBlock(
        id="mem-fresh",
        type="mnemosyne_block",
        content="fresh",
        source_agent="sir_boris",
        timestamp=fresh.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    signed = sign_block(block, secret="secret")
    assert verify_block(signed, secret="secret") is True


# ── 11. JSON serialization round-trip ──────────────────────────────────────────
def test_json_round_trip(signed_block):
    serialized = to_json(signed_block)
    # The serialized form must be a valid JSON string with all 6 fields
    restored = from_json(serialized)
    assert restored == signed_block
    assert restored.id == signed_block.id
    assert restored.hmac == signed_block.hmac


def test_from_json_rejects_malformed():
    with pytest.raises(VikingProtocolError, match="invalid JSON"):
        from_json("not-json-at-all")
    with pytest.raises(VikingProtocolError, match="missing required fields"):
        from_json('{"id":"x"}')  # missing type, content, source_agent, timestamp


# ── 12. Canonical bytes are stable / deterministic ─────────────────────────────
def test_canonical_bytes_deterministic():
    block1 = VikingBlock(
        id="mem-001", type="mnemosyne_block", content="x",
        source_agent="sir_boris",
        timestamp="2026-07-14T12:00:00Z",
    )
    block2 = VikingBlock(
        id="mem-001", type="mnemosyne_block", content="x",
        source_agent="sir_boris",
        timestamp="2026-07-14T12:00:00Z",
    )
    # Same dict contents → same canonical bytes
    assert to_canonical_bytes(block1) == to_canonical_bytes(block2)


def test_missing_secret_raises_protocol_error(monkeypatch):
    """When no secret is provided AND env var unset, raise VikingProtocolError."""
    monkeypatch.delenv(DEFAULT_SECRET_KEY_ENV, raising=False)
    block = VikingBlock(
        id="mem-001", type="mnemosyne_block", content="x",
        source_agent="sir_boris",
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    with pytest.raises(VikingProtocolError, match="HMAC secret not configured"):
        sign_block(block, secret=None)


def test_env_secret_resolution(monkeypatch):
    """Env var resolution works when secret=None is passed."""
    monkeypatch.setenv(DEFAULT_SECRET_KEY_ENV, "env-secret-12345")
    block = VikingBlock(
        id="mem-env", type="mnemosyne_block", content="x",
        source_agent="sir_boris",
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    signed = sign_block(block, secret=None)
    assert signed.hmac != ""
    assert verify_block(signed, secret="env-secret-12345") is True
    assert verify_block(signed, secret="wrong-secret") is False
