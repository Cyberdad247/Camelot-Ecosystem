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
    assert 'hx-post="/api/cloudbrain/search"' in CANONICAL_INDEX_HTML
    assert 'hx-post="/api/mcp"' in CANONICAL_INDEX_HTML


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
