# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Titan Omega Memory Engine — Core Implementation

Three-tier memory system for Project Chimera:
1. Ω-Graph: Structured knowledge graph (NetworkX)
2. Ω-Vault: Semantic vector store (FAISS)
3. Ω-Flux: Ephemeral working memory (in-memory + TTL)

This is the foundation for Context Expansion Protocol (CEP) and RAG.
"""

import os
import json
import time
import hashlib
import warnings
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import networkx as nx

try:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r"builtin type SwigPyPacked has no __module__ attribute",
            category=DeprecationWarning,
        )
        warnings.filterwarnings(
            "ignore",
            message=r"builtin type SwigPyObject has no __module__ attribute",
            category=DeprecationWarning,
        )
        warnings.filterwarnings(
            "ignore",
            message=r"builtin type swigvarlink has no __module__ attribute",
            category=DeprecationWarning,
        )
        import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False

from .titan_schemas import (
    GraphNode, GraphEdge, GraphNodeProvenance,
    VaultEmbedding, FluxNode, TitanOmegaConfig
)


# =========================================
# Ω-GRAPH: Knowledge Graph Engine
# =========================================

class OmegaGraph:
    """
    Structured knowledge graph using NetworkX.
    Stores: agents, skills, cartridges, canonical facts, provenance chains.
    """
    
    def __init__(self, persist_path: Optional[str] = None):
        self.graph = nx.DiGraph()
        self.persist_path = persist_path or "data/omega_graph.json"
        self.load()
    
    def add_node(self, node: GraphNode) -> str:
        """Add or update a node in the graph."""
        # Ensure hash is current
        if not node.provenance.hash:
            node.provenance.hash = node.compute_hash()
        
        # Add to NetworkX graph
        self.graph.add_node(
            node.node_id,
            type=node.type,
            attributes=node.attributes,
            trust_score=node.trust_score,
            provenance=node.provenance.model_dump(),
            updated_at=node.updated_at.isoformat()
        )
        
        # Add edges
        for edge in node.edges:
            self.graph.add_edge(
                node.node_id,
                edge.to,
                relationship=edge.relationship,
                weight=edge.weight
            )
        
        print(f"[Ω-Graph] Added node: {node.node_id} (type: {node.type})")
        return node.node_id
    
    def query(self, pattern: Dict[str, Any]) -> List[GraphNode]:
        """
        Query nodes by pattern matching.
        Pattern: {"type": "Agent", "attributes.role": "Engineer"}
        """
        results = []
        
        for node_id in self.graph.nodes():
            node_data = self.graph.nodes[node_id]
            
            # Simple pattern matching
            match = True
            for key, value in pattern.items():
                if "." in key:
                    # Nested attribute
                    parts = key.split(".")
                    current = node_data.get(parts[0], {})
                    for part in parts[1:]:
                        if isinstance(current, dict):
                            current = current.get(part)
                        else:
                            match = False
                            break
                    if current != value:
                        match = False
                else:
                    # Direct attribute
                    if node_data.get(key) != value:
                        match = False
                
                if not match:
                    break
            
            if match:
                # Reconstruct GraphNode
                results.append(self._node_data_to_obj(node_id, node_data))
        
        return results
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Retrieve a single node by ID."""
        if node_id not in self.graph.nodes():
            return None
        return self._node_data_to_obj(node_id, self.graph.nodes[node_id])
    
    def _node_data_to_obj(self, node_id: str, data: Dict) -> GraphNode:
        """Convert NetworkX node data back to GraphNode object."""
        edges = []
        for _, target, edge_data in self.graph.out_edges(node_id, data=True):
            edges.append(GraphEdge(
                to=target,
                relationship=edge_data.get("relationship", ""),
                weight=edge_data.get("weight", 1.0)
            ))
        
        return GraphNode(
            node_id=node_id,
            type=data.get("type", "Unknown"),
            attributes=data.get("attributes", {}),
            edges=edges,
            provenance=GraphNodeProvenance(**data.get("provenance", {})),
            trust_score=data.get("trust_score", 1.0),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.utcnow().isoformat()))
        )
    
    def save(self):
        """Persist graph to disk."""
        os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
        data = nx.node_link_data(self.graph)
        
        # Convert datetime objects to ISO strings for JSON serialization
        def serialize_datetimes(obj):
            if isinstance(obj, dict):
                return {k: serialize_datetimes(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize_datetimes(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            else:
                return obj
        
        data = serialize_datetimes(data)
        
        with open(self.persist_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[Ω-Graph] Saved {len(self.graph.nodes())} nodes to {self.persist_path}")
    
    def load(self):
        """Load graph from disk."""
        if os.path.exists(self.persist_path):
            try:
                with open(self.persist_path, "r") as f:
                    data = json.load(f)
                self.graph = nx.node_link_graph(data, directed=True)
                print(f"[Ω-Graph] Loaded {len(self.graph.nodes())} nodes from {self.persist_path}")
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"[Ω-Graph] Warning: Could not load graph from {self.persist_path}: {e}")
                print(f"[Ω-Graph] Starting with empty graph")
                self.graph = nx.DiGraph()
        else:
            print(f"[Ω-Graph] No existing graph found, starting fresh")


# =========================================
# Ω-VAULT: Vector Store Engine
# =========================================

class OmegaVault:
    """
    Semantic vector store using FAISS.
    Stores: document embeddings, cartridge blobs, symbolect snippets.
    """
    
    def __init__(self, dimension: int = 384, persist_path: Optional[str] = None):
        if not VECTOR_AVAILABLE:
            raise ImportError("FAISS and sentence-transformers required for OmegaVault")
        
        self.dimension = dimension
        self.persist_path = persist_path or "data/omega_vault.index"
        self.index = faiss.IndexFlatL2(dimension)
        self.embeddings: Dict[str, VaultEmbedding] = {}
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')  # 384-dim model
        
        self.load()
    
    def add_embedding(self, embedding: VaultEmbedding):
        """Add a pre-computed embedding to the vault."""
        vector = np.array(embedding.vector, dtype=np.float32).reshape(1, -1)
        self.index.add(vector)
        self.embeddings[embedding.embedding_id] = embedding
        print(f"[Ω-Vault] Added embedding: {embedding.embedding_id} (source: {embedding.source_id})")
    
    def add_text(self, text: str, source_id: str, metadata: Optional[Dict] = None) -> str:
        """Encode text and add to vault."""
        vector = self.encoder.encode([text])[0]
        embedding_id = f"vec_{hashlib.sha256(text.encode()).hexdigest()[:8]}"
        
        embedding = VaultEmbedding(
            embedding_id=embedding_id,
            vector=vector.tolist(),
            source_id=source_id,
            metadata=metadata or {},
            type="text"
        )
        
        self.add_embedding(embedding)
        return embedding_id
    
    def vector_search(self, query: str, k: int = 5) -> List[Tuple[VaultEmbedding, float]]:
        """
        Perform approximate nearest neighbor search.
        Returns: List of (VaultEmbedding, distance) tuples.
        """
        if not self.embeddings:
            print(f"[Ω-Vault] No embeddings in vault, returning empty results")
            return []
        
        query_vector = self.encoder.encode([query])[0].reshape(1, -1)
        distances, indices = self.index.search(query_vector, k)
        
        results = []
        embedding_list = list(self.embeddings.values())
        
        # Check if search returned any results
        if len(indices) > 0 and len(indices[0]) > 0:
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(embedding_list) and idx >= 0:
                    results.append((embedding_list[idx], float(distance)))
        
        print(f"[Ω-Vault] Search for '{query[:50]}...' returned {len(results)} results")
        return results
    
    def save(self):
        """Persist FAISS index and embeddings."""
        os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
        faiss.write_index(self.index, self.persist_path)
        
        embeddings_path = self.persist_path.replace(".index", ".json")
        with open(embeddings_path, "w") as f:
            json.dump({k: v.model_dump() for k, v in self.embeddings.items()}, f, indent=2)
        
        print(f"[Ω-Vault] Saved {len(self.embeddings)} embeddings to {self.persist_path}")
    
    def load(self):
        """Load FAISS index and embeddings from disk."""
        if os.path.exists(self.persist_path):
            self.index = faiss.read_index(self.persist_path)
            
            embeddings_path = self.persist_path.replace(".index", ".json")
            with open(embeddings_path, "r") as f:
                data = json.load(f)
            
            self.embeddings = {k: VaultEmbedding(**v) for k, v in data.items()}
            print(f"[Ω-Vault] Loaded {len(self.embeddings)} embeddings from {self.persist_path}")


# =========================================
# Ω-FLUX: Ephemeral Memory Engine
# =========================================

class OmegaFlux:
    """
    Ephemeral working memory for transient reasoning.
    Stores: GoT fragments, intermediate calculations, session state.
    Auto-expires based on TTL.
    """
    
    def __init__(self, default_ttl: int = 90):
        self.nodes: Dict[str, FluxNode] = {}
        self.default_ttl = default_ttl
    
    def store_event(self, session_id: str, content: str, priority: str = "medium", ttl: Optional[int] = None) -> str:
        """Store an ephemeral event/reasoning fragment."""
        flux_id = f"flux_{session_id}_{int(time.time() * 1000)}"
        
        node = FluxNode(
            flux_node_id=flux_id,
            ttl_seconds=ttl or self.default_ttl,
            content=content,
            priority=priority,
            session_id=session_id
        )
        
        self.nodes[flux_id] = node
        print(f"[Ω-Flux] Stored event: {flux_id} (TTL: {node.ttl_seconds}s)")
        return flux_id
    
    def get_session_events(self, session_id: str) -> List[FluxNode]:
        """Retrieve all non-expired events for a session."""
        self.cleanup_expired()
        return [node for node in self.nodes.values() if node.session_id == session_id]
    
    def cleanup_expired(self):
        """Remove expired flux nodes."""
        expired = [fid for fid, node in self.nodes.items() if node.is_expired()]
        for fid in expired:
            del self.nodes[fid]
        if expired:
            print(f"[Ω-Flux] Cleaned up {len(expired)} expired nodes")


# =========================================
# UNIFIED TITAN OMEGA INTERFACE
# =========================================

class TitanOmega:
    """
    Unified interface for the Titan Omega memory stack.
    Orchestrates Ω-Graph, Ω-Vault, and Ω-Flux.
    """
    
    def __init__(self, config: Optional[TitanOmegaConfig] = None):
        self.config = config or TitanOmegaConfig()
        
        # Initialize sub-systems
        self.graph = OmegaGraph(persist_path="data/omega_graph.json")
        
        if VECTOR_AVAILABLE:
            self.vault = OmegaVault(dimension=384, persist_path="data/omega_vault.index")
        else:
            print("[WARN] FAISS not available; Ω-Vault disabled")
            self.vault = None
        
        self.flux = OmegaFlux(default_ttl=self.config.flux_ttl_default)
        
        print("[TitanΩ] Memory stack initialized")
    
    def commit(self, node: GraphNode, signed_by: str) -> str:
        """
        Commit a node to Ω-Graph with provenance.
        Returns the cryptographic hash.
        """
        node.provenance.created_by = signed_by
        node.provenance.hash = node.compute_hash()
        
        node_id = self.graph.add_node(node)
        self.graph.save()
        
        return node.provenance.hash
    
    def hybrid_search(self, query: str, k: int = 5) -> Dict[str, Any]:
        """
        Hybrid RAG search: combines Ω-Vault vector search + Ω-Graph pattern matching.
        """
        results = {"vector_results": [], "graph_results": []}
        
        # Vector search
        if self.vault:
            vector_hits = self.vault.vector_search(query, k=k)
            results["vector_results"] = [
                {"source_id": emb.source_id, "distance": dist, "metadata": emb.metadata}
                for emb, dist in vector_hits
            ]
        
        # Graph search (simple keyword match on attributes)
        # TODO: More sophisticated graph traversal
        graph_hits = []
        for node in self.graph.query({"type": "Fact"}):
            if query.lower() in str(node.attributes).lower():
                graph_hits.append(node)
        
        results["graph_results"] = [
            {"node_id": node.node_id, "attributes": node.attributes}
            for node in graph_hits[:k]
        ]
        
        return results
