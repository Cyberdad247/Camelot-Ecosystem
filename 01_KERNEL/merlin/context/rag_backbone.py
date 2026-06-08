# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
RAG Backbone — Hybrid Retrieval Engine

Combines vector search (Ω-Vault) and graph pattern matching (Ω-Graph)
for comprehensive context retrieval in the Context Expansion Protocol.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../memory')))

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from titan_omega import TitanOmega
from titan_schemas import GraphNode


@dataclass
class RetrievalResult:
    """Unified result from hybrid retrieval."""
    source_id: str
    content: str
    score: float
    source_type: str  # 'vector' or 'graph'
    metadata: Dict[str, Any]


class RAGBackbone:
    """
    Hybrid retrieval combining vector similarity and graph traversal.
    
    Architecture:
    1. Vector Search: Ω-Vault ANN queries for semantic similarity
    2. Graph Search: Ω-Graph pattern matching for structured knowledge
    3. Result Merging: Deduplication and relevance ranking
    4. Contextual Boosting: Trust score and recency weighting
    """
    
    def __init__(self, titan: TitanOmega):
        self.titan = titan
        self.vector_weight = 0.6  # Weight for vector search scores
        self.graph_weight = 0.4   # Weight for graph search scores
    
    def retrieve(
        self, 
        query: str, 
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """
        Perform hybrid retrieval combining vector and graph sources.
        
        Args:
            query: Natural language query
            k: Number of results to return
            filters: Optional filters like {"agent_type": "Engineer"}
        
        Returns:
            List of RetrievalResult objects ranked by relevance
        """
        print(f"[RAG] Hybrid retrieval for: '{query[:60]}...'")
        
        # 1. Vector search from Ω-Vault
        vector_results = self._vector_search(query, k=k*2)  # Get 2x for merging
        
        # 2. Graph search from Ω-Graph
        graph_results = self._graph_search(query, filters=filters, k=k*2)
        
        # 3. Merge and deduplicate
        merged = self._merge_results(vector_results, graph_results)
        
        # 4. Rank by composite score
        ranked = self._rank_results(merged)
        
        # 5. Return top-k
        return ranked[:k]
    
    def _vector_search(self, query: str, k: int) -> List[RetrievalResult]:
        """Search Ω-Vault using vector similarity."""
        if not self.titan.vault:
            print("[RAG] Ω-Vault not available, skipping vector search")
            return []
        
        vault_hits = self.titan.vault.vector_search(query, k=k)
        
        results = []
        for emb, distance in vault_hits:
            # Convert distance to similarity score (inverse)
            similarity = 1.0 / (1.0 + distance)
            
            # Apply trust score boost
            boosted_score = similarity * emb.trust_score
            
            results.append(RetrievalResult(
                source_id=emb.source_id,
                content=emb.metadata.get("content", f"[Vector embedding {emb.embedding_id}]"),
                score=boosted_score,
                source_type="vector",
                metadata={
                    "embedding_id": emb.embedding_id,
                    "trust_score": emb.trust_score,
                    "recency": emb.recency,
                    "distance": distance
                }
            ))
        
        print(f"[RAG] Vector search: {len(results)} results")
        return results
    
    def _graph_search(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        k: int = 5
    ) -> List[RetrievalResult]:
        """Search Ω-Graph using pattern matching and keyword search."""
        results = []
        
        # Strategy 1: Direct pattern match if filters provided
        if filters:
            nodes = self.titan.graph.query(filters)
            for node in nodes[:k]:
                results.append(self._node_to_result(node, score=0.9))
        
        # Strategy 2: Keyword search in node attributes
        query_lower = query.lower()
        keywords = query_lower.split()
        
        # Get all nodes and score by keyword overlap
        all_nodes = self.titan.graph.query({})  # Get all nodes
        
        for node in all_nodes:
            # Calculate keyword match score
            node_text = str(node.attributes).lower()
            matches = sum(1 for kw in keywords if kw in node_text)
            
            if matches > 0:
                # Score based on keyword density and trust
                keyword_score = (matches / len(keywords)) * node.trust_score
                results.append(self._node_to_result(node, score=keyword_score))
        
        # Sort by score and return top-k
        results.sort(key=lambda r: r.score, reverse=True)
        print(f"[RAG] Graph search: {len(results[:k])} results")
        return results[:k]
    
    def _node_to_result(self, node: GraphNode, score: float) -> RetrievalResult:
        """Convert a GraphNode to a RetrievalResult."""
        # Format node content as readable text
        content_parts = [f"Type: {node.type}"]
        for key, value in node.attributes.items():
            content_parts.append(f"{key}: {value}")
        
        return RetrievalResult(
            source_id=node.node_id,
            content="\n".join(content_parts),
            score=score,
            source_type="graph",
            metadata={
                "node_type": node.type,
                "trust_score": node.trust_score,
                "edges": len(node.edges),
                "provenance": node.provenance.created_by
            }
        )
    
    def _merge_results(
        self, 
        vector_results: List[RetrievalResult],
        graph_results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """
        Merge vector and graph results, removing duplicates.
        Duplicates are identified by source_id match.
        """
        seen_ids = set()
        merged = []
        
        # Combine both lists
        all_results = vector_results + graph_results
        
        for result in all_results:
            if result.source_id not in seen_ids:
                seen_ids.add(result.source_id)
                merged.append(result)
            else:
                # If duplicate from different source, boost the existing entry
                for existing in merged:
                    if existing.source_id == result.source_id:
                        # Average the scores if from different sources
                        if existing.source_type != result.source_type:
                            existing.score = (existing.score + result.score) / 2
                        break
        
        print(f"[RAG] Merged to {len(merged)} unique results")
        return merged
    
    def _rank_results(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """
        Final ranking with weighted combination of:
        - Base score (from vector/graph search)
        - Source type preference (vector vs graph)
        - Trust and recency (from metadata)
        """
        for result in results:
            # Apply source type weighting
            if result.source_type == "vector":
                result.score *= self.vector_weight
            else:
                result.score *= self.graph_weight
            
            # Apply trust boost if available
            trust = result.metadata.get("trust_score", 1.0)
            recency = result.metadata.get("recency", 1.0)
            result.score *= (0.7 * trust + 0.3 * recency)
        
        # Sort by final weighted score
        results.sort(key=lambda r: r.score, reverse=True)
        return results
    
    def format_context_bundle(self, results: List[RetrievalResult]) -> str:
        """
        Format retrieval results into a context string for LLM injection.
        """
        if not results:
            return "[No relevant context found]"
        
        context_parts = ["## Retrieved Context\n"]
        
        for i, result in enumerate(results, 1):
            context_parts.append(f"### Source {i}: {result.source_id} ({result.source_type})")
            context_parts.append(f"**Relevance**: {result.score:.3f}")
            context_parts.append(f"**Content**:\n{result.content}\n")
        
        return "\n".join(context_parts)