# SPDX-License-Identifier: MIT

import json


from control_plane import boot_sequence
from control_plane.cli.parser import _build_parser


def test_vps_hermes_prime_contract_binds_startup_command_and_bifrost(tmp_path):
    from control_plane.infra.vps_hermes_prime import build_vps_hermes_prime_contract

    topology_path = tmp_path / "03_VAULT" / "runtime_state" / "sovereign_mesh_topology.json"
    topology_path.parent.mkdir(parents=True)
    topology_path.write_text(
        json.dumps(
            {
                "nodes": {
                    "vps_hub_kvm563": {
                        "public_ip": "162.35.107.134",
                        "tailscale_ip": "100.110.180.18",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    contract = build_vps_hermes_prime_contract(root=tmp_path)

    assert contract["status"] == "CONFIGURED"
    assert contract["node_id"] == "vps_hub_kvm563"
    assert contract["assigned_knight"] == "HERMES_PRIME"
    assert contract["global_startup_command"] == "awaken"
    assert contract["global_cli_command"] == "camelot hermes"
    assert contract["secret_values_serialized"] is False
    assert contract["tailscale_ip"] == "100.110.180.18"

    cliproxy = contract["inference_links"]["cliproxy_sie"]
    assert cliproxy["selector"] == "cliproxy:default"
    assert cliproxy["governing_knight"] == "HERMES_PRIME"
    assert cliproxy["secret_values_serialized"] is False

    bifrost_bridge = cliproxy["bifrost_bridge"]
    assert bifrost_bridge["gateway_url"] == "http://100.110.180.18:3001"
    assert bifrost_bridge["mesh_bridge_url"] == "http://100.110.180.18:8095"
    assert bifrost_bridge["auth"]["secret_values_serialized"] is False


def test_vps_hermes_prime_live_status_uses_probe_injection(tmp_path):
    from control_plane.infra.vps_hermes_prime import summarize_vps_hermes_prime

    seen: list[tuple[str, int]] = []

    def fake_probe(host: str, port: int, timeout: float = 0.0) -> bool:
        seen.append((host, port))
        return port in {3001, 8095}

    status = summarize_vps_hermes_prime(
        root=tmp_path,
        tailscale_ip="100.110.180.18",
        probe_live=True,
        port_probe=fake_probe,
    )

    assert status["status"] == "ONLINE"
    assert status["services"]["bifrost_gateway"]["state"] == "ONLINE"
    assert status["services"]["mesh_bridge"]["state"] == "ONLINE"
    assert status["services"]["ssh"]["state"] == "OFFLINE"
    assert ("100.110.180.18", 3001) in seen
    assert ("100.110.180.18", 8095) in seen


def test_boot_sequence_has_non_blocking_vps_hermes_prime_phase(tmp_path):
    ok, detail = boot_sequence.boot_vps_hermes_prime(tmp_path, probe_live=False)

    assert ok is True
    assert "HERMES_PRIME" in detail
    assert "Bifrost" in detail
    assert "camelot hermes" in detail


def test_camelot_control_plane_parser_registers_hermes_command():
    args = _build_parser().parse_args(["hermes", "--json", "--no-probe"])

    assert args.command == "hermes"
    assert args.json is True
    assert args.probe_live is False


def test_global_camelot_hermes_command_emits_json(monkeypatch, capsys, tmp_path):
    import bin.camelot as camelot

    monkeypatch.setattr(camelot, "_REPO", tmp_path)
    monkeypatch.setattr("sys.argv", ["camelot", "hermes", "--json", "--no-probe"])

    camelot.main()

    payload = json.loads(capsys.readouterr().out)
    assert payload["assigned_knight"] == "HERMES_PRIME"
    assert payload["global_cli_command"] == "camelot hermes"
    assert payload["secret_values_serialized"] is False
