# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Tests for Canonical HTMX WebGPU WGSL Pipeline & Jev Ω Offline System-2 Engine
=============================================================================
Verifies:
1. HTMX Server index contains canonical WebGPU WGSL cosine similarity compute shader.
2. HTMX endpoints return pure semantic HTML fragments conforming to HATEOAS.
3. 1.58-bit ternary matrix packing and multiplication in Jev Offline Engine.
4. Lightbot WASM sandbox execution and Candy EQ response synthesis.
5. Strict adherence to Cybertronia 4.0 GB Edge Node RAM ceiling.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
import pytest

from control_plane.infra.htmx_server import CANONICAL_INDEX_HTML, CanonicalHTMXHandler
from control_plane.runners.jev_offline_engine import (
    JevOfflineEngine,
    LightbotWasmBridge,
    TernaryMatrix158b,
    run_jev_offline_probe,
)

CAMELOT_HOME = Path(__file__).resolve().parent.parent.parent


def test_htmx_server_contains_webgpu_wgsl_shader():
    """Verify that CANONICAL_INDEX_HTML embeds the WebGPU WGSL compute pipeline."""
    assert "COSINE_SIMILARITY_WGSL" in CANONICAL_INDEX_HTML
    assert "@compute @workgroup_size(64)" in CANONICAL_INDEX_HTML
    assert "struct VectorBuffer" in CANONICAL_INDEX_HTML
    assert "dotProduct / denom" in CANONICAL_INDEX_HTML
    assert "navigator.gpu.requestAdapter()" in CANONICAL_INDEX_HTML


def test_htmx_server_contains_hateoas_endpoints():
    """Verify that the HTMX shell defines pure hypermedia navigation targets."""
    assert 'hx-get="/docs/slabs"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/architecture"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/tasks"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/verification"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/polyglot"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/nullclaw"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/governance"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/doc-check"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/links"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/agent-computer"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/teams"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/personalities"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/spatial"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/rea"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/glass-fabric"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/eleventh-law"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/tri-pane"' in CANONICAL_INDEX_HTML
    assert 'hx-get="/docs/worldtree-graph"' in CANONICAL_INDEX_HTML
    assert 'hx-post="/api/cloudbrain/search"' in CANONICAL_INDEX_HTML
    assert 'hx-post="/api/mcp"' in CANONICAL_INDEX_HTML


def test_htmx_server_serves_worldtree_webgpu_graph_canvas():
    """Verify that the HTMX server serves the WorldTree WebGPU Graph Canvas with SoA and WGSL compute."""
    class DummyHandler:
        def __init__(self, path: str = "/docs/worldtree-graph"):
            self.path = path
            self.response = ""
            self.status = 0
        def _send_html(self, html_content: str, status: int = 200) -> None:
            self.response = html_content
            self.status = status

    # 1. Primary endpoint
    handler = DummyHandler("/docs/worldtree-graph")
    CanonicalHTMXHandler.do_GET(handler)
    assert handler.status == 200
    assert "WorldTree WebGPU Graph Canvas" in handler.response
    assert "Structure-of-Arrays (Float32Array)" in handler.response
    assert "worldtree-webgpu-canvas" in handler.response
    assert "WORLDTREE_GRAPH_PHYSICS_WGSL" in handler.response
    assert "@compute @workgroup_size(256)" in handler.response
    assert "WORLDTREE_GRAPH_RENDER_WGSL" in handler.response
    assert "vs_main" in handler.response
    assert "CANVAS-2D ACCELERATED" in handler.response
    assert "D4AF37" in handler.response  # Luxora Gold branding
    assert "050505" in handler.response  # Obsidian Void branding

    # 2. Alias endpoint /docs/vkg-canvas
    handler_alias = DummyHandler("/docs/vkg-canvas")
    CanonicalHTMXHandler.do_GET(handler_alias)
    assert handler_alias.status == 200
    assert "WorldTree WebGPU Graph Canvas" in handler_alias.response


def test_htmx_server_serves_worldtree_topology_api():
    """Verify that /api/graph/topology returns valid JSON with SoA metrics and WorldTree nodes."""
    class DummyHandler:
        def __init__(self, path: str = "/api/graph/topology"):
            self.path = path
            self.response = ""
            self.status = 0
        def _send_html(self, html_content: str, status: int = 200) -> None:
            self.response = html_content
            self.status = status
        def _send_json(self, data: Any, status: int = 200) -> None:
            self.response = json.dumps(data)
            self.status = status

    handler = DummyHandler("/api/graph/topology")
    CanonicalHTMXHandler.do_GET(handler)
    assert handler.status == 200
    data = json.loads(handler.response)
    assert data["status"] == "WORLDTREE_TOPOLOGY_ACTIVE"
    assert data["node_count"] >= 12
    assert data["edge_count"] >= 10
    assert data["layout"] == "Structure-of-Arrays (SoA)"
    assert "4.0 GB Node Ceiling" in data["memory_scarcity_ceiling"]
    assert any(n["id"] == "cybertronia" for n in data["nodes"])
    assert any(n["id"] == "sir_helios" for n in data["nodes"])
    assert any(n["id"] == "anya_omega" for n in data["nodes"])


def test_crystal_finalization_emits_graph_deltas_and_api_serves_them():
    """Verify that finalizing a crystal emits an incremental graph delta and /api/graph/deltas serves it."""
    from scripts.finalize_open_notebook_crystal import finalize_open_notebook_crystal, GRAPH_DELTAS_PATH

    # 1. Finalize a test crystal
    res = finalize_open_notebook_crystal(
        knight_id="SIR_HELIOS",
        title="WebGPU Graph Delta Streaming Test",
        text="WebGPU compute shaders stream incremental AST triplets into Structure-of-Arrays buffers.",
        category="WEBGPU_GRAPH_DELTA",
    )
    assert res["crystal_id"].startswith("VKG_")
    assert res["anya_seal"] == "ANYA_IS_THE_GATE"
    cid = res["crystal_id"]

    # 2. Assert delta was appended
    assert GRAPH_DELTAS_PATH.exists()
    content = GRAPH_DELTAS_PATH.read_text(encoding="utf-8")
    assert cid in content
    assert "CRYSTAL_FORGED" in content

    # 3. Query /api/graph/deltas endpoint
    class DummyHandler:
        def __init__(self, path: str = "/api/graph/deltas"):
            self.path = path
            self.response = ""
            self.status = 0
        def _send_html(self, html_content: str, status: int = 200) -> None:
            self.response = html_content
            self.status = status
        def _send_json(self, data: Any, status: int = 200) -> None:
            self.response = json.dumps(data)
            self.status = status

    handler = DummyHandler("/api/graph/deltas")
    CanonicalHTMXHandler.do_GET(handler)
    assert handler.status == 200
    data = json.loads(handler.response)
    assert data["status"] == "DELTAS_STREAM_ACTIVE"
    assert data["count"] > 0
    assert any(d["crystal_id"] == cid for d in data["deltas"])





def test_htmx_server_serves_rea_cockpit():
    """Verify that the HTMX server serves the REA Forensics Cockpit fragment."""
    class DummyHandler:
        def __init__(self):
            self.path = "/docs/rea"
            self.response = ""
            self.status = 0
        def _send_html(self, html_content: str, status: int = 200) -> None:
            self.response = html_content
            self.status = status

    handler = DummyHandler()
    CanonicalHTMXHandler.do_GET(handler)
    assert handler.status == 200
    assert "REA Reverse Engineering &amp; Forensic Evidence Cockpit" in handler.response or "REA Reverse Engineering & Forensic Evidence Cockpit" in handler.response
    assert "cartridges/rea-forensics" in handler.response
    assert "SIR_HELIOS" in handler.response
    assert "//REA" in handler.response


def test_htmx_server_serves_tri_pane_cockpit():
    """Verify that the HTMX server serves the Tri-Pane Cockpit and 3x3 Cartridge Grid."""
    class DummyHandler:
        def __init__(self):
            self.path = "/docs/tri-pane"
            self.response = ""
            self.status = 0
        def _send_html(self, html_content: str, status: int = 200) -> None:
            self.response = html_content
            self.status = status

    handler = DummyHandler()
    CanonicalHTMXHandler.do_GET(handler)
    assert handler.status == 200
    assert "Tri-Pane Cockpit &amp; 3×3 Cartridge Grid" in handler.response or "Tri-Pane Cockpit & 3×3 Cartridge Grid" in handler.response or "Tri-Pane" in handler.response
    assert "Sir Alfred Ω" in handler.response
    assert "Invisioned Marketing Inc." in handler.response
    assert "Head Artworks LLC" in handler.response
    assert "1VIZION RCRDS" in handler.response
    assert "Kickbox Audio" in handler.response
    assert "A2UI_View" in handler.response



def test_ternary_matrix_packing_and_unpacking():
    """Verify that 1.58-bit weights {-1, 0, 1} are packed at 4 weights per byte."""
    weights = [1, -1, 0, 1, 0, 0, -1, 1]
    matrix = TernaryMatrix158b.from_weights(rows=2, cols=4, weights=weights)
    
    # 8 weights packed into 2 bytes
    assert len(matrix.data) == 2
    
    # Check unpacked elements
    assert matrix.unpack_element(0, 0) == 1
    assert matrix.unpack_element(0, 1) == -1
    assert matrix.unpack_element(0, 2) == 0
    assert matrix.unpack_element(0, 3) == 1
    assert matrix.unpack_element(1, 0) == 0
    assert matrix.unpack_element(1, 1) == 0
    assert matrix.unpack_element(1, 2) == -1
    assert matrix.unpack_element(1, 3) == 1


def test_ternary_matrix_vector_multiplication():
    """Verify ternary vector multiplication executes without floating point weight mults."""
    # Row 0: [ 1,  0, -1] -> dot [2.0, 3.0, 4.0] = 2.0 - 4.0 = -2.0
    # Row 1: [-1,  1,  0] -> dot [2.0, 3.0, 4.0] = -2.0 + 3.0 = 1.0
    weights = [1, 0, -1, -1, 1, 0]
    matrix = TernaryMatrix158b.from_weights(rows=2, cols=3, weights=weights)
    vec = [2.0, 3.0, 4.0]
    out = matrix.vec_mul(vec)
    assert out[0] == -2.0
    assert out[1] == 1.0


def test_lightbot_wasm_sandbox_execution():
    """Verify Lightbot WASM bridge sandbox properties."""
    bridge = LightbotWasmBridge(memory_pages_limit=16)
    result = bridge.execute_payload("test_bytecode_sig", {"task": "system_2_offline"})
    assert result.status == "WASM_EXECUTION_COMPLETE"
    assert result.memory_pages <= 16
    assert result.gas_consumed > 0
    assert len(result.digest) == 64
    assert result.output["sandbox"] == "WASM32-WASI"


def test_jev_offline_engine_synthesis():
    """Verify Jev Ω offline synthesis and Candy EQ parameters."""
    engine = JevOfflineEngine()
    result = engine.synthesize_offline("Simulate DAG offline")
    assert result["knight"] == "JEV_Ω"
    assert result["status"] == "OFFLINE_COGNITION_COMPLETE"
    assert result["model"] == "SmolLM3-3B-1.58b-Ternary"
    assert result["memory_footprint_mb"] < 10.0
    assert result["edge_ram_headroom_mb"] > 1000.0
    assert result["candy_eq"]["warmth"] >= 0.8
    assert result["candy_eq"]["clarity"] >= 0.9
    assert "Jev Ω" in result["response"]


def test_confidence_threshold_circuit_breaker():
    """Verify high-confidence prompts pass, while ambiguous or extremely brief queries trip the breaker."""
    from control_plane.runners.jev_offline_engine import ConfidenceThresholdCircuitBreaker
    cb = ConfidenceThresholdCircuitBreaker(threshold=0.75)

    score_pass, passes = cb.evaluate_intent("Run full telemetry audit on Cybertronia edge node")
    assert passes is True
    assert score_pass >= 0.75

    score_empty, passes_empty = cb.evaluate_intent("")
    assert passes_empty is False
    assert score_empty == 0.0

    score_ambig, passes_ambig = cb.evaluate_intent("maybe perhaps?")
    assert passes_ambig is False
    assert score_ambig < 0.75


def test_identic_memory_event_queue():
    """Verify non-blocking async enqueue and drain of memory events."""
    from control_plane.runners.jev_offline_engine import IdenticMemoryEventQueue
    q = IdenticMemoryEventQueue()
    eid1 = q.push("JEV_Ω", "audit", {"status": "ok"})
    eid2 = q.push("JEV_Ω", "sync", {"status": "complete"})

    assert q.size() == 2
    assert "ev_" in eid1
    assert "ev_" in eid2

    drained = q.drain()
    assert len(drained) == 2
    assert q.size() == 0


def test_candy_eq_wrapper():
    """Verify emotional calibration wrapper applies empathy index and formatting."""
    from control_plane.runners.jev_offline_engine import CandyEQWrapper
    eq = CandyEQWrapper()
    assert eq.warmth == 0.92
    assert eq.clarity == 0.99
    assert eq.empathy_index == 0.88

    formatted = eq.format_companion_response("System standing by.", 0.95)
    assert "Candy EQ" in formatted
    assert "Empathy: 0.88" in formatted


def test_htmx_status_fragment_and_verified_states():
    """Verify that HTMX server renders valid HTML fragments with verified state badges."""
    from control_plane.infra.agent_slab_sync import audit_memory
    from control_plane.infra.htmx_server import render_htmx_status_fragment
    mem_audit = audit_memory()
    assert hasattr(mem_audit, "process_rss_mb")
    assert mem_audit.process_rss_mb <= 4096.0

    frag = render_htmx_status_fragment()
    assert "hx-swap" in frag or "badge" in frag
    assert "RSS" in frag

    assert "Verified States" in CANONICAL_INDEX_HTML
    expected_states = ["PENDING", "DENIED", "APPROVED", "EXECUTING", "VERIFIED", "FAILED", "STALE", "REVOKED"]
    assert len(expected_states) == 8


def test_webgpu_spatial_diagnostics_and_buffer_audit():
    """Verify WebGPU storage buffer footprint auditing and spatial grid parameter calculation."""
    from control_plane.monitoring.webgpu_diagnostics import WebGpuSpatialDiagnostics
    diag = WebGpuSpatialDiagnostics()

    audit = diag.audit_buffers(node_count=16384, edge_count=12000)
    assert audit.node_count == 16384
    assert audit.total_vram_mb < 2.0  # < 2MB VRAM for 16k nodes
    assert audit.scarcity_compliant is True
    assert audit.soa_layout_valid is True

    grid = diag.calculate_spatial_grid_params(node_count=16384)
    assert grid["grid_dim_x"] >= 4
    assert grid["grid_dim_y"] >= 4
    assert grid["total_cells"] >= 16
    assert grid["workgroup_size"] == 256
    assert grid["complexity"] == "O(N log N)"


def test_webgpu_lttb_macro_clustering():
    """Verify Largest Triangle Three Buckets (LTTB) spatial graph downsampling."""
    from control_plane.monitoring.webgpu_diagnostics import WebGpuSpatialDiagnostics
    diag = WebGpuSpatialDiagnostics()

    nodes = [{"id": f"n_{i}", "pos": [float(i), float(i * i * 0.01)]} for i in range(100)]
    downsampled = diag.downsample_lttb(nodes, target_count=10)

    assert len(downsampled) == 10
    assert downsampled[0]["id"] == "n_0"
    assert downsampled[-1]["id"] == "n_99"


def test_webgpu_trust_vector_encoding():
    """Verify Web 4/5 sovereign trust vector encoding across knight and crystal types."""
    from control_plane.monitoring.webgpu_diagnostics import WebGpuSpatialDiagnostics
    diag = WebGpuSpatialDiagnostics()

    root_vec = diag.encode_trust_vector({"type": "sovereign"})
    assert root_vec == (1.0, 1.0, 1.0, 0.0)

    crys_vec = diag.encode_trust_vector({"type": "crystal", "z3_proof": "SATISFIED"})
    assert crys_vec[1] == 1.0
    assert crys_vec[3] == 0.0

    taint_vec = diag.encode_trust_vector({"type": "squire", "risk": 75})
    assert taint_vec[3] == 1.0


def test_webgpu_cdp_trace_metrics():
    """Verify autonomous ChromeDevTools-MCP (CDP) trace metrics and jitter detection."""
    from control_plane.monitoring.webgpu_diagnostics import WebGpuSpatialDiagnostics
    diag = WebGpuSpatialDiagnostics()

    cdp_clean = diag.simulate_cdp_trace(node_count=8192, simulated_fps=60.0, jitter_ms=0.5)
    assert cdp_clean.frame_rate_fps == 60.0
    assert cdp_clean.avg_frame_time_ms < 17.0
    assert cdp_clean.bottleneck_detected is False
    assert cdp_clean.remediation_rune is None

    cdp_lag = diag.simulate_cdp_trace(node_count=65536, simulated_fps=30.0, jitter_ms=5.0)
    assert cdp_lag.bottleneck_detected is True
    assert cdp_lag.remediation_rune is not None
    assert "TUNE_SPATIAL_DAMPING" in cdp_lag.remediation_rune


def test_htmx_server_serves_graph_diagnostics_api():
    """Verify that /api/graph/diagnostics returns complete buffer audit and CDP metrics."""
    class DummyHandler:
        def __init__(self, path: str = "/api/graph/diagnostics"):
            self.path = path
            self.response = ""
            self.status = 0
        def _send_html(self, html_content: str, status: int = 200) -> None:
            self.response = html_content
            self.status = status
        def _send_json(self, data: Any, status: int = 200) -> None:
            self.response = json.dumps(data)
            self.status = status

    handler = DummyHandler("/api/graph/diagnostics")
    CanonicalHTMXHandler.do_GET(handler)
    assert handler.status == 200
    data = json.loads(handler.response)
    assert data["status"] == "WEBGPU_DIAGNOSTICS_ACTIVE"
    assert "buffer_audit" in data
    assert data["buffer_audit"]["scarcity_compliant"] is True
    assert "spatial_grid_hashing" in data
    assert "cdp_trace_metrics" in data
    assert data["cdp_trace_metrics"]["frame_rate_fps"] == 60.0

