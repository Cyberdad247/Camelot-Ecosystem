# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
MEMORY DECAY PHIAL: Smart Forgetting Engine
Extracted from: supermemoryai/supermemory architecture
Purpose: Reduce context waste by ~40% via intelligent memory pruning.

The algorithm mimics human memory decay:
- Recency: Recently accessed memories score higher.
- Access Frequency: Frequently accessed memories persist.
- Relevance Decay: Unused memories fade over time.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MemoryNode:
    """A single memory unit with decay tracking."""

    id: str
    content: str
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    relevance_score: float = 1.0
    metadata: Dict = field(default_factory=dict)

    def touch(self):
        """Mark memory as accessed."""
        self.last_accessed = time.time()
        self.access_count += 1


class MemoryDecayEngine:
    """
    Implements "Smart Forgetting" from supermemory architecture.

    Core formula:
        decay_score = (recency_weight * recency_factor) + (access_weight * access_factor)

    Where:
        recency_factor = 1 / (1 + time_since_access_hours)
        access_factor = min(access_count / max_access_norm, 1.0)
    """

    def __init__(
        self,
        recency_weight: float = 0.6,
        access_weight: float = 0.4,
        decay_threshold: float = 0.2,
        max_access_norm: int = 10,
        max_age_hours: float = 168.0,  # 7 days default
    ):
        self.recency_weight = recency_weight
        self.access_weight = access_weight
        self.decay_threshold = decay_threshold
        self.max_access_norm = max_access_norm
        self.max_age_hours = max_age_hours
        self.memory_store: Dict[str, MemoryNode] = {}

    def add(self, node: MemoryNode) -> None:
        """Add a memory node to the store."""
        self.memory_store[node.id] = node

    def get(self, node_id: str) -> Optional[MemoryNode]:
        """Retrieve and touch a memory node."""
        node = self.memory_store.get(node_id)
        if node:
            node.touch()
        return node

    def compute_decay_score(self, node: MemoryNode) -> float:
        """Compute the current decay score for a memory node."""
        now = time.time()
        time_since_access_hours = (now - node.last_accessed) / 3600.0

        # Recency factor: decays as time passes
        recency_factor = 1.0 / (1.0 + time_since_access_hours)

        # Access factor: normalized by max_access_norm
        access_factor = min(node.access_count / self.max_access_norm, 1.0)

        # Weighted sum
        score = (self.recency_weight * recency_factor) + (self.access_weight * access_factor)

        return score

    def prune(self) -> List[str]:
        """
        Remove memories below the decay threshold.
        Returns list of pruned node IDs.
        """
        pruned_ids = []
        for node_id, node in list(self.memory_store.items()):
            score = self.compute_decay_score(node)
            if score < self.decay_threshold:
                del self.memory_store[node_id]
                pruned_ids.append(node_id)
        return pruned_ids

    def get_active_memories(self, top_k: int = 10) -> List[MemoryNode]:
        """Return top-k memories by decay score."""
        scored = [(self.compute_decay_score(n), n) for n in self.memory_store.values()]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [n for _, n in scored[:top_k]]

    def stats(self) -> Dict:
        """Return memory pool statistics."""
        return {
            "total_nodes": len(self.memory_store),
            "decay_threshold": self.decay_threshold,
            "avg_access_count": sum(n.access_count for n in self.memory_store.values())
            / max(len(self.memory_store), 1),
        }


# ═══════════════════════════════════════════════════════════════════
# CAMELOT INTEGRATION POINT
# ═══════════════════════════════════════════════════════════════════

_global_decay_engine: Optional[MemoryDecayEngine] = None


def get_decay_engine() -> MemoryDecayEngine:
    """Singleton accessor for Camelot Kernel integration."""
    global _global_decay_engine
    if _global_decay_engine is None:
        _global_decay_engine = MemoryDecayEngine()
    return _global_decay_engine


if __name__ == "__main__":
    # Quick demo
    engine = MemoryDecayEngine(decay_threshold=0.3)

    # Add some memories
    engine.add(MemoryNode(id="mem_1", content="Important fact", access_count=5))
    engine.add(MemoryNode(id="mem_2", content="Barely used fact", access_count=0))
    engine.add(MemoryNode(id="mem_3", content="Old fact", last_accessed=time.time() - 86400 * 3))  # 3 days old

    print("Before prune:", engine.stats())

    pruned = engine.prune()
    print(f"Pruned: {pruned}")
    print("After prune:", engine.stats())