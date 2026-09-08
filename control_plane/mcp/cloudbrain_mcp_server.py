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
from vfs.notebooklm_client import NOTEBOOKLM_AVAILABLE
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
def query_cloudbrain(knight_id: str, question: str) -> str:
    """Query a specific Knight Cloudbrain node (eg SIR_BORIS, HERMES_PRIME, BIO_KINETIC_SWARM, ANYA_OMEGA)."""
    kid = knight_id.upper()
    connector = CloudBrainConnector(knight_id=kid)
    answer = connector.query_notebook(question)
    if answer:
        return answer
    return f"No response or notebook not queryable for node: {kid}"


@mcp_server.tool()
def push_cloudbrain_note(knight_id: str, title: str, content: str) -> str:
    """Push an artifact or operational note to a Knight Cloudbrain node and local Open-Notebook tissue."""
    kid = knight_id.upper()
    connector = CloudBrainConnector(knight_id=kid)
    ok = connector.push_to_notebook(artifact_type="note", content=content, title=title)
    if ok:
        return f"Successfully pushed note '{title}' to {kid} Cloudbrain."
    return f"Local tissue mirrored, but remote NotebookLM push skipped/failed for {kid}."


@mcp_server.tool()
def push_cloudbrain_source(knight_id: str, title: str, content: str) -> str:
    """Push a full text source or code artifact to a Knight Cloudbrain notebook."""
    kid = knight_id.upper()
    connector = CloudBrainConnector(knight_id=kid)
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


if __name__ == "__main__":
    mcp_server.run()

