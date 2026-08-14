# SPDX-License-Identifier: MIT

import json
from pathlib import Path

from control_plane import runic_router
from scripts import nano_swarm_expand


def test_nano_swarm_alias_routes_manifest_dry_run(tmp_path, monkeypatch):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")

    result = runic_router.detect_and_route(
        "//nano-swarm expand --node Node_A_Frontend --dry-run",
        context={"surface": "pytest"},
    )

    assert result is not None
    assert result.rune == "//NANO_SWARM_EXPAND"
    assert result.knight == "sir_boris"
    assert result.mode == "SWARM"
    assert result.queued is True
    assert result.metadata["action"] == "nano_swarm_expand"
    assert result.metadata["dry_run"] is True
    assert result.metadata["status"] == "DRY_RUN_READY"
    assert result.metadata["node"] == "Node_A_Frontend"


def test_dry_run_expand_validates_manifest_and_writes_artifact(tmp_path):
    manifest = tmp_path / "ukg.json"
    output_dir = tmp_path / "dry_runs"
    manifest.write_text(
        json.dumps(
            {
                "artifact": "OMEGA-GLYPH-V1000-OMNI-CODEX",
                "artifact_type": "UKG_Nano_Crystal_Proposal",
                "version": "1000.3.0",
                "evidence_status": "planned",
                "physical_nodes": {
                    "Node_A_Frontend": {
                        "stack": ["React", "Zustand", "Tailwind_v4"],
                        "claimed_core_logic": "Anya_Codec_UI + Chrome_Native_Messaging_Bridge",
                        "evidence_class": "planned",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    result = nano_swarm_expand.dry_run_expand(
        node_name="Node_A_Frontend",
        manifest_path=manifest,
        output_dir=output_dir,
    )

    assert result["status"] == "DRY_RUN_READY"
    assert result["node"] == "Node_A_Frontend"
    artifact_path = Path(result["artifact_path"])
    assert artifact_path.exists()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["node"] == "Node_A_Frontend"
    assert artifact["rollback"] == "delete_dry_run_artifact"


def test_generate_node_artifact_writes_reversible_manifest(tmp_path):
    manifest = tmp_path / "ukg.json"
    output_dir = tmp_path / "generated"
    manifest.write_text(
        json.dumps(
            {
                "artifact": "OMEGA-GLYPH-V1000-OMNI-CODEX",
                "artifact_type": "UKG_Nano_Crystal_Proposal",
                "version": "1000.3.0",
                "evidence_status": "planned",
                "physical_nodes": {
                    "Node_A_Frontend": {
                        "stack": ["React", "Zustand", "Tailwind_v4"],
                        "claimed_core_logic": "Anya_Codec_UI + Chrome_Native_Messaging_Bridge",
                        "evidence_class": "planned",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    result = nano_swarm_expand.generate_node_artifact(
        node_name="Node_A_Frontend",
        manifest_path=manifest,
        output_dir=output_dir,
    )

    assert result["status"] == "GENERATED"
    node_dir = Path(result["node_dir"])
    assert (node_dir / "manifest.json").exists()
    assert (node_dir / "rollback.json").exists()
    generated = json.loads((node_dir / "manifest.json").read_text(encoding="utf-8"))
    rollback = json.loads((node_dir / "rollback.json").read_text(encoding="utf-8"))
    assert generated["node"] == "Node_A_Frontend"
    assert rollback["rollback_action"] == "delete_generated_node_dir"


def test_generate_node_source_writes_frontend_files_and_rollback(tmp_path):
    manifest = tmp_path / "ukg.json"
    output_dir = tmp_path / "generated"
    manifest.write_text(
        json.dumps(
            {
                "artifact": "OMEGA-GLYPH-V1000-OMNI-CODEX",
                "artifact_type": "UKG_Nano_Crystal_Proposal",
                "version": "1000.3.0",
                "evidence_status": "planned",
                "physical_nodes": {
                    "Node_A_Frontend": {
                        "stack": ["React", "Zustand", "Tailwind_v4"],
                        "claimed_core_logic": "Anya_Codec_UI + Chrome_Native_Messaging_Bridge",
                        "evidence_class": "planned",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    result = nano_swarm_expand.generate_node_source(
        node_name="Node_A_Frontend",
        manifest_path=manifest,
        output_dir=output_dir,
    )

    assert result["status"] == "SOURCE_GENERATED"
    node_dir = Path(result["node_dir"])
    assert (node_dir / "package.json").exists()
    assert (node_dir / "index.html").exists()
    assert (node_dir / "src" / "App.tsx").exists()
    assert (node_dir / "src" / "main.tsx").exists()
    assert (node_dir / "src" / "store.ts").exists()
    assert (node_dir / "src" / "nativeBridge.ts").exists()
    native_bridge = (node_dir / "src" / "nativeBridge.ts").read_text(encoding="utf-8")
    assert "fetchNanoSwarmStatus" in native_bridge
    assert "http://127.0.0.1:4180" in native_bridge
    rollback = json.loads((node_dir / "rollback.json").read_text(encoding="utf-8"))
    assert rollback["rollback_action"] == "delete_generated_node_dir"


def test_generate_node_source_writes_bifrost_rust_files(tmp_path):
    manifest = tmp_path / "ukg.json"
    output_dir = tmp_path / "generated"
    manifest.write_text(
        json.dumps(
            {
                "artifact": "OMEGA-GLYPH-V1000-OMNI-CODEX",
                "artifact_type": "UKG_Nano_Crystal_Proposal",
                "version": "1000.3.0",
                "evidence_status": "planned",
                "physical_nodes": {
                    "Node_B_Bifrost": {
                        "stack": ["Rust", "Tokio", "Serde"],
                        "claimed_core_logic": "4-Byte_Length_Prefixed_IO + Tailscale_TCP_Forwarding",
                        "evidence_class": "planned",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    result = nano_swarm_expand.generate_node_source(
        node_name="Node_B_Bifrost",
        manifest_path=manifest,
        output_dir=output_dir,
    )

    node_dir = Path(result["node_dir"])
    assert result["status"] == "SOURCE_GENERATED"
    assert (node_dir / "Cargo.toml").exists()
    assert (node_dir / "src" / "main.rs").exists()
    assert (node_dir / "rollback.json").exists()
    main_rs = (node_dir / "src" / "main.rs").read_text(encoding="utf-8")
    assert "--serve" in main_rs
    assert "serve_health" in main_rs


def test_generate_node_source_writes_omni_router_go_files(tmp_path):
    manifest = tmp_path / "ukg.json"
    output_dir = tmp_path / "generated"
    manifest.write_text(
        json.dumps(
            {
                "artifact": "OMEGA-GLYPH-V1000-OMNI-CODEX",
                "artifact_type": "UKG_Nano_Crystal_Proposal",
                "version": "1000.3.0",
                "evidence_status": "planned",
                "physical_nodes": {
                    "Node_C_Omni_Router": {
                        "stack": ["Go", "tsnet"],
                        "claimed_core_logic": "Embedded_Zero_Trust_VPN + MCP_Multiplexing",
                        "evidence_class": "planned",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    result = nano_swarm_expand.generate_node_source(
        node_name="Node_C_Omni_Router",
        manifest_path=manifest,
        output_dir=output_dir,
    )

    node_dir = Path(result["node_dir"])
    assert result["status"] == "SOURCE_GENERATED"
    assert (node_dir / "go.mod").exists()
    assert (node_dir / "main.go").exists()
    assert (node_dir / "rollback.json").exists()
    main_go = (node_dir / "main.go").read_text(encoding="utf-8")
    assert "BuildHTTPHandler" in main_go
    assert "/v1/nano-swarm/status" in main_go


def test_generate_node_source_writes_microvm_wasm_files(tmp_path):
    manifest = tmp_path / "ukg.json"
    output_dir = tmp_path / "generated"
    manifest.write_text(
        json.dumps(
            {
                "artifact": "OMEGA-GLYPH-V1000-OMNI-CODEX",
                "artifact_type": "UKG_Nano_Crystal_Proposal",
                "version": "1000.3.0",
                "evidence_status": "planned",
                "physical_nodes": {
                    "Node_D_MicroVM": {
                        "stack": ["Rust", "wasm-bindgen"],
                        "claimed_core_logic": "Deterministic_Soul_Algorithm_Execution",
                        "evidence_class": "aspirational",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    result = nano_swarm_expand.generate_node_source(
        node_name="Node_D_MicroVM",
        manifest_path=manifest,
        output_dir=output_dir,
    )

    node_dir = Path(result["node_dir"])
    assert result["status"] == "SOURCE_GENERATED"
    assert (node_dir / "Cargo.toml").exists()
    assert (node_dir / "src" / "lib.rs").exists()
    assert (node_dir / "src" / "main.rs").exists()
    assert (node_dir / "rollback.json").exists()
    main_rs = (node_dir / "src" / "main.rs").read_text(encoding="utf-8")
    assert "--serve" in main_rs
    assert "serve_health" in main_rs


def test_validate_ukg_proposal_returns_schema_and_evidence_summary(tmp_path):
    manifest = tmp_path / "ukg.json"
    manifest.write_text(
        json.dumps(
            {
                "artifact": "OMEGA-GLYPH-V1000-OMNI-CODEX",
                "artifact_type": "UKG_Nano_Crystal_Proposal",
                "version": "1000.3.0",
                "evidence_status": "planned",
                "physical_nodes": {
                    "Node_A_Frontend": {
                        "stack": ["React", "Zustand", "Tailwind_v4"],
                        "claimed_core_logic": "Anya_Codec_UI + Chrome_Native_Messaging_Bridge",
                        "evidence_class": "generated_artifact",
                    }
                },
                "claims_requiring_verification": [
                    "Z3 proof of zero memory leaks",
                    "instant rehydration via //nano-swarm expand",
                ],
            }
        ),
        encoding="utf-8",
    )

    result = nano_swarm_expand.validate_ukg_proposal(manifest)

    assert result["status"] == "SCHEMA_VALID"
    assert result["node_count"] == 1
    assert result["claims_requiring_verification"] == 2
    assert result["evidence_classes"]["generated_artifact"] == 1


def test_write_evidence_report_persists_schema_result(tmp_path):
    manifest = tmp_path / "ukg.json"
    report_dir = tmp_path / "reports"
    manifest.write_text(
        json.dumps(
            {
                "artifact": "OMEGA-GLYPH-V1000-OMNI-CODEX",
                "artifact_type": "UKG_Nano_Crystal_Proposal",
                "version": "1000.3.0",
                "evidence_status": "planned",
                "physical_nodes": {
                    "Node_A_Frontend": {
                        "stack": ["React"],
                        "claimed_core_logic": "Anya_Codec_UI",
                        "evidence_class": "generated_artifact",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    result = nano_swarm_expand.write_evidence_report(manifest, report_dir)

    report_path = Path(result["report_path"])
    assert result["status"] == "EVIDENCE_RECORDED"
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["schema"]["status"] == "SCHEMA_VALID"
    assert report["source_manifest"].endswith("ukg.json")


def test_nano_swarm_evidence_route_records_report(tmp_path, monkeypatch):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")
    manifest = tmp_path / "ukg.json"
    manifest.write_text(
        json.dumps(
            {
                "artifact": "OMEGA-GLYPH-V1000-OMNI-CODEX",
                "artifact_type": "UKG_Nano_Crystal_Proposal",
                "version": "1000.3.0",
                "evidence_status": "planned",
                "physical_nodes": {
                    "Node_A_Frontend": {
                        "stack": ["React"],
                        "claimed_core_logic": "Anya_Codec_UI",
                        "evidence_class": "generated_artifact",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    result = runic_router.detect_and_route(
        f"//nano-swarm expand --manifest {manifest} --report-dir {tmp_path / 'route_reports'} --evidence",
        context={"surface": "pytest"},
    )

    assert result is not None
    assert result.metadata["status"] == "EVIDENCE_RECORDED"
    assert result.metadata["schema_status"] == "SCHEMA_VALID"
    assert Path(result.metadata["report_path"]).exists()


def test_create_checkpoint_records_verified_milestone(tmp_path):
    manifest = tmp_path / "ukg.json"
    checkpoint_dir = tmp_path / "checkpoints"
    manifest.write_text(
        json.dumps(
            {
                "artifact": "OMEGA-GLYPH-V1000-OMNI-CODEX",
                "artifact_type": "UKG_Nano_Crystal_Proposal",
                "version": "1000.3.0",
                "evidence_status": "planned",
                "physical_nodes": {
                    "Node_A_Frontend": {
                        "stack": ["React"],
                        "claimed_core_logic": "Anya_Codec_UI",
                        "evidence_class": "built_verified",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    result = nano_swarm_expand.create_checkpoint(manifest, checkpoint_dir)

    checkpoint_path = Path(result["checkpoint_path"])
    assert result["status"] == "CHECKPOINT_RECORDED"
    assert checkpoint_path.exists()
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    assert checkpoint["manifest"]["artifact"] == "OMEGA-GLYPH-V1000-OMNI-CODEX"


def test_rollback_generated_node_deletes_only_declared_target(tmp_path):
    node_dir = tmp_path / "generated" / "Node_A_Frontend" / "source"
    node_dir.mkdir(parents=True)
    (node_dir / "App.tsx").write_text("export function App() { return null; }\n", encoding="utf-8")
    rollback = node_dir / "rollback.json"
    rollback.write_text(
        json.dumps(
            {
                "node": "Node_A_Frontend",
                "rollback_action": "delete_generated_node_dir",
                "target": str(node_dir),
                "safe_to_delete": True,
            }
        ),
        encoding="utf-8",
    )

    result = nano_swarm_expand.rollback_generated_node("Node_A_Frontend", rollback)

    assert result["status"] == "ROLLED_BACK"
    assert not node_dir.exists()


def test_promote_generated_node_copies_to_forge_path(tmp_path):
    source_dir = tmp_path / "source"
    forge_dir = tmp_path / "forge"
    source_dir.mkdir()
    (source_dir / "README.md").write_text("source\n", encoding="utf-8")
    (source_dir / "rollback.json").write_text(
        json.dumps(
            {
                "node": "Node_A_Frontend",
                "rollback_action": "delete_generated_node_dir",
                "target": str(source_dir),
                "safe_to_delete": True,
            }
        ),
        encoding="utf-8",
    )

    result = nano_swarm_expand.promote_generated_node(
        "Node_A_Frontend",
        source_dir=source_dir,
        forge_root=forge_dir,
    )

    promoted_dir = Path(result["promoted_dir"])
    assert result["status"] == "PROMOTED"
    assert (promoted_dir / "README.md").exists()
    assert (promoted_dir / "promotion.json").exists()


def test_formal_claims_gate_blocks_until_all_formally_evidenced(tmp_path):
    audit = tmp_path / "formal_claims_audit.json"
    audit.write_text(
        json.dumps(
            {
                "claims": [
                    {"claim": "compression", "status": "FORMALLY_EVIDENCED"},
                    {"claim": "z3", "status": "UNPROVEN"},
                ]
            }
        ),
        encoding="utf-8",
    )

    result = nano_swarm_expand.evaluate_formal_claims_gate(audit)

    assert result["status"] == "BLOCKED"
    assert result["ready_for_omni_codex_compiled"] is False


def test_formal_claims_gate_allows_production_release_with_aspirational_claims_gated(tmp_path):
    audit = tmp_path / "formal_claims_audit.json"
    audit.write_text(
        json.dumps(
            {
                "claims": [
                    {"claim": "absolute z3 proof", "status": "UNPROVEN"},
                ],
                "production_release_gate": {
                    "status": "READY",
                    "checks": [
                        {"claim": "builds pass", "status": "EVIDENCED"},
                        {"claim": "runtime services start", "status": "EVIDENCED"},
                    ],
                },
            }
        ),
        encoding="utf-8",
    )

    result = nano_swarm_expand.evaluate_formal_claims_gate(audit)

    assert result["status"] == "READY"
    assert result["ready_for_production_release"] is True
    assert result["ready_for_omni_codex_compiled"] is False
    assert result["aspirational_claims_gated"][0]["claim"] == "absolute z3 proof"


def test_bifrost_preflight_detects_existing_listener(monkeypatch):
    monkeypatch.setattr(nano_swarm_expand, "_port_open", lambda host, port: True)

    result = nano_swarm_expand.bifrost_sidecar_preflight()

    assert result["status"] == "ALREADY_RUNNING"
    assert result["should_launch"] is False
