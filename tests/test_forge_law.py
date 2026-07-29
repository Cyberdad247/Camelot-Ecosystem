from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from control_plane import forge_law, runic_router
from control_plane.ledger_sync import compute_entry_hash
from control_plane.provenance import ProvenanceManager, VerificationRun


def _write_source(root: Path, operations: list[dict] | None = None) -> Path:
    source = root / "blueprints" / "test"
    source.mkdir(parents=True, exist_ok=True)
    for name in ("blueprint.md", "tasks.md", "verification.md"):
        (source / name).write_text(f"# {name}\n\nVerified fixture.\n", encoding="utf-8")
    contract = {
        "protocolVersion": "forge-law/v1",
        "title": "Verified fixture",
        "targetRoot": ".",
        "risk": {"level": "medium"},
        "operations": operations
        or [
            {
                "id": "compile-check",
                "type": "run_check",
                "dependsOn": [],
                "argv": ["python", "-m", "compileall", "control_plane"],
                "cwd": ".",
                "timeoutSeconds": 30,
            }
        ],
        "verification": [(operations or [{"id": "compile-check"}])[-1]["id"]],
    }
    (source / "forge.json").write_text(json.dumps(contract), encoding="utf-8")
    return source


def _hashes(source: Path) -> dict[str, str]:
    return {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in forge_law.SOURCE_FILES}


def _write_verified_ledger(path: Path, hashes: dict[str, str]) -> None:
    entry = {
        "run_id": "forge-test-run",
        "timestamp_utc": "2026-07-13T12:00:00+00:00",
        "operator": "pytest",
        "command": "verify forge fixture",
        "results": {"event_type": "forge_upgrade_verified", "source_hashes": hashes},
        "success": True,
        "entry_id": 1,
        "parent_hash": None,
    }
    entry["entry_hash"] = compute_entry_hash(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entry) + "\n", encoding="utf-8")


def test_crystallization_requires_matching_chained_verification(tmp_path):
    source = _write_source(tmp_path)
    store = tmp_path / "runtime"
    ledger = tmp_path / "ledger.jsonl"
    with pytest.raises(forge_law.ForgeLawError, match="ledger is unavailable"):
        forge_law.crystallize_source(source, root=tmp_path, store=store, ledger=ledger)

    _write_verified_ledger(ledger, _hashes(source))
    cartridge = forge_law.crystallize_source(source, root=tmp_path, store=store, ledger=ledger)
    assert cartridge["id"].startswith("forge-")
    assert forge_law.inspect_cartridge(cartridge["id"], store=store)["digest"] == cartridge["digest"]
    repeated = forge_law.crystallize_source(source, root=tmp_path, store=store, ledger=ledger)
    assert repeated["id"] == cartridge["id"]
    assert repeated["createdAt"] == cartridge["createdAt"]

    (source / "tasks.md").write_text("changed after verification", encoding="utf-8")
    with pytest.raises(forge_law.ForgeLawError, match="no successful"):
        forge_law.crystallize_source(source, root=tmp_path, store=store, ledger=ledger)


def test_contract_rejects_traversal_secrets_and_cycles(tmp_path):
    traversal = [{"id": "write", "type": "write_file", "dependsOn": [], "path": "../escape.txt", "content": "safe"}]
    source = _write_source(tmp_path, traversal)
    with pytest.raises(forge_law.ForgeLawError, match="escapes"):
        forge_law.validate_source(source, root=tmp_path)

    secret = [{"id": "write", "type": "write_file", "dependsOn": [], "path": "safe.txt", "content": "api_key=abcdefghijklmnop"}]
    source = _write_source(tmp_path, secret)
    with pytest.raises(forge_law.ForgeLawError, match="secret"):
        forge_law.validate_source(source, root=tmp_path)

    cycle = [
        {"id": "first", "type": "run_check", "dependsOn": ["second"], "argv": ["python", "-m", "compileall", "."]},
        {"id": "second", "type": "run_check", "dependsOn": ["first"], "argv": ["python", "-m", "compileall", "."]},
    ]
    source = _write_source(tmp_path, cycle)
    with pytest.raises(forge_law.ForgeLawError, match="cycle"):
        forge_law.validate_source(source, root=tmp_path)


def test_failed_execution_restores_file_and_records_rollback(tmp_path):
    target = tmp_path / "owned.txt"
    target.write_text("original", encoding="utf-8")
    (tmp_path / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    operations = [
        {"id": "write", "type": "write_file", "dependsOn": [], "path": "owned.txt", "content": "replacement"},
        {
            "id": "check",
            "type": "run_check",
            "dependsOn": ["write"],
            "argv": ["python", "-m", "compileall", "broken.py"],
            "cwd": ".",
            "timeoutSeconds": 30,
        },
    ]
    source = _write_source(tmp_path, operations)
    ledger = tmp_path / "ledger.jsonl"
    store = tmp_path / "runtime"
    _write_verified_ledger(ledger, _hashes(source))
    cartridge = forge_law.crystallize_source(source, root=tmp_path, store=store, ledger=ledger)
    approval = {
        "version": 2,
        "approval_id": "appr-test",
        "cartridge_digest": cartridge["digest"],
        "target_root": ".",
    }
    with pytest.raises(forge_law.ForgeLawError, match="failed with exit code"):
        forge_law.execute_cartridge(cartridge["id"], approval, root=tmp_path, store=store)
    assert target.read_text(encoding="utf-8") == "original"
    assert forge_law.inspect_cartridge(cartridge["id"], store=store)["state"] == "rolled_back"


def test_execute_prompt_requires_digest_bound_approval(monkeypatch, tmp_path):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "queue.jsonl")
    denied = runic_router.route_rune("//EXECUTE_PROMPT", "forge-0123456789abcdef")
    assert denied.queued is False
    assert "approval" in (denied.queue_error or "").lower()

    digest = "b" * 64
    monkeypatch.setattr(forge_law, "approval_binding", lambda _: {"cartridgeDigest": digest, "targetRoot": "."})
    approved = runic_router.route_rune(
        "//EXECUTE_PROMPT",
        "forge-0123456789abcdef",
        context={"approval_grant": {"version": 2, "cartridge_digest": digest, "target_root": "."}},
    )
    assert approved.queued is True
    queued = json.loads((tmp_path / "queue.jsonl").read_text(encoding="utf-8"))
    assert queued["knight"] == "lukas_omega"
    assert queued["approval_grant"]["cartridge_digest"] == digest


def test_verified_event_triggers_automatic_crystallization(monkeypatch, tmp_path):
    calls: list[tuple[str, Path]] = []
    manager = ProvenanceManager(vault_path=tmp_path / "missions")
    manager.mempalace = SimpleNamespace(store=lambda **_: None)
    monkeypatch.setattr(
        forge_law,
        "crystallize_source",
        lambda source, *, ledger: calls.append((source, ledger)) or {"id": "forge-0123456789abcdef"},
    )
    manager.log_verification(
        VerificationRun(
            run_id="auto-crystallize",
            operator="pytest",
            command="verify source",
            results={"event_type": "forge_upgrade_verified", "source_dir": "blueprints/test", "source_hashes": {}},
            success=True,
        )
    )
    assert calls == [("blueprints/test", manager.verification_ledger)]


def test_cartridge_id_from_command():
    # Happy path
    assert forge_law.cartridge_id_from_command("//EXECUTE_PROMPT forge-0123456789abcdef") == "forge-0123456789abcdef"

    # Varying whitespace
    assert forge_law.cartridge_id_from_command("  //EXECUTE_PROMPT   forge-0123456789abcdef  ") == "forge-0123456789abcdef"

    # Case-insensitivity (hex and command)
    assert forge_law.cartridge_id_from_command("//execute_prompt FORGE-0123456789ABCDEF") == "forge-0123456789abcdef"
    assert forge_law.cartridge_id_from_command("//Execute_Prompt FoRgE-0123456789aBcDeF") == "forge-0123456789abcdef"

    # Invalid length
    assert forge_law.cartridge_id_from_command("//EXECUTE_PROMPT forge-0123456789abcde") is None
    assert forge_law.cartridge_id_from_command("//EXECUTE_PROMPT forge-0123456789abcdef0") is None

    # Missing prefix
    assert forge_law.cartridge_id_from_command("//EXECUTE_PROMPT 0123456789abcdef") is None

    # No match
    assert forge_law.cartridge_id_from_command("some random text") is None
    assert forge_law.cartridge_id_from_command("//EXECUTE_PROMPT") is None
