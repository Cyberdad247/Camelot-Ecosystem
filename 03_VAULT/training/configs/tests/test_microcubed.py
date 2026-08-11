from __future__ import annotations

import json
import sys
from pathlib import Path

from control_plane.infra.microcubed import MicrocubedRequest

from control_plane.infra import microcubed


def test_forge_house_writes_contract_and_manifest(monkeypatch, tmp_path: Path):
    state_dir = tmp_path / "runtime_state" / "microcubed"
    monkeypatch.setattr(microcubed, "STATE_DIR", state_dir)
    monkeypatch.setattr(microcubed, "LATEST_PATH", state_dir / "microcubed_latest.json")
    monkeypatch.setattr(microcubed, "INDEX_PATH", state_dir / "microcubed_index.jsonl")
    monkeypatch.setattr(microcubed, "QUEUE_FILE", tmp_path / "logs" / "harness_queue.jsonl")

    result = microcubed.forge_house(
        MicrocubedRequest(
            objective="verify isolated task house",
            knight="sir_forge",
            timeout_seconds=120,
            max_write_mb=5,
        )
    )

    contract_path = Path(result["contract"]["paths"]["contract"])
    manifest_path = Path(result["contract"]["paths"]["manifest"])
    assert result["status"] == "READY"
    assert result["contract"]["tenant"] == "sir_forge"
    assert result["contract"]["resource_caps"]["timeout_seconds"] == 120
    assert contract_path.exists()
    assert manifest_path.exists()
    assert json.loads(contract_path.read_text(encoding="utf-8"))["status"] == "READY"
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["teardown_ready"] is False


def test_forge_house_can_queue_tenant_directive(monkeypatch, tmp_path: Path):
    state_dir = tmp_path / "runtime_state" / "microcubed"
    queue_path = tmp_path / "logs" / "harness_queue.jsonl"
    monkeypatch.setattr(microcubed, "STATE_DIR", state_dir)
    monkeypatch.setattr(microcubed, "LATEST_PATH", state_dir / "microcubed_latest.json")
    monkeypatch.setattr(microcubed, "INDEX_PATH", state_dir / "microcubed_index.jsonl")
    monkeypatch.setattr(microcubed, "QUEUE_FILE", queue_path)

    result = microcubed.forge_house(
        MicrocubedRequest(objective="queue contained work", knight="sir_codex", queue=True)
    )

    assert result["queue"]["queued"] is True
    queued = json.loads(queue_path.read_text(encoding="utf-8").splitlines()[0])
    assert queued["knight"] == "sir_codex"
    assert queued["microcubed_house"] == result["contract"]["house_id"]


def test_teardown_archives_and_removes_house(monkeypatch, tmp_path: Path):
    state_dir = tmp_path / "runtime_state" / "microcubed"
    monkeypatch.setattr(microcubed, "STATE_DIR", state_dir)
    monkeypatch.setattr(microcubed, "LATEST_PATH", state_dir / "microcubed_latest.json")
    monkeypatch.setattr(microcubed, "INDEX_PATH", state_dir / "microcubed_index.jsonl")

    result = microcubed.forge_house(MicrocubedRequest(objective="temporary house"))
    house_id = result["contract"]["house_id"]
    house_path = Path(result["house"])

    torn_down = microcubed.teardown_house(house_id)

    assert torn_down["status"] == "TORN_DOWN"
    assert not house_path.exists()
    assert Path(torn_down["archive"]).exists()


def test_execute_house_runs_command_inside_workspace_and_captures_output(monkeypatch, tmp_path: Path):
    state_dir = tmp_path / "runtime_state" / "microcubed"
    monkeypatch.setattr(microcubed, "STATE_DIR", state_dir)
    monkeypatch.setattr(microcubed, "LATEST_PATH", state_dir / "microcubed_latest.json")
    monkeypatch.setattr(microcubed, "INDEX_PATH", state_dir / "microcubed_index.jsonl")

    forged = microcubed.forge_house(MicrocubedRequest(objective="execute contained command"))
    house_id = forged["contract"]["house_id"]
    workspace = Path(forged["contract"]["paths"]["workspace"])

    result = microcubed.execute_house(
        house_id,
        [
            sys.executable,
            "-c",
            "from pathlib import Path; Path('out.txt').write_text('ok', encoding='utf-8'); print(Path.cwd())",
        ],
    )

    manifest = json.loads(Path(forged["contract"]["paths"]["manifest"]).read_text(encoding="utf-8"))
    latest = json.loads((state_dir / "microcubed_latest.json").read_text(encoding="utf-8"))
    output_log = Path(result["execution"]["output_log"])
    assert result["status"] == "COMPLETE"
    assert result["execution"]["returncode"] == 0
    assert output_log.exists()
    assert str(workspace) in json.loads(output_log.read_text(encoding="utf-8"))["stdout"]
    assert (workspace / "out.txt").read_text(encoding="utf-8") == "ok"
    assert manifest["status"] == "COMPLETE"
    assert latest["status"] == "COMPLETE"
    assert "out.txt" in manifest["workspace_files"]


def test_execute_house_blocks_dangerous_command_before_subprocess(monkeypatch, tmp_path: Path):
    state_dir = tmp_path / "runtime_state" / "microcubed"
    monkeypatch.setattr(microcubed, "STATE_DIR", state_dir)
    monkeypatch.setattr(microcubed, "LATEST_PATH", state_dir / "microcubed_latest.json")
    monkeypatch.setattr(microcubed, "INDEX_PATH", state_dir / "microcubed_index.jsonl")

    forged = microcubed.forge_house(MicrocubedRequest(objective="block destructive command"))
    house_id = forged["contract"]["house_id"]

    result = microcubed.execute_house(house_id, ["powershell", "-Command", "Remove-Item -Recurse C:\\tmp"])

    manifest = json.loads(Path(forged["contract"]["paths"]["manifest"]).read_text(encoding="utf-8"))
    assert result["status"] == "BLOCKED_BY_SENTINEL"
    assert result["preflight"]["status"] == "BLOCKED_BY_SENTINEL"
    assert manifest["status"] == "BLOCKED_BY_SENTINEL"
    assert "execution" not in result


def test_execute_house_marks_failed_on_nonzero_returncode(monkeypatch, tmp_path: Path):
    state_dir = tmp_path / "runtime_state" / "microcubed"
    monkeypatch.setattr(microcubed, "STATE_DIR", state_dir)
    monkeypatch.setattr(microcubed, "LATEST_PATH", state_dir / "microcubed_latest.json")
    monkeypatch.setattr(microcubed, "INDEX_PATH", state_dir / "microcubed_index.jsonl")

    forged = microcubed.forge_house(MicrocubedRequest(objective="capture failed command"))
    house_id = forged["contract"]["house_id"]

    result = microcubed.execute_house(
        house_id,
        [sys.executable, "-c", "import sys; print('bad exit'); sys.exit(3)"],
    )

    manifest = json.loads(Path(forged["contract"]["paths"]["manifest"]).read_text(encoding="utf-8"))
    output_log = Path(result["execution"]["output_log"])
    assert result["status"] == "FAILED"
    assert result["execution"]["returncode"] == 3
    assert json.loads(output_log.read_text(encoding="utf-8"))["stdout"].strip() == "bad exit"
    assert manifest["status"] == "FAILED"


def test_inspect_house_summarizes_contract_manifest_and_last_output(monkeypatch, tmp_path: Path):
    state_dir = tmp_path / "runtime_state" / "microcubed"
    monkeypatch.setattr(microcubed, "STATE_DIR", state_dir)
    monkeypatch.setattr(microcubed, "LATEST_PATH", state_dir / "microcubed_latest.json")
    monkeypatch.setattr(microcubed, "INDEX_PATH", state_dir / "microcubed_index.jsonl")

    forged = microcubed.forge_house(MicrocubedRequest(objective="inspect completed house", knight="sir_codex"))
    house_id = forged["contract"]["house_id"]
    microcubed.execute_house(
        house_id,
        [sys.executable, "-c", "from pathlib import Path; Path('inspect.txt').write_text('ready', encoding='utf-8'); print('inspect-ok')"],
    )

    result = microcubed.inspect_house(house_id)

    assert result["status"] == "OK"
    assert result["house_id"] == house_id
    assert result["contract"]["tenant"] == "sir_codex"
    assert result["manifest"]["status"] == "COMPLETE"
    assert result["teardown_ready"] is True
    assert result["workspace_files"] == ["inspect.txt"]
    assert result["last_execution"]["returncode"] == 0
    assert result["last_output"]["stdout"].strip() == "inspect-ok"
    assert Path(result["paths"]["contract"]).exists()
