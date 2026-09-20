# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""RadixAttention Multi-Turn Audio KV Cache Engine.
=================================================
Assimilated from: sgl-project/mini-sglang & sgl-project/sglang-omni
Domain: CAMELOT-OS Omni S2S Nexus
Forged by: SIR_CODEX & SIR_SONUS

Solves multi-turn Speech-to-Speech latency degradation by preserving and
reusing KV cache vectors for continuous audio and text tokens in a Radix Tree.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class RadixNode:
    """A node in the Radix Attention tree holding cached KV state."""
    node_id: str
    tokens: Tuple[int, ...]
    children: Dict[int, RadixNode] = field(default_factory=dict)
    parent: Optional[RadixNode] = None
    kv_cache_ref: Optional[Dict[str, Any]] = None
    is_audio: bool = False
    last_accessed: float = field(default_factory=time.time)
    token_count: int = 0

    def __post_init__(self):
        self.token_count = len(self.tokens)

    def access(self) -> None:
        self.last_accessed = time.time()


class RadixAudioCache:
    """High-efficiency Radix Tree prefix cache for multi-turn S2S tokens."""

    def __init__(self, max_cached_tokens: int = 16384):
        self.max_cached_tokens = max_cached_tokens
        self.root = RadixNode(node_id="root", tokens=())
        self.total_tokens_cached = 0
        self.hits = 0
        self.misses = 0
        self._node_counter = 0

    def match_prefix(self, token_seq: List[int]) -> Tuple[Optional[RadixNode], int]:
        """Finds the deepest node matching the prefix of token_seq.
        
        Returns: (matching_node, matched_token_count)
        """
        if not token_seq:
            return self.root, 0

        curr = self.root
        curr.access()
        idx = 0
        total_matched = 0

        while idx < len(token_seq):
            first_token = token_seq[idx]
            if first_token not in curr.children:
                break

            child = curr.children[first_token]
            edge_len = len(child.tokens)

            # Compare tokens along the edge
            matched_edge = 0
            while (
                matched_edge < edge_len
                and idx + matched_edge < len(token_seq)
                and child.tokens[matched_edge] == token_seq[idx + matched_edge]
            ):
                matched_edge += 1

            if matched_edge == edge_len:
                # Full edge matched, advance to child
                curr = child
                curr.access()
                idx += edge_len
                total_matched += edge_len
            else:
                # Partial match inside edge
                total_matched += matched_edge
                break

        if total_matched > 0:
            self.hits += 1
        else:
            self.misses += 1

        return curr, total_matched

    def insert_sequence(
        self,
        token_seq: List[int],
        kv_data: Optional[Dict[str, Any]] = None,
        is_audio: bool = False,
    ) -> RadixNode:
        """Inserts token_seq into the Radix Tree, splitting edges where necessary."""
        if not token_seq:
            return self.root

        # Evict if exceeding memory budget
        if self.total_tokens_cached + len(token_seq) > self.max_cached_tokens:
            self._evict_lru(len(token_seq))

        curr = self.root
        idx = 0

        while idx < len(token_seq):
            first_token = token_seq[idx]

            if first_token not in curr.children:
                # Insert remaining tokens as a new leaf
                self._node_counter += 1
                new_node = RadixNode(
                    node_id=f"node_{self._node_counter}",
                    tokens=tuple(token_seq[idx:]),
                    parent=curr,
                    kv_cache_ref=kv_data,
                    is_audio=is_audio,
                )
                curr.children[first_token] = new_node
                self.total_tokens_cached += len(new_node.tokens)
                return new_node

            child = curr.children[first_token]
            edge_len = len(child.tokens)

            matched_edge = 0
            while (
                matched_edge < edge_len
                and idx + matched_edge < len(token_seq)
                and child.tokens[matched_edge] == token_seq[idx + matched_edge]
            ):
                matched_edge += 1

            if matched_edge == edge_len:
                # Traversed entire edge
                curr = child
                curr.access()
                idx += edge_len
            else:
                # Split edge: child becomes grandchild, create intermediate node
                self._node_counter += 1
                split_tokens = child.tokens[:matched_edge]
                remaining_child_tokens = child.tokens[matched_edge:]

                # Create intermediate split node
                split_node = RadixNode(
                    node_id=f"node_{self._node_counter}_split",
                    tokens=split_tokens,
                    parent=curr,
                    is_audio=child.is_audio,
                )
                curr.children[first_token] = split_node

                # Re-attach child under split node
                child.tokens = remaining_child_tokens
                child.parent = split_node
                child.token_count = len(remaining_child_tokens)
                split_node.children[remaining_child_tokens[0]] = child

                # Insert new branch for remaining tokens
                idx += matched_edge
                if idx < len(token_seq):
                    self._node_counter += 1
                    new_branch = RadixNode(
                        node_id=f"node_{self._node_counter}_branch",
                        tokens=tuple(token_seq[idx:]),
                        parent=split_node,
                        kv_cache_ref=kv_data,
                        is_audio=is_audio,
                    )
                    split_node.children[token_seq[idx]] = new_branch
                    self.total_tokens_cached += len(new_branch.tokens)
                    return new_branch
                else:
                    split_node.kv_cache_ref = kv_data
                    return split_node

        curr.kv_cache_ref = kv_data
        return curr

    def _evict_lru(self, tokens_needed: int) -> int:
        """Evicts oldest leaf nodes to free up token capacity."""
        evicted = 0
        leaves = self._collect_leaves(self.root)
        leaves.sort(key=lambda n: n.last_accessed)

        for leaf in leaves:
            if leaf.parent and leaf.tokens:
                first_t = leaf.tokens[0]
                if first_t in leaf.parent.children:
                    del leaf.parent.children[first_t]
                    tokens_freed = len(leaf.tokens)
                    self.total_tokens_cached = max(0, self.total_tokens_cached - tokens_freed)
                    evicted += tokens_freed
                    if evicted >= tokens_needed:
                        break

        return evicted

    def _collect_leaves(self, node: RadixNode) -> List[RadixNode]:
        if not node.children:
            return [node] if node != self.root else []
        leaves: List[RadixNode] = []
        for child in node.children.values():
            leaves.extend(self._collect_leaves(child))
        return leaves

    def get_stats(self) -> Dict[str, Any]:
        total_queries = self.hits + self.misses
        hit_rate = (self.hits / total_queries * 100.0) if total_queries > 0 else 0.0
        return {
            "cached_tokens": self.total_tokens_cached,
            "max_tokens": self.max_cached_tokens,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": round(hit_rate, 1),
            "estimated_ttft_saving_ms": round(self.hits * 18.5, 1),
        }
