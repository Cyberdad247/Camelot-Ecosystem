# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
NANO GRAPH ADAPTER PHIAL: Lightweight GraphRAG
Extracted from: gusye1234/nano-graphrag architecture (~1100 LOC)
Purpose: Provide hackable, async-capable GraphRAG with minimal overhead.

Key Features:
- ~60% less code than MS GraphRAG
- Async operations for integration with Faiss, Neo4j, Ollama
- Batch and incremental inserts
- Local/Global query modes
"""

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional


class QueryMode(Enum):
    NAIVE = "naive"  # Direct similarity match
    LOCAL = "local"  # Entity-focused neighborhood
    GLOBAL = "global"  # Community-level synthesis


@dataclass
class Entity:
    """A node in the knowledge graph."""

    id: str
    name: str
    entity_type: str
    description: str
    source_ids: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class Relation:
    """An edge in the knowledge graph."""

    id: str
    source_id: str
    target_id: str
    relation_type: str
    description: str
    weight: float = 1.0


@dataclass
class Community:
    """A cluster of related entities."""

    id: str
    entity_ids: List[str]
    summary: str
    level: int = 0  # Hierarchy level
    importance: float = 0.0


class NanoGraphAdapter:
    """
    Lightweight GraphRAG adapter inspired by nano-graphrag.

    Architecture:
        Documents → LLM Entity Extraction → Graph Storage → Query Routing

    Query Modes:
        - NAIVE: Basic text match (fallback)
        - LOCAL: Expand from matched entities to 1-hop neighbors
        - GLOBAL: Use top-K important communities for synthesis
    """

    def __init__(self, llm_fn: Callable[[str], str] = None, embedding_fn: Callable[[str], List[float]] = None):
        self.llm_fn = llm_fn or self._mock_llm
        self.embedding_fn = embedding_fn

        # In-memory stores (can be swapped for Neo4j, etc.)
        self.entities: Dict[str, Entity] = {}
        self.relations: Dict[str, Relation] = {}
        self.communities: Dict[str, Community] = {}
        self.doc_chunks: Dict[str, str] = {}  # chunk_id -> content

    def _mock_llm(self, prompt: str) -> str:
        """Mock LLM for testing."""
        return json.dumps(
            {"entities": [{"name": "TestEntity", "type": "concept", "description": "A test entity"}], "relations": []}
        )

    def _generate_id(self, content: str) -> str:
        """Generate deterministic ID from content."""
        return hashlib.md5(content.encode()).hexdigest()[:12]

    async def insert(self, doc_id: str, content: str, chunk_size: int = 500) -> Dict:
        """
        Insert a document into the graph.

        Steps:
        1. Chunk the document
        2. Extract entities and relations via LLM
        3. Merge into graph
        4. Update communities
        """
        # Chunk the document
        chunks = self._chunk_text(content, chunk_size)

        extracted_entities = []
        extracted_relations = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            self.doc_chunks[chunk_id] = chunk

            # LLM extraction
            extraction_prompt = f"""Extract entities and relations from this text.
TEXT: {chunk}

Respond in JSON:
{{
    "entities": [{{"name": "...", "type": "person|org|concept|location", "description": "..."}}],
    "relations": [{{"source": "entity_name", "target": "entity_name", "type": "...", "description": "..."}}]
}}
"""
            response = self.llm_fn(extraction_prompt)

            try:
                extraction = json.loads(response)
            except json.JSONDecodeError:
                extraction = {"entities": [], "relations": []}

            # Merge entities
            for ent_data in extraction.get("entities", []):
                ent_id = self._generate_id(ent_data["name"])
                if ent_id not in self.entities:
                    self.entities[ent_id] = Entity(
                        id=ent_id,
                        name=ent_data["name"],
                        entity_type=ent_data.get("type", "unknown"),
                        description=ent_data.get("description", ""),
                        source_ids=[chunk_id],
                    )
                    extracted_entities.append(ent_id)
                else:
                    self.entities[ent_id].source_ids.append(chunk_id)

            # Merge relations
            for rel_data in extraction.get("relations", []):
                src_id = self._generate_id(rel_data["source"])
                tgt_id = self._generate_id(rel_data["target"])
                rel_id = self._generate_id(f"{src_id}_{tgt_id}_{rel_data['type']}")

                if rel_id not in self.relations and src_id in self.entities and tgt_id in self.entities:
                    self.relations[rel_id] = Relation(
                        id=rel_id,
                        source_id=src_id,
                        target_id=tgt_id,
                        relation_type=rel_data.get("type", "related_to"),
                        description=rel_data.get("description", ""),
                    )
                    extracted_relations.append(rel_id)

        return {
            "doc_id": doc_id,
            "chunks": len(chunks),
            "entities_added": len(extracted_entities),
            "relations_added": len(extracted_relations),
        }

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Recursive character-based splitting to maintain semantic integrity.
        Splits on double newlines, single newlines, and then spaces.
        """
        separators = ["\n\n", "\n", " ", ""]

        def _recursive_split(current_text: str, seps: List[str]) -> List[str]:
            if len(current_text) <= chunk_size:
                return [current_text]

            if not seps:
                return [current_text[i : i + chunk_size] for i in range(0, len(current_text), chunk_size)]

            sep = seps[0]
            splits = current_text.split(sep)

            current_chunk = ""
            results = []

            for part in splits:
                if len(current_chunk) + len(part) + len(sep) <= chunk_size:
                    current_chunk += (sep if current_chunk else "") + part
                else:
                    if current_chunk:
                        results.append(current_chunk)

                    # If a single part is larger than chunk_size, recurse with next seps
                    if len(part) > chunk_size:
                        results.extend(_recursive_split(part, seps[1:]))
                        current_chunk = ""
                    else:
                        current_chunk = part

            if current_chunk:
                results.append(current_chunk)

            return results

        return _recursive_split(text, separators)

    def query(self, query: str, mode: QueryMode = QueryMode.LOCAL, top_k: int = 5) -> Dict:
        """
        Query the knowledge graph.

        Args:
            query: User query string.
            mode: NAIVE, LOCAL, or GLOBAL query mode.
            top_k: Number of results to return.

        Returns:
            {"entities": [...], "context": str, "mode": str}
        """
        if mode == QueryMode.NAIVE:
            return self._query_naive(query, top_k)
        elif mode == QueryMode.LOCAL:
            return self._query_local(query, top_k)
        elif mode == QueryMode.GLOBAL:
            return self._query_global(query, top_k)
        else:
            return self._query_naive(query, top_k)

    def _query_naive(self, query: str, top_k: int) -> Dict:
        """Naive text match against entity descriptions."""
        query_lower = query.lower()
        matches = []

        for ent in self.entities.values():
            score = sum(1 for word in query_lower.split() if word in ent.description.lower())
            if score > 0:
                matches.append((score, ent))

        matches.sort(key=lambda x: x[0], reverse=True)
        top_entities = [e for _, e in matches[:top_k]]

        context = "\n".join(f"- {e.name}: {e.description}" for e in top_entities)

        return {"entities": top_entities, "context": context, "mode": "naive"}

    def _query_local(self, query: str, top_k: int) -> Dict:
        """Local mode: Expand from matched entities to neighbors."""
        naive_result = self._query_naive(query, top_k // 2)
        seed_ids = {e.id for e in naive_result["entities"]}

        # Expand to 1-hop neighbors
        neighbor_ids = set()
        for rel in self.relations.values():
            if rel.source_id in seed_ids:
                neighbor_ids.add(rel.target_id)
            if rel.target_id in seed_ids:
                neighbor_ids.add(rel.source_id)

        all_ids = seed_ids | neighbor_ids
        all_entities = [self.entities[eid] for eid in all_ids if eid in self.entities][:top_k]

        context = "\n".join(f"- {e.name}: {e.description}" for e in all_entities)

        return {"entities": all_entities, "context": context, "mode": "local"}

    def _query_global(self, query: str, top_k: int) -> Dict:
        """Global mode: Use community summaries (simplified)."""
        # In full implementation, we'd use pre-computed community summaries
        # For now, fall back to local with broader reach
        return self._query_local(query, top_k * 2)

    def stats(self) -> Dict:
        """Return graph statistics."""
        return {
            "entities": len(self.entities),
            "relations": len(self.relations),
            "communities": len(self.communities),
            "chunks": len(self.doc_chunks),
        }


# ═══════════════════════════════════════════════════════════════════
# CAMELOT INTEGRATION POINT
# ═══════════════════════════════════════════════════════════════════

_global_graph_adapter: Optional[NanoGraphAdapter] = None


def get_graph_adapter(llm_fn: Callable[[str], str] = None) -> NanoGraphAdapter:
    """Singleton accessor for Camelot Kernel integration."""
    global _global_graph_adapter
    if _global_graph_adapter is None:
        _global_graph_adapter = NanoGraphAdapter(llm_fn=llm_fn)
    return _global_graph_adapter


if __name__ == "__main__":
    import asyncio

    async def demo():
        adapter = NanoGraphAdapter()

        # Insert a document
        doc_content = """
        The Camelot Operating System is an AI-native platform.
        It uses Universal Knowledge Glyphs for memory persistence.
        ANYA is the Cognitive Compiler that processes user intent.
        Merlin is the backend inference engine.
        """

        result = await adapter.insert("camelot_doc", doc_content)
        print(f"Insert result: {result}")
        print(f"Graph stats: {adapter.stats()}")

        # Query
        query_result = adapter.query("What is ANYA?", mode=QueryMode.LOCAL)
        print("\nQuery result:")
        print(f"Mode: {query_result['mode']}")
        print(f"Context:\n{query_result['context']}")

    asyncio.run(demo())