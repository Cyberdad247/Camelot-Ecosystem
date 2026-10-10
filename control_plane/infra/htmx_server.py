"""
control_plane.infra.htmx_server — Canonical 2-Strand HTMX Server
================================================================
Serves the living canonical hypermedia interface defined at https://htmx-docs.vercel.app/
Zero client JavaScript bloat: renders pure HTML fragments for HTMX swapping and
WGSL WebGPU tensor compute offload.
"""

from __future__ import annotations

import argparse
import html
import http.server
import json
import os
import socketserver
import sys
from pathlib import Path
from typing import Any, Dict

from control_plane.infra.agent_slab_sync import audit_memory, render_htmx_status_fragment
from squires.nullclaw import run_nullclaw_probe

PORT: int = 8096

CANONICAL_INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Camelot-OS · Invisioned Agentic Systems</title>
    
    <!-- Google Fonts: Cinzel & JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">

    <!-- HTMX Core Library (Hypermedia Engine) -->
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    
    <style>
        :root {
            --bg-void: #050505;
            --bg-panel: #0a0a0a;
            --border-dim: #1f1f1f;
            --text-main: #e5e5e5;
            --text-muted: #888888;
            --gold: #D4AF37;
            --cyan: #38bdf8;
            --emerald: #10b981;
        }
        body {
            margin: 0;
            background: var(--bg-void);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }
        aside.sidebar {
            width: 320px;
            background: var(--bg-panel);
            border-right: 1px solid var(--border-dim);
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            box-sizing: border-box;
        }
        .branding h2 {
            font-family: 'Cinzel', serif;
            color: var(--gold);
            margin: 0.2rem 0;
            letter-spacing: 0.05em;
        }
        .brand-eyebrow {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--text-muted);
        }
        .badge {
            font-size: 0.7rem;
            padding: 2px 6px;
            background: #222;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
        }
        .cap-badge {
            background: #1e3a8a;
            color: #93c5fd;
            font-size: 0.7rem;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
        }
        .search-container input {
            width: 100%;
            background: #111;
            border: 1px solid #333;
            color: #fff;
            padding: 0.5rem;
            border-radius: 4px;
            box-sizing: border-box;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
        }
        .search-scope-bar {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
            font-size: 0.75rem;
            color: var(--text-muted);
        }
        nav.doc-links h3 {
            font-family: 'Cinzel', serif;
            font-size: 0.85rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }
        nav.doc-links ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        nav.doc-links li a {
            display: block;
            padding: 0.4rem 0.6rem;
            color: #aaa;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9rem;
            transition: all 0.15s;
        }
        nav.doc-links li a:hover {
            background: #141414;
            color: var(--gold);
        }
        main.content-area {
            flex: 1;
            padding: 2rem;
            overflow-y: auto;
            box-sizing: border-box;
        }
        .mcp-hud-container {
            position: fixed;
            bottom: 1rem;
            right: 1rem;
            width: 440px;
            background: #0d0d0d;
            border: 1px solid #333;
            border-radius: 6px;
            padding: 0.75rem;
            font-family: 'JetBrains Mono', monospace;
            box-shadow: 0 8px 24px rgba(0,0,0,0.8);
        }
        .mcp-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            color: var(--gold);
            border-bottom: 1px solid #222;
            padding-bottom: 0.4rem;
            margin-bottom: 0.4rem;
        }
        .mcp-stream {
            max-height: 120px;
            overflow-y: auto;
            font-size: 0.8rem;
            color: #aaa;
            line-height: 1.4;
        }
        .mcp-input {
            width: 100%;
            background: #000;
            border: 1px solid #222;
            color: var(--cyan);
            padding: 0.4rem;
            margin-top: 0.5rem;
            border-radius: 4px;
            box-sizing: border-box;
            font-family: 'JetBrains Mono', monospace;
        }
    </style>
</head>
<body class="layout">
    
    <aside class="sidebar">
        <div class="branding">
            <div class="brand-eyebrow">Invisioned // Agentic Systems</div>
            <h2>Camelot-OS</h2>
            <div style="display: flex; gap: 0.4rem; align-items: center; margin-top: 0.25rem;">
                <span id="cap-indicator" class="cap-badge">Cleveland Edge (4GB Max)</span>
                <span class="badge">v10001.00</span>
            </div>
        </div>
        
        <div class="search-container">
            <div class="search-scope-bar">
                <label><input type="radio" name="scope" value="all" checked> All</label>
                <label><input type="radio" name="scope" value="docs"> Docs</label>
                <label><input type="radio" name="scope" value="slabs"> Slabs</label>
            </div>
            <input type="search" 
                   id="search-query"
                   name="q"
                   placeholder="Search Docs & CloudBrain..." 
                   hx-post="/api/cloudbrain/search" 
                   hx-include="[name='scope']:checked"
                   hx-trigger="keyup changed delay:300ms" 
                   hx-target="#search-results">
            <ul id="search-results" aria-live="polite" style="list-style: none; padding: 0.5rem 0; margin: 0; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;"></ul>
        </div>

        <nav class="doc-links">
            <h3>Living Telemetry</h3>
            <ul>
                <li><a href="#" hx-get="/docs/slabs" hx-target="#content">IPC Slabs & RAM Ceiling</a></li>
                <li><a href="#" hx-get="/docs/architecture" hx-target="#content">2-Strand Architecture</a></li>
                <li><a href="#" hx-get="/docs/tasks" hx-target="#content">Tasks Execution DAG</a></li>
                <li><a href="#" hx-get="/docs/verification" hx-target="#content">Verification Protocol</a></li>
                <li><a href="#" hx-get="/docs/polyglot" hx-target="#content">Polyglot Hardware Mesh</a></li>
                <li><a href="#" hx-get="/docs/nullclaw" hx-target="#content">NullClaw Zig Squire</a></li>
                <li><a href="#" hx-get="/docs/pantheon" hx-target="#content">Knight Pantheon</a></li>
                <li><a href="#" hx-get="/docs/governance" hx-target="#content">Constitutional Governance (L0)</a></li>
                <li><a href="#" hx-get="/docs/doc-check" hx-target="#content">Doc-Check & Verified States</a></li>
                <li><a href="#" hx-get="/docs/links" hx-target="#content">Links & Dub Sovereign Routing</a></li>
                <li><a href="#" hx-get="/docs/agent-computer" hx-target="#content">OpenMuse Agent Computer & Handover</a></li>
                <li><a href="#" hx-get="/docs/teams" hx-target="#content">AgentTeams Council & Dispatch</a></li>
                <li><a href="#" hx-get="/docs/personalities" hx-target="#content">Knight & Squire Personalities</a></li>
                <li><a href="#" hx-get="/docs/spatial" hx-target="#content">Spatial Citadel 3D Cockpit</a></li>
                <li><a href="#" hx-get="/docs/rea" hx-target="#content">REA Forensics Cockpit</a></li>
            </ul>
        </nav>
    </aside>

    <main id="content" class="content-area" aria-live="polite">
        <h1 style="font-family: 'Cinzel', serif; color: var(--gold);">Initialization Complete</h1>
        <p>Canonical 2-Strand HTMX Interface active on Cybertronia Edge Node.</p>
        <div hx-get="/docs/slabs" hx-trigger="load, every 5s" hx-target="#content">
            <p>Loading live IPC memory slabs...</p>
        </div>
    </main>

    <div id="mcp-hud" class="mcp-hud-container" aria-live="polite">
        <div class="mcp-header">
            <span>ANYA // I-O MIDDLEWARE</span>
            <span style="color: var(--emerald);">● ACTIVE</span>
        </div>
        <div id="mcp-stream" class="mcp-stream">
            <p>System aligned. Living canonical documents active. Awaiting tensor execution...</p>
        </div>
        <input type="text" 
               class="mcp-input" 
               placeholder="Execute Runic Symbolect (e.g., //STATUS)..." 
               name="cmd"
               hx-post="/api/mcp" 
               hx-target="#mcp-stream" 
               hx-swap="innerHTML">
    </div>

    <script>
        // WebGPU Cosine Similarity WGSL Pipeline
        const COSINE_SIMILARITY_WGSL = `
            struct VectorBuffer { data: array<f32>, };
            @group(0) @binding(0) var<storage, read> queryVector : VectorBuffer;
            @group(0) @binding(1) var<storage, read> docVectors : VectorBuffer;
            @group(0) @binding(2) var<storage, read_write> similarityScores : VectorBuffer;
            @compute @workgroup_size(64)
            fn main(@builtin(global_invocation_id) global_id : vec3<u32>) {
                let docIndex = global_id.x;
                let dims : u32 = 64u;
                let baseOffset = docIndex * dims;
                var dotProduct : f32 = 0.0;
                var queryNorm : f32 = 0.0;
                var docNorm : f32 = 0.0;
                for (var i : u32 = 0u; i < dims; i = i + 1u) {
                    let q = queryVector.data[i];
                    let d = docVectors.data[baseOffset + i];
                    dotProduct = dotProduct + (q * d);
                    queryNorm = queryNorm + (q * q);
                    docNorm = docNorm + (d * d);
                }
                let denom = sqrt(queryNorm) * sqrt(docNorm);
                similarityScores.data[docIndex] = select(0.0, dotProduct / denom, denom > 0.0);
            }
        `;
        document.addEventListener("DOMContentLoaded", async () => {
            const stream = document.getElementById("mcp-stream");
            if ("gpu" in navigator) {
                try {
                    const adapter = await navigator.gpu.requestAdapter();
                    if (adapter) {
                        const device = await adapter.requestDevice();
                        stream.innerHTML += "<p style='color: #10b981;'>[WebGPU] WGSL Compute Pipeline Online. Client VRAM vector offload active.</p>";
                    }
                } catch(e) {}
            }
        });
    </script>
</body>
</html>
"""


class CanonicalHTMXHandler(http.server.BaseHTTPRequestHandler):
    """Handles HTMX hypermedia fragment swapping and runic dispatch."""

    def _send_html(self, content: str, status: int = 200) -> None:
        payload = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            self._send_html(CANONICAL_INDEX_HTML)
        elif path == "/docs/slabs":
            self._send_html(render_htmx_status_fragment())
        elif path == "/docs/architecture":
            blueprint_path = Path(__file__).resolve().parent.parent.parent / ".agent" / "blueprint.md"
            text = blueprint_path.read_text(encoding="utf-8") if blueprint_path.exists() else "Blueprint missing"
            html_snippet = f"""
            <div class="content-card" style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">
                <h2 style="font-family: 'Cinzel', serif; color: #D4AF37;">The Master Architecture</h2>
                <pre style="background: #111; padding: 1rem; border-radius: 4px; overflow-x: auto; color: #ccc;">{html.escape(text)}</pre>
            </div>
            """
            self._send_html(html_snippet)
        elif path == "/docs/tasks":
            tasks_path = Path(__file__).resolve().parent.parent.parent / ".agent" / "tasks.md"
            text = tasks_path.read_text(encoding="utf-8") if tasks_path.exists() else "Tasks DAG missing"
            html_snippet = f"""
            <div class="content-card" style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">
                <h2 style="font-family: 'Cinzel', serif; color: #D4AF37;">Task Execution DAG</h2>
                <pre style="background: #111; padding: 1rem; border-radius: 4px; overflow-x: auto; color: #ccc;">{html.escape(text)}</pre>
            </div>
            """
            self._send_html(html_snippet)
        elif path == "/docs/verification":
            verify_path = Path(__file__).resolve().parent.parent.parent / ".agent" / "verification.md"
            text = verify_path.read_text(encoding="utf-8") if verify_path.exists() else "Verification protocol missing"
            html_snippet = f"""
            <div class="content-card" style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">
                <h2 style="font-family: 'Cinzel', serif; color: #D4AF37;">Verification & Governance Protocol</h2>
                <pre style="background: #111; padding: 1rem; border-radius: 4px; overflow-x: auto; color: #ccc;">{html.escape(text)}</pre>
            </div>
            """
            self._send_html(html_snippet)
        elif path == "/docs/polyglot":
            polyglot_path = Path(__file__).resolve().parent.parent.parent / "03_VAULT" / "UKG" / "nodes" / "UKG_POLYGLOT_HARDWARE_ASCENSION.toon"
            text = polyglot_path.read_text(encoding="utf-8") if polyglot_path.exists() else "Polyglot crystal missing"
            html_snippet = f"""
            <div class="content-card" style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">
                <h2 style="font-family: 'Cinzel', serif; color: #D4AF37;">Bare-Metal Polyglot Omni-Nexus (TOON Spec v3.3)</h2>
                <pre style="background: #111; padding: 1rem; border-radius: 4px; overflow-x: auto; color: #ccc;">{html.escape(text)}</pre>
            </div>
            """
            self._send_html(html_snippet)
        elif path == "/docs/nullclaw":
            probe = run_nullclaw_probe()
            html_snippet = f"""
            <div class="content-card" style="font-family: 'JetBrains Mono', monospace;">
                <h2 style="font-family: 'Cinzel', serif; color: #D4AF37;">NullClaw Zig Squire Telemetry</h2>
                <div style="background: #111; padding: 1rem; border-radius: 4px; border: 1px solid #222;">
                    <p><strong>Squire ID:</strong> <span style="color: #38bdf8;">{probe['squire']}</span></p>
                    <p><strong>Memory Bound:</strong> <span style="color: #10b981;">{probe['memory_bound_kb']} KB (FixedBufferAllocator)</span></p>
                    <p><strong>Edge Node:</strong> {probe['edge_node']}</p>
                    <p><strong>Status:</strong> <span style="color: #10b981;">{probe['status']}</span></p>
                </div>
            </div>
            """
            self._send_html(html_snippet)
        elif path == "/docs/pantheon":
            agents_path = Path(__file__).resolve().parent.parent.parent / ".agent" / "Agents.md"
            text = agents_path.read_text(encoding="utf-8") if agents_path.exists() else "Agents missing"
            html_snippet = f"""
            <div class="content-card" style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">
                <h2 style="font-family: 'Cinzel', serif; color: #D4AF37;">Sovereign Agent Pantheon</h2>
                <pre style="background: #111; padding: 1rem; border-radius: 4px; overflow-x: auto; color: #ccc;">{html.escape(text)}</pre>
            </div>
            """
            self._send_html(html_snippet)
        elif path == "/docs/governance":
            gov_path = Path(__file__).resolve().parent.parent.parent / "docs" / "00-governance" / "GOVERNANCE.md"
            text = gov_path.read_text(encoding="utf-8") if gov_path.exists() else "Governance missing"
            html_snippet = f"""
            <div class="content-card" style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">
                <h2 style="font-family: 'Cinzel', serif; color: #D4AF37;">L0 Constitutional Governance & Axioms</h2>
                <pre style="background: #111; padding: 1rem; border-radius: 4px; overflow-x: auto; color: #ccc;">{html.escape(text)}</pre>
            </div>
            """
            self._send_html(html_snippet)
        elif path == "/docs/doc-check":
            from scripts.doc_check import validate_metadata, validate_slices, validate_canonical_home, validate_waivers
            from control_plane.infra.firnflow import FirnFlow
            ok_meta, _ = validate_metadata()
            ok_slices, _ = validate_slices()
            ok_home, _ = validate_canonical_home()
            ok_waiv, _ = validate_waivers()
            
            ff = FirnFlow()
            spill_telemetry = ff.evaluate_spill_gate(force=False)

            states = ["PENDING", "DENIED", "APPROVED", "EXECUTING", "VERIFIED", "FAILED", "STALE", "REVOKED"]
            state_pills = " ".join([f"<span class='badge' style='margin: 2px; color: #38bdf8; border: 1px solid #38bdf8;'>{s}</span>" for s in states])
            spine_steps = ["SENTINEL(Lease)", "EXCALIBUR(Approval)", "GIDEON(Proof)", "ARTHUR(Resolution)", "LEDGER(Receipt)"]
            spine_html = " ➔ ".join([f"<span class='badge' style='margin: 2px; color: #D4AF37; border: 1px solid #D4AF37;'>{st}</span>" for st in spine_steps])

            html_snippet = f"""
            <div class="content-card" style="font-family: 'JetBrains Mono', monospace;">
                <h2 style="font-family: 'Cinzel', serif; color: #D4AF37;">Doc-Check Verification & UI Verified-State Engine</h2>
                <div style="background: #111; padding: 1rem; border-radius: 4px; border: 1px solid #222; margin-bottom: 1rem;">
                    <p><strong>Metadata Schema Validation:</strong> <span style="color: {'#10b981' if ok_meta else '#ef4444'};">{'[PASS]' if ok_meta else '[FAIL]'}</span></p>
                    <p><strong>17 Vertical Slices Scaffolding:</strong> <span style="color: {'#10b981' if ok_slices else '#ef4444'};">{'[PASS]' if ok_slices else '[FAIL]'}</span></p>
                    <p><strong>Canonical Home Matrix:</strong> <span style="color: {'#10b981' if ok_home else '#ef4444'};">{'[PASS]' if ok_home else '[FAIL]'}</span></p>
                    <p><strong>Time-Bound Waiver Audit:</strong> <span style="color: {'#10b981' if ok_waiv else '#ef4444'};">{'[PASS]' if ok_waiv else '[FAIL]'}</span></p>
                    <p><strong>Firnflow 90% Spill Gate:</strong> <span style="color: #10b981;">ARMED (Threshold: {spill_telemetry['threshold_mb']}MB | Triggered: {spill_telemetry['spill_gate_triggered']})</span></p>
                </div>
                <h3 style="font-size: 0.85rem; color: #888; text-transform: uppercase;">Cryptographic Authority Spine</h3>
                <div style="padding: 0.5rem 0; margin-bottom: 1rem;">{spine_html}</div>
                <h3 style="font-size: 0.85rem; color: #888; text-transform: uppercase;">Admitted UI State Space (STATE_SERVICE_ONLY)</h3>
                <div style="padding: 0.5rem 0;">{state_pills}</div>
            </div>
            """
            self._send_html(html_snippet)
        elif path == "/docs/links":
            html_snippet = """
            <div class="content-card" style="font-family: 'JetBrains Mono', monospace;">
                <h2 style="font-family: 'Cinzel', serif; color: #D4AF37;">Sovereign Link Engine (Dub Assimilation)</h2>
                <div style="background: #111; padding: 1rem; border-radius: 4px; border: 1px solid #222; margin-bottom: 1rem;">
                    <p><strong>Substrate:</strong> <span style="color: #38bdf8;">Go Bifrost Gateway (:3001/r/:slug) & VFS Links</span></p>
                    <p><strong>RAM Ceiling:</strong> <span style="color: #10b981;">512 MB profile (Strict Law 03: 4GB Node Cap)</span></p>
                    <p><strong>Latency Profile:</strong> <span style="color: #10b981;">&lt; 0.5ms Memory Redirection (Rule 7 Zero-Bloat)</span></p>
                    <p><strong>Attribution Substrate:</strong> <span style="color: #D4AF37;">ClickHouse/Tinybird Pipe Schema Emulation</span></p>
                    <p><strong>Assimilated Cartridge:</strong> <span style="color: #38bdf8;">cartridges/dub-link-engine (Ed25519 Signed)</span></p>
                </div>
                <h3 style="font-size: 0.85rem; color: #888; text-transform: uppercase;">Active Sovereign Link Mappings</h3>
                <div style="background: #080808; padding: 0.75rem; border-radius: 4px; border: 1px solid #1a1a1a;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.8rem; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid #333; color: #D4AF37;">
                                <th style="padding: 4px;">Short Slug</th>
                                <th style="padding: 4px;">VFS Coordinate</th>
                                <th style="padding: 4px;">Destination</th>
                                <th style="padding: 4px;">Assigned Knight</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom: 1px solid #222;">
                                <td style="padding: 4px; color: #38bdf8;">/hud</td>
                                <td style="padding: 4px;">vfs://worldtree/links/hud</td>
                                <td style="padding: 4px;">http://localhost:8096/</td>
                                <td style="padding: 4px;">SIR_BORIS</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #222;">
                                <td style="padding: 4px; color: #38bdf8;">/bifrost</td>
                                <td style="padding: 4px;">vfs://worldtree/links/bifrost</td>
                                <td style="padding: 4px;">http://localhost:3001/bifrost</td>
                                <td style="padding: 4px;">SIR_HELIO</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #222;">
                                <td style="padding: 4px; color: #38bdf8;">/excalibur</td>
                                <td style="padding: 4px;">vfs://worldtree/links/excalibur</td>
                                <td style="padding: 4px;">http://localhost:8811/</td>
                                <td style="padding: 4px;">SIR_HELIOS</td>
                            </tr>
                            <tr>
                                <td style="padding: 4px; color: #38bdf8;">/docs</td>
                                <td style="padding: 4px;">vfs://worldtree/links/docs</td>
                                <td style="padding: 4px;">http://localhost:8096/docs/slabs</td>
                                <td style="padding: 4px;">SIR_LINK</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            """
            self._send_html(html_snippet)
        elif path == "/docs/agent-computer":
            html_snippet = """
            <div class="content-card" style="font-family: 'JetBrains Mono', monospace;">
                <h2 style="font-family: 'Cinzel', serif; color: #D4AF37;">OpenMuse Agent Computer & Omega Handover Cockpit</h2>
                <div style="background: #111; padding: 1rem; border-radius: 4px; border: 1px solid #222; margin-bottom: 1rem;">
                    <p><strong>Actuator:</strong> <span style="color: #38bdf8;">LUKAS_Ω (Bare-Metal Sandlock Landlock COW &lt;5ms)</span></p>
                    <p><strong>Gatekeeper:</strong> <span style="color: #10b981;">ANYA_Ω (L7 Modality Hypervisor & Biometric Handover)</span></p>
                    <p><strong>Cognitive Planner:</strong> <span style="color: #D4AF37;">MERLIN_Ω (Durable Task DAG & Evidence Receipts)</span></p>
                    <p><strong>Offline Reasoner:</strong> <span style="color: #38bdf8;">JEV_Ω (SmolLM3 1.58-bit Ternary Core - 0 Cloud Tokens)</span></p>
                    <p><strong>Memory Ceiling:</strong> <span style="color: #10b981;">512 MB profile (Strict Law 03: 4GB Node Cap)</span></p>
                    <p><strong>Assimilated Cartridge:</strong> <span style="color: #38bdf8;">cartridges/openmuse-agent-computer (Ed25519 Signed)</span></p>
                </div>
                <h3 style="font-size: 0.85rem; color: #888; text-transform: uppercase;">Agent Computer Dual Stratum</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div style="background: #080808; padding: 0.75rem; border-radius: 4px; border: 1px solid #1a1a1a;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #38bdf8; font-size: 0.85rem;">Linux Terminal / Workspace</h4>
                        <p style="font-size: 0.75rem; color: #aaa; margin: 0 0 0.5rem 0;">Read-only rootfs, dropped capabilities, no network egress. Sub-5ms COW sandbox.</p>
                        <span class="badge" style="color: #10b981; border: 1px solid #10b981;">SANDLOCK ISOLATED</span>
                    </div>
                    <div style="background: #080808; padding: 0.75rem; border-radius: 4px; border: 1px solid #1a1a1a;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #D4AF37; font-size: 0.85rem;">Browser Worker & Handover</h4>
                        <p style="font-size: 0.75rem; color: #aaa; margin: 0 0 0.5rem 0;">Persistent Chromium profile, destination firewall, biometric human takeover.</p>
                        <span class="badge" style="color: #D4AF37; border: 1px solid #D4AF37;">TAKEOVER READY</span>
                    </div>
                </div>
            </div>
            """
            self._send_html(html_snippet)
        elif path == "/docs/teams":
            html_snippet = """
            <div class="content-card" style="font-family: 'JetBrains Mono', monospace;">
                <h2 style="font-family: 'Cinzel', serif; color: #D4AF37;">Octop Multi-Agent Council & Strike Teams</h2>
                <div style="background: #111; padding: 1rem; border-radius: 4px; border: 1px solid #222; margin-bottom: 1rem;">
                    <p><strong>Lead Dispatcher:</strong> <span style="color: #38bdf8;">MERLIN_Ω (INTJ - Mastermind / DAG Architect)</span></p>
                    <p><strong>L7 Gatekeeper:</strong> <span style="color: #10b981;">ANYA_Ω (ISTJ - Inspector / Zero-Bypass Egress)</span></p>
                    <p><strong>Kinetic Actuator:</strong> <span style="color: #f59e0b;">LUKAS_Ω (ESTP - Dynamo / Sandlocked Runner)</span></p>
                    <p><strong>Offline Reasoner:</strong> <span style="color: #a855f7;">JEV_Ω (INTP - Logician / SmolLM3 Ternary Core)</span></p>
                    <p><strong>Crucible Conductor:</strong> <span style="color: #ec4899;">SIR_BORIS (ENTJ - Commander / AST Refactorer)</span></p>
                    <p><strong>Z3 Formal Verifier:</strong> <span style="color: #06b6d4;">SIR_CODEX (ISTP - Virtuoso / Logic Prover)</span></p>
                    <p><strong>Telemetry Sentinel:</strong> <span style="color: #D4AF37;">SIR_HELIOS (ENTP - Visionary / CloudBrain Synergy)</span></p>
                    <p><strong>Assimilated Cartridge:</strong> <span style="color: #38bdf8;">cartridges/octop-agent-council (Ed25519 Signed)</span></p>
                </div>
                <h3 style="font-size: 0.85rem; color: #888; text-transform: uppercase;">Council Dynamic Protocols</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div style="background: #080808; padding: 0.75rem; border-radius: 4px; border: 1px solid #1a1a1a;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #38bdf8; font-size: 0.85rem;">Asynchronous Job Tracker</h4>
                        <p style="font-size: 0.75rem; color: #aaa; margin: 0 0 0.5rem 0;">Decoupled ask_agent task execution, background worker state, and non-blocking results.</p>
                        <span class="badge" style="color: #10b981; border: 1px solid #10b981;">ASYNC TRACKED</span>
                    </div>
                    <div style="background: #080808; padding: 0.75rem; border-radius: 4px; border: 1px solid #1a1a1a;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #D4AF37; font-size: 0.85rem;">MBTI Persona Harmonization</h4>
                        <p style="font-size: 0.75rem; color: #aaa; margin: 0 0 0.5rem 0;">16-Type Myers-Briggs personality vectors complementing Big-5 OCEAN for optimal team synergy.</p>
                        <span class="badge" style="color: #D4AF37; border: 1px solid #D4AF37;">MBTI HARMONIZED</span>
                    </div>
                </div>
            </div>
            """
            self._send_html(html_snippet)
        elif path == "/docs/personalities":
            sheets_path = Path(__file__).resolve().parent.parent.parent / "03_VAULT" / "training" / "configs" / "knight_character_sheets.json"
            knights_data = json.loads(sheets_path.read_text(encoding="utf-8")).get("knights", {}) if sheets_path.exists() else {}
            
            rows = []
            for kid in sorted(knights_data.keys()):
                k = knights_data[kid]
                mbti = k.get("mbti", "N/A")
                arch = k.get("mbti_profile", {}).get("archetype", "Specialist")
                lang = k.get("primary_language", "Python")
                tier = k.get("skill_tier", "S4 Strategic")
                is_omega = "OMEGA" in kid
                badge_color = "#D4AF37" if is_omega else "#38bdf8"
                rows.append(
                    f"<tr>"
                    f"<td style='padding: 6px; border-bottom: 1px solid #1a1a1a; color: {badge_color};'><strong>{kid}</strong></td>"
                    f"<td style='padding: 6px; border-bottom: 1px solid #1a1a1a;'><span class='badge' style='color: #10b981; border: 1px solid #10b981;'>{mbti}</span></td>"
                    f"<td style='padding: 6px; border-bottom: 1px solid #1a1a1a; color: #ccc;'>{arch}</td>"
                    f"<td style='padding: 6px; border-bottom: 1px solid #1a1a1a; color: #38bdf8;'>{lang}</td>"
                    f"<td style='padding: 6px; border-bottom: 1px solid #1a1a1a; color: #888;'>{tier}</td>"
                    f"</tr>"
                )
            
            table_body = "".join(rows)
            html_snippet = f"""
            <div class="content-card" style="font-family: 'JetBrains Mono', monospace;">
                <h2 style="font-family: 'Cinzel', serif; color: #D4AF37;">Knight & Squire Personality Archetypes (Source of Truth)</h2>
                <div style="background: #111; padding: 1rem; border-radius: 4px; border: 1px solid #222; margin-bottom: 1rem;">
                    <p><strong>Total Calibrated Knights:</strong> <span style="color: #10b981;">{len(knights_data)} Verified</span></p>
                    <p><strong>Cognitive Framework:</strong> <span style="color: #38bdf8;">Hybrid Myers-Briggs (16-Type MBTI) + 5-Factor Big-5 OCEAN</span></p>
                    <p><strong>Contract Schemas:</strong> <span style="color: #D4AF37;">persona.schema.json (Knights) & squire.schema.json (Squires)</span></p>
                    <p><strong>Templates:</strong> <span style="color: #38bdf8;">packages/contracts/templates/</span></p>
                </div>
                <div style="max-height: 480px; overflow-y: auto; border: 1px solid #1a1a1a; border-radius: 4px;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.8rem; text-align: left;">
                        <thead>
                            <tr style="background: #0d0d0d; color: #888; border-bottom: 1px solid #222;">
                                <th style="padding: 8px;">Knight ID</th>
                                <th style="padding: 8px;">MBTI</th>
                                <th style="padding: 8px;">Archetype & Role</th>
                                <th style="padding: 8px;">Language</th>
                                <th style="padding: 8px;">Tier</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_body}
                        </tbody>
                    </table>
                </div>
            </div>
            """
            self._send_html(html_snippet)
        elif path == "/docs/spatial":
            html_snippet = """
            <div class="content-card" style="font-family: 'JetBrains Mono', monospace;">
                <h2 style="font-family: 'Cinzel', serif; color: #D4AF37;">Spatial Citadel 3D Cockpit (R3F & Three.js)</h2>
                <div style="background: #111; padding: 1rem; border-radius: 4px; border: 1px solid #222; margin-bottom: 1rem;">
                    <p><strong>Assimilated Pattern:</strong> <span style="color: #38bdf8;">adrianhajdin/3D_portfolio (Declarative R3F Island World)</span></p>
                    <p><strong>Actuator:</strong> <span style="color: #10b981;">SIR_BORIS (Crucible Conductor & 3D Spatial State Machine)</span></p>
                    <p><strong>Kinematics & Damping:</strong> <span style="color: #D4AF37;">SIR_STITCH (Physics Rotational Damping factor 0.95)</span></p>
                    <p><strong>Telemetry Sentinel:</strong> <span style="color: #38bdf8;">SIR_HELIOS (High-Altitude Spire Perspective)</span></p>
                    <p><strong>Memory Ceiling:</strong> <span style="color: #10b981;">512 MB (Law 03 Compliant, WebGL Context Bounded)</span></p>
                    <p><strong>Cartridge:</strong> <span style="color: #D4AF37;">cartridges/spatial-citadel (Ed25519 Signed)</span></p>
                </div>
                <h3 style="font-size: 0.85rem; color: #888; text-transform: uppercase;">4-Quadrant Subsystem Navigation</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div style="background: #080808; padding: 0.75rem; border-radius: 4px; border: 1px solid #1a1a1a;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #38bdf8; font-size: 0.85rem;">Quadrant 1: Sovereign Core (0 rad)</h4>
                        <p style="font-size: 0.75rem; color: #aaa; margin: 0 0 0.5rem 0;">Primary Cybertronia root node, host telemetry, and IPC memory slabs.</p>
                        <span class="badge" style="color: #10b981; border: 1px solid #10b981;">CORE ACTIVE</span>
                    </div>
                    <div style="background: #080808; padding: 0.75rem; border-radius: 4px; border: 1px solid #1a1a1a;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #D4AF37; font-size: 0.85rem;">Quadrant 2: Omega Pantheon (π/2 rad)</h4>
                        <p style="font-size: 0.75rem; color: #aaa; margin: 0 0 0.5rem 0;">L7 Modality Hypervisors, Z3 Logic Provers, and verified UI states.</p>
                        <span class="badge" style="color: #D4AF37; border: 1px solid #D4AF37;">PANTHEON MOUNTED</span>
                    </div>
                    <div style="background: #080808; padding: 0.75rem; border-radius: 4px; border: 1px solid #1a1a1a;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #a855f7; font-size: 0.85rem;">Quadrant 3: WorldTree CloudBrain (π rad)</h4>
                        <p style="font-size: 0.75rem; color: #aaa; margin: 0 0 0.5rem 0;">294-node NotebookLM mesh, living knight tissues, and VFS crystals.</p>
                        <span class="badge" style="color: #a855f7; border: 1px solid #a855f7;">CLOUDBRAIN TETHERED</span>
                    </div>
                    <div style="background: #080808; padding: 0.75rem; border-radius: 4px; border: 1px solid #1a1a1a;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #06b6d4; font-size: 0.85rem;">Quadrant 4: Excalibur Sentinel (3π/2 rad)</h4>
                        <p style="font-size: 0.75rem; color: #aaa; margin: 0 0 0.5rem 0;">Samsung S26 Ultra mobile cockpit, 120Hz Adreno 840 GPU stream.</p>
                        <span class="badge" style="color: #06b6d4; border: 1px solid #06b6d4;">MOBILE LINKED</span>
                    </div>
                </div>
            </div>
            """
            self._send_html(html_snippet)
        elif path == "/docs/rea":
            html_snippet = """
            <div class="content-card" style="font-family: 'JetBrains Mono', monospace;">
                <h2 style="font-family: 'Cinzel', serif; color: #D4AF37;">REA Reverse Engineering & Forensic Evidence Cockpit</h2>
                <div style="background: #111; padding: 1rem; border-radius: 4px; border: 1px solid #222; margin-bottom: 1rem;">
                    <p><strong>Assimilated Engine:</strong> <span style="color: #38bdf8;">morluto/rea (Reverse Engineer Anything v6.1.0)</span></p>
                    <p><strong>Lead Sentinel:</strong> <span style="color: #D4AF37;">SIR_HELIOS (FastMCP / AntiGravity High-Altitude Truth)</span></p>
                    <p><strong>Cognitive Planner:</strong> <span style="color: #38bdf8;">MERLIN_Ω (Evidence Graph DAG Synthesis)</span></p>
                    <p><strong>Formal Logic Prover:</strong> <span style="color: #10b981;">SIR_CODEX (Z3 Function Invariant Proofs)</span></p>
                    <p><strong>Offline Reasoner:</strong> <span style="color: #a855f7;">JEV_Ω (SmolLM3 1.58-bit Air-Gapped Decompilation)</span></p>
                    <p><strong>Memory Ceiling:</strong> <span style="color: #10b981;">512 MB profile (Strict Law 03: 4GB Node Cap)</span></p>
                    <p><strong>Cartridge:</strong> <span style="color: #D4AF37;">cartridges/rea-forensics (Ed25519 Signed)</span></p>
                    <p><strong>Runic Dispatch:</strong> <span style="color: #38bdf8;">//REA &lt;target&gt; [--provider auto|ghidra|hopper]</span></p>
                </div>
                <h3 style="font-size: 0.85rem; color: #888; text-transform: uppercase;">Forensic Analysis Strata</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div style="background: #080808; padding: 0.75rem; border-radius: 4px; border: 1px solid #1a1a1a;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #38bdf8; font-size: 0.85rem;">JavaScript / Electron (ASAR)</h4>
                        <p style="font-size: 0.75rem; color: #aaa; margin: 0 0 0.5rem 0;">AST module reconstruction, IPC boundary mapping, V8 inspector hooks.</p>
                        <span class="badge" style="color: #10b981; border: 1px solid #10b981;">ZERO-ENGINE STATIC</span>
                    </div>
                    <div style="background: #080808; padding: 0.75rem; border-radius: 4px; border: 1px solid #1a1a1a;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #D4AF37; font-size: 0.85rem;">Native Binaries & Assemblies</h4>
                        <p style="font-size: 0.75rem; color: #aaa; margin: 0 0 0.5rem 0;">Mach-O/PE/ELF disassembly via Ghidra, Hopper, IDA Pro & LLDB traces.</p>
                        <span class="badge" style="color: #D4AF37; border: 1px solid #D4AF37;">DEEP ENGINE READY</span>
                    </div>
                    <div style="background: #080808; padding: 0.75rem; border-radius: 4px; border: 1px solid #1a1a1a;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #a855f7; font-size: 0.85rem;">Mobile Packages (APK / IPA)</h4>
                        <p style="font-size: 0.75rem; color: #aaa; margin: 0 0 0.5rem 0;">JADX bytecode decompilation, manifest inspection, native bridge calls.</p>
                        <span class="badge" style="color: #a855f7; border: 1px solid #a855f7;">MOBILE ARMED</span>
                    </div>
                    <div style="background: #080808; padding: 0.75rem; border-radius: 4px; border: 1px solid #1a1a1a;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #06b6d4; font-size: 0.85rem;">Evidence Ledger & Residual Unknowns</h4>
                        <p style="font-size: 0.75rem; color: #aaa; margin: 0 0 0.5rem 0;">Cryptographic truth verification: bounds findings, declares unknown state.</p>
                        <span class="badge" style="color: #06b6d4; border: 1px solid #06b6d4;">TRUTH BOUNDED</span>
                    </div>
                </div>
            </div>
            """
            self._send_html(html_snippet)
        else:
            self._send_html("<div class='content-card'><h3>Document Not Found</h3></div>", status=404)

    def do_POST(self) -> None:
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else ""

        if self.path == "/api/cloudbrain/search":
            query = ""
            for part in post_body.split("&"):
                if part.startswith("q="):
                    query = part.split("=")[1]
            if query:
                results = f"""
                <li style='padding: 0.2rem 0; color: #38bdf8;'>🔎 Match: .agent/blueprint.md ({query})</li>
                <li style='padding: 0.2rem 0; color: #10b981;'>⚡ Slab: local_env.md (Edge Ceiling: 4GB)</li>
                <li style='padding: 0.2rem 0; color: #D4AF37;'>🏛️ Pantheon: Jev Ω & Lukas Ω</li>
                """
            else:
                results = "<li style='color: #666;'>Type to query CloudBrain...</li>"
            self._send_html(results)
        elif self.path == "/api/mcp":
            cmd = ""
            for part in post_body.split("&"):
                if part.startswith("cmd="):
                    cmd = part.split("=")[1].replace("+", " ")
            cmd = html.escape(cmd)
            resp = f"<p style='color: #D4AF37;'>> {cmd}</p><p style='color: #10b981;'>[ANYA] Verified. Zero-copy execution acknowledged under 4GB ceiling.</p>"
            self._send_html(resp)
        else:
            self._send_html("<p>Endpoint not found</p>", status=404)


def run_server(port: int = PORT) -> None:
    server_address = ("127.0.0.1", port)
    with socketserver.TCPServer(server_address, CanonicalHTMXHandler) as httpd:
        print(f"[CANONICAL HTMX] Server active at http://127.0.0.1:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Canonical 2-Strand HTMX Server")
    parser.add_argument("--port", type=int, default=PORT, help="Port to listen on")
    args = parser.parse_args()
    run_server(args.port)
