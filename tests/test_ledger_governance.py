from pathlib import Path

from control_plane import worker

REPO_ROOT = Path(__file__).resolve().parents[1]
SPRINT_ENRICHMENT_SCRIPTS = [
    REPO_ROOT / "scripts" / "sprint5_enrichment.py",
    REPO_ROOT / "scripts" / "sprint7_enrichment.py",
    REPO_ROOT / "scripts" / "sprint8_enrichment.py",
]


def test_sprint_enrichment_scripts_use_shared_provenance_helper():
    for script in SPRINT_ENRICHMENT_SCRIPTS:
        text = script.read_text(encoding="utf-8")
        assert "append_provenance_entry" in text
        assert "LEDGER.write_text(row + existing" not in text
        assert "re.finditer" not in text


def test_worker_ledger_entry_delegates_to_shared_helper(monkeypatch):
    calls = []

    def fake_append_provenance_entry(**kwargs):
        calls.append(kwargs)
        return {"status": "UPDATED"}

    monkeypatch.setattr(
        "control_plane.infra.ledger_sync.append_provenance_entry",
        fake_append_provenance_entry,
    )
    monkeypatch.setattr(worker, "_log", lambda message: None)

    task = worker.QueueTask(
        id="task-123",
        knight="sir_forge",
        directive="//FORGE build durable ledger route",
    )

    worker._ledger_entry(
        task,
        written=[str(REPO_ROOT / "control_plane" / "example.py")],
        piv="PIV passed",
        git="git:abc123",
    )

    assert calls == [
        {
            "title": "[FORGE:task-123] //FORGE build durable ledger route",
            "actor": "SIR_FORGE",
            "scope": ["1 file(s): example.py"],
            "verification": ["worker PIV gate", "PIV passed", "git:abc123"],
            "tag": "worker_forge",
        }
    ]
