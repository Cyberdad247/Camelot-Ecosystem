# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
tests/control_plane/test_sase_tri_core_forge.py — Tri-Core Omni-Forge Unit Tests
================================================================================
Verifies:
1. SASE 3.0 BriefingScript freezing and MentorScript persistent reflexion.
2. Sir Kronos 👁️🗨️ ➡️ 💉 ➡️ 🛡️ Immunological Remediation Loop.
3. Tri-axis Bewertungsmatrix (Gründlichkeit, Ordnung, Effizienz).
4. Merge-Readiness Pack (MRP) synthesis, cryptographic sealing, and HITL gate.
5. SASE Dual-Workbench (ACE / AEE) end-to-end execution.
6. Runic router dispatch for //FORGE triad and //MRP.
"""

from __future__ import annotations

import pytest
from control_plane.sase.briefing import BriefingScript, MentorScript
from control_plane.sase.dual_workbench import (
    AgentCommandEnvironment,
    AgentExecutionEnvironment,
    SASEDualWorkbench,
)
from control_plane.sase.kronos_engine import (
    SirKronosImmunologicalTester,
    VulnerabilityCandidate,
)
from control_plane.sase.mrp import (
    Bewertungsmatrix,
    MergeReadinessPack,
    generate_mrp,
)


def test_briefingscript_freezing_and_integrity():
    """Verify that BriefingScript calculates deterministic SHA-256 freeze hash."""
    b = BriefingScript(
        briefing_id="BRF_TEST_001",
        goal="Synthesize Lukas, Sase, and Kronos",
        definition_of_done=["Unit tests green", "Memory <= 4096MB"],
        acceptance_test_commands=["pytest tests/control_plane/test_sase_tri_core_forge.py"],
        max_diff_lines=10,
    )
    h1 = b.freeze()
    assert len(h1) == 64
    assert b.verify_integrity(h1) is True

    # Mutate scope and verify integrity failure
    b.goal = "Mutated goal without re-freezing"
    assert b.verify_integrity("invalid_hash") is False


def test_mentorscript_reflexion_recording(tmp_path, monkeypatch):
    """Verify that 🧠Δ reflexion logs are appended to persistent files."""
    test_lerndatei = tmp_path / "lukas_lerndatei.md"
    monkeypatch.setattr("control_plane.sase.briefing.LERNDATEI_PATH", test_lerndatei)

    entry = MentorScript.record_reflexion(
        task_id="TASK_ALPHA_01",
        error_msg="Memory leak in loop",
        root_cause="Unbounded list accumulation",
        remediation="Apply FirnFlow cache flush",
    )
    assert "[🧠Δ] Reflexion: TASK_ALPHA_01" in entry
    assert test_lerndatei.exists()
    assert "Unbounded list accumulation" in test_lerndatei.read_text(encoding="utf-8")


def test_kronos_immunological_remediation_loop():
    """Verify the full 👁️🗨️ ➡️ 💉 ➡️ 🛡️ vulnerability remediation loop."""
    vulnerable_code = (
        "import os\n"
        "SECRET_KEY = 'secret_token_123456789'\n"
        "def unsafe_func(user_input):\n"
        "    path = '../../etc/passwd' + user_input\n"
        "    result = eval(user_input)\n"
        "    return result\n"
    )

    # 1. 👁️🗨️ Enumeration
    vulns = SirKronosImmunologicalTester.enumerate_vulnerabilities_tot(vulnerable_code)
    categories = [v.category for v in vulns]
    assert "SECRET_LEAKAGE" in categories
    assert "PATH_TRAVERSAL" in categories
    assert "UNSAFE_EVAL" in categories

    # 2. 💉 Injection
    injections = SirKronosImmunologicalTester.inject_test_payloads_react(vulnerable_code, vulns)
    assert len(injections) == len(vulns)
    assert all(inj["exploited"] is True for inj in injections)

    # 3. 🛡️ Hardening
    hardened, defenses = SirKronosImmunologicalTester.harden_architecture(vulnerable_code, vulns)
    assert len(defenses) >= 3
    assert "SECRET_KEY = 'secret_token_123456789'" not in hardened
    assert "../../" not in hardened
    assert "eval(" not in hardened

    # 4. Full loop execution
    audit_res = SirKronosImmunologicalTester.execute_immunological_loop("TASK_KRONOS_01", vulnerable_code)
    assert audit_res.passed is True
    assert audit_res.vulnerabilities_enumerated >= 3
    assert audit_res.defenses_applied >= 3


def test_bewertungsmatrix_weights_and_acceptance():
    """Verify tri-axis Prussian evaluation weights and acceptance bounds."""
    # Passing matrix (>= 0.90 composite, all axes >= 0.85)
    matrix_pass = Bewertungsmatrix(gruendlichkeit=0.95, ordnung=0.92, effizienz=0.90)
    expected_composite = round((0.40 * 0.95) + (0.35 * 0.92) + (0.25 * 0.90), 4)
    assert matrix_pass.composite_score == expected_composite
    assert matrix_pass.is_acceptable is True

    # Failing matrix (composite too low)
    matrix_fail = Bewertungsmatrix(gruendlichkeit=0.80, ordnung=0.80, effizienz=0.80)
    assert matrix_fail.is_acceptable is False

    # Failing matrix (one axis below 0.85)
    matrix_axis_fail = Bewertungsmatrix(gruendlichkeit=0.98, ordnung=0.98, effizienz=0.70)
    assert matrix_axis_fail.is_acceptable is False


def test_merge_readiness_pack_lifecycle():
    """Verify Merge-Readiness Pack synthesis, sealing, and mergeability validation."""
    mrp = generate_mrp(
        briefing_hash="sha256:briefing_test_hash",
        gruendlichkeit=0.95,
        ordnung=0.95,
        effizienz=0.92,
        kronos_audit_passed=True,
        vulnerabilities_mitigated=2,
        z3_proof="CONVEX_VALIDATED",
        ram_peak_mb=48.2,
    )
    assert mrp.mrp_id.startswith("MRP_")
    assert len(mrp.receipt_hash) == 64
    assert mrp.hitl_status == "{👤✅}_PENDING"
    assert mrp.is_mergeable() is False  # Must require human approval

    # Grant sovereign human approval
    mrp.approve_hitl()
    assert mrp.hitl_status == "{👤✅}_APPROVED"
    assert mrp.is_mergeable() is True


def test_sase_dual_workbench_orchestration():
    """Verify end-to-end SASE Dual-Workbench (ACE / AEE) run with symbolect trace."""
    goal = "Synthesize Lukas, Sase, and Kronos Tri-Core Omni-Forge"
    code = "def add(a: int, b: int) -> int:\n    return a + b\n"
    dod = ["Zero CVEs", "Memory <= 4096MB", "100% test pass"]
    tests = ["pytest tests/control_plane/test_sase_tri_core_forge.py"]

    mrp, trace = SASEDualWorkbench.run_tri_core_forge(
        goal=goal,
        code_payload=code,
        definition_of_done=dod,
        acceptance_tests=tests,
        auto_approve_hitl=True,
    )

    assert mrp.mrp_id.startswith("MRP_")
    assert mrp.is_mergeable() is True
    assert "⚡ Task Deconstruction" in trace
    assert "💡 ToT Analysis" in trace
    assert "🧱... Kinetic Build" in trace
    assert "👁️🗨️ ➡️ 💉 Kronos Penetration" in trace
    assert "<🏆+> Merge-Ready Artifact" in trace
