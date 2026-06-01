# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Supermemory Adapter for Titan Memory System
Knight: Sir Chronos (Memory Systems)
Version: 1.0.0
Date: 2026-01-27
"""

from abc import ABC, abstractmethod
from typing import Dict, List

import requests


class MemoryAdapter(ABC):
    """Abstract base class for memory adapters"""

    @abstractmethod
    def add(self, content: str, metadata: dict) -> str:
        """Add memory, return ID"""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> list:
        """Semantic search, return results"""
        pass

    @abstractmethod
    def get(self, memory_id: str) -> dict:
        """Retrieve specific memory"""
        pass

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete memory"""
        pass


class SupermemoryAdapter(MemoryAdapter):
    """Adapter for Supermemory API"""

    def __init__(self, api_url: str, api_key: str):
        """
        Initialize Supermemory adapter

        Args:
            api_url: Base URL for Supermemory API (e.g., http://localhost:3000/api)
            api_key: API key for authentication
        """
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    def add(self, content: str, metadata: dict = None) -> str:
        """
        Add memory to Supermemory

        Args:
            content: Memory content (text)
            metadata: Optional metadata (source, tags, etc.)

        Returns:
            Memory ID
        """
        if metadata is None:
            metadata = {}

        payload = {
            "content": content,
            "type": metadata.get("type", "note"),
            "metadata": {
                "source": metadata.get("source", "camelot_os"),
                "tags": metadata.get("tags", []),
                "knight": metadata.get("knight", "unknown"),
                "timestamp": metadata.get("timestamp", ""),
            },
        }

        try:
            response = requests.post(f"{self.api_url}/memories", headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("id", "")
        except requests.exceptions.RequestException as e:
            print(f"[SUPERMEMORY] ERROR adding memory: {e}")
            return ""

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Semantic search across memories

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of memory results with relevance scores
        """
        try:
            response = requests.get(
                f"{self.api_url}/memories/search", headers=self.headers, params={"q": query, "limit": limit}, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except requests.exceptions.RequestException as e:
            print(f"[SUPERMEMORY] ERROR searching memories: {e}")
            return []

    def get(self, memory_id: str) -> Dict:
        """
        Retrieve specific memory by ID

        Args:
            memory_id: Memory ID

        Returns:
            Memory data
        """
        try:
            response = requests.get(f"{self.api_url}/memories/{memory_id}", headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[SUPERMEMORY] ERROR retrieving memory: {e}")
            return {}

    def delete(self, memory_id: str) -> bool:
        """
        Delete memory by ID

        Args:
            memory_id: Memory ID

        Returns:
            True if successful
        """
        try:
            response = requests.delete(f"{self.api_url}/memories/{memory_id}", headers=self.headers, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"[SUPERMEMORY] ERROR deleting memory: {e}")
            return False

    def batch_add(self, memories: List[Dict]) -> List[str]:
        """
        Add multiple memories in batch

        Args:
            memories: List of {content, metadata} dicts

        Returns:
            List of memory IDs
        """
        ids = []
        for memory in memories:
            memory_id = self.add(memory.get("content", ""), memory.get("metadata", {}))
            if memory_id:
                ids.append(memory_id)
        return ids


class TitanMemoryBridge:
    """Bridge between Titan Memory and Supermemory"""

    def __init__(self, supermemory_adapter: SupermemoryAdapter):
        self.supermemory = supermemory_adapter
        self.fallback_enabled = True

    def store_memory(self, content: str, knight: str = "unknown", tags: List[str] = None) -> str:
        """
        Store memory with Titan Memory interface

        Args:
            content: Memory content
            knight: Knight who created the memory
            tags: Optional tags

        Returns:
            Memory ID
        """
        if tags is None:
            tags = []

        metadata = {"knight": knight, "tags": tags, "source": "titan_memory", "type": "note"}

        return self.supermemory.add(content, metadata)

    def recall_memory(self, query: str, limit: int = 5) -> List[str]:
        """
        Recall memories using semantic search

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of memory contents
        """
        results = self.supermemory.search(query, limit)
        return [r.get("content", "") for r in results]

    def get_knight_memories(self, knight: str, limit: int = 10) -> List[Dict]:
        """
        Get all memories for a specific knight

        Args:
            knight: Knight name
            limit: Maximum results

        Returns:
            List of memories
        """
        # Search by knight tag
        query = f"knight:{knight}"
        return self.supermemory.search(query, limit)


# Example usage
if __name__ == "__main__":
    # Initialize adapter using environment variables (Titan Protocol)
    import os
    API_URL = os.getenv("SUPERMEMORY_API_URL", "http://localhost:3000/api")
    API_KEY = os.getenv("SUPERMEMORY_API_KEY", "your_api_key_here")
    
    adapter = SupermemoryAdapter(api_url=API_URL, api_key=API_KEY)

    # Create bridge
    bridge = TitanMemoryBridge(adapter)

    # Test storing memory
    print("Testing Supermemory adapter...")
    memory_id = bridge.store_memory(
        content="LangGraph provides graph-based agent orchestration",
        knight="Sir Oracle",
        tags=["langgraph", "agents", "orchestration"],
    )
    print(f"Stored memory: {memory_id}")

    # Test recall
    results = bridge.recall_memory("agent orchestration")
    print(f"Recalled {len(results)} memories")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result[:100]}...")