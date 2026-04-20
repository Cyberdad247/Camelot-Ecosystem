# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Graph-of-Thought (GoT) Expander

Creates intermediate reasoning nodes as ephemeral graph fragments stored in Ω-Flux.
These fragments help track multi-step reasoning chains and enable trace reconstruction.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../memory')))

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
from titan_omega import TitanOmega


@dataclass
class ThoughtNode:
    """Represents a single reasoning step in a Graph-of-Thought."""
    thought_id: str
    step_number: int
    content: str
    reasoning_type: str  # 'analysis', 'hypothesis', 'critique', 'synthesis'
    parent_ids: List[str]  # Links to previous thoughts
    confidence: float  # 0-1 confidence in this reasoning step
    metadata: Dict[str, Any]


class GoTExpander:
    """
    Graph-of-Thought expansion engine for multi-step reasoning.
    
    Creates ephemeral reasoning fragments stored in Ω-Flux with TTL.
    These fragments form a directed acyclic graph (DAG) of thought progression.
    """
    
    def __init__(self, titan: TitanOmega, default_ttl: int = 300):
        self.titan = titan
        self.default_ttl = default_ttl  # 5 minutes default TTL
        self.active_chains: Dict[str, List[ThoughtNode]] = {}
    
    def start_chain(self, session_id: str, initial_thought: str) -> ThoughtNode:
        """
        Start a new reasoning chain.
        
        Args:
            session_id: Session identifier
            initial_thought: Initial reasoning step
        
        Returns:
            ThoughtNode representing the first step
        """
        thought_id = self._generate_thought_id(session_id, 0)
        
        node = ThoughtNode(
            thought_id=thought_id,
            step_number=0,
            content=initial_thought,
            reasoning_type='analysis',
            parent_ids=[],
            confidence=1.0,
            metadata={
                "session_id": session_id,
                "created_at": datetime.utcnow().isoformat()
            }
        )
        
        # Store in Ω-Flux
        self._store_thought_in_flux(node)
        
        # Track in active chains
        self.active_chains[session_id] = [node]
        
        print(f"[GoT] Started reasoning chain for session {session_id}")
        return node
    
    def extend_chain(
        self,
        session_id: str,
        content: str,
        reasoning_type: str = 'analysis',
        parent_ids: Optional[List[str]] = None,
        confidence: float = 0.8
    ) -> ThoughtNode:
        """
        Add a new reasoning step to an existing chain.
        
        Args:
            session_id: Session identifier
            content: Reasoning content
            reasoning_type: Type of reasoning step
            parent_ids: IDs of parent thoughts (defaults to last thought)
            confidence: Confidence in this step
        
        Returns:
            New ThoughtNode
        """
        if session_id not in self.active_chains:
            raise ValueError(f"No active chain for session {session_id}")
        
        chain = self.active_chains[session_id]
        step_number = len(chain)
        
        # Default to last thought as parent
        if parent_ids is None:
            parent_ids = [chain[-1].thought_id] if chain else []
        
        thought_id = self._generate_thought_id(session_id, step_number)
        
        node = ThoughtNode(
            thought_id=thought_id,
            step_number=step_number,
            content=content,
            reasoning_type=reasoning_type,
            parent_ids=parent_ids,
            confidence=confidence,
            metadata={
                "session_id": session_id,
                "created_at": datetime.utcnow().isoformat()
            }
        )
        
        # Store in Ω-Flux
        self._store_thought_in_flux(node)
        
        # Add to active chain
        chain.append(node)
        
        print(f"[GoT] Extended chain: step {step_number} ({reasoning_type})")
        return node
    
    def branch_chain(
        self,
        session_id: str,
        branch_content: str,
        parent_thought_id: str,
        reasoning_type: str = 'hypothesis'
    ) -> ThoughtNode:
        """
        Create a branch point in reasoning (exploring alternative paths).
        
        Args:
            session_id: Session identifier
            branch_content: Content of the branch
            parent_thought_id: ID of the thought to branch from
            reasoning_type: Type of reasoning
        
        Returns:
            New branched ThoughtNode
        """
        if session_id not in self.active_chains:
            raise ValueError(f"No active chain for session {session_id}")
        
        chain = self.active_chains[session_id]
        step_number = len(chain)
        
        thought_id = self._generate_thought_id(session_id, step_number)
        
        node = ThoughtNode(
            thought_id=thought_id,
            step_number=step_number,
            content=branch_content,
            reasoning_type=reasoning_type,
            parent_ids=[parent_thought_id],
            confidence=0.7,  # Branches start with lower confidence
            metadata={
                "session_id": session_id,
                "is_branch": True,
                "created_at": datetime.utcnow().isoformat()
            }
        )
        
        self._store_thought_in_flux(node)
        chain.append(node)
        
        print(f"[GoT] Created branch from {parent_thought_id}")
        return node
    
    def get_reasoning_trace(self, session_id: str) -> List[ThoughtNode]:
        """
        Retrieve the full reasoning trace for a session.
        
        Returns list of ThoughtNodes in chronological order.
        """
        if session_id in self.active_chains:
            return self.active_chains[session_id]
        
        # Try to reconstruct from Ω-Flux
        flux_events = self.titan.flux.get_session_events(session_id)
        
        thoughts = []
        for event in flux_events:
            if event.content.startswith("[GoT]"):
                # Parse thought from flux event
                # This is a simplified reconstruction
                thoughts.append(self._parse_thought_from_flux(event.content))
        
        return thoughts
    
    def format_trace_for_context(self, session_id: str) -> str:
        """
        Format reasoning trace as human-readable context for LLM injection.
        """
        trace = self.get_reasoning_trace(session_id)
        
        if not trace:
            return "[No reasoning trace available]"
        
        lines = ["## Reasoning Trace\n"]
        
        for node in trace:
            icon = self._get_reasoning_icon(node.reasoning_type)
            lines.append(f"**Step {node.step_number}** {icon} [{node.reasoning_type}] (confidence: {node.confidence:.2f})")
            lines.append(f"{node.content}\n")
        
        return "\n".join(lines)
    
    def prune_low_confidence_branches(self, session_id: str, threshold: float = 0.5):
        """
        Remove low-confidence reasoning branches to clean up the trace.
        """
        if session_id not in self.active_chains:
            return
        
        chain = self.active_chains[session_id]
        pruned_chain = [node for node in chain if node.confidence >= threshold]
        
        removed = len(chain) - len(pruned_chain)
        if removed > 0:
            self.active_chains[session_id] = pruned_chain
            print(f"[GoT] Pruned {removed} low-confidence nodes from chain")
    
    def _generate_thought_id(self, session_id: str, step: int) -> str:
        """Generate unique thought ID."""
        base = f"{session_id}:{step}:{datetime.utcnow().isoformat()}"
        return f"thought_{hashlib.sha256(base.encode()).hexdigest()[:12]}"
    
    def _store_thought_in_flux(self, node: ThoughtNode):
        """Store ThoughtNode in Ω-Flux as ephemeral event."""
        content = f"[GoT] Step {node.step_number} ({node.reasoning_type}): {node.content}"
        
        self.titan.flux.store_event(
            session_id=node.metadata["session_id"],
            content=content,
            priority="high" if node.confidence > 0.8 else "medium",
            ttl=self.default_ttl
        )
    
    def _parse_thought_from_flux(self, flux_content: str) -> ThoughtNode:
        """Reconstruct ThoughtNode from flux event content (simplified)."""
        # This is a basic reconstruction - in production would parse full metadata
        return ThoughtNode(
            thought_id="reconstructed",
            step_number=0,
            content=flux_content,
            reasoning_type='unknown',
            parent_ids=[],
            confidence=0.5,
            metadata={}
        )
    
    def _get_reasoning_icon(self, reasoning_type: str) -> str:
        """Get emoji icon for reasoning type."""
        icons = {
            'analysis': '🔍',
            'hypothesis': '💡',
            'critique': '⚖️',
            'synthesis': '🔗',
            'conclusion': '✅'
        }
        return icons.get(reasoning_type, '📝')