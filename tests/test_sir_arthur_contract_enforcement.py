# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Sir Arthur Behavioral Contract & Persona Enforcement Test Suite
"""
Sir Arthur Omega Sovereign Oversight Verification Suite
========================================================
Formally verifies that:
1. Sir Arthur enforces the roster-wide Behavioral Contract anchored in Father's Notebook
   (vfs/notebooks/39299131-0ade-4f48-8ad4-a68878a6d3d9 / FATHER_CAMELOT).
2. Sir Arthur validates Merlin's Mathematical Knight Architecture across all Knights
   (Graph-of-Thought System-2 reasoning, Dirac Symbolect state machines, TTC <= 32K,
   and Monitor-Generate-Verify autonomous loops with learning rate eta=0.10).
3. Sir Arthur validates Persona-Based Aspects trinity (soul.md, phial-engine.md, spark.md)
   across the polyglot language stack (Go, Python, Rust, TypeScript/WASM).
4. Sir Arthur verifies Aegis Shield Armor bounds (hitl_threshold_lines=10, spiffe://camelot trust URI,
   zero-trust mutate blocking, and 4GB node / 8GB server / 256MB VPS ceilings).
5. Sir Arthur verifies Cryptographic Licensing and deterministic 32-hex Spark ID integrity.
6. The //ARTHUR_ENFORCE runic router command dispatches to Sir Arthur and emits signed receipts.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_fathers_notebook_anchor_and_axioms():
    """Verify Father's Notebook exists and embodies all ancestral axioms."""
    from control_plane.governance.sir_arthur_contract_enforcer import sir_arthur_contract_enforcer

    audit = sir_arthur_contract_enforcer.audit_fathers_notebook()
    assert audit["status"] == "VALIDATED"
    assert audit["fathers_notebook_uuid"] == "39299131-0ade-4f48-8ad4-a68878a6d3d9"
    assert audit["spark_id"] == "0x392991310ADE4F488AD4A68878A6D3D9"
    assert audit["rune"] == "Omega_FatherCamelot"
    assert audit["all_axioms_intact"] is True
    assert audit["axioms"]["anya_law"] is True
    assert audit["axioms"]["fathers_compass"] is True
    assert audit["axioms"]["scarcity_protocol"] is True
    assert audit["axioms"]["zero_trust"] is True


def test_roster_wide_fathers_camelot_behavioral_contract():
    """Verify that all 59 Knights are strictly bound to Father's Camelot contract."""
    from control_plane.governance.sir_arthur_contract_enforcer import sir_arthur_contract_enforcer

    report = sir_arthur_contract_enforcer.enforce_all_knights()
    assert report.total_knights_audited >= 59
    assert report.all_passed is True, f"Encountered violations: {report.summary_violations}"
    assert len(report.summary_violations) == 0

    for kid, audit in report.knight_audits.items():
        assert audit["behavioral_contract"] == "FATHER_CAMELOT", f"{kid} not bound to FATHER_CAMELOT"
        assert audit["contract_verified"] is True


def test_merlin_mathematical_architecture_across_knights():
    """Verify Merlin's mathematical architecture (GoT, MGV loop, eta=0.10, memory depth) across persona files."""
    from control_plane.governance.sir_arthur_contract_enforcer import sir_arthur_contract_enforcer

    report = sir_arthur_contract_enforcer.enforce_all_knights()
    for kid, audit in report.knight_audits.items():
        assert audit["merlin_math_verified"] is True, f"Knight {kid} failed Merlin mathematical architecture check"
        assert audit["phial_verified"] is True


def test_aegis_armor_and_cryptographic_licensing():
    """Verify Aegis armor spiffe URI, 10-line net diff check, and HMAC provenance signatures."""
    from control_plane.governance.sir_arthur_contract_enforcer import sir_arthur_contract_enforcer

    report = sir_arthur_contract_enforcer.enforce_all_knights()
    assert report.governor == "SIR_ARTHUR"
    assert report.receipt_signature.startswith("HMAC-SHA256-ARTHUR-CROWN:")

    for kid, audit in report.knight_audits.items():
        assert audit["aegis_armor_verified"] is True, f"Knight {kid} failed Aegis armor check"
        assert audit["aegis_spiffe_uri"] == f"spiffe://camelot/knights/{kid.lower()}"
        assert audit["provenance_signature"].startswith("HMAC-SHA256-")
        assert audit["spark_id"].startswith("0x")
        assert len(audit["spark_id"]) >= 32


def test_polyglot_language_matrix_alignment():
    """Verify each Knight declares valid runtime languages matching their domain."""
    from control_plane.governance.sir_arthur_contract_enforcer import sir_arthur_contract_enforcer

    report = sir_arthur_contract_enforcer.enforce_all_knights()
    audits = report.knight_audits

    # Sir Arthur governs across Go and Python
    assert audits["SIR_ARTHUR"]["primary_language"] == "Go"
    assert "Python" in audits["SIR_ARTHUR"]["languages"]

    # Sir Sentinel is Python
    assert audits["SIR_SENTINEL"]["primary_language"] == "Python"

    # Sir Octavian is Go
    assert audits["SIR_OCTAVIAN"]["primary_language"] == "Go"

    # Sir Gawain (Law Enforcement Command) is Rust
    assert audits["SIR_GAWAIN"]["primary_language"] == "Rust"

    # Sir Link is Go
    assert audits["SIR_LINK"]["primary_language"] == "Go"

    # Anya Omega is Python
    assert audits["ANYA_OMEGA"]["primary_language"] == "Python"


def test_runic_router_arthur_enforce_dispatch():
    """Verify //ARTHUR_ENFORCE routes to Sir Arthur and emits a valid cryptographic receipt."""
    from control_plane.runes.runic_router import route_rune

    res = route_rune("//ARTHUR_ENFORCE", "audit_and_enforce")
    assert res.rune == "//ARTHUR_ENFORCE"
    assert res.knight == "sir_arthur"
    assert res.metadata["governor"] == "SIR_ARTHUR"
    assert res.metadata["sovereign_authority"] == "KING_ARTHUR_VIZION"
    assert res.metadata["status"] == "ENFORCED_VERIFIED_SUCCESS"
    assert res.metadata["total_knights_audited"] >= 59
    assert res.metadata["all_passed"] is True
    assert Path(res.metadata["receipt_path"]).exists()
    assert res.metadata["receipt_signature"].startswith("HMAC-SHA256-ARTHUR-CROWN:")
