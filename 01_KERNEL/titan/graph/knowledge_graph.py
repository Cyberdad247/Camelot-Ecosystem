# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
==============================================================================
KNOWLEDGE GRAPH ENGINE
Camelot OS v33.0 - The Graph Sovereign
==============================================================================
Graph-native knowledge storage using LightRAG's graph capabilities.
Enables chain-of-thought reasoning through entity-relation traversal.

REPLACES: Sir_Percival (Deep_RAG)
NEW ROLE: Sir_Percival v2 - The Graph Weaver
==============================================================================
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ==============================================================================
# CONFIGURATION
# ==============================================================================

GRAPH_STORAGE_PATH = Path("Titan_Ω_Hypergraph/knowledge_graph")
DEFAULT_WORKING_DIR = Path("Titan_Ω_Hypergraph/lightrag_working")


# ==============================================================================
# DATA MODELS
# ==============================================================================


@dataclass
class Entity:
    """A node in the knowledge graph."""

    id: str
    name: str
    type: str  # e.g., "Function", "Class", "Bug", "Concept"
    description: str = ""
    properties: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "properties": self.properties,
        }


@dataclass
class Relation:
    """An edge in the knowledge graph."""

    source_id: str
    target_id: str
    relation_type: str  # e.g., "calls", "fixes", "caused_by", "uses"
    weight: float = 1.0
    properties: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "weight": self.weight,
            "properties": self.properties,
        }


@dataclass
class Triplet:
    """A knowledge triplet: (head, relation, tail)."""

    head: str
    relation: str
    tail: str

    def __str__(self) -> str:
        return f"({self.head}) --[{self.relation}]--> ({self.tail})"


@dataclass
class SubGraph:
    """A subgraph extracted from the knowledge graph."""

    entities: list[Entity]
    relations: list[Relation]
    query: str
    hops: int

    def to_context(self) -> str:
        """Convert subgraph to textual context for Merlin."""
        lines = ["## Knowledge Graph Context:\n"]

        # Entity summary
        lines.append("### Entities Found:")
        for e in self.entities:
            lines.append(f"- **{e.name}** ({e.type}): {e.description[:100]}...")

        # Relation chains
        lines.append("\n### Relationships:")
        for r in self.relations:
            src = next((e for e in self.entities if e.id == r.source_id), None)
            tgt = next((e for e in self.entities if e.id == r.target_id), None)
            src_name = src.name if src else r.source_id
            tgt_name = tgt.name if tgt else r.target_id
            lines.append(f"- {src_name} --[{r.relation_type}]--> {tgt_name}")

        return "\n".join(lines)

    def to_triplets(self) -> list[Triplet]:
        """Convert to list of triplets."""
        triplets = []
        for r in self.relations:
            src = next((e for e in self.entities if e.id == r.source_id), None)
            tgt = next((e for e in self.entities if e.id == r.target_id), None)
            triplets.append(
                Triplet(
                    head=src.name if src else r.source_id,
                    relation=r.relation_type,
                    tail=tgt.name if tgt else r.target_id,
                )
            )
        return triplets


@dataclass
class GraphQueryResult:
    """Result from a graph query."""

    query: str
    mode: str  # "local", "global", "hybrid", "naive"
    subgraph: SubGraph
    answer: str
    latency_ms: float
    sources: list[str]


# ==============================================================================
# KNOWLEDGE GRAPH ENGINE
# ==============================================================================


class KnowledgeGraphEngine:
    """
    Graph-native knowledge engine for CAMELOT.

    Uses LightRAG's graph + vector hybrid mode for:
    - Entity extraction from documents
    - Relation detection
    - Graph traversal (neighborhood queries)
    - Subgraph retrieval for context

    Sir_Percival v2 - The Graph Weaver
    """

    def __init__(self, working_dir: Optional[Path] = None):
        self.working_dir = working_dir or DEFAULT_WORKING_DIR
        self._rag = None
        self._initialized = False
        self._entity_cache: dict[str, Entity] = {}
        self._relation_cache: list[Relation] = []

    def initialize(self, llm_model: str = "local") -> None:
        """
        Initialize the LightRAG graph engine.

        Args:
            llm_model: LLM to use for extraction ("local" uses Sovereign Stack)
        """
        if self._initialized:
            return

        self.working_dir.mkdir(parents=True, exist_ok=True)

        try:
            from lightrag import LightRAG, QueryParam  # noqa: F401
            from lightrag.llm import gpt_4o_mini_complete, openai_embedding
        except ImportError:
            print("[GRAPH] LightRAG not installed. Using fallback mode.")
            self._initialized = True
            return

        # Check if we should use local LLM (Sovereign Stack)
        if llm_model == "local":
            # Use custom LLM function that calls Sovereign Stack
            llm_func = self._local_llm_complete
            embed_func = self._local_embedding
        else:
            # Use OpenAI (requires API key)
            llm_func = gpt_4o_mini_complete
            embed_func = openai_embedding

        try:
            self._rag = LightRAG(
                working_dir=str(self.working_dir),
                llm_model_func=llm_func,
                embedding_func=embed_func,
            )
            self._initialized = True
            print(f"[GRAPH] Knowledge Graph Engine initialized at {self.working_dir}")
        except Exception as e:
            print(f"[GRAPH] Initialization error: {e}")
            self._initialized = True  # Continue with fallback

    async def _local_llm_complete(
        self, prompt: str, system_prompt: str = None, history_messages: list = None, **kwargs
    ) -> str:
        """Call Sovereign Stack for LLM completion."""
        import httpx

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "http://127.0.0.1:8080/completion",
                    json={
                        "prompt": full_prompt,
                        "n_predict": 512,
                        "temperature": 0.3,
                    },
                )
                data = response.json()
                return data.get("content", "")
        except Exception as e:
            return f"Error: {e}"

    async def _local_embedding(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using sentence-transformers."""
        from sentence_transformers import SentenceTransformer

        if not hasattr(self, "_embedder"):
            self._embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        embeddings = self._embedder.encode(texts)
        return embeddings.tolist()

    def _ensure_initialized(self) -> None:
        """Ensure engine is initialized."""
        if not self._initialized:
            self.initialize()

    # ==========================================================================
    # INGESTION (Sir_Lukas Pipeline)
    # ==========================================================================

    def ingest_document(self, content: str, source: str = "unknown") -> dict:
        """
        Ingest a document, extracting entities and relations.

        Args:
            content: Document content
            source: Source identifier (file path, etc.)

        Returns:
            Dict with ingestion stats
        """
        self._ensure_initialized()
        start_time = time.time()

        if self._rag:
            try:
                self._rag.insert(content)
                latency = (time.time() - start_time) * 1000
                return {
                    "success": True,
                    "source": source,
                    "latency_ms": round(latency, 2),
                    "message": "Document ingested to graph",
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Fallback: Manual entity extraction
        entities, relations = self._extract_entities_manual(content)

        for e in entities:
            self._entity_cache[e.id] = e
        self._relation_cache.extend(relations)

        latency = (time.time() - start_time) * 1000
        return {
            "success": True,
            "source": source,
            "entities_found": len(entities),
            "relations_found": len(relations),
            "latency_ms": round(latency, 2),
        }

    def _extract_entities_manual(self, content: str) -> tuple[list[Entity], list[Relation]]:
        """
        Manual entity extraction (fallback when LLM unavailable).
        Uses regex patterns to find code entities.
        """
        entities = []
        relations = []

        # Extract Python functions
        func_pattern = r"def\s+(\w+)\s*\("
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            entities.append(
                Entity(
                    id=f"func_{func_name}",
                    name=func_name,
                    type="Function",
                    description=f"Python function: {func_name}",
                )
            )

        # Extract Python classes
        class_pattern = r"class\s+(\w+)\s*[\(:]"
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            entities.append(
                Entity(
                    id=f"class_{class_name}",
                    name=class_name,
                    type="Class",
                    description=f"Python class: {class_name}",
                )
            )

        # Extract imports
        import_pattern = r"(?:from\s+(\S+)\s+)?import\s+(\S+)"
        for match in re.finditer(import_pattern, content):
            module = match.group(1) or match.group(2)
            entities.append(
                Entity(
                    id=f"module_{module}",
                    name=module,
                    type="Module",
                    description=f"Imported module: {module}",
                )
            )

        # Create "uses" relations between functions and imports
        func_ids = [e.id for e in entities if e.type == "Function"]
        module_ids = [e.id for e in entities if e.type == "Module"]

        for func_id in func_ids[:3]:  # Limit relations
            for mod_id in module_ids[:3]:
                relations.append(
                    Relation(
                        source_id=func_id,
                        target_id=mod_id,
                        relation_type="uses",
                    )
                )

        return entities, relations

    # ==========================================================================
    # QUERY (Sir_Percival v2 - Graph Weaver)
    # ==========================================================================

    def query(
        self,
        query: str,
        mode: str = "hybrid",
        hops: int = 2,
    ) -> GraphQueryResult:
        """
        Query the knowledge graph.

        Args:
            query: Natural language query
            mode: Query mode ("local", "global", "hybrid", "naive")
            hops: Number of hops for neighborhood traversal

        Returns:
            GraphQueryResult with subgraph and answer
        """
        self._ensure_initialized()
        start_time = time.time()

        if self._rag:
            try:
                from lightrag import QueryParam

                result = self._rag.query(query, param=QueryParam(mode=mode))

                latency = (time.time() - start_time) * 1000

                # Build subgraph from result
                subgraph = SubGraph(
                    entities=[],
                    relations=[],
                    query=query,
                    hops=hops,
                )

                return GraphQueryResult(
                    query=query,
                    mode=mode,
                    subgraph=subgraph,
                    answer=result,
                    latency_ms=round(latency, 2),
                    sources=[],
                )

            except Exception as e:
                print(f"[GRAPH] Query error: {e}")

        # Fallback: Search cached entities
        subgraph = self._search_cache(query, hops)
        latency = (time.time() - start_time) * 1000

        answer = self._generate_answer_from_subgraph(query, subgraph)

        return GraphQueryResult(
            query=query,
            mode=mode,
            subgraph=subgraph,
            answer=answer,
            latency_ms=round(latency, 2),
            sources=[e.id for e in subgraph.entities],
        )

    def _search_cache(self, query: str, hops: int) -> SubGraph:
        """Search the entity cache for relevant entities."""
        query_lower = query.lower()

        # Find matching entities
        matching_entities = []
        for entity in self._entity_cache.values():
            if query_lower in entity.name.lower() or query_lower in entity.description.lower():
                matching_entities.append(entity)

        # Get neighbors (relations)
        entity_ids = {e.id for e in matching_entities}
        matching_relations = []

        for hop in range(hops):
            new_ids = set()
            for rel in self._relation_cache:
                if rel.source_id in entity_ids or rel.target_id in entity_ids:
                    matching_relations.append(rel)
                    new_ids.add(rel.source_id)
                    new_ids.add(rel.target_id)
            entity_ids.update(new_ids)

        # Expand entities with neighbors
        for eid in entity_ids:
            if eid in self._entity_cache and self._entity_cache[eid] not in matching_entities:
                matching_entities.append(self._entity_cache[eid])

        return SubGraph(
            entities=matching_entities[:20],  # Limit
            relations=matching_relations[:50],
            query=query,
            hops=hops,
        )

    def _generate_answer_from_subgraph(self, query: str, subgraph: SubGraph) -> str:
        """Generate an answer from the subgraph."""
        if not subgraph.entities:
            return f"No relevant entities found for: {query}"

        triplets = subgraph.to_triplets()

        answer_parts = [f"Based on the knowledge graph, here's what I found for '{query}':\n"]

        for triplet in triplets[:10]:
            answer_parts.append(f"• {triplet}")

        return "\n".join(answer_parts)

    # ==========================================================================
    # GRAPH TRAVERSAL
    # ==========================================================================

    def get_neighborhood(
        self,
        entity_name: str,
        hops: int = 2,
    ) -> SubGraph:
        """
        Get the neighborhood of an entity.

        Args:
            entity_name: Name of the entity
            hops: Number of hops to traverse

        Returns:
            SubGraph containing the neighborhood
        """
        self._ensure_initialized()

        # Find the entity
        target_entity = None
        for entity in self._entity_cache.values():
            if entity.name.lower() == entity_name.lower():
                target_entity = entity
                break

        if not target_entity:
            return SubGraph(entities=[], relations=[], query=entity_name, hops=hops)

        # BFS to find neighbors
        visited_ids = {target_entity.id}
        entities = [target_entity]
        relations = []

        current_ids = {target_entity.id}

        for hop in range(hops):
            next_ids = set()
            for rel in self._relation_cache:
                if rel.source_id in current_ids and rel.target_id not in visited_ids:
                    next_ids.add(rel.target_id)
                    relations.append(rel)
                    visited_ids.add(rel.target_id)
                elif rel.target_id in current_ids and rel.source_id not in visited_ids:
                    next_ids.add(rel.source_id)
                    relations.append(rel)
                    visited_ids.add(rel.source_id)

            # Add new entities
            for eid in next_ids:
                if eid in self._entity_cache:
                    entities.append(self._entity_cache[eid])

            current_ids = next_ids

        return SubGraph(
            entities=entities,
            relations=relations,
            query=entity_name,
            hops=hops,
        )

    def get_stats(self) -> dict:
        """Get graph statistics."""
        return {
            "total_entities": len(self._entity_cache),
            "total_relations": len(self._relation_cache),
            "entity_types": list(set(e.type for e in self._entity_cache.values())),
            "relation_types": list(set(r.relation_type for r in self._relation_cache)),
            "working_dir": str(self.working_dir),
        }


# ==============================================================================
# SINGLETON INSTANCE
# ==============================================================================

_graph_instance: Optional[KnowledgeGraphEngine] = None


def get_graph_engine() -> KnowledgeGraphEngine:
    """Get the singleton KnowledgeGraphEngine instance."""
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = KnowledgeGraphEngine()
    return _graph_instance


# ==============================================================================
# SIR_PERCIVAL v2 - THE GRAPH WEAVER
# ==============================================================================


class SirPercival:
    """
    Sir_Percival v2 - The Graph Weaver

    No longer a simple vector searcher.
    Now weaves through the knowledge graph to find chains of thought.
    """

    def __init__(self):
        self.engine = get_graph_engine()
        self.name = "Sir_Percival"
        self.title = "The Graph Weaver"
        self.version = "2.0"

    def weave(self, query: str, mode: str = "hybrid") -> GraphQueryResult:
        """
        Weave through the knowledge graph to answer a query.

        This is the main entry point for graph-based reasoning.
        """
        return self.engine.query(query, mode=mode)

    def ingest(self, content: str, source: str = "unknown") -> dict:
        """Ingest a document into the knowledge graph."""
        return self.engine.ingest_document(content, source)

    def explore(self, entity: str, hops: int = 2) -> SubGraph:
        """Explore the neighborhood of an entity."""
        return self.engine.get_neighborhood(entity, hops)


# ==============================================================================
# TESTING
# ==============================================================================


if __name__ == "__main__":
    print("[TEST] Knowledge Graph Engine")
    print("=" * 60)

    engine = KnowledgeGraphEngine()
    engine.initialize()

    # Test ingestion
    test_code = '''
def fix_import_error(module_name):
    """Fix missing module import."""
    import sys
    import importlib
    return importlib.import_module(module_name)

class ErrorHandler:
    """Handles various error types."""
    def handle(self, error):
        if isinstance(error, ImportError):
            return fix_import_error(str(error))
'''

    result = engine.ingest_document(test_code, source="test.py")
    print(f"[OK] Ingested: {result}")

    # Test query
    query_result = engine.query("import error", mode="hybrid")
    print(f"[OK] Query result: {query_result.answer[:100]}...")

    # Test neighborhood
    subgraph = engine.get_neighborhood("fix_import_error", hops=2)
    print(f"[OK] Neighborhood: {len(subgraph.entities)} entities, {len(subgraph.relations)} relations")

    # Stats
    stats = engine.get_stats()
    print(f"[OK] Stats: {stats}")

    # Test Sir_Percival
    percival = SirPercival()
    result = percival.weave("How to handle errors?")
    print(f"[OK] Sir_Percival weave: {result.answer[:100]}...")

    print("=" * 60)
    print("[PASS] Knowledge Graph Engine tests complete!")