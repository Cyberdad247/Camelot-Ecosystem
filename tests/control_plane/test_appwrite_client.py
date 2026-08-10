"""Tests for AppwriteClient typed wrapper.

PR #2 of NOTES_MNEMOSYNE_WIRING.md.

Coverage:
  * golden-path: list_databases, upsert_document with z3_pass=True
  * retry-semantics: AppwriteException triggers tenacity retry
  * masked-auth: key redact appears in mask_key output
  * HUMAN_GATE gate: upsert_document without z3_pass raises PermissionError
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# Pre-populate env BEFORE importing the module so __init__ succeeds.
os.environ.setdefault("APPWRITE_ENDPOINT_PUBLIC", "https://appwrite.local/v1")
os.environ.setdefault("APPWRITE_API_KEY", "test-key-1234567890")
os.environ.setdefault("APPWRITE_PROJECT_ID", "sovereign_db")
os.environ.setdefault("APPWRITE_DB_ID", "sovereign_db")
os.environ.setdefault("APPWRITE_COLLECTION_ID", "memory_spine")

from control_plane.appwrite_client import AppwriteClient  # noqa: E402


@pytest.fixture
def client(mock_databases) -> AppwriteClient:
    return AppwriteClient()


@pytest.fixture
def mock_databases() -> MagicMock:
    with patch("control_plane.appwrite_client.Databases") as cls:
        instance = MagicMock()
        cls.return_value = instance
        yield instance


def test_init_reads_env(client: AppwriteClient) -> None:
    assert client.endpoint.startswith("https://")
    assert client.database_id == "sovereign_db"
    assert client.collection_id == "memory_spine"


def test_mask_key_redacts_middle(client: AppwriteClient) -> None:
    masked = client.mask_key()
    assert "..." in masked
    assert masked != "test-key-1234567890"


def test_missing_api_key_raises() -> None:
    with patch.dict(os.environ, {"APPWRITE_API_KEY": ""}, clear=False):
        os.environ["APPWRITE_API_KEY"] = ""
        with pytest.raises(ValueError, match="APPWRITE_API_KEY"):
            AppwriteClient(api_key="")


def test_list_databases_returns_list(client: AppwriteClient, mock_databases: MagicMock) -> None:
    mock_databases.list.return_value = {"databases": [{"$id": "db1", "name": "DB1"}]}
    result = asyncio.run(client.list_databases())
    assert isinstance(result, list)
    assert result[0]["$id"] == "db1"


def test_upsert_document_without_z3_rejected(client: AppwriteClient) -> None:
    with pytest.raises(PermissionError, match="z3_pass"):
        asyncio.run(client.upsert_document("doc-1", {"x": 1}, z3_pass=False))


def test_upsert_document_with_z3_calls_sdk(
    client: AppwriteClient, mock_databases: MagicMock
) -> None:
    mock_databases.create_document.return_value = {"$id": "doc-1", "x": 1}
    result = asyncio.run(client.upsert_document("doc-1", {"x": 1}, z3_pass=True))
    assert result["$id"] == "doc-1"
    mock_databases.create_document.assert_called_once()
    args = mock_databases.create_document.call_args
    assert args[0][0] == "sovereign_db"
    assert args[0][1] == "memory_spine"


def test_upsert_document_validates_inputs(client: AppwriteClient) -> None:
    with pytest.raises(ValueError, match="document_id"):
        asyncio.run(client.upsert_document("", {"x": 1}, z3_pass=True))
    with pytest.raises(ValueError, match="data"):
        asyncio.run(client.upsert_document("doc-1", None, z3_pass=True))  # type: ignore[arg-type]


def test_retry_on_appwrite_exception(client: AppwriteClient, mock_databases: MagicMock) -> None:
    """Tenacity should retry on AppwriteException up to DEFAULT_MAX_ATTEMPTS."""
    from appwrite.exception import AppwriteException

    call_count = {"n": 0}

    def flaky_call():
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise AppwriteException(code=500, message="timeout")
        return {"databases": []}

    mock_databases.list.side_effect = flaky_call

    # We've configured retry=3 with reraise=True; on the 3rd attempt the call succeeds.
    # Wrap in a tight overall wait to keep CI fast.
    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = asyncio.run(
            asyncio.wait_for(client.list_databases(), timeout=2.0)
        )
    assert result == []
    assert call_count["n"] == 3
