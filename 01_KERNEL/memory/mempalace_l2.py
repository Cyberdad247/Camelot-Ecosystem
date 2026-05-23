import os
import json
from pathlib import Path
from typing import Any, Optional

try:
    import chromadb
except ImportError:
    chromadb = None

class MemPalaceL2:
    """Persistent local vector index manager (Layer 2 Memory)."""

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path:
            self.storage_path = storage_path
        else:
            # Default to 03_VAULT/memory/l2_index
            repo_root = Path(__file__).resolve().parent.parent.parent
            self.storage_path = repo_root / "03_VAULT" / "memory" / "l2_index"
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        if chromadb:
            self.client = chromadb.PersistentClient(path=str(self.storage_path))
        else:
            self.client = None
            # Log warning or handle gracefully
            print("WARNING: chromadb not installed. L2 Memory is in DARK mode.")

    def _get_collection_name(self, wing: str, room: str) -> str:
        """Map wing/room to a valid ChromaDB collection name."""
        return f"{wing}_{room}".replace("/", "_").replace(".", "_")

    def store(self, wing: str, room: str, content: str, metadata: Optional[dict[str, Any]] = None):
        """Store a drawer (entry) in the specified wing/room."""
        if not self.client:
            return
            
        coll_name = self._get_collection_name(wing, room)
        collection = self.client.get_or_create_collection(name=coll_name)
        
        # Use a hash of the content or metadata ID as drawer_id
        drawer_id = (metadata or {}).get("id") or hashlib.sha256(content.encode()).hexdigest()[:16]
        
        collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[str(drawer_id)]
        )

    def search(self, query: str, wing: str, room: Optional[str] = None, n_results: int = 5) -> list[dict[str, Any]]:
        """Search within a specific wing and optionally a specific room."""
        if not self.client:
            return []
            
        # If room is provided, search exactly that collection
        if room:
            coll_name = self._get_collection_name(wing, room)
            try:
                collection = self.client.get_collection(name=coll_name)
                results = collection.query(query_texts=[query], n_results=n_results)
                
                output = []
                for i in range(len(results["documents"][0])):
                    output.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "id": results["ids"][0][i],
                        "distance": results["distances"][0][i]
                    })
                return output
            except Exception:
                return []
        else:
            # Corpus-wide search in Chroma is harder (requires listing collections)
            # For Task 2, we stick to strict scoped retrieval as per Spec.
            return []

import hashlib
