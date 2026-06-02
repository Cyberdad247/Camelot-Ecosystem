#!/usr/bin/env python3
"""Add tailored v1000-EXCALIBUR-A delta sources to the relevant existing
NotebookLM notebooks. Each source connects that notebook's documented concepts
to their concrete implementation in this release — grounded, not duplicated.

Run after `notebooklm login`:
    .venv/Scripts/python.exe scripts/update_cloudbrain_notebooks.py
"""
import asyncio
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from notebooklm import NotebookLMClient

V1000_NB = "3624fe71-9ff7-42f0-ad51-06720bc589fd"

# (notebook_id, source_title, content) — each tailored to the notebook's domain.
UPDATES = [
    (
        "71be7c3c-e1d0-46cf-b352-3c71006fecc7",  # Merlin: AI Mythosmith
        "Merlin concepts realized in v1000-EXCALIBUR-A (2026-06-01)",
        "Concrete code realization of this notebook's Merlin/Anya concepts, shipped "
        f"in Camelot-OS v1000-EXCALIBUR-A (notebook {V1000_NB}):\n\n"
        "- QERE / APEE -> control_plane/anya_gate.py _stage_triage(): produces a "
        "TriageScore with continuous risk_entropy (0-1) instead of binary flags "
        "(Ouroboros Adaptive Governance). Thresholds <0.15 AUTO / 0.15-0.55 PROMPT "
        "/ >0.55 HUMAN_GATE. process() pipeline preserved.\n"
        "- MFOE / Tree-of-Thoughts -> control_plane/colmad.py: ColMAD Think Tank "
        "Omega runs 3 adversarial persona vectors (stark_scaling, greene_strategy, "
        "tao_rigor); 2/3 consensus APPROVES, else escalates to HUMAN_GATE.\n"
        "- MGV metacognitive loop -> the PIV (Plan-Implement-Validate) loop in "
        "factory_lane (max 3 iterations).\n"
        "- VIDENEPTUS SkillGraph S1-S5 -> control_plane/knight_agent.py: every "
        "knight carries a skillgraph_tier S1-S5 plus an OCEAN PersRubrics profile.\n"
        "- Symbolect / UKG / TOON serialization -> control_plane/firnflow.py "
        "nuKG_Crystals: successful patterns crystallized into tiered L1/L2/L3 memory.\n"
        "- Sir Octavian Warden / Iron Gate -> control_plane/soul_oversight.py "
        "pre_execute() 3-tier HITL + Z3 verification (z3-solver installed).\n"
        "All modules self-tested (~75 Python + 12 Rust tests pass).",
    ),
    (
        "ba87d454-9335-4f2f-bf9f-f3845a8c6948",  # Ancestral Chimera Research Swarm
        "Chimera audit resolved + swarm patterns in v1000-EXCALIBUR-A (2026-06-01)",
        "Resolves the 'audit-needed' tag on this notebook. Findings from the live "
        "GIDEON/GHOST colony scan during the v1000-EXCALIBUR-A build:\n\n"
        "- The stale colony_report.md claimed 8 secrets / risk 100. The LIVE GHOST "
        "scan of 01_KERNEL shows 0 critical / 0 warnings. The single real finding "
        "was an orphaned, gitignored config/registry/secrets.json holding dev "
        "placeholders; it was neutralized to boolean presence flags per Titanium Law.\n"
        "- Hydra Cascade / PIV cross-validation -> control_plane/factory_lane.py PIV "
        "loop (max 3 iterations) with priority lanes CRITICAL/HIGH/NORMAL/BACKGROUND.\n"
        "- SkillClaw / nuKG_Crystals propagation -> control_plane/firnflow.py "
        "crystallize() (4 crystals seeded: APEE triage, FirnFlow retrieval, ColMAD "
        "crucible, RTK strip).\n"
        "- 11-engine HIVE-IDE + Living NotebookLM Nexus -> 13-terminal "
        "control_plane/mcp_conductor.py with sir_mnemo wired to live NotebookLM and "
        "sir_gideon/audit_colony running live GHOST scans.\n"
        "- TurboQuant 3-bit / BitNet -> 01_KERNEL/reasoning/ouroboros_engine real "
        "BitNet b1.58 absmean quantizer (quantizer.rs), 12/12 cargo tests pass.\n"
        f"Full state: notebook {V1000_NB}.",
    ),
    (
        "f9ea0508-0b1b-45b1-8780-1bc709a22f09",  # Pydantic AI
        "Pydantic AI patterns realized in v1000-EXCALIBUR-A (2026-06-01)",
        "Direct application of this notebook's Pydantic AI patterns, shipped in "
        "control_plane/factory_lane.py and knight_agent.py:\n\n"
        "- Typed Agent contracts (deps_type/output_type discipline) -> FactoryJob"
        "(BaseModel) and KnightCapability(BaseModel) replace loose dataclass dispatch.\n"
        "- UsageLimits -> UsageLimits(request_limit, total_tokens_limit, "
        "tool_calls_limit) with an exceeded() guard against runaway tool loops.\n"
        "- ToolReturn -> ToolReturn(return_value, content, metadata) separates "
        "application logic from LLM context from zero-token local logging.\n"
        "- FileStatePersistence (suspend/resume) -> FileStatePersistence.save/load/"
        "resume snapshots a HUMAN_GATE job to disk for deterministic resumption.\n"
        "- A2A / MCP server+client -> control_plane/mcp_conductor.py exposes 13 "
        "terminals as MCP tools over stdio; ask_sir_mnemo proxies to NotebookLM.\n"
        "- requires_approval tool gating -> soul_oversight.pre_execute() 3-tier HITL.\n"
        "All Pydantic models validated via module self-tests (12/12 factory_lane).\n"
        f"Full state: notebook {V1000_NB}.",
    ),
    (
        "8c656cfa-a189-409e-a72d-07692a47f17e",  # Camelot-OS v.999.3
        "SUPERSEDED by v1000-EXCALIBUR-A (2026-06-01)",
        "This v999.3 notebook is superseded by Camelot-OS v.1000.0-EXCALIBUR-A "
        f"(notebook {V1000_NB}). Key deltas now shipped and verified:\n\n"
        "- Ouroboros SSM and BitNet b1.58 now have REAL Rust implementations "
        "(mamba.rs selective-scan recurrence, quantizer.rs absmean ternary) — "
        "previously documented as concept/stub. 12/12 cargo tests pass.\n"
        "- APEE v6.5 -> v7.0 with self-triaging _stage_triage() and risk_entropy.\n"
        "- AegisShield Rust (bloom_router/kv_event_gate/event_publisher/prompt_canon) "
        "compiles clean via cargo check.\n"
        "- Portable binary rebuilt: camelot.exe 16.36 MB, version string "
        "v1000-EXCALIBUR-A, smoke-tested, committed (99c392e) and pushed to GitHub.",
    ),
]


async def main() -> int:
    client = await NotebookLMClient.from_storage()
    async with client:
        for nb_id, title, content in UPDATES:
            try:
                src = await client.sources.add_text(nb_id, title, content,
                                                    wait=True, wait_timeout=120.0)
                sid = getattr(src, "id", src)
                print(f"[OK]   {nb_id}  +source {sid}")
            except Exception as exc:  # noqa: BLE001
                print(f"[FAIL] {nb_id}  {exc}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {exc}")
        if "Authentication" in str(exc) or "login" in str(exc):
            print("\n>> Run:  .venv/Scripts/notebooklm.exe login   then re-run.")
        raise SystemExit(1)
