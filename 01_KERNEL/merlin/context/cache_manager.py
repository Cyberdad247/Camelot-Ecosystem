# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Cache Manager — Adaptive Multi-Tier Caching

Implements hot/warm/cold cache tiers with LRU × relevance × trust scoring
and TTL-based expiration for the Context Expansion Protocol.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../memory')))

import hashlib
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class CacheEntry:
    """Entry in the context cache."""
    cache_key: str
    content: str
    tier: str  # 'hot', 'warm', 'cold'
    trust_score: float
    relevance_score: float
    access_count: int
    created_at: datetime
    last_accessed: datetime
    ttl_seconds: int
    
    def is_expired(self) -> bool:
        """Check if entry has exceeded TTL."""
        elapsed = (datetime.utcnow() - self.created_at).total_seconds()
        return elapsed > self.ttl_seconds
    
    def recency_score(self) -> float:
        """Calculate time-decay score (1.0 = just created, decays to 0)."""
        elapsed = (datetime.utcnow() - self.last_accessed).total_seconds()
        # Decay rate: 50% after 1 hour, 25% after 2 hours
        decay_rate = 0.001  # per second
        return max(0.0, 1.0 - (elapsed * decay_rate))
    
    def composite_score(self) -> float:
        """
        Calculate composite priority score for cache eviction.
        Higher score = higher priority to keep in cache.
        """
        usage_factor = min(1.0, self.access_count / 10.0)  # Cap at 10 accesses
        recency_factor = self.recency_score()
        
        return (
            0.4 * usage_factor +
            0.3 * recency_factor +
            0.2 * self.trust_score +
            0.1 * self.relevance_score
        )


class CacheManager:
    """
    Adaptive multi-tier cache for context retrieval results.
    
    Tiers:
    - Hot: Frequently accessed, high trust, recent (LRU size: 50)
    - Warm: Moderately accessed, medium trust (LRU size: 200)
    - Cold: Rarely accessed, low trust, older (LRU size: 500)
    
    Eviction: LRU × composite_score
    """
    
    def __init__(
        self,
        hot_size: int = 50,
        warm_size: int = 200,
        cold_size: int = 500,
        default_ttl: int = 3600  # 1 hour
    ):
        self.hot_size = hot_size
        self.warm_size = warm_size
        self.cold_size = cold_size
        self.default_ttl = default_ttl
        
        # OrderedDict for LRU behavior
        self.hot_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.warm_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.cold_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        
        # Stats
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "promotions": 0,
            "demotions": 0
        }
    
    def get(self, query: str, filters: Optional[Dict] = None) -> Optional[str]:
        """
        Retrieve cached content for a query.
        
        Args:
            query: Query string
            filters: Optional filters used in the query
        
        Returns:
            Cached content if found, None otherwise
        """
        cache_key = self._generate_key(query, filters)
        
        # Check hot cache first
        if cache_key in self.hot_cache:
            entry = self.hot_cache[cache_key]
            if not entry.is_expired():
                self._access_entry(entry, "hot")
                self.stats["hits"] += 1
                return entry.content
            else:
                del self.hot_cache[cache_key]
        
        # Check warm cache
        if cache_key in self.warm_cache:
            entry = self.warm_cache[cache_key]
            if not entry.is_expired():
                self._access_entry(entry, "warm")
                self._promote_to_hot(cache_key, entry)
                self.stats["hits"] += 1
                return entry.content
            else:
                del self.warm_cache[cache_key]
        
        # Check cold cache
        if cache_key in self.cold_cache:
            entry = self.cold_cache[cache_key]
            if not entry.is_expired():
                self._access_entry(entry, "cold")
                self._promote_to_warm(cache_key, entry)
                self.stats["hits"] += 1
                return entry.content
            else:
                del self.cold_cache[cache_key]
        
        self.stats["misses"] += 1
        return None
    
    def put(
        self,
        query: str,
        content: str,
        trust_score: float = 0.8,
        relevance_score: float = 0.8,
        filters: Optional[Dict] = None,
        ttl: Optional[int] = None
    ):
        """
        Store content in cache with automatic tier assignment.
        """
        cache_key = self._generate_key(query, filters)
        
        # Create new entry
        entry = CacheEntry(
            cache_key=cache_key,
            content=content,
            tier="hot",  # New entries start hot
            trust_score=trust_score,
            relevance_score=relevance_score,
            access_count=1,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            ttl_seconds=ttl or self.default_ttl
        )
        
        # Store in hot cache
        self.hot_cache[cache_key] = entry
        self._enforce_size_limit("hot")
        
        print(f"[Cache] Stored in HOT tier: {cache_key[:16]}...")
    
    def invalidate(self, query: str, filters: Optional[Dict] = None):
        """Remove entry from all cache tiers."""
        cache_key = self._generate_key(query, filters)
        
        if cache_key in self.hot_cache:
            del self.hot_cache[cache_key]
        if cache_key in self.warm_cache:
            del self.warm_cache[cache_key]
        if cache_key in self.cold_cache:
            del self.cold_cache[cache_key]
        
        print(f"[Cache] Invalidated: {cache_key[:16]}...")
    
    def cleanup_expired(self):
        """Remove all expired entries across all tiers."""
        removed = 0
        
        # Hot tier
        expired_hot = [k for k, v in self.hot_cache.items() if v.is_expired()]
        for key in expired_hot:
            del self.hot_cache[key]
            removed += 1
        
        # Warm tier
        expired_warm = [k for k, v in self.warm_cache.items() if v.is_expired()]
        for key in expired_warm:
            del self.warm_cache[key]
            removed += 1
        
        # Cold tier
        expired_cold = [k for k, v in self.cold_cache.items() if v.is_expired()]
        for key in expired_cold:
            del self.cold_cache[key]
            removed += 1
        
        if removed > 0:
            print(f"[Cache] Cleaned up {removed} expired entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Return cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0.0
        
        return {
            **self.stats,
            "hit_rate": hit_rate,
            "hot_size": len(self.hot_cache),
            "warm_size": len(self.warm_cache),
            "cold_size": len(self.cold_cache),
            "total_cached": len(self.hot_cache) + len(self.warm_cache) + len(self.cold_cache)
        }
    
    def _generate_key(self, query: str, filters: Optional[Dict]) -> str:
        """Generate cache key from query and filters."""
        key_base = query
        if filters:
            key_base += str(sorted(filters.items()))
        
        return hashlib.sha256(key_base.encode()).hexdigest()
    
    def _access_entry(self, entry: CacheEntry, tier: str):
        """Update access metadata for an entry."""
        entry.access_count += 1
        entry.last_accessed = datetime.utcnow()
        
        # Move to end of OrderedDict (most recently used)
        if tier == "hot":
            self.hot_cache.move_to_end(entry.cache_key)
        elif tier == "warm":
            self.warm_cache.move_to_end(entry.cache_key)
        else:
            self.cold_cache.move_to_end(entry.cache_key)
    
    def _promote_to_hot(self, key: str, entry: CacheEntry):
        """Promote entry from warm to hot tier."""
        del self.warm_cache[key]
        entry.tier = "hot"
        self.hot_cache[key] = entry
        self._enforce_size_limit("hot")
        self.stats["promotions"] += 1
        print(f"[Cache] Promoted to HOT: {key[:16]}...")
    
    def _promote_to_warm(self, key: str, entry: CacheEntry):
        """Promote entry from cold to warm tier."""
        del self.cold_cache[key]
        entry.tier = "warm"
        self.warm_cache[key] = entry
        self._enforce_size_limit("warm")
        self.stats["promotions"] += 1
    
    def _demote_to_warm(self, key: str, entry: CacheEntry):
        """Demote entry from hot to warm tier."""
        del self.hot_cache[key]
        entry.tier = "warm"
        self.warm_cache[key] = entry
        self.stats["demotions"] += 1
    
    def _demote_to_cold(self, key: str, entry: CacheEntry):
        """Demote entry from warm to cold tier."""
        del self.warm_cache[key]
        entry.tier = "cold"
        self.cold_cache[key] = entry
        self.stats["demotions"] += 1
    
    def _enforce_size_limit(self, tier: str):
        """Evict least valuable entries if tier exceeds size limit."""
        if tier == "hot" and len(self.hot_cache) > self.hot_size:
            # Evict based on composite score
            victim_key = self._find_eviction_victim(self.hot_cache)
            victim = self.hot_cache[victim_key]
            self._demote_to_warm(victim_key, victim)
            self.stats["evictions"] += 1
        
        elif tier == "warm" and len(self.warm_cache) > self.warm_size:
            victim_key = self._find_eviction_victim(self.warm_cache)
            victim = self.warm_cache[victim_key]
            self._demote_to_cold(victim_key, victim)
            self.stats["evictions"] += 1
        
        elif tier == "cold" and len(self.cold_cache) > self.cold_size:
            # Cold evictions are permanent
            victim_key = self._find_eviction_victim(self.cold_cache)
            del self.cold_cache[victim_key]
            self.stats["evictions"] += 1
    
    def _find_eviction_victim(self, cache: OrderedDict) -> str:
        """
        Find entry with lowest composite score for eviction.
        Falls back to LRU if scores are equal.
        """
        if not cache:
            raise ValueError("Cannot evict from empty cache")
        
        # Score all entries
        scored_entries = [(k, v.composite_score()) for k, v in cache.items()]
        
        # Sort by score (ascending) - lowest score first
        scored_entries.sort(key=lambda x: x[1])
        
        # Return key with lowest score
        return scored_entries[0][0]