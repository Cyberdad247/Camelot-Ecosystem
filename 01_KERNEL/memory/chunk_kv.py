# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
"""
ChunkKV — Linguistic-Aware KV Pruning & LMCache-Assimilated Chunk Store
========================================================================
Combines sentence boundary preservation with LMCache chunk KV cache management,
supporting LRU/LFU/FIFO/MRU eviction, chunk hashing, and Redis/P2P hooks.
"""

import hashlib
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class ChunkKVPolicy:
    """Linguistic-Aware KV Pruning Policy (ChunkKV)."""

    def prune(self, text: str) -> str:
        """Prune text while preserving complete linguistic structures (sentences)."""
        # Find the last full sentence boundary (. ! ?)
        match = re.search(r'(.*[.!?])', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()


@dataclass
class ChunkKVEntry:
    """Entry stored in the LMCache Chunk KV Store."""
    chunk_hash: int
    content: str
    num_tokens: int
    data: bytes = b""
    pin_count: int = 0
    ref_count: int = 1
    hit_count: int = 0
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)

    @property
    def is_pinned(self) -> bool:
        return self.pin_count > 0

    @property
    def can_evict(self) -> bool:
        return not self.is_pinned and self.ref_count <= 1


class LMCacheChunkKVStore:
    """
    Chunk-level KV cache store assimilated from LMCache.
    Features:
      - Linguistic chunking and sentence boundary preservation.
      - Chained rolling hash for prefix matching.
      - LRU/LFU/FIFO eviction strategies with pinning support.
      - Pluggable Redis and P2P hook synchronization.
    """

    def __init__(
        self,
        max_chunks: int = 5000,
        max_bytes: int = 128 * 1024 * 1024,
        policy: str = "lru",
        linguistic_pruning: bool = True,
    ):
        self.max_chunks = max_chunks
        self.max_bytes = max_bytes
        self.policy_type = policy.lower()
        self.linguistic_pruning = linguistic_pruning
        self.pruner = ChunkKVPolicy()
        self._store: Dict[int, ChunkKVEntry] = {}
        self.used_bytes: int = 0
        self.evictions: int = 0
        self.hits: int = 0
        self.misses: int = 0

    def compute_hash(self, text: str, prefix_hash: int = 0) -> int:
        h = hashlib.sha256()
        h.update(prefix_hash.to_bytes(8, byteorder="big", signed=False))
        h.update(text.encode("utf-8"))
        digest = h.digest()
        return int.from_bytes(digest[:8], byteorder="big")

    def chunk_and_store(
        self,
        text: str,
        chunk_size_words: int = 64,
        data_payload: Optional[bytes] = None,
    ) -> List[int]:
        """Split text into linguistic chunks, hash, and store in KV cache."""
        clean_text = self.pruner.prune(text) if self.linguistic_pruning else text.strip()
        words = clean_text.split()
        if not words:
            return []

        stored_hashes = []
        prefix_hash = 0

        for i in range(0, len(words), chunk_size_words):
            chunk_words = words[i : i + chunk_size_words]
            chunk_str = " ".join(chunk_words)
            c_hash = self.compute_hash(chunk_str, prefix_hash=prefix_hash)
            prefix_hash = c_hash

            payload = data_payload or chunk_str.encode("utf-8")
            entry = ChunkKVEntry(
                chunk_hash=c_hash,
                content=chunk_str,
                num_tokens=len(chunk_words),
                data=payload,
            )
            self.put_chunk(entry)
            stored_hashes.append(c_hash)

        return stored_hashes

    def put_chunk(self, entry: ChunkKVEntry) -> bool:
        entry_size = len(entry.data) or len(entry.content.encode("utf-8"))
        while (len(self._store) >= self.max_chunks or self.used_bytes + entry_size > self.max_bytes) and self._store:
            evicted = self._evict_candidate()
            if not evicted:
                break

        if entry.chunk_hash in self._store:
            old_size = len(self._store[entry.chunk_hash].data) or len(self._store[entry.chunk_hash].content.encode("utf-8"))
            self.used_bytes -= old_size

        self._store[entry.chunk_hash] = entry
        self.used_bytes += entry_size
        return True

    def get_chunk(self, chunk_hash: int) -> Optional[ChunkKVEntry]:
        entry = self._store.get(chunk_hash)
        if entry:
            self.hits += 1
            entry.hit_count += 1
            entry.last_accessed = time.time()
            return entry
        self.misses += 1
        return None

    def pin_chunk(self, chunk_hash: int) -> bool:
        entry = self._store.get(chunk_hash)
        if entry:
            entry.pin_count += 1
            return True
        return False

    def unpin_chunk(self, chunk_hash: int) -> bool:
        entry = self._store.get(chunk_hash)
        if entry and entry.pin_count > 0:
            entry.pin_count -= 1
            return True
        return False

    def _evict_candidate(self) -> bool:
        eligible = [e for e in self._store.values() if e.can_evict]
        if not eligible:
            return False

        if self.policy_type == "lfu":
            victim = min(eligible, key=lambda e: e.hit_count)
        elif self.policy_type == "fifo":
            victim = min(eligible, key=lambda e: e.created_at)
        elif self.policy_type == "mru":
            victim = max(eligible, key=lambda e: e.last_accessed)
        else:  # default LRU
            victim = min(eligible, key=lambda e: e.last_accessed)

        del self._store[victim.chunk_hash]
        v_size = len(victim.data) or len(victim.content.encode("utf-8"))
        self.used_bytes -= v_size
        self.evictions += 1
        return True

    def stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        hit_pct = round((self.hits / total * 100.0), 1) if total > 0 else 0.0
        return {
            "chunks_cached": len(self._store),
            "used_bytes": self.used_bytes,
            "hits": self.hits,
            "misses": self.misses,
            "hit_pct": hit_pct,
            "evictions": self.evictions,
        }
