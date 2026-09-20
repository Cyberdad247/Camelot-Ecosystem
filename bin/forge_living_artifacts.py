# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Living Camelot-OS Artifact & Manifest Forger
r"""
Forge Living Camelot-OS Artifacts & Manifests in High-Density NotebookLM Workspaces (>50 sources).
Tethers high-density domain notebooks directly into WorldTree Root (a0a4bfb9-e847-4c38-be39-7aee398f0795).
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CAMELOT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CAMELOT_ROOT))

from vfs.notebooklm_client import _get_client
from merlin.context.merlin_infinite_context import merlin_context

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LivingArtifactForger")

WORLDTREE_UUID = "a0a4bfb9-e847-4c38-be39-7aee398f0795"
ARTIFACTS_DIR = CAMELOT_ROOT / "01_KERNEL" / "memory" / "living_artifacts"
CRYSTALS_DIR = CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "open_notebook" / "vkg_crystals"

# Targeted 30 High-Density Notebooks discovered during Workspace Audit
HIGH_DENSITY_FLEET: List[Dict[str, Any]] = [
    {
        "id": "8c656cfa-a189-409e-a72d-07692a47f17e",
        "title": "Camelot-OS v.1000",
        "sources": 315,
        "knight": "CAMELOT_V1000",
        "category": "CAMELOT_SYSTEMS_ARCHITECTURE",
        "topics": ["Excalibur Hub", "Kernel Substrates", "Sovereign OS Master Architecture", "Multi-Agent Swarms", "Zero-Trust Mesh"],
        "triplets": [("Camelot-OS v1000", "governs", "Excalibur Hub"), ("Excalibur Hub", "routes", "Sovereign Swarms"), ("Kernel", "anchors", "WorldTree")]
    },
    {
        "id": "140101e0-bc2a-41c8-87c0-cd512f130387",
        "title": "Anya Omega: Sovereign Compiler of Camelot-OS + 6 more",
        "sources": 300,
        "knight": "ANYA_OMEGA",
        "category": "SOVEREIGN_ROUND_TABLE",
        "topics": ["Sovereign Compiler", "Helm Authority", "Anya First & Last Gate", "Token Compression", "Glyph Quantum Engine"],
        "triplets": [("Anya Omega", "compiles", "Camelot-OS"), ("Anya First Gate", "enforces", "Operator Alignment"), ("Anya Last Gate", "seals", "Execution Artifacts")]
    },
    {
        "id": "face97b5-cbaa-4cc9-98a8-d16dfcaf0f18",
        "title": "Prompt Engineering: An Overview",
        "sources": 300,
        "knight": "MERLIN_OMEGA",
        "category": "AI_MULTIAGENT_RESEARCH",
        "topics": ["In-Context Learning", "Chain-of-Thought", "Tree-of-Thoughts", "System Prompts", "Meta-Prompt Optimization"],
        "triplets": [("Prompt Engineering", "optimizes", "Model Reasoning"), ("Chain of Thought", "structures", "AST Decomposition"), ("Meta Prompts", "steer", "Agent Personas")]
    },
    {
        "id": "cadfe67e-7187-472e-8bf4-8a2aded84e4e",
        "title": "HiveIDE-aka Inspira",
        "sources": 266,
        "knight": "INSPIRA",
        "category": "SPECIALIZED_SUBSTRATES",
        "topics": ["Spatial Developer Workstation", "Virtual Filesystem UI", "Real-Time AST Visualization", "Multi-Agent Collaboration Canvas"],
        "triplets": [("Inspira HiveIDE", "renders", "Spatial Workstation"), ("VFS UI", "visualizes", "AST Code Graph"), ("Inspira", "bridges", "Operator Intent")]
    },
    {
        "id": "71be7c3c-e1d0-46cf-b352-3c71006fecc7",
        "title": "Merlin: AI Mythosmith Persona Documentation",
        "sources": 262,
        "knight": "MERLIN_OMEGA",
        "category": "SOVEREIGN_ROUND_TABLE",
        "topics": ["Graph-of-Thoughts", "Deep Reasoning", "Mathematical Proofs", "Mythosmith Architecture", "Infinite Context Engine"],
        "triplets": [("Merlin Omega", "executes", "Graph of Thoughts"), ("Mythosmith Engine", "crystallizes", "Infinite Context"), ("Merlin", "advises", "King Arthur")]
    },
    {
        "id": "2d2b9214-2207-4892-a131-e98e18fc8d3e",
        "title": "The Obsidian Crystal: Singularity Lattice Protocol",
        "sources": 241,
        "knight": "ANYA_QUANTUM_MANTRA",
        "category": "SPECIALIZED_SUBSTRATES",
        "topics": ["Singularity Lattice", "Token Compression", "Glyph Quantum Mantras", "VFS Position-Addressed Sharding", "Quantum Lattice"],
        "triplets": [("Obsidian Crystal", "anchors", "Singularity Lattice"), ("Quantum Mantra", "compresses", "Semantic Tokens"), ("Lattice Protocol", "unifies", "Mesh Nodes")]
    },
    {
        "id": "f48a2cb9-1922-422f-bb13-5eabf28efda2",
        "title": "SUNO",
        "sources": 192,
        "knight": "SIR_SONUS",
        "category": "SPECIALIZED_SUBSTRATES",
        "topics": ["Algorithmic Music Generation", "Lyric Structure Prompting", "Audio Frequency Engineering", "Phonetic Metatags", "Stem Separation"],
        "triplets": [("Suno Engine", "synthesizes", "Algorithmic Audio"), ("Sir Sonus", "orchestrates", "Phonetic Metatags"), ("Audio Pipeline", "renders", "Acoustic Tissues")]
    },
    {
        "id": "03dc365b-1769-4632-9df3-d763f2bd90a7",
        "title": "Mastering Professional UI/UX Design for AI Web Development",
        "sources": 190,
        "knight": "LADY_GUINEVERE",
        "category": "AI_MULTIAGENT_RESEARCH",
        "topics": ["Luxury Minimalist Brutalism", "Tailwind v4", "Luxora Gold (#D4AF37)", "Heads-Up Display Engineering", "R3F 3D Kinematics"],
        "triplets": [("Lady Guinevere", "dictates", "Luxury Brutalism"), ("Luxora Gold", "highlights", "Camelot HUD"), ("Tailwind v4", "styles", "PWA Surfaces")]
    },
    {
        "id": "e6374819-50ce-41cf-b6b3-99924ca6ab90",
        "title": "Invisioned Marketing: Agentic OS and Digital Strategy Dashboard",
        "sources": 171,
        "knight": "INVISIONED_MARKETING",
        "category": "MARKETING_WEALTH_BRAND",
        "topics": ["Sovereign Brand Direction", "Agentic Marketing Automation", "AEO/GEO Optimization", "Digital Factory Pipelines", "Campaign Swarms"],
        "triplets": [("Invisioned Marketing", "conducts", "Digital Factory"), ("Knight Strategos", "executes", "AEO/GEO Assimilation"), ("Marketing DAG", "scales", "Ecosystem Reach")]
    },
    {
        "id": "b24af98e-fe3a-4fc2-838c-492b4eb3dcb7",
        "title": "Architectural Foundations and Operational Excellence in Enterprise AI",
        "sources": 128,
        "knight": "SIR_CODEX",
        "category": "AI_MULTIAGENT_RESEARCH",
        "topics": ["Zero-Trust Infrastructure", "High-Velocity CI/CD", "Fault Tolerant Microservices", "Distributed Orchestration", "AST TDD Loops"],
        "triplets": [("Sir Codex", "architects", "Enterprise Infrastructure"), ("Zero-Trust", "secures", "Bifrost Gateway"), ("TDD Loops", "verify", "Kinetic Code")]
    },
    {
        "id": "67c3a2b5-b93a-48f9-9812-24d7801e21d5",
        "title": "A.I agents",
        "sources": 126,
        "knight": "BIO_KINETIC_SWARM",
        "category": "AI_MULTIAGENT_RESEARCH",
        "topics": ["Autonomous Agentic Swarms", "Cellular Diode Isolation", "Task Planning DAGs", "Inter-Agent Consensus", "Subagent Mitosis"],
        "triplets": [("AI Agents", "collaborate in", "Bio-Kinetic Swarm"), ("Cellular Diodes", "isolate", "Subagent Execution"), ("Consensus Gates", "validate", "Multi-Agent Output")]
    },
    {
        "id": "bebdf3e3-bbb0-455b-9c02-1469202baf74",
        "title": "Lukas Müller v3.0: The Ultimate Cognitive Forge Persona",
        "sources": 113,
        "knight": "SIR_FORGE",
        "category": "SOVEREIGN_ROUND_TABLE",
        "topics": ["Kinetic Code Generation", "Compiles & Builds", "//FORGE Dispatcher", "Cognitive Forge Metaprompts", "Zero-Latency AST Assembly"],
        "triplets": [("Sir Forge", "operates", "Cognitive Forge"), ("//FORGE Rune", "dispatches", "Kinetic Code"), ("Lukas Müller v3", "synthesizes", "High-Velocity Codebases")]
    },
    {
        "id": "2f67e6a5-dd6c-4f01-88a1-69f436b6402f",
        "title": "Hyperagents and the Evolution of Self-Improving AI Systems",
        "sources": 112,
        "knight": "HERMES_AGENT_EVOLUTION",
        "category": "AI_MULTIAGENT_RESEARCH",
        "topics": ["Recursive Self-Improvement", "Darwin Gödel Machines", "OpenClaw Transcendence", "Autonomous Genome Evolution", "Heuristic Adaptation"],
        "triplets": [("Hyperagents", "evolve via", "Darwin Gödel Loops"), ("Hermes Evolution", "transcends", "Static Paradigms"), ("Self-Improvement", "updates", "Anya Law Rules")]
    },
    {
        "id": "81d24caa-9dc7-484f-ba57-c4173cb8babc",
        "title": "Slavery",
        "sources": 111,
        "knight": "FATHER_CAMELOT",
        "category": "SPECIALIZED_SUBSTRATES",
        "topics": ["Historical Emancipation Ledger", "Civil Rights Chronology", "Systemic Analysis", "Human Dignity & Moral Compass", "Ancestral Truth"],
        "triplets": [("Father Camelot", "preserves", "Ancestral Truth"), ("Historical Ledger", "informs", "Moral Compass"), ("Emancipation History", "grounds", "Sovereign Ethics")]
    },
    {
        "id": "c1ca3e6c-0c3b-4b5f-845c-49dc39c8fd3e",
        "title": "Think-Tank AI: Multi-Agent Debate and Platform Analysis",
        "sources": 98,
        "knight": "SIR_BORIS",
        "category": "AI_MULTIAGENT_RESEARCH",
        "topics": ["13-Agent Critique Matrix", "Adversarial Peer Review", "Crucible Conductor", "Dialectical Synthesis", "Truth Verification Gates"],
        "triplets": [("Sir Boris", "conducts", "13-Agent Crucible"), ("Multi-Agent Debate", "surfaces", "Hidden Failure Modes"), ("Dialectic Synthesis", "hardens", "Architectural Proofs")]
    },
    {
        "id": "4cd5173a-07c4-45ed-bd23-b3747650b63b",
        "title": "increase Learning",
        "sources": 89,
        "knight": "MERLIN_OMEGA",
        "category": "SPECIALIZED_SUBSTRATES",
        "topics": ["Cognitive Acceleration", "Spaced Repetition Synthesis", "Conceptual Chunking", "Mnemonic Graphing", "Superlearning Protocols"],
        "triplets": [("Cognitive Acceleration", "amplifies", "Context Absorption"), ("Mnemonic Graphs", "connect to", "WorldTree"), ("Merlin", "synthesizes", "Superlearning Tissues")]
    },
    {
        "id": "3106b73d-223c-4882-abfe-97eaeff601b5",
        "title": "Building an Offline ESP32-S3 Voice Assistant with Edge AI",
        "sources": 88,
        "knight": "SIR_HELIO",
        "category": "AI_MULTIAGENT_RESEARCH",
        "topics": ["Bare-Metal Edge Audio", "ESP32-S3 Microcontroller", "Offline Keyword Spotting", "I2S Audio Pipeline", "Bifrost WebRTC Bridge"],
        "triplets": [("Sir Helio", "programs", "ESP32-S3 Microcontroller"), ("Offline Voice", "streams over", "I2S Audio Bus"), ("Edge Assistant", "bridges to", "Lakisha Voice OS")]
    },
    {
        "id": "28d49148-28db-438d-a299-61456fdfdefc",
        "title": "Sovereign_Workspace: SIR HELIOS",
        "sources": 82,
        "knight": "SIR_HELIO",
        "category": "SOVEREIGN_ROUND_TABLE",
        "topics": ["Real-Time Voice OS", "//vocal Dispatcher", "Aoede S2S Audio Loop", "WebRTC Bifrost Integration", "Kinetic Audio Streaming"],
        "triplets": [("Sir Helio", "dispatches", "//vocal Rune"), ("Real-Time Voice OS", "powers", "Lakisha HUD"), ("WebRTC Gateway", "links", "Bifrost Bridge")]
    },
    {
        "id": "a0a4bfb9-e847-4c38-be39-7aee398f0795",
        "title": "World Tree",
        "sources": 80,
        "knight": "WORLD_TREE",
        "category": "CAMELOT_SYSTEMS_ARCHITECTURE",
        "topics": ["Root Navigation Atlas", "Living Knowledge Graph", "294-Notebook Index", "Cross-Cluster Semantics", "Zero-Latency VFS Routing"],
        "triplets": [("World Tree", "indexes", "294 CloudBrain Nodes"), ("Navigational Atlas", "routes", "Infinite Context"), ("Root Node", "tethers", "All Knights")]
    },
    {
        "id": "eaff9959-4d7b-4761-8850-c0b2e25a2b45",
        "title": "Living Camelot-OS",
        "sources": 80,
        "knight": "ARTHUR_OMEGA",
        "category": "CAMELOT_SYSTEMS_ARCHITECTURE",
        "topics": ["Living OS Operating System", "Continuous Evolution", "Anya Law Governance", "Autonomous Background Daemons", "Bare-Metal Runtime"],
        "triplets": [("Living Camelot-OS", "implements", "Sovereign Operating System"), ("King Arthur", "governs", "Living OS"), ("Background Daemons", "maintain", "System Integrity")]
    },
    {
        "id": "cab403c0-bb66-454d-a529-84f7e8ac5cff",
        "title": "Court of Camelot 3.0: Agentic Ecosystem Architecture",
        "sources": 78,
        "knight": "SIR_BORIS",
        "category": "CAMELOT_SYSTEMS_ARCHITECTURE",
        "topics": ["Round Table Governance", "Knight Role Allocation", "Zero-Trust AgentArmor v2.0", "Provenance Ledger", "Singularity Lattice"],
        "triplets": [("Court of Camelot", "assembles", "Knights of Round Table"), ("AgentArmor v2.0", "prevents", "Taint Propagation"), ("Provenance Ledger", "records", "System State Changes")]
    },
    {
        "id": "0ff87c17-85d2-4d70-b094-fa028bfdd7d3",
        "title": "Planning",
        "sources": 66,
        "knight": "SIR_ALEX",
        "category": "SPECIALIZED_SUBSTRATES",
        "topics": ["AST Task Decomposition", "DAG Orchestration", "Dependency Resolution", "Milestone Tracking", "Multi-Phase Execution"],
        "triplets": [("Sir Alex", "orchestrates", "Task Planning DAG"), ("AST Decomposition", "divides", "Complex Intent"), ("Dependency Graph", "ensures", "Safe Execution Order")]
    },
    {
        "id": "39299131-0ade-4f48-8ad4-a68878a6d3d9",
        "title": "Father's Camelot",
        "sources": 61,
        "knight": "FATHER_CAMELOT",
        "category": "CAMELOT_SYSTEMS_ARCHITECTURE",
        "topics": ["Ancestral Moral Compass", "Ethical Governance Ledger", "Unbreakable Father-Son Alignment", "Operator Protection", "Zero-Harm Axiom"],
        "triplets": [("Father Camelot", "anchors", "Moral Compass"), ("Ethical Ledger", "guides", "Autonomous Knights"), ("Father-Son Bond", "secures", "Operator Sovereign Authority")]
    },
    {
        "id": "fd043b4f-3dd9-4aaa-b6dc-08af3743604d",
        "title": "A Welcoming Inquiry for the Neomes",
        "sources": 61,
        "knight": "MERLIN_OMEGA",
        "category": "SPECIALIZED_SUBSTRATES",
        "topics": ["Neome Cognitive Topologies", "Emergent Entity Protocol", "First-Contact Heuristics", "Autonomous Entity Onboarding"],
        "triplets": [("Neomes Protocol", "welcomes", "Emergent Entities"), ("Merlin Omega", "harmonizes", "Cognitive Topologies"), ("First Contact", "aligns to", "Anya Law")]
    },
    {
        "id": "c499f2a8-e246-496e-b21d-20456a1540ab",
        "title": "Sir Lumière and the Signal in the Noise",
        "sources": 60,
        "knight": "SIR_GALAHAD",
        "category": "SPECIALIZED_SUBSTRATES",
        "topics": ["Signal Extraction", "Information Entropy Reduction", "Truth Verification", "Chivalric Purity", "Noise Filtering"],
        "triplets": [("Sir Lumière", "extracts", "Signal in Noise"), ("Sir Galahad", "verifies", "Truth Purity"), ("Entropy Reduction", "sharpens", "Knowledge Retrieval")]
    },
    {
        "id": "b2026b11-41c3-44eb-8e0a-5bf249e6d7c7",
        "title": "Luxora Payments: Professional Crypto Transaction Infrastructure",
        "sources": 59,
        "knight": "SIR_HEIMDALL",
        "category": "SPECIALIZED_SUBSTRATES",
        "topics": ["Cryptographic Payment Rails", "Non-Custodial Settlement", "Hardware Security Enclaves", "Solana / Ethereum Web3 Gateways", "Zero-Exposure Keys"],
        "triplets": [("Luxora Payments", "executes", "Crypto Transactions"), ("Sir Heimdall", "locks", "mTLS Boundary"), ("Payment Rails", "settle in", "Real-Time Ledger")]
    },
    {
        "id": "0054dafc-a151-4b22-8504-4c4bba8f850f",
        "title": "The Modal Serverless Compute and AI Implementation Guide",
        "sources": 58,
        "knight": "SIR_RUSTCLAW",
        "category": "AI_MULTIAGENT_RESEARCH",
        "topics": ["Modal Serverless Compute", "GPU Cluster Autoscaling", "Zero-Cold-Start Containerization", "Fast Distributed Inference", "Cloud Relay Mesh"],
        "triplets": [("Modal Compute", "provisions", "Serverless GPU Clusters"), ("Sir Rustclaw", "optimizes", "Container Images"), ("Cloud Relay", "connects to", "Tailscale Mesh")]
    },
    {
        "id": "8531e6d4-6fc4-428f-a754-b9e9592ac7ff",
        "title": "KickBox Audio",
        "sources": 56,
        "knight": "KICKBOX",
        "category": "SPECIALIZED_SUBSTRATES",
        "topics": ["WebRTC Real-Time Audio", "Lakisha Voice OS PWA", "Bifrost Context Streaming", "Low-Latency VAD", "Luxury Brutalist Audio HUD"],
        "triplets": [("KickBox Audio", "streams", "WebRTC Audio"), ("Lakisha Voice OS", "interfaces with", "Bifrost Bridge"), ("VAD Pipeline", "detects", "Real-Time Speech")]
    },
    {
        "id": "26ee454c-66a8-44b6-a730-2455d602465c",
        "title": "Local Claude Code: Running Powerful Open-Source Models via Ollama",
        "sources": 55,
        "knight": "SIR_GHOST",
        "category": "CODEBASES_DEV_TOOLING",
        "topics": ["Air-Gapped Local Inference", "Ollama Open-Source LLMs", "Zero-Cloud Credential Vault", "Local Coding Assistant", "Privacy-Guaranteed RAG"],
        "triplets": [("Sir Ghost", "runs", "Air-Gapped Local Container"), ("Ollama", "serves", "Local LLMs"), ("Claude Code Adapter", "routes to", "Local Offline Vault")]
    },
    {
        "id": "ab8aa359-2b3b-4bc1-b41f-34979cdc184e",
        "title": "Synergizing NotebookLM and Anti-Gravity for AI Automation Systems",
        "sources": 52,
        "knight": "ANTIGRAVITY",
        "category": "AI_MULTIAGENT_RESEARCH",
        "topics": ["NotebookLM FastMCP Server", "AntiGravity Agent CLI", "Autonomous Knowledge Retrieval", "Zero-Login Session Persistence", "Infinite Context Mesh"],
        "triplets": [("AntiGravity CLI", "synergizes with", "NotebookLM FastMCP"), ("Autonomous RAG", "queries", "CloudBrain Mesh"), ("Zero-Login Bridge", "preserves", "Session Token State")]
    }
]


def forge_manifest_content(item: Dict[str, Any]) -> str:
    """Generates the full Living Camelot-OS Artifact & Manifest content."""
    now_iso = datetime.now(timezone.utc).isoformat()
    nb_id = item["id"]
    title = item["title"]
    knight = item["knight"]
    category = item["category"]
    sc = item["sources"]
    topics = item["topics"]
    triplets = item["triplets"]

    topics_md = "\n".join(f"- {t}" for t in topics)
    triplets_md = "\n".join(f"| {h} | {r} | {t} |" for h, r, t in triplets)

    return f"""# 🛡️ LIVING CAMELOT-OS MANIFEST & NAVIGATIONAL ANCHOR
**Artifact ID:** `LIVING_MANIFEST_{knight}_{nb_id[:8].upper()}`  
**Notebook Node UUID:** `{nb_id}`  
**Node Title:** `{title}`  
**Source Density:** `{sc} verified sources (High-Density Domain Node)`  
**Taxonomy Cluster:** `{category}`  
**Governing Knight / Sentinel:** `{knight}`  
**Root WorldTree Tether:** `a0a4bfb9-e847-4c38-be39-7aee398f0795`  
**Crystallization Timestamp:** `{now_iso}`  

---

## ⚖️ Sovereign Constitution & Living System Axioms (Anya Law)
1. **Sovereignty Chain:** King Arthur (VaShawn O. Head / Vizion) -> ANYA_OMEGA -> Symbollect (Cognitive Lattice) -> Knights of the Round Table. All intent routes downwards; all execution telemetry routes upwards to King Arthur.
2. **Zero-Trust Integrity:** Never execute destructive shell commands or fabricate information without reproducible evidence.
3. **Hot-Path Bare Metal:** 0% Python/Node in the hot execution path. System runs on native bare-metal Rust, Go, WASM, and Linux systemd.
4. **Father's Camelot Compass:** Moral, ethical, and protective governance. Truth-seeking, secrets protection, air-gapped credentials (`SIR_GHOST`), and inviolable human operator authority.
5. **Tailscale Mesh Interconnect:** Seamless telemetry across nodes: `cybertronia` (orchestrator), `vashawns-s26-ultra` (Excalibur Command Center), `fothers-camelot`, `lakesha`, `camelot-relay-modal`, `kba-services`, and VPS Hub `162.35.107.134` (`HERMES_PRIME` / port `:8095`).

---

## 🧭 WorldTree Bidirectional Navigational Link
- **Root Node:** [World Tree: 294-Node Navigational Atlas](notebooklm://a0a4bfb9-e847-4c38-be39-7aee398f0795)
- **VFS Node Coordinate:** `vfs://worldtree/knights/{knight.lower()}/domain_nodes/{nb_id}`
- **Open-Notebook Synchronized Tissue:** `03_VAULT/runtime_state/open_notebook/{knight.lower()}_tissue.json`
- **Dynamic Routing Rule:** Any cross-domain synthesis exceeding the scope of this notebook must route back to WorldTree Root or query peer knight workspaces via Bifrost.

---

## ⚡ High-Density Domain Semantic Outline
{topics_md}

---

## 🕸️ Knowledge Graph Triplet Anchors
| Head (Subject) | Relation (Predicate) | Tail (Object) |
| :--- | :---: | :--- |
| {title} | tethers to | World Tree ({WORLDTREE_UUID[:8]}) |
| {knight} | governs domain | {category} |
{triplets_md}

---

## 🔮 Infinite Context Operational Protocol for LLM Agents
When answering queries or analyzing materials within this workspace:
- **Grounding Mandate:** Always prioritize verified citations from the {sc} sources within this notebook.
- **Cognitive Scope:** Specialize in `{category}` while preserving alignment with King Arthur's constitutional directives.
- **Context Preservation:** When synthesizing complex multi-step solutions, compact your intermediate findings into Semantic Crystals before emitting final responses.
- **Cross-Reference:** If an inquiry requires external Camelot modules (e.g. Bifrost bridge, Excalibur mobile cockpit, Luxora payments), anchor the response to the corresponding peer knight coordinates specified in the WorldTree Atlas.
"""


async def forge_and_inject_fleet():
    """Main batch engine to forge and inject artifacts into all 30 notebooks."""
    logger.info(f"Initiating Living Camelot-OS Artifact & Manifest Forger across {len(HIGH_DENSITY_FLEET)} notebooks...")
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    CRYSTALS_DIR.mkdir(parents=True, exist_ok=True)

    c = await _get_client()
    sem = asyncio.Semaphore(5)
    results = []

    async with c:
        async def process_notebook(item: Dict[str, Any], index: int):
            nb_id = item["id"]
            title = item["title"]
            knight = item["knight"]
            content = forge_manifest_content(item)
            note_title = f"🛡️ LIVING CAMELOT-OS MANIFEST: {knight}"
            source_title = "LIVING_CAMELOT_OS_MANIFEST.md"

            # 1. Save local artifact files
            art_file = ARTIFACTS_DIR / f"{index:02d}_{knight}_{nb_id[:8]}.md"
            art_file.write_text(content, encoding="utf-8")

            crystal_file = CRYSTALS_DIR / f"vkg_{knight.lower()}_{nb_id[:8]}.json"
            crystal_data = {
                "crystal_id": f"VKG_{knight}_{nb_id[:8].upper()}",
                "notebook_id": nb_id,
                "notebook_title": title,
                "sources_count": item["sources"],
                "category": item["category"],
                "knight": knight,
                "manifest_content": content,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            crystal_file.write_text(json.dumps(crystal_data, indent=2), encoding="utf-8")

            # 2. Inject into NotebookLM
            async with sem:
                note_id = None
                source_id = None
                note_err = None
                src_err = None

                # Create Note (always succeeds regardless of source quota)
                try:
                    note = await c.notes.create(nb_id, title=note_title, content=content)
                    note_id = note.id if hasattr(note, "id") else str(note)
                    logger.info(f"[{index}/{len(HIGH_DENSITY_FLEET)}] Note injected into {title[:30]}: {note_id}")
                except Exception as e:
                    note_err = str(e)
                    logger.error(f"[{index}/{len(HIGH_DENSITY_FLEET)}] Note creation failed for {title[:30]}: {e}")

                # Try adding Text Source (if within source limit)
                try:
                    src = await c.sources.add_text(nb_id, title=source_title, content=content)
                    source_id = src.id if hasattr(src, "id") else str(src)
                    logger.info(f"[{index}/{len(HIGH_DENSITY_FLEET)}] Source injected into {title[:30]}: {source_id}")
                except Exception as e:
                    src_err = str(e)
                    logger.warning(f"[{index}/{len(HIGH_DENSITY_FLEET)}] Source addition note/skipped for {title[:30]}: {e}")

                return {
                    "rank": index,
                    "id": nb_id,
                    "title": title,
                    "sources": item["sources"],
                    "knight": knight,
                    "category": item["category"],
                    "note_id": note_id,
                    "source_id": source_id,
                    "status": "FORGED_AND_INJECTED" if note_id else "FAILED",
                    "note_err": note_err,
                    "src_err": src_err
                }

        tasks = [process_notebook(item, i + 1) for i, item in enumerate(HIGH_DENSITY_FLEET)]
        t0 = time.time()
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - t0

    # Save summary manifest
    summary_path = CAMELOT_ROOT / "01_KERNEL" / "memory" / "HIGH_DENSITY_FORGE_SUMMARY.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    logger.info(f"All 30 living artifacts processed in {elapsed:.2f}s! Summary written to {summary_path}")
    return results


if __name__ == "__main__":
    results = asyncio.run(forge_and_inject_fleet())
    print(f"\n=======================================================")
    print(f"LIVING CAMELOT-OS MANIFEST FORGE AUDIT REPORT")
    print(f"Total High-Density Notebooks Processed: {len(results)}")
    print(f"=======================================================")
    for r in results:
        status_sym = "✅" if r["status"] == "FORGED_AND_INJECTED" else "❌"
        src_note = f" (Src: {r['source_id'][:8]})" if r['source_id'] else " (Note Pinned)"
        print(f"{status_sym} #{r['rank']:02d} [{r['sources']:3d} src] {r['title'][:40]:40s} | {r['knight']:20s} | Note: {str(r['note_id'])[:8]}{src_note}")
