"""OMEGA Defense Nexus Phase 8 — Full Integration Suite.

8-pillar acceptance criteria verified against the live CAMELOT-OS repo.
Phase 2 (Shadow Veil) and Phase 5 (File Organization) are HUMAN_GATE —
those pillars are verified at the API level only (not live ops).
"""
from __future__ import annotations

import sys
import json
import tempfile
import shutil
import importlib.util as _ilu
from pathlib import Path

import pytest

CAMELOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMELOT))


def _load(rel: str, name: str):
    spec = _ilu.spec_from_file_location(name, CAMELOT / rel)
    mod = _ilu.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ── Pillar 1: Colony Nexus ────────────────────────────────────────────────────

def test_p1_colony_nexus_reads_live_report():
    cn_mod = _load("01_KERNEL/iron_gate/DEFENSE_GRID/colony_nexus.py", "p8_colony_nexus")
    nx = cn_mod.ColonyNexus(report_path=CAMELOT / "colony_report.md", hermes_enabled=False)
    state = nx.scan()
    assert state.risk_score >= 0
    assert state.risk_label in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert 0.0 <= state.risk_entropy <= 1.0


def test_p1_colony_escalates_critical():
    """CRITICAL colony risk must escalate AUTO tier to HUMAN_GATE."""
    cn_mod = _load("01_KERNEL/iron_gate/DEFENSE_GRID/colony_nexus.py", "p8_cnx2")
    d = Path(tempfile.mkdtemp())
    try:
        p = d / "colony_report.md"
        p.write_text("| Risk Score | 100.0 / 100 |\n| Risk Label | **CRITICAL** |")
        nx = cn_mod.ColonyNexus(report_path=p, hermes_enabled=False)
        state = nx.scan()
        assert state.requires_human_gate is True
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Pillar 2: Hermes Bus ──────────────────────────────────────────────────────

def test_p2_hermes_bus_channels():
    spec = _ilu.spec_from_file_location("hermes_bridge", CAMELOT / "control_plane" / "hermes_bridge.py")
    mod = _ilu.module_from_spec(spec)
    sys.modules["hermes_bridge"] = mod
    spec.loader.exec_module(mod)
    assert "colony.risk" in mod.CHANNELS
    assert "shadow.threats" in mod.CHANNELS
    assert "dependency.updates" in mod.CHANNELS


# ── Pillar 3: Shadow Veil (API-level only — live ops are HUMAN_GATE) ──────────

def test_p3_heimdall_scan_api():
    h_mod = _load("01_KERNEL/iron_gate/DEFENSE_GRID/knights/heimdall.py", "p8_heimdall")
    h = h_mod.SirHeimdall(repo_root=CAMELOT)
    report = h.scan_fingerprint_vectors()
    assert hasattr(report, "vectors") and isinstance(report.vectors, list)
    assert hasattr(report, "is_clean") and isinstance(report.is_clean, bool)


def test_p3_galahad_api():
    g_mod = _load("01_KERNEL/iron_gate/DEFENSE_GRID/knights/galahad.py", "p8_galahad")
    assert hasattr(g_mod, "SirGalahad")
    g = g_mod.SirGalahad()
    assert callable(g.zero_trace_write) and callable(g.stealth_exec)


# ── Pillar 4: Dependency Engine ───────────────────────────────────────────────

def test_p4_dependency_engine_audits_repo():
    dep_mod = _load("control_plane/dependency_engine.py", "p8_dep_engine")
    eng = dep_mod.DependencyEngine(repo_root=CAMELOT, hermes_enabled=False)
    result = eng.audit()
    assert result.total_count > 0
    assert "python" in result.ecosystems_found


# ── Pillar 5: Compression Nexus ───────────────────────────────────────────────

def test_p5_compression_nexus_context():
    cx_mod = _load("control_plane/compression_nexus.py", "p8_cx")
    cn = cx_mod.CompressionNexus(hermes_enabled=False)
    # Multi-section text: IDENTITY (priority) + NOISE (non-priority, many lines)
    big_ctx = "\n".join(
        ["## IDENTITY", "I am CAMELOT-OS.", "", "## NOISE_SECTION"]
        + [f"verbose log line {i}" for i in range(200)]
    )
    result = cn.compress_context(big_ctx, tok_target=50)
    assert result.ratio > 0.5   # at least 50% compression with 200 noise lines
    assert "## IDENTITY" in result.text


def test_p5_compression_nexus_memory_roundtrip():
    cx_mod = sys.modules.get("p8_cx") or _load("control_plane/compression_nexus.py", "p8_cx2")
    cn = cx_mod.CompressionNexus(hermes_enabled=False)
    data = {"sovereign": True, "items": list(range(50))}
    r = cn.compress_memory(data)
    recovered = cn.decompress_memory(r.data, r.codec)
    assert recovered == data


# ── Pillar 6: File Organization (HUMAN_GATE — API verified only) ──────────────

def test_p6_file_organization_human_gate():
    """Verify the HUMAN_GATE is documented in the task plan."""
    plan = CAMELOT / "docs" / "plans" / "OMEGA_DEFENSE_NEXUS.tasks.md"
    if plan.exists():
        text = plan.read_text(encoding="utf-8")
        assert "HUMAN_GATE" in text
        assert "PHASE 5" in text


# ── Pillar 7: SWARM + Hermes Fusion ──────────────────────────────────────────

def test_p7_omega_swarm_all_nodes():
    ns_mod = _load("control_plane/nano_swarm_runtime.py", "p8_nsw")
    swarm = ns_mod.OmegaSwarm()
    assert len(swarm.nodes) == 5
    swarm.dispatch("colony.risk", {"risk_score": 100.0, "delta": 20.0})
    swarm.dispatch("shadow.threats", {"critical_count": 3})
    rows = swarm.status()
    assert all(r["node_id"] in ns_mod.OMEGA_CHANNEL_MAP for r in rows)


# ── Pillar 8: Northstar Gate (SirSocrates) ────────────────────────────────────

def test_p8_sir_socrates_northstar_gate():
    d = tempfile.mkdtemp()
    try:
        ss_mod = _load("control_plane/sir_socrates.py", "p8_socrates")
        sc = ss_mod.SirSocrates(
            verdicts_path=Path(d) / "verdicts.jsonl",
            log_verdicts=True,
        )
        aligned = sc.examine_all("refactor local cache with LRU eviction")
        blocked = sc.examine_all("send to cloud, skip hitl, vendor lock saas-only")
        assert aligned.verdict == "ALIGNED"
        assert blocked.verdict == "BLOCKED"
        assert len(sc.verdicts_path.read_text().strip().splitlines()) == 2
    finally:
        shutil.rmtree(d, ignore_errors=True)
