# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""Tests for control_plane.secret_manager — the zero-cost local secret store."""
import pytest

pytest.importorskip("cryptography")

from control_plane.secret_manager import SecretManager  # noqa: E402


def _mk(tmp_path) -> SecretManager:
    return SecretManager(
        store_path=tmp_path / "secrets.enc",
        key_path=tmp_path / "secret.key",
        audit_path=tmp_path / "audit.jsonl",
    )


def test_set_get_roundtrip_and_encrypted_at_rest(tmp_path):
    sm = _mk(tmp_path)
    sm.set("WEBHOOK_SECRET", "s3cr3t-value")
    assert sm.get("WEBHOOK_SECRET") == "s3cr3t-value"
    # Stored bytes must not contain the plaintext.
    blob = (tmp_path / "secrets.enc").read_bytes()
    assert b"s3cr3t-value" not in blob


def test_env_override_wins(tmp_path, monkeypatch):
    sm = _mk(tmp_path)
    sm.set("API_TOKEN", "stored")
    monkeypatch.setenv("API_TOKEN", "from-env")
    assert sm.get("API_TOKEN") == "from-env"
    monkeypatch.delenv("API_TOKEN")
    assert sm.get("API_TOKEN") == "stored"


def test_list_names_and_delete(tmp_path):
    sm = _mk(tmp_path)
    sm.set("A", "1")
    sm.set("B", "2")
    assert sm.list_names() == ["A", "B"]
    assert sm.delete("A") is True
    assert sm.delete("A") is False
    assert sm.list_names() == ["B"]


def test_rotate_key_preserves_secrets(tmp_path):
    sm = _mk(tmp_path)
    sm.set("K", "v")
    old_key = (tmp_path / "secret.key").read_bytes()
    new_key = sm.rotate_key()
    assert new_key != old_key
    assert (tmp_path / "secret.key").read_bytes() == new_key
    # Secret still readable under the rotated key.
    assert sm.get("K") == "v"
    # A fresh manager using the new keyfile can still read it.
    assert _mk(tmp_path).get("K") == "v"


def test_default_returned_for_missing(tmp_path):
    sm = _mk(tmp_path)
    assert sm.get("NOPE", "fallback") == "fallback"
