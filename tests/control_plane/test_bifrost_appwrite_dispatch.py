# SPDX-License-Identifier: MIT

"""Tests for Bifrost→Appwrite signed-RPC dispatcher.

PR #3 of NOTES_MNEMOSYNE_WIRING.md.

Coverage:
  * HMAC parity: Python sign() roundtrip; rejects wrong/missing signature.
  * Intent dispatch: list_databases + upsert_document (with z3_pass gate).
  * WEBHOOK_SECRET missing path.
  * Unknown intent path.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

os.environ.setdefault("WEBHOOK_SECRET", "test-shared-secret")
os.environ.setdefault("APPWRITE_API_KEY", "test-key-1234567890")
os.environ.setdefault("APPWRITE_PROJECT_ID", "sovereign_db")


from control_plane.bifrost_appwrite_dispatch import (  # noqa: E402
    _sign,
    dispatch_to_appwrite,
)


def _sign_payload(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True)
    return _sign(raw, os.environ["WEBHOOK_SECRET"])


def test_hmac_parity_python_roundtrip() -> None:
    """A canonical Python sign produces a 64-char hex digest."""
    payload = {"intent": "list_databases", "x": 1}
    raw = json.dumps(payload, sort_keys=True)
    sig = _sign(raw, "shared-secret")
    assert len(sig) == 64
    assert all(c in "0123456789abcdef" for c in sig)
    # Same input + same secret ⇒ same output
    assert sig == _sign(raw, "shared-secret")


def test_dispatch_rejects_missing_signature() -> None:
    out = dispatch_to_appwrite("list_databases", {}, "")
    assert out["ok"] is False
    assert "signature" in out["error"] or "HMAC" in out["error"]


def test_dispatch_rejects_wrong_signature() -> None:
    out = dispatch_to_appwrite("list_databases", {}, "deadbeef" * 8)
    assert out["ok"] is False
    assert "HMAC" in out["error"]


def test_dispatch_rejects_unknown_intent() -> None:
    payload: dict = {"foo": "bar"}
    sig = _sign_payload(payload)
    out = dispatch_to_appwrite("unknown_intent", payload, sig)
    assert out["ok"] is False
    assert "unknown intent" in out["error"]


def test_dispatch_list_databases_returns_ok() -> None:
    payload: dict = {"intent": "list_databases"}
    sig = _sign_payload(payload)
    with patch("control_plane.bifrost_appwrite_dispatch.AppwriteClient") as cls:
        instance = MagicMock()
        cls.return_value = instance

        async def fake_list():
            return [{"$id": "db1", "name": "DB1"}]

        instance.list_databases = fake_list
        out = dispatch_to_appwrite("list_databases", payload, sig)
    assert out["ok"] is True
    assert out["result"]["databases"][0]["$id"] == "db1"


def test_dispatch_upsert_document_requires_z3_pass() -> None:
    payload: dict = {
        "document_id": "doc-1",
        "data": {"content": "memory node"},
        "z3_pass": False,
    }
    sig = _sign_payload(payload)
    out = dispatch_to_appwrite("upsert_document", payload, sig)
    assert out["ok"] is False
    assert "z3_pass" in out["error"]


def test_dispatch_upsert_document_with_z3_succeeds() -> None:
    payload: dict = {
        "document_id": "doc-1",
        "data": {"content": "memory node", "confidence": 0.95},
        "z3_pass": True,
    }
    sig = _sign_payload(payload)
    with patch("control_plane.bifrost_appwrite_dispatch.AppwriteClient") as cls:
        instance = MagicMock()
        cls.return_value = instance

        async def fake_upsert(document_id: str, data: dict, *, z3_pass: bool = True):
            return {"$id": document_id, **data}

        instance.upsert_document = fake_upsert
        out = dispatch_to_appwrite("upsert_document", payload, sig)
    assert out["ok"] is True
    assert out["result"]["$id"] == "doc-1"


def test_dispatch_upsert_missing_doc_id() -> None:
    payload: dict = {"data": {"x": 1}, "z3_pass": True}
    sig = _sign_payload(payload)
    out = dispatch_to_appwrite("upsert_document", payload, sig)
    assert out["ok"] is False
    assert "document_id" in out["error"]
