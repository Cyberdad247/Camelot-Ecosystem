# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Test Suite for Arthur-Merlin Handshake Protocol (`AM-HANDSHAKE/1`).
===================================================================
Verifies:
1. Low-risk fast-path auto-clearance (T0/T1).
2. Bounded mutation atomic governance (T2 <= 10 lines).
3. Consequential mutation suspension (T3/T4 or > 10 lines) requiring HITL.
4. Memory scarcity ceiling rejection (> 256MB).
5. Sir Gideon 13-gate ethical veto (eval/exec dynamic execution).
6. King Arthur Sovereign Golden Seal cryptographic Ed25519 signing & verification.
7. Runic router integration for //HANDSHAKE and //ARTHUR_MERLIN.
"""

from __future__ import annotations

import pytest
from control_plane.security.arthur_merlin_handshake import (
    ArthurMerlinHandshakeEngine,
    HandshakeStatus,
)
from control_plane.runes.runic_router import route_rune


@pytest.fixture
def engine() -> ArthurMerlinHandshakeEngine:
    return ArthurMerlinHandshakeEngine()


# ── 1. Low-Risk Fast-Path ─────────────────────────────────────────────────────

def test_handshake_low_risk_auto_cleared(engine: ArthurMerlinHandshakeEngine):
    """Verify that read-only / status queries are auto-cleared with low-risk lease."""
    verdict = engine.evaluate_intent(
        intent="Read telemetry from Excalibur mobile cockpit",
        target_knight="sir_helios",
        payload="",
        explicit_risk_tier="T1",
        memory_estimate_mb=5.0,
    )
    assert verdict.status == HandshakeStatus.AUTO_CLEARED
    assert verdict.proposal.requires_hitl is False
    assert verdict.capability_lease is not None
    assert verdict.capability_lease["authorized_by"] == "ANYA_FAST_PATH"
    assert verdict.capability_lease["schema_version"] == "camelot-lease/1"


# ── 2. Bounded Atomic Mutation ────────────────────────────────────────────────

def test_handshake_atomic_governed_under_ten_lines(engine: ArthurMerlinHandshakeEngine):
    """Verify that bounded mutations under 10 lines are governed atomically."""
    snippet = "def update_port(p: int) -> int:\n    return p + 1\n"
    verdict = engine.evaluate_intent(
        intent="Patch audio port offset",
        target_knight="sir_boris",
        payload=snippet,
        explicit_risk_tier="T2",
        memory_estimate_mb=8.0,
    )
    assert verdict.status == HandshakeStatus.ATOMIC_GOVERNED
    assert verdict.proposal.estimated_lines == 2
    assert verdict.proposal.requires_hitl is False
    assert verdict.capability_lease is not None


# ── 3. High-Risk / Consequential Mutation (HITL Required) ─────────────────────

def test_handshake_suspends_on_critical_tier(engine: ArthurMerlinHandshakeEngine):
    """Verify that T3/T4 intents are suspended immediately awaiting Arthur's seal."""
    verdict = engine.evaluate_intent(
        intent="Deploy Nostr relay and bridge to Bifrost Gateway",
        target_knight="sir_helio",
        payload="line1\nline2\n",
        explicit_risk_tier="T3",
        memory_estimate_mb=30.0,
    )
    assert verdict.status == HandshakeStatus.SUSPENDED_AWAITING_HITL
    assert verdict.proposal.requires_hitl is True
    assert verdict.capability_lease is None
    assert verdict.arthur_resolution is None


def test_handshake_suspends_on_lines_over_ten(engine: ArthurMerlinHandshakeEngine):
    """Verify that payloads exceeding 10 lines suspend for HITL even on T2."""
    big_payload = "\n".join([f"x_{i} = {i}" for i in range(16)])
    verdict = engine.evaluate_intent(
        intent="Write new configuration block",
        target_knight="sir_codex",
        payload=big_payload,
        explicit_risk_tier="T2",
        memory_estimate_mb=10.0,
    )
    assert verdict.status == HandshakeStatus.SUSPENDED_AWAITING_HITL
    assert verdict.proposal.requires_hitl is True
    assert verdict.proposal.estimated_lines == 16


# ── 4. Scarcity & Ethical Bounds ──────────────────────────────────────────────

def test_handshake_rejects_memory_breach(engine: ArthurMerlinHandshakeEngine):
    """Verify memory delta exceeding 256MB is rejected for Scarcity Violation."""
    verdict = engine.evaluate_intent(
        intent="Allocate large buffer in host memory",
        target_knight="sir_codex",
        payload="",
        explicit_risk_tier="T2",
        memory_estimate_mb=350.0,  # Exceeds 256MB
    )
    assert verdict.status == HandshakeStatus.REJECTED_MEMORY_CEILING
    assert "Scarcity violation" in verdict.rejection_reason


def test_handshake_rejects_dynamic_eval(engine: ArthurMerlinHandshakeEngine):
    """Verify Gideon 13-gate pre-flight vetoes dynamic code execution."""
    bad_payload = "eval('__import__(\"os\").system(\"whoami\")')"
    verdict = engine.evaluate_intent(
        intent="Execute dynamic snippet",
        target_knight="sir_codex",
        payload=bad_payload,
        explicit_risk_tier="T2",
    )
    assert verdict.status == HandshakeStatus.REJECTED_ETHICAL_VETO
    assert "eval/exec" in verdict.rejection_reason


# ── 5. Arthur Sovereign Golden Seal Release ───────────────────────────────────

def test_arthur_golden_seal_unlocks_suspended_handshake(engine: ArthurMerlinHandshakeEngine):
    """Verify King Arthur's Sovereign Golden Seal signs and releases a suspended task."""
    verdict = engine.evaluate_intent(
        intent="Purge unverified temporary models and reindex cache",
        target_knight="sir_forge",
        payload="purge()",
        explicit_risk_tier="T4",
        memory_estimate_mb=25.0,
    )
    assert verdict.status == HandshakeStatus.SUSPENDED_AWAITING_HITL
    hs_id = verdict.handshake_id

    # Apply Arthur's seal
    released = engine.apply_arthur_golden_seal(
        handshake_id=hs_id,
        directive_type="CONSENSUS_RATIFICATION",
        rationale="Operator verified diff and authorized model purge.",
    )

    assert released.status == HandshakeStatus.SEALED_AUTHORIZED
    assert released.arthur_resolution is not None
    assert released.arthur_resolution["sovereign_seal"]["king_id"] == "ARTHUR_OMEGA"
    assert released.arthur_resolution["sovereign_seal"]["seal_type"] == "SOVEREIGN_GOLDEN_SEAL"
    assert released.capability_lease is not None
    assert released.capability_lease["authorized_by"] == "ARTHUR_OMEGA"

    # Cryptographically verify the resolution
    is_valid = engine.governor.verify_resolution(released.arthur_resolution)
    assert is_valid is True


# ── 6. Runic Router Dispatch ──────────────────────────────────────────────────

def test_runic_dispatch_handshake_and_aliases():
    """Verify that //HANDSHAKE and //ARTHUR_MERLIN route to merlin_omega."""
    res = route_rune("//HANDSHAKE Status Check")
    assert res.queued is True
    assert res.metadata["status"] in ("AUTO_CLEARED", "ATOMIC_GOVERNED", "SUSPENDED_AWAITING_HITL")

    res_alias = route_rune("//ARTHUR_MERLIN Telemetry Inspection")
    assert res_alias.queued is True
    assert res_alias.metadata["proposal"]["target_knight"] == "merlin_omega"
