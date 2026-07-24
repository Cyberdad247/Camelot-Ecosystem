# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Titan Omega Seeder Pipelines

ETL (Extract, Transform, Load) pipelines to hydrate the memory stack:
- Documents: Process text/markdown into Omega-Vault
- Graph Entities: Extract facts and agents into Omega-Graph
- Code Analysis: Index repositories into specialized graph sub-structures
"""

import hashlib
import os
from datetime import datetime
from typing import Any, Dict, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter

from .titan_omega import TitanOmega
from .titan_schemas import GraphEdge, GraphNode, GraphNodeProvenance


class TitanSeeder:
    """
    Orchestration engine for hydrating the Titan Omega memory stack.
    Handles chunking, metadata enrichment, and ingestion path routing.
    """
    
    def __init__(self, titan: TitanOmega):
        self.titan = titan
        print("[Titan-Seeder] Seeder Pipeline online")

    def seed_text_document(self, content: str, source_id: str, metadata: Optional[Dict] = None):
        """
        Process a long-form text document into Omega-Vault chunks.
        Also attempts to extract a 'Fact' node for Omega-Graph.
        """
        print(f"[Titan-Seeder] Seeding document: {source_id}")
        
        # 1. Chunking for Omega-Vault (Semantic chunking via RecursiveCharacterTextSplitter)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
        )
        raw_chunks = splitter.split_text(content)
        chunks = [c.strip() for c in raw_chunks if len(c.strip()) > 50]
        
        for i, chunk in enumerate(chunks):
            chunk_metadata = (metadata or {}).copy()
            chunk_metadata.update({"chunk_index": i, "total_chunks": len(chunks)})
            
            # Add to Vector Vault
            self.titan.vault.add_text(
                text=chunk,
                source_id=source_id,
                metadata=chunk_metadata
            )
            
        # 2. Extract and Add a Fact node to Omega-Graph
        # This is a high-level anchor for the document
        fact_id = f"fact_{hashlib.sha256(content.encode()).hexdigest()[:12]}"
        
        provenance = GraphNodeProvenance(
            created_by="TitanSeeder",
            created_at=datetime.utcnow(),
            hash="" # Will be computed
        )
        
        node = GraphNode(
            node_id=fact_id,
            type="Fact",
            attributes={
                "title": source_id,
                "summary": chunks[0][:200] if chunks else "No summary available",
                "metadata": metadata or {}
            },
            edges=[
                GraphEdge(to="STRATEGY_CORE", relationship="informs", weight=0.8) # Default link
            ],
            provenance=provenance,
            trust_score=1.0,
            updated_at=datetime.utcnow()
        )
        
        self.titan.commit(node, signed_by="TitanSeeder")
        print(f"[Titan-Seeder] Anchored document fact: {fact_id}")

    def seed_agent_cartridge(self, manifest: Dict[str, Any]):
        """
        Hydrate Omega-Graph with agent and cartridge metadata from a manifest.
        """
        cartridge_id = manifest.get("cartridge_id")
        print(f"[Titan-Seeder] Seeding cartridge: {cartridge_id}")
        
        provenance = GraphNodeProvenance(
            created_by="TitanSeeder",
            created_at=datetime.utcnow(),
            hash=""
        )
        
        # Add Cartridge Node
        node = GraphNode(
            node_id=cartridge_id,
            type="Cartridge",
            attributes={
                "description": manifest.get("description"),
                "version": manifest.get("version"),
                "capabilities": manifest.get("capabilities", [])
            },
            edges=[],
            provenance=provenance,
            trust_score=1.0,
            updated_at=datetime.utcnow()
        )
        
        self.titan.commit(node, signed_by="TitanSeeder")
        
        # Add Agent Nodes and link them to the Cartridge
        for agent_id in manifest.get("agents", []):
            agent_node = GraphNode(
                node_id=agent_id,
                type="Agent",
                attributes={
                    "role": "Consultant", # Default
                    "status": "Ready"
                },
                edges=[
                    GraphEdge(to=cartridge_id, relationship="assigned_to", weight=1.0)
                ],
                provenance=provenance,
                trust_score=1.0,
                updated_at=datetime.utcnow()
            )
            self.titan.commit(agent_node, signed_by="TitanSeeder")

    def run_directory_pipeline(self, dir_path: str):
        """
        Scan a directory and seed all supported files.
        """
        if not os.path.isdir(dir_path):
            print(f"[Titan-Seeder] Error: {dir_path} is not a directory")
            return

        print(f"[Titan-Seeder] Starting directory pipeline for: {dir_path}")
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".md") or file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        self.seed_text_document(
                            content=content,
                            source_id=file,
                            metadata={"path": file_path}
                        )

if __name__ == "__main__":
    # Quick sanity test
    from titan_omega import TitanOmega
    
    titan = TitanOmega()
    seeder = TitanSeeder(titan)
    
    # Seed a sample fact
    test_content = """
    Project Chimera is a multi-node agent ecosystem designed for Camelot OS.
    It utilizes Titan Omega as its persistent memory layer, combining graph and vector search.
    The system is engineered to be self-optimizing and highly scalable.
    """
    seeder.seed_text_document(test_content, "Chimera_Overview.md", {"topic": "architecture"})
    
    # Verify via hybrid search
    results = titan.hybrid_search("What is Project Chimera?")
    print(f"Hybrid Search Results: {results}")