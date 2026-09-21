# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Cloudbrain MCP Server
r"""
Cloudbrain Model Context Protocol (MCP) Server.
Exposes Camelot OS Worldtree Cloudbrain nodes (NotebookLM) to Antigravity CLI,
Claude Code, and any MCP-compliant agent harness.
"""

import sys
from pathlib import Path

CAMELOT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(CAMELOT_ROOT))
sys.path.insert(0, str(CAMELOT_ROOT / "01_KERNEL"))
sys.path.insert(0, str(CAMELOT_ROOT / "vfs"))

from mcp.server.fastmcp import FastMCP
from memory.cloudbrain_connector import (
    CloudBrainConnector,
    KNIGHT_NOTEBOOKS,
    NOTEBOOK_DOMAIN_TAGS,
    list_all_notebooks,
    route_by_domain,
    batch_query,
)
from vfs.notebooklm_client import (
    NOTEBOOKLM_AVAILABLE,
    query_notebook_async,
    push_note_async,
    push_source_async,
)
from control_plane.memcastle import MemCastle
from control_plane.graphify import extract_triplets
from memory.graphiti_engine import KnightGraphitiEngine

mcp_server = FastMCP("camelot-cloudbrain")


@mcp_server.tool()
def list_cloudbrains() -> list[dict]:
    """List all registered Camelot Worldtree Cloudbrain nodes and their active NotebookLM UUUDs."""
    return list_all_notebooks()


@mcp_server.tool()
def route_cloudbrain_by_domain(keywords: list[str]) -> list[str]:
    """Find the best Cloudbrain nodes for a task using keyword routing."""
    return route_by_domain(keywords)


@mcp_server.tool()
async def query_cloudbrain(knight_id: str, question: str) -> str:
    """Query a specific Knight Cloudbrain node (eg SIR_BORIS, HERMES_PRIME, BIO_KINETIC_SWARM, ANYA_OMEGA)."""
    kid = knight_id.upper()
    if NOTEBOOKLM_AVAILABLE:
        try:
            answer = await query_notebook_async(kid, question)
            if answer:
                return answer
        except Exception:
            pass
    connector = CloudBrainConnector(knight_id=kid)
    answer = connector.query_notebook(question)
    if answer:
        return answer
    return f"No response or notebook not queryable for node: {kid}"


@mcp_server.tool()
async def push_cloudbrain_note(knight_id: str, title: str, content: str) -> str:
    """Push an artifact or operational note to a Knight Cloudbrain node and local Open-Notebook tissue."""
    kid = knight_id.upper()
    connector = CloudBrainConnector(knight_id=kid)
    connector._sync_open_notebook_local("note", title, content)
    ok = False
    if NOTEBOOKLM_AVAILABLE:
        try:
            ok = await push_note_async(kid, title, content)
        except Exception:
            pass
    if not ok:
        ok = connector.push_to_notebook(artifact_type="note", content=content, title=title)
    if ok:
        return f"Successfully pushed note '{title}' to {kid} Cloudbrain."
    return f"Local tissue mirrored, but remote NotebookLM push skipped/failed for {kid}."


@mcp_server.tool()
async def push_cloudbrain_source(knight_id: str, title: str, content: str) -> str:
    """Push a full text source or code artifact to a Knight Cloudbrain notebook."""
    kid = knight_id.upper()
    connector = CloudBrainConnector(knight_id=kid)
    connector._sync_open_notebook_local("source", title, content)
    ok = False
    if NOTEBOOKLM_AVAILABLE:
        try:
            ok = await push_source_async(kid, title, content)
        except Exception:
            pass
    if not ok:
        ok = connector.push_to_notebook(artifact_type="source", content=content, title=title)
    if ok:
        return f"Successfully pushed source '{title}' to {kid} Cloudbrain."
    return f"Local tissue mirrored, but remote NotebookLM source upload skipped/failed for {kid}."


@mcp_server.tool()
def memcastle_store(text: str, source: str = "mcp", knight: str = "SIR_MNEMO") -> str:
    """Store text and semantic embedding into Tier-2 MemCastle (sqlite-vec KNN)."""
    mc = MemCastle()
    try:
        row_id = mc.store(text=text, source=source, knight=knight)
        return f"Stored into MemCastle (Row ID: {row_id}, Knight: {knight})"
    finally:
        mc.close()


@mcp_server.tool()
def memcastle_search(query: str, k: int = 5) -> list[dict]:
    """Search Tier-2 MemCastle vector database using sqlite-vec KNN search."""
    mc = MemCastle()
    try:
        results = mc.search(query=query, k=k)
        return results
    finally:
        mc.close()


@mcp_server.tool()
def graphify_extract(text: str) -> list[dict]:
    """Extract semantic (subject, predicate, object) triplets from text using Graphify."""
    triplets = extract_triplets(text)
    return [{"head": t.head, "relation": t.relation, "tail": t.tail} for t in triplets]


@mcp_server.tool()
def assimilation_status() -> dict:
    """Return status of assimilated intelligence, memory layers, and CloudBrain integrations."""
    return {
        "tier_1_context": "Ouroboros WAL / In-Memory Session",
        "tier_2_vector": "MemCastle sqlite-vec + Graphify NLP Triplet Extractor",
        "tier_3_cloudbrain": "WorldTree VFS (open_viking://) + NotebookLM CloudBrain",
        "assimilated_components": [
            "Understand-Anything (Codebase Knowledge Graph & AST Flow)",
            "book-to-skill (Procedural Technical Document to Agent Skill)",
            "codebase-memory-mcp (Photographic AST & Dependency Graph)",
            "notebooklm-py (Async NotebookLM Client Substrate)",
            "anything-to-notebooklm (Multi-Source Document & Media Preprocessor)",
            "notebooklm-mcp (FastMCP CloudBrain Citation & Query Server)"
        ],
        "qdrant_rest_cluster": "https://2b135578-55c5-43d0-b82a-f5061f4ff6ee.us-east4-0.gcp.cloud.qdrant.io",
        "status": "ASSIMILATED_ACTIVE",
    }


@mcp_server.tool()
def graphiti_query(knight_id: str, entity_name: str, limit: int = 25) -> dict:
    """Query a Knight's Graphiti temporal knowledge graph for targeted entity subgraphs, reducing token consumption."""
    engine = KnightGraphitiEngine(knight_id=knight_id)
    return engine.query_subgraph(entity_name=entity_name, limit=limit)


@mcp_server.tool()
def graphiti_add_fact(
    knight_id: str,
    subject: str,
    predicate: str,
    object_: str,
    source: str = "mcp",
) -> str:
    """Add a temporal fact triplet to a Knight's Graphiti knowledge graph."""
    engine = KnightGraphitiEngine(knight_id=knight_id)
    fact_id = engine.add_fact(subject=subject, predicate=predicate, object_=object_, source=source)
    return f"Fact {fact_id} added to {knight_id.upper()} Graphiti knowledge graph."


@mcp_server.tool()
def graphiti_stats(knight_id: str) -> dict:
    """Get entity, fact count, and database size for a Knight's Graphiti knowledge graph."""
    engine = KnightGraphitiEngine(knight_id=knight_id)
    return engine.stats()


@mcp_server.tool()
def cloudbrain_status() -> dict:
    """Check the health and integration status of NotebookLM and Worldtree Cloudbrain."""
    return {
        "notebooklm_library_available": NOTEBOOKLM_AVAILABLE,
        "registered_nodes_count": len(KNIGHT_NOTEBOOKS),
        "active_uuid_nodes_count": len(list_all_notebooks()),
        "auth_state_exists": Path(r"C:\Users\vizio\.notebooklm\storage_state.json").exists(),
        "graphiti_engine_partitioned_knights": len(KNIGHT_NOTEBOOKS),
    }


@mcp_server.tool()
def excalibur_mobile_scrcpy_command(
    device_ip: str = "100.106.246.126:5555",
    bitrate_mbps: int = 8,
    audio_opus: bool = True,
) -> str:
    """Generate the native scrcpy low-latency command for Excalibur Command Center (S26 Ultra)."""
    audio_flag = "--audio-codec=opus" if audio_opus else "--no-audio"
    return f"scrcpy -s {device_ip} --video-bit-rate {bitrate_mbps}M --max-fps 60 {audio_flag}"


@mcp_server.tool()
def excalibur_adb_tap(x: int, y: int, device_ip: str = "100.106.246.126:5555") -> str:
    """Inject a tap touch action into the Excalibur mobile sentinel via ADB over Tailscale."""
    import subprocess
    cmd = ["adb", "-s", device_ip, "shell", "input", "tap", str(x), str(y)]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return f"Tap at ({x}, {y}) dispatched to {device_ip}. Exit: {res.returncode}"
    except Exception as e:
        return f"Tap failed: {e}"


@mcp_server.tool()
def get_notebook_manifest() -> dict:
    """Get the master NotebookLM WorldTree Manifest summary across all 294 nodes and 7 categories."""
    try:
        from merlin.context.merlin_infinite_context import merlin_context
        return {
            "version": merlin_context.manifest.get("version", "2.0.0"),
            "total_notebooks": merlin_context.manifest.get("total_notebooks", 294),
            "worldtree_root_uuid": merlin_context.manifest.get("worldtree_root_uuid"),
            "categories": merlin_context.manifest.get("categories", []),
            "active_sovereign_knights": len(KNIGHT_NOTEBOOKS),
        }
    except Exception as e:
        return {"error": str(e), "total_knights": len(KNIGHT_NOTEBOOKS)}


@mcp_server.tool()
def route_by_manifest(intent_or_query: str) -> dict:
    """Route an intent or query using Merlin Infinite Context Engine across the 294 NotebookLM Manifest."""
    try:
        from merlin.context.merlin_infinite_context import merlin_context
        category, knight_id, notebook_uuid = merlin_context.categorize_intent(intent_or_query)
        meta = merlin_context.manifest.get("notebooks", {}).get(notebook_uuid, {})
        return {
            "intent": intent_or_query,
            "recommended_category": category,
            "recommended_knight": knight_id,
            "target_notebook_uuid": notebook_uuid,
            "notebook_title": meta.get("title", "Unknown"),
            "anchor_tether": meta.get("anchor_tether", "a0a4bfb9-e847-4c38-be39-7aee398f0795"),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp_server.tool()
def crystallize_infinite_context(
    raw_text: str,
    title: str,
    category: str = "",
    target_knight: str = "",
) -> dict:
    """Crystallize arbitrary text using Merlin Infinite Context Engine with living system instructions."""
    try:
        from merlin.context.merlin_infinite_context import merlin_context
        cat = category if category else None
        kid = target_knight.upper() if target_knight else None
        crystal = merlin_context.crystallize(
            raw_text=raw_text,
            title=title,
            category_override=cat,
            target_knight=kid,
        )
        return {
            "crystal_id": crystal.crystal_id,
            "category": crystal.category,
            "target_knight": crystal.target_knight,
            "target_notebook_uuid": crystal.target_notebook_uuid,
            "l0_flash_summary": crystal.l0_flash_summary,
            "l1_semantic_outline": crystal.l1_semantic_outline,
            "l2_triplets_count": len(crystal.l2_knowledge_triplets),
            "full_markdown_length": len(crystal.full_markdown_source),
            "created_at": crystal.created_at,
        }
    except Exception as e:
        return {"error": str(e)}


@mcp_server.tool()
def omni_s2s_turn(
    prompt: str = "Fortress status report",
    knight_id: str = "reya_companion",
    channel_name: str = "camelot_omni_s2s",
    chunked: bool = True,
) -> dict:
    """Execute real-time Omni S2S speech turn using RadixAttention KV cache and Agora SD-RTN."""
    s2s_dir = CAMELOT_ROOT / "02_FORGE" / "assimilation" / "omni_s2s"
    if str(s2s_dir) not in sys.path:
        sys.path.insert(0, str(s2s_dir))
    try:
        from omni_s2s_engine import get_omni_s2s_engine
        import math
        import struct

        engine = get_omni_s2s_engine()
        samples = [int(1500 * math.sin(2 * math.pi * 220 * i / 16000)) for i in range(8000)]
        pcm_bytes = struct.pack(f"<{len(samples)}h", *samples)

        if chunked:
            chunks = [pcm_bytes[i:i + 3200] for i in range(0, len(pcm_bytes), 3200)]
            res = engine.process_chunked_speech_turn(
                chunks, transcript_hint=prompt, knight_id=knight_id, enable_speculative_decode=True
            )
        else:
            res = engine.process_speech_turn(pcm_bytes, transcript_hint=prompt, knight_id=knight_id)
        return res.to_dict()
    except Exception as e:
        return {"error": str(e), "status": "OMNI_S2S_ERROR"}


@mcp_server.tool()
def omni_s2s_status() -> dict:
    """Return status of RadixAudioCache, Agora RTC transport, and shared memory slabs."""
    s2s_dir = CAMELOT_ROOT / "02_FORGE" / "assimilation" / "omni_s2s"
    if str(s2s_dir) not in sys.path:
        sys.path.insert(0, str(s2s_dir))
    try:
        from omni_s2s_engine import get_omni_s2s_engine

        engine = get_omni_s2s_engine()
        return {
            "radix_cache": engine.radix_cache.get_stats(),
            "agora_rtc": engine.agora_bridge.get_stats(),
            "turns_completed": engine.turn_counter,
            "shm_slab": engine.agora_bridge.shm_slab_path,
            "status": "OMNI_S2S_OPERATIONAL",
        }
    except Exception as e:
        return {"error": str(e), "status": "OMNI_S2S_ERROR"}


@mcp_server.tool()
def read_glass_observatory(view_type: str = "all") -> dict:
    """Read the impenetrable Glass Observatory (transcripts, RPG leaderboard, evaluations, and compendium path)."""
    try:
        from control_plane.observatory.glass_observatory import get_glass_observatory
        obs = get_glass_observatory()
        return obs.get_glass_wall_view(view_type=view_type)
    except Exception as e:
        return {"error": str(e), "status": "OBSERVATORY_ERROR"}


@mcp_server.tool()
def magsafe_process_audio(
    audio_path: str,
    target_knight: str = "SIR_HELIOS",
    tenant_id: str = "Vizion Sky",
    auto_dispatch: bool = False,
) -> dict:
    """Ingest MagSafe voice recording, perform SecondBrain summarization, tap Glass Observatory, and dispatch kinetic actions."""
    import importlib.util
    bridge_path = CAMELOT_ROOT / "02_FORGE" / "assimilation" / "magsafe" / "magsafe_audio_bridge.py"
    spec = importlib.util.spec_from_file_location("magsafe_audio_bridge", str(bridge_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        bridge = mod.get_magsafe_bridge()
        res = bridge.process_audio_file(
            audio_file_path=audio_path,
            target_knight=target_knight,
            tenant_id=tenant_id,
            auto_dispatch=auto_dispatch,
        )
        return res.to_dict()
    return {"error": "Failed to load magsafe_audio_bridge", "status": "MAGSAFE_ERROR"}


@mcp_server.tool()
def magsafe_status() -> dict:
    """Return status of MagSafe Audio Sentinel, cgroups memory ceiling (<350MB), and Glass Observatory tap."""
    import importlib.util
    bridge_path = CAMELOT_ROOT / "02_FORGE" / "assimilation" / "magsafe" / "magsafe_audio_bridge.py"
    spec = importlib.util.spec_from_file_location("magsafe_audio_bridge", str(bridge_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        bridge = mod.get_magsafe_bridge()
        return {
            "status": "ARMED_AND_ACTIVE",
            "memory_ceiling_mb": bridge.cgroups_memory_max_mb,
            "recorded_sessions": len(bridge.get_sessions()),
            "glass_observatory_tap": "ACTIVE" if mod.get_glass_observatory is not None else "INACTIVE",
            "reya_fabric_layer": "ACTIVE" if mod.get_reya_fabric is not None else "INACTIVE",
            "handshake_gate": "ACTIVE" if mod.get_handshake_gate is not None else "INACTIVE",
        }
    return {"error": "Failed to load magsafe_audio_bridge", "status": "MAGSAFE_ERROR"}


@mcp_server.tool()
def freellmapi_chat(
    prompt: str,
    model: str = "auto",
    system_prompt: str = "You are a helpful sovereign intelligence assistant in Camelot-OS.",
    calling_knight: str = "SIR_HELIOS",
) -> dict:
    """Execute zero-cost chat completion via FreeLLMAPI multi-provider gateway. Strictly rejects secrets."""
    import importlib.util
    bridge_path = CAMELOT_ROOT / "02_FORGE" / "assimilation" / "freellmapi" / "freellmapi_bridge.py"
    spec = importlib.util.spec_from_file_location("freellmapi_bridge", str(bridge_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        bridge = mod.get_freellmapi_bridge()
        try:
            resp = bridge.chat_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                calling_knight=calling_knight,
            )
            return resp.to_dict()
        except mod.SecretSanitizationViolation as e:
            return {"error": str(e), "status": "SECRET_FENCE_TRIGGERED"}
        except Exception as e:
            return {"error": str(e), "status": "DISPATCH_ERROR"}
    return {"error": "Failed to load freellmapi_bridge", "status": "MODULE_LOAD_ERROR"}


@mcp_server.tool()
def freellmapi_status() -> dict:
    """Query live status of FreeLLMAPI zero-cost pooled gateway."""
    import importlib.util
    bridge_path = CAMELOT_ROOT / "02_FORGE" / "assimilation" / "freellmapi" / "freellmapi_bridge.py"
    spec = importlib.util.spec_from_file_location("freellmapi_bridge", str(bridge_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        bridge = mod.get_freellmapi_bridge()
        alive, msg = bridge.is_alive()
        return {
            "status": "ONLINE" if alive else "STANDBY",
            "base_url": bridge.base_url,
            "gateway_message": msg,
            "observatory_tap": "ENABLED" if bridge.enable_observatory_tap else "DISABLED",
            "curated_model_count": len(mod.FREE_MODEL_CATALOG),
        }
    return {"error": "Failed to load freellmapi_bridge", "status": "MODULE_LOAD_ERROR"}


@mcp_server.tool()
def freellmapi_list_models() -> list[dict]:
    """List all available free LLM models from FreeLLMAPI gateway or curated fallback catalog."""
    import importlib.util
    bridge_path = CAMELOT_ROOT / "02_FORGE" / "assimilation" / "freellmapi" / "freellmapi_bridge.py"
    spec = importlib.util.spec_from_file_location("freellmapi_bridge", str(bridge_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        bridge = mod.get_freellmapi_bridge()
        return bridge.list_models()
    return []


@mcp_server.tool()
def omniroute_compress_prompt(text: str, mode: str = "rtk_caveman") -> dict:
    """Compress prompt using RTK + Caveman stacked compression (saving 15-95% tokens)."""
    import importlib.util
    bridge_path = CAMELOT_ROOT / "02_FORGE" / "assimilation" / "omniroute" / "omniroute_bridge.py"
    spec = importlib.util.spec_from_file_location("omniroute_bridge", str(bridge_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod.RTKCavemanCompressor.compress(text, mode=mode)
    return {"error": "Failed to load omniroute_bridge"}


@mcp_server.tool()
def omniroute_status() -> dict:
    """Return status of OmniRoute (:20128) and 9router-go (:3002) gateways and routing strategies."""
    import importlib.util
    bridge_path = CAMELOT_ROOT / "02_FORGE" / "assimilation" / "omniroute" / "omniroute_bridge.py"
    spec = importlib.util.spec_from_file_location("omniroute_bridge", str(bridge_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        bridge = mod.get_omniroute_bridge()
        return bridge.check_gateways()
    return {"error": "Failed to load omniroute_bridge"}


@mcp_server.tool()
def bitrouter_evaluate_loop(
    loop_id: str,
    task: str,
    knight_id: str = "SIR_CODEX",
    added_tokens: int = 0,
    added_cost: float = 0.0,
    step_type: str = "tool_call",
) -> dict:
    """Evaluate agent loop iteration and tighten model tier to prevent tokenmaxxing."""
    import importlib.util
    bridge_path = CAMELOT_ROOT / "02_FORGE" / "assimilation" / "bitrouter" / "bitrouter_guardrails.py"
    spec = importlib.util.spec_from_file_location("bitrouter_guardrails", str(bridge_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        engine = mod.get_bitrouter_engine()
        state = engine.start_or_update_loop(
            loop_id=loop_id,
            task=task,
            knight_id=knight_id,
            added_tokens=added_tokens,
            added_cost=added_cost,
            step_type=step_type,
        )
        return state.to_dict()
    return {"error": "Failed to load bitrouter_guardrails"}


@mcp_server.tool()
def northstar_dispatch_goal(title: str, objective: str = "", knight: str = "MERLIN_Ω") -> dict:
    """Decompose and dispatch an autonomous Northstar Goal background worker inside a Personal CPU Sandbox."""
    import importlib.util
    engine_path = CAMELOT_ROOT / "02_FORGE" / "assimilation" / "workers" / "northstar_worker_engine.py"
    spec = importlib.util.spec_from_file_location("northstar_worker_engine", str(engine_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        engine = mod.NorthstarWorkerEngine()
        goal = engine.decompose_goal(title=title, objective=objective or title, lead_knight=knight)
        return {
            "status": "DISPATCHED",
            "goal_id": goal.goal_id,
            "worker_id": goal.worker_id,
            "lead_knight": goal.lead_knight,
            "milestones": [m.to_dict() for m in goal.milestones]
        }
    return {"error": "Failed to load northstar_worker_engine"}


@mcp_server.tool()
def northstar_worker_status(worker_id: str = "") -> dict:
    """Query active Northstar background workers, CPU/Memory telemetry, and pending HITL requests."""
    import importlib.util
    engine_path = CAMELOT_ROOT / "02_FORGE" / "assimilation" / "workers" / "northstar_worker_engine.py"
    spec = importlib.util.spec_from_file_location("northstar_worker_engine", str(engine_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        engine = mod.NorthstarWorkerEngine()
        if worker_id:
            try:
                return engine.get_worker_status(worker_id)
            except Exception as e:
                return {"error": str(e)}
        return {"workers": engine.list_all_workers()}
    return {"error": "Failed to load northstar_worker_engine"}


@mcp_server.tool()
def northstar_permission_review(
    request_id: str,
    action: str = "approve",
    operator_id: str = "Arthur_Omega",
    reason: str = "Approved via FastMCP"
) -> dict:
    """Review and approve/deny an inline HITL permission request from a sandboxed worker."""
    import importlib.util
    engine_path = CAMELOT_ROOT / "02_FORGE" / "assimilation" / "workers" / "northstar_worker_engine.py"
    spec = importlib.util.spec_from_file_location("northstar_worker_engine", str(engine_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        engine = mod.NorthstarWorkerEngine()
        if action.lower() == "approve":
            ok = engine.broker.approve(request_id, operator_id=operator_id, reason=reason)
            return {"request_id": request_id, "action": "approve", "success": ok}
        else:
            ok = engine.broker.deny(request_id, operator_id=operator_id, reason=reason)
            return {"request_id": request_id, "action": "deny", "success": ok}
    return {"error": "Failed to load northstar_worker_engine"}


if __name__ == "__main__":
    mcp_server.run()

