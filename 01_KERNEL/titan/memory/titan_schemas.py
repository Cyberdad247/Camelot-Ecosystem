# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Titan Omega Memory Stack — Core Schemas

This module defines the data structures for the three-tier memory system:
- Omega-Graph: Structured knowledge graph (canonical facts, agent metadata, provenance)
- Omega-Vault: Semantic vector store (embeddings for RAG)
- Omega-Flux: Ephemeral working memory (GoT reasoning fragments)
"""

import hashlib
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    """Return a timezone-aware UTC datetime for schema defaults and comparisons."""
    return datetime.now(UTC)


# =========================================
# Omega-GRAPH: Structured Knowledge Graph
# =========================================

class GraphEdge(BaseModel):
    """Relationship between graph nodes."""
    to: str = Field(..., description="Target node ID")
    relationship: str = Field(..., description="Edge type (e.g., 'belongs_to', 'expert_in')")
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class GraphNodeProvenance(BaseModel):
    """Cryptographic provenance for audit trail."""
    created_by: str = Field(..., description="Agent or system that created this node")
    created_at: datetime = Field(default_factory=utc_now)
    hash: str = Field(..., description="SHA-256 hash of node content")
    signature: Optional[str] = Field(None, description="Cryptographic signature")


class GraphNode(BaseModel):
    """
    Node in the Omega-Graph knowledge graph.
    Used for: canonical facts, agent profiles, templates, constraints.
    """
    node_id: str = Field(..., description="Unique identifier")
    type: str = Field(..., description="Node type (Agent, Skill, Cartridge, Fact, etc.)")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Node properties")
    edges: List[GraphEdge] = Field(default_factory=list, description="Outgoing relationships")
    provenance: GraphNodeProvenance = Field(..., description="Audit trail")
    trust_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Node reliability")
    updated_at: datetime = Field(default_factory=utc_now)

    def compute_hash(self) -> str:
        """Generate SHA-256 hash of node content for provenance."""
        content = f"{self.node_id}:{self.type}:{self.attributes}:{self.updated_at.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()


# =========================================
# Omega-VAULT: Semantic Vector Store
# =========================================

class VaultEmbedding(BaseModel):
    """
    Entry in the Omega-Vault vector store.
    Optimized for approximate nearest neighbor (ANN) queries.
    """
    embedding_id: str = Field(..., description="Unique identifier")
    vector: List[float] = Field(..., description="Dense embedding (384 or 768 dims)")
    source_id: str = Field(..., description="Source document/node ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    recency: float = Field(default=1.0, ge=0.0, le=1.0, description="Time-decay score")
    trust_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Reliability")
    type: str = Field(default="longform_doc", description="Content type")


# =========================================
# Omega-FLUX: Ephemeral Working Memory
# =========================================

class FluxNode(BaseModel):
    """
    Temporary node in Omega-Flux working memory.
    Used for: GoT reasoning fragments, intermediate calculations, transient state.
    Automatically expires after TTL.
    """
    flux_node_id: str = Field(..., description="Unique identifier")
    ttl_seconds: int = Field(default=90, description="Time-to-live in seconds")
    content: str = Field(..., description="Ephemeral reasoning step or state")
    links: List[str] = Field(default_factory=list, description="Related node IDs")
    priority: str = Field(default="medium", description="Priority (low/medium/high)")
    created_at: datetime = Field(default_factory=utc_now)
    session_id: Optional[str] = Field(None, description="Associated session")

    def is_expired(self) -> bool:
        """Check if this flux node has exceeded its TTL."""
        elapsed = (utc_now() - self.created_at).total_seconds()
        return elapsed > self.ttl_seconds


# =========================================
# UNIFIED TITAN OMEGA INTERFACE
# =========================================

class TitanOmegaConfig(BaseModel):
    """Configuration for the Titan Omega memory stack."""
    graph_backend: str = Field(default="networkx", description="Graph storage (networkx, neo4j)")
    vault_backend: str = Field(default="faiss", description="Vector store (faiss, chroma)")
    flux_ttl_default: int = Field(default=90, description="Default TTL for flux nodes")
    enable_provenance: bool = Field(default=True, description="Enable cryptographic provenance")
    enable_offloading: bool = Field(default=True, description="Enable real-time offloading")
    # Tier Grafting fields (alpha_omega = all three tiers)
    tier: str = Field(default="alpha_omega", description="Active tier set: alpha_omega | graph_only | vault_only")
    mode: str = Field(default="development", description="Runtime mode: production | development")
    persist_strategy: str = Field(default="on_demand", description="Persist policy: all | on_demand")
    graph_persist_path: Optional[str] = Field(None, description="Absolute path override for Omega-Graph JSON")
    vault_persist_path: Optional[str] = Field(None, description="Absolute path override for Omega-Vault index")
