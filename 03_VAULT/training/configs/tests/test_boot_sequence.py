from __future__ import annotations

import shutil
from pathlib import Path

from control_plane.cloud_services import CloudServiceName

from control_plane import boot_sequence


def _case_dir(name: str) -> Path:
    root = Path("data") / "pytest-boot-sequence" / name
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True)
    return root


def test_boot_morgana_bridge_reports_existing_secure_bridge(monkeypatch):
    home = _case_dir("morgana-existing")
    monkeypatch.setattr(boot_sequence, "_read_bifrost_token", lambda: "token")
    monkeypatch.setattr(
        boot_sequence,
        "_morgana_bridge_status",
        lambda token: (True, "health=200 protected=200 unauth=401"),
    )

    ok, message = boot_sequence.boot_morgana_bridge(home)

    assert ok is True
    assert "already running" in message
    assert "unauth=401" in message


def test_boot_morgana_bridge_requires_token(monkeypatch):
    home = _case_dir("morgana-missing-token")
    binary = home / "01_KERNEL" / "senses" / "morgana_bridge" / "target" / "debug" / "morgana_bridge.exe"
    binary.parent.mkdir(parents=True)
    binary.write_text("stub", encoding="utf-8")
    monkeypatch.setattr(boot_sequence, "_read_bifrost_token", lambda: None)
    monkeypatch.setattr(boot_sequence, "_morgana_bridge_binary", lambda _: binary)
    monkeypatch.setattr(
        boot_sequence,
        "_morgana_bridge_status",
        lambda token: (False, "health=unreachable"),
    )

    ok, message = boot_sequence.boot_morgana_bridge(home)

    assert ok is False
    assert "token missing" in message


def test_boot_morgana_bridge_spawns_and_verifies_secure_routes(monkeypatch):
    home = _case_dir("morgana-spawn") / "CAMELOT_OS"
    binary = home / "01_KERNEL" / "senses" / "morgana_bridge" / "target" / "debug" / "morgana_bridge.exe"
    binary.parent.mkdir(parents=True)
    binary.write_text("stub", encoding="utf-8")
    calls = {"status": 0}

    class _Proc:
        pid = 1234
        returncode = None

        def poll(self):
            return None

    def _status(token):
        calls["status"] += 1
        if calls["status"] == 1:
            return False, "health=unreachable"
        return True, "health=200 protected=200 unauth=401"

    def _popen(args, **kwargs):
        assert args == [str(binary)]
        assert kwargs["env"]["CAMELOT_GATEWAY_TOKEN"] == "token"
        assert kwargs["env"]["BIFROST_BIND_ADDR"] == "127.0.0.1:8001"
        assert Path(kwargs["cwd"]).name == "morgana_bridge"
        return _Proc()

    monkeypatch.setattr(boot_sequence, "_read_bifrost_token", lambda: "token")
    monkeypatch.setattr(boot_sequence, "_morgana_bridge_binary", lambda _: binary)
    monkeypatch.setattr(boot_sequence, "_morgana_bridge_status", _status)
    monkeypatch.setattr(boot_sequence, "_child_spawn_kwargs", lambda *, cwd: {"cwd": cwd})
    monkeypatch.setattr(boot_sequence.platform, "system", lambda: "Linux")
    monkeypatch.setattr(boot_sequence.subprocess, "Popen", _popen)
    monkeypatch.setattr(boot_sequence.time, "sleep", lambda _: None)

    ok, message = boot_sequence.boot_morgana_bridge(home)

    assert ok is True
    assert "PID=1234" in message
    assert (home / "logs" / "morgana_bridge.pid").read_text(encoding="ascii") == "1234"


def test_boot_cloud_brain_keeps_local_ready_when_remote_check_is_blocked(monkeypatch):
    class _Result:
        success = True
        source = "local"
        error = "All connection attempts failed"
        result = {
            "topology": {"service": "long_term_cloudbrain"},
            "remote_runtime_error": "All connection attempts failed",
        }

    class _Router:
        async def invoke(self, request):
            assert request.service == CloudServiceName.CLOUDBRAIN_STATUS
            return _Result()

    monkeypatch.setattr(boot_sequence, "CloudServiceRouter", _Router)

    ok, message = boot_sequence.boot_cloud_brain(_case_dir("cloudbrain-local-ready"))

    assert ok is True
    assert "LOCAL READY" in message
    assert "remote check blocked" in message


def test_boot_telemetry_hidden_windows_tui_is_available_not_failed(monkeypatch):
    home = _case_dir("telemetry-hidden")
    binary = home / "bin" / "vizion-telemetry.exe"
    binary.parent.mkdir(parents=True)
    binary.write_text("stub", encoding="utf-8")

    class _Proc:
        returncode = 1

        def poll(self):
            return 1

    monkeypatch.delenv("CAMELOT_VISIBLE_CHILDREN", raising=False)
    monkeypatch.setattr(boot_sequence.platform, "system", lambda: "Windows")
    monkeypatch.setattr(boot_sequence.subprocess, "Popen", lambda *_, **__: _Proc())
    monkeypatch.setattr(boot_sequence.time, "sleep", lambda _: None)

    ok, message = boot_sequence.boot_telemetry(home)

    assert ok is True
    assert "interactive TUI skipped" in message


def test_child_python_env_isolates_venv_and_forces_utf8():
    python_exe = Path("C:/tmp/camelot/.venv_camelot/Scripts/python.exe")

    env = boot_sequence._child_python_env(str(python_exe))

    assert "PYTHONHOME" not in env
    assert "PYTHONPATH" not in env
    assert "__PYVENV_LAUNCHER__" not in env
    assert env["PYTHONNOUSERSITE"] == "1"
    assert env["PYTHONUTF8"] == "1"
    assert env["PYTHONIOENCODING"] == "utf-8"
    assert env["VIRTUAL_ENV"].endswith(".venv_camelot")


def test_start_local_lt_memory_windows_launcher_sets_clean_env(monkeypatch):
    home = _case_dir("lt-memory-windows") / "CAMELOT_OS"
    server = home / "03_VAULT" / "training" / "configs" / "local_lt_memory.py"
    server.parent.mkdir(parents=True)
    server.write_text("app = object()\n", encoding="utf-8")
    venv_py = home / ".venv_camelot" / "Scripts" / "python.exe"
    venv_py.parent.mkdir(parents=True)
    venv_py.write_text("stub", encoding="utf-8")
    probes = {"count": 0}

    class _Completed:
        returncode = 0
        stdout = "4321\n"
        stderr = ""

    def _probe(_host, _port, timeout=1.0):
        probes["count"] += 1
        return probes["count"] > 1

    def _run(args, **kwargs):
        assert args[0] == "powershell"
        assert kwargs["env"]["LT_MEMORY_PYTHON"] == str(venv_py)
        assert kwargs["env"]["CAMELOT_OS_HOME"] == str(home)
        assert kwargs["env"]["PYTHONIOENCODING"] == "utf-8"
        assert kwargs["env"]["PYTHONNOUSERSITE"] == "1"
        return _Completed()

    monkeypatch.setattr(boot_sequence.platform, "system", lambda: "Windows")
    monkeypatch.setattr(boot_sequence, "_probe_port", _probe)
    monkeypatch.setattr(boot_sequence.subprocess, "run", _run)
    monkeypatch.setattr(boot_sequence.time, "sleep", lambda _: None)
    monkeypatch.setenv("CAMELOT_ALLOW_NONINTERACTIVE_LT_SPAWN", "1")

    ok, message = boot_sequence.start_local_lt_memory(home)

    assert ok is True
    assert "PID=4321" in message
    assert (home / "logs" / "lt_memory.pid").read_text(encoding="utf-8") == "4321"
