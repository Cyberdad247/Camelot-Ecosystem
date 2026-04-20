# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from typing import List

from . import parser, registry, reporting, verification
from .types import AssimilationRequest, AssimilationResult


def assimilate_repo(
    repo_path: str,
    tags: List[str],
    origin: str = "local",
    description: str = "",
) -> AssimilationResult:
    """
    High-level Repo Assimilation pipeline for Camelot-OS.

    1) Scan & chunk repo into semantic units.
    2) Insert chunks into graph + memory stores.
    3) Register skills/guild mappings.
    4) Build Assimilation report and run verification.
    5) Append PROVENANCE ledger entry and return result.
    """

    request = AssimilationRequest(
        repo_path=repo_path,
        origin=origin,
        tags=tags,
        description=description or repo_path,
    )

    # Phase II: Harmony Gate (New in V5)
    harmony_result = verification.check_harmony(request)
    if harmony_result["status"] != "ok":
        return AssimilationResult(
            repo_path=request.repo_path,
            origin=request.origin,
            tags=request.tags,
            status="error",
            messages=harmony_result["messages"],
            # Fill other fields with empty/zero values
            files_indexed=0, chunks_created=0, graph_nodes_created=0, skills_registered=0, rag_collections=[], report_path="", ledger_entry_id=""
        )
    
    # 1. Scan & chunk via Phials / Graphrag
    scan_result = parser.scan_and_chunk_repo(request)  # wraps treesitterphial + semantictreerag
    # scan_result: { "files_indexed": int, "chunks": List[Chunk], "messages": [...] }

    # 2. Persist into graph + memory / RAG
    graph_result = registry.register_chunks_in_graph(request, scan_result)
    # graph_result: { "graph_nodes_created": int, "rag_collections": [...], "messages": [...] }

    # 3. Extract and register skills/guild bindings
    skills_result = registry.register_repo_skills(request, scan_result, graph_result)
    # skills_result: { "skills_registered": int, "messages": [...] }

    # 4. Generate human-readable assimilation report
    report_path = reporting.generate_assimilation_report(request, scan_result, graph_result, skills_result)

    # 5. Run structural verification
    verification_result = verification.run_assimilation_checks(
        request=request,
        scan_result=scan_result,
        graph_result=graph_result,
        skills_result=skills_result,
        report_path=report_path,
    )
    # verification_result: { "status": "ok" | "warn" | "fail", "messages": [...] }

    # 6. Append to PROVENANCELEDGER and/or titanledger
    ledger_entry_id = verification.commit_to_ledger(
        request=request,
        scan_result=scan_result,
        graph_result=graph_result,
        skills_result=skills_result,
        verification_result=verification_result,
        report_path=report_path,
    )

    status = "success" if verification_result["status"] == "ok" else "partial"

    messages = (
        scan_result.get("messages", [])
        + graph_result.get("messages", [])
        + skills_result.get("messages", [])
        + verification_result.get("messages", [])
    )

    return AssimilationResult(
        repo_path=request.repo_path,
        origin=request.origin,
        tags=request.tags,
        files_indexed=scan_result.get("files_indexed", 0),
        chunks_created=len(scan_result.get("chunks", [])),
        graph_nodes_created=graph_result.get("graph_nodes_created", 0),
        skills_registered=skills_result.get("skills_registered", 0),
        rag_collections=graph_result.get("rag_collections", []),
        report_path=report_path,
        ledger_entry_id=ledger_entry_id,
        status=status,
        messages=messages,
    )