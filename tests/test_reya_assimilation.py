# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Test Suite for Reya Assimilation Protocol & Mark-XXXIX Hybrid Nexus
===================================================================
Verifies:
1. Anya_Ω 10-line atomic code firewall and Triple-QFT distillation.
2. Memory slab (< 256MB) allocation and zero-copy shared memory boundaries.
3. Reya scaffold manifest and Hybrid Routing Matrix specification.
4. Runic router handlers for all 6 Reya and Mark-XXXIX harmony runes.
5. Dual-harness νKG crystals (REYA_NEXUS_PENDING and OMEGA_MARK39_REYA_NEXUS).
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from control_plane.runes.runic_router import route_rune
import importlib.util

CAMELOT_HOME = Path(__file__).resolve().parent.parent

import sys

# Dynamically import ReyaHypervisorGate from 02_FORGE
gate_path = CAMELOT_HOME / "02_FORGE" / "assimilation" / "reya" / "reya_hypervisor_gate.py"
spec = importlib.util.spec_from_file_location("reya_hypervisor_gate", str(gate_path))
assert spec is not None and spec.loader is not None
reya_gate_mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = reya_gate_mod
spec.loader.exec_module(reya_gate_mod)
ReyaHypervisorGate = reya_gate_mod.ReyaHypervisorGate


# ── 1. Anya_Ω Hypervisor Gate & Ingress Firewall Tests ────────────────────────

def test_atomic_code_firewall_accepts_valid_chunk():
    """Verify that chunks with <= 10 functional lines pass the ingress firewall."""
    gate = ReyaHypervisorGate(max_atomic_lines=10)
    snippet = "def reya_process(token: str) -> str:\n    return token.strip().lower()\n"
    verdict = gate.evaluate_ingress(snippet)
    assert verdict.passed is True
    assert verdict.line_count == 2
    assert verdict.ast_valid is True
    assert verdict.rejection_reason is None


def test_atomic_code_firewall_rejects_oversized_chunk():
    """Verify that chunks exceeding 10 functional lines are strictly rejected."""
    gate = ReyaHypervisorGate(max_atomic_lines=10)
    lines = [f"val_{i} = {i}" for i in range(14)]
    oversized = "\n".join(lines)
    verdict = gate.evaluate_ingress(oversized)
    assert verdict.passed is False
    assert verdict.line_count == 14
    assert "BREACH" in verdict.rejection_reason


def test_triple_qft_distillation_purges_fluff():
    """Verify that Triple-QFT eliminates conversational filler and disclaimers."""
    gate = ReyaHypervisorGate()
    fluff_payload = (
        "Certainly! Here is the Reya logic for your swarm:\n"
        "```python\n"
        "class ReyaNode:\n"
        "    pass\n"
        "```\n"
        "Let me know if you need anything else!"
    )
    distilled, stripped = gate.triple_qft_distill(fluff_payload)
    assert "Certainly" not in distilled
    assert "Let me know" not in distilled
    assert "class ReyaNode:" in distilled
    assert stripped >= 2


def test_memory_slab_bounds():
    """Verify zero-copy shared memory slab respects < 256MB ceiling."""
    gate = ReyaHypervisorGate(memory_ceiling_mb=256)
    slab = gate.provision_memory_slab()
    assert slab["max_mb"] <= 256
    assert slab["max_bytes"] <= 268435456
    assert slab["status"] == "ALLOCATED_BOUNDED"


# ── 2. Scaffold Manifest & Specs Verification ─────────────────────────────────

def test_reya_scaffold_manifest_integrity():
    """Verify scaffold manifest parameters and boundary definitions."""
    manifest_path = CAMELOT_HOME / "02_FORGE" / "assimilation" / "reya" / "scaffold" / "scaffold_manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["hypervisor"] == "ANYA_Ω"
    assert manifest["memory_envelope"]["allocated_slab_mb"] == 256
    assert manifest["ingress_gate"]["max_atomic_lines"] == 10


def test_hybrid_routing_matrix_spec_presence():
    """Verify presence and keywords of the HYBRID_ROUTING_MATRIX spec."""
    matrix_path = CAMELOT_HOME / "02_FORGE" / "assimilation" / "reya" / "specs" / "HYBRID_ROUTING_MATRIX.md"
    assert matrix_path.exists()
    content = matrix_path.read_text(encoding="utf-8")
    assert "Gemini Live API" in content
    assert "Sub-100ms TTFA" in content
    assert "OpenRouter FreeTier" in content


# ── 3. Crystals Verification ──────────────────────────────────────────────────

def test_vkg_crystals_exist_and_valid():
    """Verify that both pending crystals are syntactically valid and match specs."""
    vkg_dir = CAMELOT_HOME / "03_VAULT" / "runtime_state" / "open_notebook" / "vkg_crystals"

    crystal_reya = vkg_dir / "vkg_reya_nexus_pending.json"
    assert crystal_reya.exists()
    data_reya = json.loads(crystal_reya.read_text(encoding="utf-8"))
    assert data_reya["system_identity"] == "REYA_NEXUS_PENDING"
    assert data_reya["prime_directive"]["root"] == "ANYA_Ω"

    crystal_mark39 = vkg_dir / "vkg_omega_mark39_reya_nexus.json"
    assert crystal_mark39.exists()
    data_mark39 = json.loads(crystal_mark39.read_text(encoding="utf-8"))
    assert data_mark39["system_identity"] == "OMEGA_MARK39_REYA_NEXUS"
    assert data_mark39["prime_directive"]["constraint"] == "8GB_EDGE_CEILING ➔ (Python_Bloat == PURGED)"


# ── 4. Runic Dispatch Verification ────────────────────────────────────────────

def test_runic_dispatch_forge_reya_scaffold():
    """Test //FORGE_REYA_SCAFFOLD execution."""
    res = route_rune("//FORGE_REYA_SCAFFOLD")
    assert res.queued is True
    assert res.metadata.get("status") == "SCAFFOLD_FORGED"


def test_runic_dispatch_await_reya_uncloaking():
    """Test //AWAIT_REYA_UNCLOAKING execution."""
    res = route_rune("//AWAIT_REYA_UNCLOAKING")
    assert res.metadata.get("status") == "ARMED_STANDBY"
    assert res.metadata.get("ready_for_raw_payload") is True


def test_runic_dispatch_extract_mark_39_audio_core():
    """Test //EXTRACT_MARK_39_AUDIO_CORE execution."""
    res = route_rune("//EXTRACT_MARK_39_AUDIO_CORE")
    assert res.metadata.get("status") == "MARK_39_CORE_EXTRACTED"
    assert "Sub-100ms TTFA" in res.metadata.get("voice_vision_engine", "")


def test_runic_dispatch_sandbox_python_dependencies():
    """Test //SANDBOX_PYTHON_DEPENDENCIES execution."""
    res = route_rune("//SANDBOX_PYTHON_DEPENDENCIES")
    assert res.metadata.get("status") == "PYTHON_DEPENDENCIES_SANDBOXED"
    assert "pyautogui" in res.metadata.get("purged_dependencies", [])


def test_runic_dispatch_hitl_iron_gate_approval():
    """Test //HITL_IRON_GATE_APPROVAL threshold check."""
    # Under limit
    res_under = route_rune("//HITL_IRON_GATE_APPROVAL", "line 1\nline 2")
    assert res_under.metadata.get("requires_hitl") is False
    assert res_under.metadata.get("status") == "HITL_APPROVED_ATOMIC"

    # Over limit
    big_payload = "\n".join([f"line_{i}" for i in range(15)])
    res_over = route_rune("//HITL_IRON_GATE_APPROVAL", big_payload)
    assert res_over.metadata.get("requires_hitl") is True
    assert res_over.metadata.get("status") == "HITL_REQUIRED"


# ── 5. Systemd Daemon & Nostr Transport Tests ─────────────────────────────────

def test_systemd_daemon_script_and_cgroups():
    """Verify systemd daemon service file enforces cgroups v2 limits and strict isolation."""
    service_path = CAMELOT_HOME / "infra" / "systemd" / "camelot-reya-edge.service"
    assert service_path.exists()
    content = service_path.read_text(encoding="utf-8")
    assert "MemoryMax=350M" in content
    assert "MemoryHigh=300M" in content
    assert "CPUQuota=60%" in content
    assert "ProtectSystem=strict" in content
    assert "ProtectHome=read-only" in content
    assert "PrivateTmp=true" in content
    assert "Slice=camelot-workers.slice" in content

    install_script = CAMELOT_HOME / "infra" / "systemd" / "install-reya-edge.sh"
    assert install_script.exists()


def test_runic_dispatch_activate_reya_nostr_bridge():
    """Test //ACTIVATE_REYA_NOSTR_BRIDGE execution and QR-Pill pairing."""
    res = route_rune("//ACTIVATE_REYA_NOSTR_BRIDGE", "vashawns-s26-ultra")
    assert res.queued is True
    assert res.metadata.get("status") == "REYA_NOSTR_BRIDGE_ACTIVE"
    assert res.metadata.get("knight") == "SIR_HELIO"
    assert res.metadata.get("device_id") == "vashawns-s26-ultra"
    assert res.metadata.get("systemd_present") is True
    assert "hmac_digest" in res.metadata.get("qr_pill", {})


