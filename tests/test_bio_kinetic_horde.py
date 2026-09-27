# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Tests for Bio-Kinetic Swarm & Horde Substrate
==============================================
Validates:
  1. CamouflageCipher: AES-256-GCM encryption, HMAC verification, stealth masquerade.
  2. AegisShield: 4-Knight validation (Merlin ToT, Anya 10-line HITL, Forge AST, Sentinel secrets).
  3. BioHordeEngine: 20 fauna micro-workers, mode shifting (SWARM vs. HORDE), batch creation, reverse engineering.
  4. LadyApisConductor: API methods, Chimera Protocol v400.0, CloudBrain integration.
  5. Runic Router: //REVERSE_ENGINEER, //REVERSE, //HORDE REVERSE, //CORVUS dispatch.
"""

from __future__ import annotations

import importlib
from pathlib import Path
import sys
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control_plane.runes.runic_router import route_rune


@pytest.fixture
def bio_kinetic_module():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    return importlib.import_module("01_KERNEL.bio_kinetic")


def test_camouflage_cipher_encrypt_decrypt(bio_kinetic_module):
    cipher = bio_kinetic_module.CamouflageCipher()
    payload = {"mission": "secret_mission_01", "tokens": 120}
    envelope = cipher.encrypt_directive(payload)

    assert envelope["status"] == "COMPLIANT_OK"
    assert "_perf_blob" in envelope
    assert "_cache_digest" in envelope

    decrypted = cipher.decrypt_directive(envelope)
    assert decrypted["mission"] == "secret_mission_01"
    assert decrypted["tokens"] == 120


def test_camouflage_tamper_detection(bio_kinetic_module):
    cipher = bio_kinetic_module.CamouflageCipher()
    envelope = cipher.encrypt_directive({"data": "original"})
    parts = envelope["_perf_blob"].split(".", 1)
    tampered_blob = parts[0] + "." + parts[1][:-4] + "AAAA"
    envelope["_perf_blob"] = tampered_blob

    with pytest.raises(Exception):
        cipher.decrypt_directive(envelope)


def test_aegis_shield_governance(bio_kinetic_module):
    aegis = bio_kinetic_module.AegisShield(hitl_threshold_lines=10)

    # 1. Normal task passes
    res = aegis.audit_task("task_01", "BATCH_CREATION", {"target": "auth"}, diff_lines=5)
    assert res.passed is True
    assert res.hitl_required is False

    # 2. Over 10-line threshold triggers HITL
    res_hitl = aegis.audit_task("task_02", "BATCH_CREATION", {"target": "auth"}, diff_lines=25)
    assert res_hitl.passed is True
    assert res_hitl.hitl_required is True

    # 3. Secret keyword triggers Sentinel block
    res_sec = aegis.audit_task("task_03", "BATCH_CREATION", {"target": "auth", "secret": "sk-1234567890abcdef1234567890"})
    assert res_sec.passed is False
    assert any("SENTINEL_BLOCKED" in v for v in res_sec.violations)


def test_bio_horde_engine_workers_and_mode_shift(bio_kinetic_module, tmp_path):
    engine = bio_kinetic_module.BioHordeEngine(base_dir=tmp_path)
    assert len(engine.workers) == 20
    assert "formica_01" in engine.workers
    assert "corvus_01" in engine.workers
    assert "owl_01" in engine.workers

    # Mode shift
    engine.set_mode(bio_kinetic_module.HordeMode.HORDE)
    assert engine.mode == bio_kinetic_module.HordeMode.HORDE
    assert engine.cipher.get_stealth_process_title("HORDE") == "cargo-clippy-telemetry-daemon"


def test_bio_horde_batch_creation_execution(bio_kinetic_module, tmp_path):
    engine = bio_kinetic_module.BioHordeEngine(base_dir=tmp_path)
    engine.set_mode(bio_kinetic_module.HordeMode.HORDE)

    task = engine.submit_batch_task("TestWidget", ["generate_ast", "apply_luxora_gold"], worker_type="beaver")
    assert task.assigned_worker == "beaver_01"
    assert task.task_type == "BATCH_CREATION"

    tick_res = engine.tick()
    assert tick_res["tasks_processed"] == 1
    assert task.completed is True
    assert task.result_hash is not None


def test_bio_horde_reverse_engineering_execution(bio_kinetic_module, tmp_path):
    engine = bio_kinetic_module.BioHordeEngine(base_dir=tmp_path)
    engine.set_mode(bio_kinetic_module.HordeMode.HORDE)

    # Create dummy legacy target file
    legacy_file = tmp_path / "legacy_module.py"
    legacy_file.write_text(
        "import sys\nimport os\n\nclass LegacyEngine:\n    def run(self, arg):\n        pass\n\ndef helper():\n    return 42\n",
        encoding="utf-8",
    )

    task = engine.submit_reverse_engineering_task(str(legacy_file), worker_type="corvus")
    assert task.assigned_worker == "corvus_01"
    assert task.task_type == "REVERSE_ENGINEER"

    tick_res = engine.tick()
    assert tick_res["tasks_processed"] == 1
    assert task.completed is True
    assert task.reverse_engineering_artifact is not None

    artifact = task.reverse_engineering_artifact
    assert artifact["decompilation_status"] == "SUCCESS"
    class_names = [c["name"] for c in artifact["ast_symbols"]["classes"]]
    func_names = [f["name"] for f in artifact["ast_symbols"]["functions"]]
    assert "LegacyEngine" in class_names
    assert "helper" in func_names
    assert "skill_manifest" in artifact["synthesized_skill"]


def test_lady_apis_conductor_interface(bio_kinetic_module, tmp_path):
    conductor = bio_kinetic_module.LadyApisConductor(base_dir=tmp_path)
    status = conductor.get_status()
    assert status["commander"] == "LADY_APIS"
    assert status["workers_registered"] == 20

    # Chimera protocol pulse
    chimera_pulse = conductor.execute_chimera_research_pulse("test objective")
    assert chimera_pulse["chimera_protocol"] == "v400.0"
    assert len(chimera_pulse["rounds"]) == 3
    assert chimera_pulse["rounds"][0]["phase"] == "Semantic Auditing"

    # CloudBrain sync
    cloudbrain_sync = conductor.sync_ancestral_chimera_protocol()
    assert cloudbrain_sync["status"] == "SYNCHRONIZED"
    assert cloudbrain_sync["cloudbrain_node_uuid"] == "ba87d454-9335-4f2f-bf9f-f3845a8c6948"


def test_runic_router_reverse_engineering_routes():
    # Test //REVERSE_ENGINEER
    r1 = route_rune("//REVERSE_ENGINEER test_path", {})
    assert r1.rune == "//REVERSE_ENGINEER"
    assert r1.knight == "sir_codex"
    assert r1.queued is True

    # Test //REVERSE
    r2 = route_rune("//REVERSE test_path", {})
    assert r2.rune == "//REVERSE"
    assert r2.knight == "sir_codex"
    assert r2.queued is True

    # Test //HORDE with REVERSE directive
    r3 = route_rune("//HORDE REVERSE legacy_component", {})
    assert r3.rune == "//HORDE"
    assert r3.knight == "lady_apis"
    assert r3.queued is True

    # Test //CORVUS
    r4 = route_rune("//CORVUS legacy_component", {})
    assert r4.rune == "//CORVUS"
    assert r4.knight == "sir_codex"
    assert r4.queued is True
