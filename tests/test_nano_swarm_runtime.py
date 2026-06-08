import json
from pathlib import Path

from control_plane import runic_router
from control_plane import nano_swarm_runtime
from control_plane.camelot_cli import _build_parser


def _write_node(root: Path, node: str) -> None:
    node_dir = root / node
    node_dir.mkdir(parents=True)
    for rel in nano_swarm_runtime.EXPECTED_NODES[node]["required_files"]:
        marker = node_dir / rel
        marker.parent.mkdir(parents=True, exist_ok=True)
        if marker.name != "promotion.json":
            marker.write_text("marker\n", encoding="utf-8")
    (node_dir / "promotion.json").write_text(
        json.dumps({"status": "PROMOTED", "node": node}),
        encoding="utf-8",
    )


def test_runtime_status_reports_promoted_nodes_and_formal_gate(tmp_path):
    promoted_root = tmp_path / "forge" / "ukg"
    evidence_dir = tmp_path / "evidence"
    state_dir = tmp_path / "state"
    evidence_dir.mkdir()
    for node in nano_swarm_runtime.EXPECTED_NODES:
        _write_node(promoted_root, node)
    (evidence_dir / "verify_all_latest.json").write_text(
        json.dumps({"status": "VERIFIED", "formal_gate": {"status": "BLOCKED"}}),
        encoding="utf-8",
    )

    result = nano_swarm_runtime.read_runtime_status(
        promoted_root=promoted_root,
        evidence_dir=evidence_dir,
        state_dir=state_dir,
    )

    assert result["status"] == "RUNTIME_READY_FORMAL_GATE_BLOCKED"
    assert result["runtime_ready"] is True
    assert result["formal_gate_status"] == "BLOCKED"
    assert sorted(result["nodes"]) == sorted(nano_swarm_runtime.EXPECTED_NODES)
    assert all(node["promoted"] for node in result["nodes"].values())


def test_write_runtime_status_persists_latest_artifact(tmp_path):
    promoted_root = tmp_path / "forge" / "ukg"
    evidence_dir = tmp_path / "evidence"
    state_dir = tmp_path / "state"
    evidence_dir.mkdir()
    for node in nano_swarm_runtime.EXPECTED_NODES:
        _write_node(promoted_root, node)
    (evidence_dir / "verify_all_latest.json").write_text(
        json.dumps({"status": "VERIFIED", "formal_gate": {"status": "BLOCKED"}}),
        encoding="utf-8",
    )

    result = nano_swarm_runtime.write_runtime_status(
        promoted_root=promoted_root,
        evidence_dir=evidence_dir,
        state_dir=state_dir,
    )

    artifact_path = Path(result["artifact_path"])
    assert result["status"] == "RUNTIME_READY_FORMAL_GATE_BLOCKED"
    assert artifact_path.exists()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runtime_ready"] is True


def test_nano_swarm_runtime_status_route_records_status(tmp_path, monkeypatch):
    promoted_root = tmp_path / "forge" / "ukg"
    evidence_dir = tmp_path / "evidence"
    state_dir = tmp_path / "state"
    evidence_dir.mkdir()
    for node in nano_swarm_runtime.EXPECTED_NODES:
        _write_node(promoted_root, node)
    (evidence_dir / "verify_all_latest.json").write_text(
        json.dumps({"status": "VERIFIED", "formal_gate": {"status": "BLOCKED"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")
    monkeypatch.setattr(nano_swarm_runtime, "PROMOTED_ROOT", promoted_root)
    monkeypatch.setattr(nano_swarm_runtime, "EVIDENCE_DIR", evidence_dir)
    monkeypatch.setattr(nano_swarm_runtime, "RUNTIME_STATE_DIR", state_dir)

    result = runic_router.detect_and_route(
        "//nano-swarm expand --runtime-status",
        context={"surface": "pytest"},
    )

    assert result is not None
    assert result.metadata["runtime_status"] is True
    assert result.metadata["status"] == "RUNTIME_READY_FORMAL_GATE_BLOCKED"
    assert result.metadata["runtime_ready"] is True
    assert Path(result.metadata["artifact_path"]).parent == state_dir


def test_camelot_cli_parser_accepts_nano_swarm_status():
    parser = _build_parser()

    args = parser.parse_args(["nano-swarm", "status"])

    assert args.command == "nano-swarm"
    assert args.nano_swarm_command == "status"


def test_supervisor_status_reports_startable_and_non_startable_nodes(tmp_path):
    promoted_root = tmp_path / "forge" / "ukg"
    state_dir = tmp_path / "state"
    for node in nano_swarm_runtime.EXPECTED_NODES:
        _write_node(promoted_root, node)

    result = nano_swarm_runtime.supervise_nodes(
        "status",
        promoted_root=promoted_root,
        state_dir=state_dir,
    )

    assert result["status"] == "SUPERVISOR_STATUS"
    assert result["nodes"]["Node_A_Frontend"]["startable"] is True
    assert result["nodes"]["Node_A_Frontend"]["process_status"] == "STOPPED"
    assert result["nodes"]["Node_C_Omni_Router"]["startable"] is True
    assert result["nodes"]["Node_C_Omni_Router"]["process_status"] == "STOPPED"
    assert result["nodes"]["Node_B_Bifrost"]["startable"] is True
    assert result["nodes"]["Node_B_Bifrost"]["process_status"] == "STOPPED"
    assert result["nodes"]["Node_D_MicroVM"]["startable"] is True
    assert result["nodes"]["Node_D_MicroVM"]["process_status"] == "STOPPED"


def test_supervisor_start_non_startable_node_is_blocked(tmp_path, monkeypatch):
    promoted_root = tmp_path / "forge" / "ukg"
    state_dir = tmp_path / "state"
    for node in nano_swarm_runtime.EXPECTED_NODES:
        _write_node(promoted_root, node)
    patched_nodes = {
        name: {**spec}
        for name, spec in nano_swarm_runtime.EXPECTED_NODES.items()
    }
    patched_nodes["Node_B_Bifrost"]["service_command"] = None
    monkeypatch.setattr(nano_swarm_runtime, "EXPECTED_NODES", patched_nodes)

    result = nano_swarm_runtime.supervise_nodes(
        "start",
        node_name="Node_B_Bifrost",
        promoted_root=promoted_root,
        state_dir=state_dir,
    )

    assert result["status"] == "SUPERVISOR_BLOCKED"
    assert result["nodes"]["Node_B_Bifrost"]["reason"] == "node has no durable service command"


def test_nano_swarm_supervise_route_reports_status(tmp_path, monkeypatch):
    promoted_root = tmp_path / "forge" / "ukg"
    state_dir = tmp_path / "state"
    for node in nano_swarm_runtime.EXPECTED_NODES:
        _write_node(promoted_root, node)
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")
    monkeypatch.setattr(nano_swarm_runtime, "PROMOTED_ROOT", promoted_root)
    monkeypatch.setattr(nano_swarm_runtime, "RUNTIME_STATE_DIR", state_dir)

    result = runic_router.detect_and_route(
        "//nano-swarm supervise status",
        context={"surface": "pytest"},
    )

    assert result is not None
    assert result.metadata["supervise"] is True
    assert result.metadata["status"] == "SUPERVISOR_STATUS"
    assert result.metadata["nodes"]["Node_A_Frontend"]["startable"] is True


def test_camelot_cli_parser_accepts_nano_swarm_supervise_start():
    parser = _build_parser()

    args = parser.parse_args(["nano-swarm", "supervise", "start", "--node", "Node_A_Frontend"])

    assert args.command == "nano-swarm"
    assert args.nano_swarm_command == "supervise"
    assert args.supervise_action == "start"
    assert args.node == "Node_A_Frontend"
