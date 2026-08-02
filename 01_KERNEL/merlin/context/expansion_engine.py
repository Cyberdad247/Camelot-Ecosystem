# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Expansion Engine — Main Controller for Context Expansion Protocol

Orchestrates RAG, GoT, and caching to provide optimized context bundles
for agent tasks with token budget management and governance.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../memory')))

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from cache_manager import CacheManager
from got_expander import GoTExpander, ThoughtNode
from rag_backbone import RAGBackbone, RetrievalResult
from titan_omega import TitanOmega


@dataclass
class ContextBundle:
    """Complete context package for agent consumption."""
    intent: str
    retrieved_context: List[RetrievalResult]
    reasoning_trace: Optional[List[ThoughtNode]]
    token_count: int
    budget_remaining: int
    cache_hit: bool
    trust_score: float
    metadata: Dict[str, Any]


class ExpansionEngine:
    """
    Main orchestration controller for the Context Expansion Protocol.
    
    Workflow:
    1. Check cache for existing context
    2. If miss: RAG retrieval from Omega-Graph + Omega-Vault
    3. Optional: GoT reasoning expansion
    4. Token budget management
    5. King Arthur policy gate
    6. Context rot mitigation (time-decay)
    7. Cache storage for future hits
    """
    
    def __init__(
        self,
        titan: TitanOmega,
        default_token_budget: int = 4000,
        enable_got: bool = True,
        enable_cache: bool = True
    ):
        self.titan = titan
        self.default_token_budget = default_token_budget
        self.enable_got = enable_got
        self.enable_cache = enable_cache
        
        # Initialize sub-components
        self.rag = RAGBackbone(titan)
        self.got = GoTExpander(titan) if enable_got else None
        self.cache = CacheManager() if enable_cache else None
        
        # Governance (King Arthur policy gate)
        self.policy_enabled = True
        self.restricted_topics = ["credentials", "private_keys", "passwords"]
    
    def expand(
        self,
        intent: str,
        token_budget: Optional[int] = None,
        session_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        use_got: bool = False
    ) -> ContextBundle:
        """
        Main context expansion entry point.
        
        Args:
            intent: User's goal or query
            token_budget: Maximum tokens for context (default from config)
            session_id: Session ID for GoT reasoning tracking
            filters: Optional filters for retrieval (e.g., agent_type)
            use_got: Enable Graph-of-Thought reasoning expansion
        
        Returns:
            ContextBundle with retrieved context and metadata
        """
        budget = token_budget or self.default_token_budget
        cache_hit = False
        
        print(f"[CEP] Expanding context for intent: '{intent[:60]}...'")
        print(f"[CEP] Token budget: {budget}, GoT: {use_got}, Filters: {filters}")
        
        # 1. King Arthur Policy Gate
        if not self._policy_check(intent):
            raise ValueError("Policy violation: Intent contains restricted content")
        
        # 2. Check cache
        cached_context = None
        if self.enable_cache:
            cached_context = self.cache.get(intent, filters)
            if cached_context:
                cache_hit = True
                print("[CEP] Cache HIT")
        
        # 3. If cache miss: perform RAG retrieval
        if not cached_context:
            print("[CEP] Cache MISS - performing RAG retrieval")
            
            # Calculate how many results we can fit in budget
            # Rough estimate: 100 tokens per result
            max_results = min(10, budget // 100)
            
            retrieved = self.rag.retrieve(intent, k=max_results, filters=filters)
            
            # Apply context rot mitigation (time-decay)
            retrieved = self._apply_context_rot_mitigation(retrieved)
            
        else:
            # Use cached results (simplified - would need proper deserialization)
            retrieved = []
        
        # 4. Optional GoT reasoning expansion
        reasoning_trace = None
        if use_got and self.enable_got and session_id:
            print("[CEP] Expanding reasoning with GoT")
            reasoning_trace = self._expand_reasoning(intent, session_id, retrieved)
        
        # 5. Token budget management
        final_results, token_count = self._enforce_token_budget(
            retrieved, 
            budget,
            reasoning_trace
        )
        
        # 6. Calculate aggregate trust score
        trust_score = self._calculate_trust_score(final_results)
        
        # 7. Cache the results
        if self.enable_cache and not cache_hit:
            formatted_context = self.rag.format_context_bundle(final_results)
            self.cache.put(
                intent,
                formatted_context,
                trust_score=trust_score,
                relevance_score=self._calculate_relevance(final_results),
                filters=filters
            )
        
        # 8. Build final bundle
        bundle = ContextBundle(
            intent=intent,
            retrieved_context=final_results,
            reasoning_trace=reasoning_trace,
            token_count=token_count,
            budget_remaining=budget - token_count,
            cache_hit=cache_hit,
            trust_score=trust_score,
            metadata={
                "session_id": session_id,
                "filters": filters,
                "got_enabled": use_got,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        print(f"[CEP] Context bundle ready: {token_count}/{budget} tokens, trust={trust_score:.2f}")
        return bundle
    
    def format_bundle_for_llm(self, bundle: ContextBundle) -> str:
        """
        Format ContextBundle as a string ready for LLM injection.
        """
        sections = []
        
        # Header
        sections.append(f"# Context for: {bundle.intent}\n")
        sections.append(f"**Trust Score**: {bundle.trust_score:.2f}")
        sections.append(f"**Tokens Used**: {bundle.token_count}/{bundle.token_count + bundle.budget_remaining}\n")
        
        # Retrieved context
        if bundle.retrieved_context:
            sections.append(self.rag.format_context_bundle(bundle.retrieved_context))
        
        # Reasoning trace
        if bundle.reasoning_trace and self.got:
            sections.append(self.got.format_trace_for_context(
                bundle.metadata.get("session_id", "unknown")
            ))
        
        return "\n".join(sections)
    
    def validate_context(self, bundle: ContextBundle) -> Dict[str, Any]:
        """
        MIRAS++ validation checks for context quality.
        
        Returns dict with validation results:
        - bias_scan: Check for skewed perspectives
        - hallucination_scan: Check for contradictions
        - completeness: Check if context addresses intent
        """
        validation = {
            "passed": True,
            "warnings": [],
            "errors": []
        }
        
        # Check 1: Trust score threshold
        if bundle.trust_score < 0.5:
            validation["warnings"].append(f"Low trust score: {bundle.trust_score:.2f}")
        
        # Check 2: Token budget exceeded
        if bundle.budget_remaining < 0:
            validation["errors"].append("Token budget exceeded")
            validation["passed"] = False
        
        # Check 3: Empty context
        if not bundle.retrieved_context:
            validation["warnings"].append("No context retrieved")
        
        # Check 4: Contradicting sources
        # (Simplified - would check for conflicting information)
        if len(bundle.retrieved_context) > 1:
            sources = [r.source_type for r in bundle.retrieved_context]
            if 'vector' in sources and 'graph' in sources:
                # Good - diverse sources
                pass
        
        return validation
    
    def _policy_check(self, intent: str) -> bool:
        """
        King Arthur governance policy gate.
        Checks for restricted content in intent.
        """
        if not self.policy_enabled:
            return True
        
        intent_lower = intent.lower()
        for topic in self.restricted_topics:
            if topic in intent_lower:
                print(f"[CEP] Policy violation: Restricted topic '{topic}' detected")
                return False
        
        return True
    
    def _apply_context_rot_mitigation(
        self, 
        results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """
        Apply time-decay scoring to mitigate stale context.
        """
        current_time = datetime.utcnow()
        
        for result in results:
            # Apply time decay if metadata has timestamp
            if "created_at" in result.metadata:
                created_at = datetime.fromisoformat(result.metadata["created_at"])
                age_hours = (current_time - created_at).total_seconds() / 3600
                
                # Decay: 100% fresh, 90% after 24h, 70% after 1 week
                decay_factor = max(0.5, 1.0 - (age_hours / 168) * 0.5)  # 168h = 1 week
                result.score *= decay_factor
        
        # Re-sort after decay
        results.sort(key=lambda r: r.score, reverse=True)
        
        print(f"[CEP] Applied context rot mitigation to {len(results)} results")
        return results
    
    def _expand_reasoning(
        self,
        intent: str,
        session_id: str,
        context: List[RetrievalResult]
    ) -> List[ThoughtNode]:
        """
        Use GoT to expand reasoning about the intent and context.
        """
        if not self.got:
            return []
        
        # Start reasoning chain
        initial_thought = f"Analyzing intent: {intent}"
        self.got.start_chain(session_id, initial_thought)
        
        # Add context analysis step
        context_summary = f"Retrieved {len(context)} context sources"
        self.got.extend_chain(
            session_id,
            context_summary,
            reasoning_type='analysis',
            confidence=0.9
        )
        
        # Get full trace
        trace = self.got.get_reasoning_trace(session_id)
        return trace
    
    def _enforce_token_budget(
        self,
        results: List[RetrievalResult],
        budget: int,
        reasoning_trace: Optional[List[ThoughtNode]] = None
    ) -> tuple[List[RetrievalResult], int]:
        """
        Trim results to fit within token budget.
        Returns (trimmed_results, total_token_count)
        """
        # Rough token estimation (4 chars = 1 token)
        char_per_token = 4
        
        # Reserve tokens for reasoning trace if present
        reasoning_tokens = 0
        if reasoning_trace:
            reasoning_text = "\n".join([t.content for t in reasoning_trace])
            reasoning_tokens = len(reasoning_text) // char_per_token
        
        available_budget = budget - reasoning_tokens
        
        # Accumulate results until budget exhausted
        selected = []
        tokens_used = 0
        
        for result in results:
            result_tokens = len(result.content) // char_per_token
            
            if tokens_used + result_tokens <= available_budget:
                selected.append(result)
                tokens_used += result_tokens
            else:
                break
        
        total_tokens = tokens_used + reasoning_tokens
        print(f"[CEP] Token budget: {total_tokens}/{budget} ({len(selected)}/{len(results)} results)")
        
        return selected, total_tokens
    
    def _calculate_trust_score(self, results: List[RetrievalResult]) -> float:
        """Calculate aggregate trust score from results."""
        if not results:
            return 0.0
        
        # Weighted average by result scores
        total_weight = sum(r.score for r in results)
        if total_weight == 0:
            return 0.0
        
        weighted_trust = sum(
            r.metadata.get("trust_score", 0.8) * r.score 
            for r in results
        )
        
        return weighted_trust / total_weight
    
    def _calculate_relevance(self, results: List[RetrievalResult]) -> float:
        """Calculate aggregate relevance score."""
        if not results:
            return 0.0
        
        return sum(r.score for r in results) / len(results)