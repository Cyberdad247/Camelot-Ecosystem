import json
import subprocess

from control_plane import boot_sequence, runic_router


def test_boot_rune_points_to_single_awaken_command(tmp_path, monkeypatch):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")

    result = runic_router.detect_and_route("//BOOT")

    assert result is not None
    assert result.metadata["canonical_command"] == "awaken"
    assert result.metadata["fallback"] == "python bin/awaken.py"


def test_hermes_omniroute_assignment_writes_zero_cost_artifact(tmp_path):
    home = tmp_path
    config_dir = home / "03_VAULT" / "training" / "configs" / "config"
    config_dir.mkdir(parents=True)
    hermes_dir = home / "02_FORGE" / "KINETIC_ARMORY" / "hermes-agent"
    hermes_dir.mkdir(parents=True)
    (hermes_dir / "cli.py").write_text("print('hermes')\n", encoding="utf-8")
    (config_dir / "omniroute.json").write_text(
        json.dumps(
            {
                "engines": {
                    "open_coder": {
                        "status": "active",
                        "provider": "local",
                        "tier": "free",
                    },
                    "gemini_flash": {
                        "status": "active",
                        "provider": "google",
                        "tier": "google_free",
                    },
                    "paid_model": {
                        "status": "active",
                        "provider": "vendor",
                        "tier": "paid",
                    },
                },
                "routing_matrix": {"strategy": "zero_cost_first"},
            }
        ),
        encoding="utf-8",
    )

    ok, detail = boot_sequence.boot_hermes_omniroute_orchestrator(home)

    artifact = json.loads(
        (
            home
            / "03_VAULT"
            / "runtime_state"
            / "hermes_omniroute_orchestrator_latest.json"
        ).read_text(encoding="utf-8")
    )
    assert ok is True
    assert "Hermes orchestrator assigned" in detail
    assert artifact["global_startup_command"] == "awaken"
    assert artifact["orchestrator"] == "sir_hermes"
    assert "open_coder" in artifact["zero_cost_engines"]
    assert "gemini_flash" in artifact["zero_cost_engines"]
    assert "paid_model" not in artifact["zero_cost_engines"]
    assert "sir_hermes" in artifact["free_terminals"]


def test_omniroute_uses_node_c_fallback_when_binary_missing(tmp_path, monkeypatch):
    home = tmp_path
    node_c = home / "02_FORGE" / "generated" / "ukg_omega_glyph_v1000" / "Node_C_Omni_Router"
    node_c.mkdir(parents=True)
    (node_c / "main.go").write_text("package main\n", encoding="utf-8")
    (node_c / "node_c_omni_router.exe").write_text("binary\n", encoding="utf-8")

    class FakeProc:
        pid = 4242
        returncode = None

        def poll(self):
            return None

    captured = {}

    monkeypatch.setattr(boot_sequence.platform, "system", lambda: "Linux")
    monkeypatch.setattr(boot_sequence, "_probe_port", lambda host, port: False)
    monkeypatch.setattr(boot_sequence.shutil, "which", lambda name: "go.exe" if name == "go" else None)

    def fake_popen(cmd, stdout=None, stderr=None, **kwargs):
        captured["cmd"] = cmd
        captured["cwd"] = kwargs["cwd"]
        return FakeProc()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    ok, detail = boot_sequence.boot_omniroute_gateway(home)

    assert ok is True
    assert "Node C Omni Router fallback spawned PID=4242" in detail
    assert captured["cmd"] == [
        str(node_c / "node_c_omni_router.exe"),
        "-serve",
        "-host",
        "127.0.0.1",
        "-port",
        "20128",
    ]
    assert captured["cwd"] == str(node_c)
