"""Tests for the NotebookLM bridge sync surface."""

import asyncio
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import notebooklm_bridge


def test_build_sync_snapshot_uses_local_files(monkeypatch):
    repo = Path(__file__).resolve().parent / "_tmp_sync_snapshot"
    if repo.exists():
        shutil.rmtree(repo)
    (repo / "logs" / "defense_grid").mkdir(parents=True)
    (repo / "VERSION").write_text("401.0.0\n", encoding="utf-8")
    (repo / "PROVENANCE_LEDGER.md").write_text("ledger-line-1\nledger-line-2\n", encoding="utf-8")
    (repo / "verification.md").write_text("# Verification\n- ok\n", encoding="utf-8")
    (repo / "logs" / "defense_grid" / "ledger_sync_status.json").write_text(
        '{"status":"SYNCED"}',
        encoding="utf-8",
    )

    monkeypatch.setattr(notebooklm_bridge, "REPO_ROOT", repo)
    monkeypatch.setattr(notebooklm_bridge, "LEDGER_PATH", repo / "PROVENANCE_LEDGER.md")
    monkeypatch.setattr(notebooklm_bridge, "VERIFICATION_PATH", repo / "verification.md")
    monkeypatch.setattr(
        notebooklm_bridge,
        "LEDGER_SYNC_STATUS_PATH",
        repo / "logs" / "defense_grid" / "ledger_sync_status.json",
    )
    monkeypatch.setattr(notebooklm_bridge, "VERSION_PATH", repo / "VERSION")

    snapshot = notebooklm_bridge._build_sync_snapshot(extra_summary="fresh state")

    assert "Camelot-OS Canonical Sync Snapshot" in snapshot
    assert "fresh state" in snapshot
    assert "ledger-line-2" in snapshot
    assert '"status":"SYNCED"' in snapshot
    assert "401.0.0" in snapshot
    shutil.rmtree(repo)


def test_async_sync_state_creates_note(monkeypatch):
    class FakeNote:
        def __init__(self, note_id: str, title: str):
            self.id = note_id
            self.title = title

    class FakeNotes:
        def __init__(self):
            self.items = []
            self.created = []

        async def list(self, notebook_id):
            return self.items

        async def create(self, notebook_id, title, content):
            self.created.append((notebook_id, title, content))
            note = FakeNote("note-created", title)
            self.items.append(note)
            return note

    class FakeClient:
        def __init__(self):
            self.notes = FakeNotes()

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

    fake_client = FakeClient()

    async def fake_build_client():
        return fake_client

    monkeypatch.setattr(notebooklm_bridge, "_build_client", fake_build_client)

    result = asyncio.run(
        notebooklm_bridge.async_sync_state(
            notebook_id="nb-1",
            note_title="Snapshot",
            content="hello world",
        )
    )

    assert result["action"] == "created"
    assert result["note_id"] == "note-created"
    assert fake_client.notes.created[0][0] == "nb-1"
    assert fake_client.notes.created[0][1] == "Snapshot"
    assert fake_client.notes.created[0][2] == "hello world"


def test_async_sync_state_updates_existing_note(monkeypatch):
    class FakeNote:
        def __init__(self, note_id: str, title: str):
            self.id = note_id
            self.title = title

    class FakeNotes:
        def __init__(self):
            self.items = [FakeNote("note-existing", "Snapshot")]
            self.updated = []

        async def list(self, notebook_id):
            return self.items

        async def update(self, notebook_id, note_id, content, title):
            self.updated.append((notebook_id, note_id, content, title))

    class FakeClient:
        def __init__(self):
            self.notes = FakeNotes()

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

    fake_client = FakeClient()

    async def fake_build_client():
        return fake_client

    monkeypatch.setattr(notebooklm_bridge, "_build_client", fake_build_client)

    result = asyncio.run(
        notebooklm_bridge.async_sync_state(
            notebook_id="nb-2",
            note_title="Snapshot",
            content="updated content",
        )
    )

    assert result["action"] == "updated"
    assert result["note_id"] == "note-existing"
    assert fake_client.notes.updated == [("nb-2", "note-existing", "updated content", "Snapshot")]
