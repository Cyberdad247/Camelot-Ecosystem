import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_REPO_ROOT / "vfs") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "vfs"))

import pytest
import asyncio
from vfs.cloudbrain_outbox import CloudBrainOutbox, check_source_caps, resolve_canonical_workspace_uuid

def test_cloudbrain_outbox_lifecycle(tmp_path):
    outbox_file = tmp_path / "test_outbox.jsonl"
    outbox = CloudBrainOutbox(outbox_path=outbox_file)

    assert outbox.pending_count() == 0

    item = outbox.enqueue(
        item_type="NOTE",
        knight_id="SIR_HELIOS",
        title="Test Telemetry Note",
        content="Testing Tier 4 outbox buffering.",
        metadata={"priority": "HIGH"}
    )

    assert item["status"] == "QUEUED"
    assert outbox.pending_count() == 1

    entries = outbox.read_all_pending()
    assert len(entries) == 1
    assert entries[0]["title"] == "Test Telemetry Note"
    assert entries[0]["knight_id"] == "SIR_HELIOS"

def test_check_source_caps():
    caps = check_source_caps()
    assert isinstance(caps, list)
    # The actual manifest has multiple notebooks near or over the 50 limit
    assert len(caps) > 0
    assert any(c["cap"] == 50 for c in caps)

def test_resolve_canonical_workspace_uuid():
    uuid = resolve_canonical_workspace_uuid("SIR_BORIS")
    assert uuid == "f7707daa-2d10-4db8-8fda-be4661a27793"
    uuid_apis = resolve_canonical_workspace_uuid("LADY_APIS")
    assert uuid_apis == "378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f"


def test_cloudbrain_outbox_drain_loop(tmp_path):
    outbox_file = tmp_path / "test_outbox_loop.jsonl"
    outbox = CloudBrainOutbox(outbox_path=outbox_file)

    # Run 1 idle iteration
    asyncio.run(outbox.run_drain_loop(interval_seconds=0, max_iterations=1))
    assert outbox.pending_count() == 0
