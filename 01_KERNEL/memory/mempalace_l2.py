# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

import hashlib
import hmac
import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("MemPalaceL2")

try:
    import chromadb
except ImportError:
    chromadb = None

try:
    from .cloudbrain_connector import CloudBrainConnector
except ImportError:
    try:
        from cloudbrain_connector import CloudBrainConnector  # noqa: F811
    except ImportError:
        CloudBrainConnector = None  # type: ignore[assignment]

class MemPalaceL2:
    """Persistent local vector index manager (Layer 2 Memory)."""

    def __init__(self, storage_path: Optional[Path] = None):
        # System-level secret for HMAC salting
        secret_env = os.environ.get("MEMPALACE_SECRET")
        if not secret_env:
            logger.warning("SECURITY WARNING: Using default MEMPALACE_SECRET. Provide one in env for production purity.")
            secret_env = "OMEGA_DEER_CORE_FIX_2026"
            
        self._secret = secret_env.encode()
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
            logger.warning("chromadb not installed. L2 Memory is in DARK mode.")

    def _get_collection_name(self, wing: str, room: str, tenant_id: str = "default") -> str:
        """Map wing/room/tenant to a valid ChromaDB collection name."""
        name = f"{tenant_id}_{wing}_{room}"
        return name.replace("/", "_").replace(".", "_").replace("-", "_")

    def _generate_salted_id(self, content: str, tenant_id: str) -> str:
        """Generate a salted HMAC-SHA256 ID for content and tenant."""
        h = hmac.new(self._secret, digestmod=hashlib.sha256)
        h.update(tenant_id.encode())
        h.update(content.encode())
        return h.hexdigest()

    def store(self, wing: str, room: str, content: str, metadata: Optional[dict[str, Any]] = None, tenant_id: str = "default", push_to_cloudbrain: bool = True):
        """Store a drawer (entry) in the specified wing/room with integrity checksum."""
        if not self.client:
            return
            
        coll_name = self._get_collection_name(wing, room, tenant_id)
        collection = self.client.get_or_create_collection(name=coll_name)
        
        meta = metadata or {}
        # Calculate SHA-256 checksum of content for L5 integrity (if not provided)
        if "checksum" not in meta:
            meta["checksum"] = hashlib.sha256(content.encode()).hexdigest()
        
        # Use a salted HMAC of the content + tenant_id as drawer_id
        drawer_id = meta.get("id") or self._generate_salted_id(content, tenant_id)
        
        collection.upsert(
            documents=[content],
            metadatas=[meta],
            ids=[str(drawer_id)]
        )

        if push_to_cloudbrain:
            try:
                # We map tenant_id to knight_id conceptually. Default to ANYA_OMEGA if "default"
                knight_id = tenant_id if tenant_id != "default" else "ANYA_OMEGA"
                cloudbrain = CloudBrainConnector(knight_id=knight_id)
                cloudbrain.push_to_notebook(
                    artifact_type="source",
                    content=content,
                    title=f"L2_Vector_Index_{wing}_{room}_{drawer_id}"
                )
            except Exception as e:
                print(f"Failed to push vector data to Cloud Brain: {e}")

    def search(self, query: str, wing: str, room: Optional[str] = None, n_results: int = 5, tenant_id: str = "default", verify_integrity: bool = False) -> list[dict[str, Any]]:
        """Search within a specific wing/room with optional integrity verification."""
        if not self.client:
            return []
            
        # If room is provided, search exactly that collection
        if room:
            coll_name = self._get_collection_name(wing, room, tenant_id)
            try:
                collection = self.client.get_collection(name=coll_name)
                results = collection.query(query_texts=[query], n_results=n_results)
                
                output = []
                for i in range(len(results["documents"][0])):
                    content = results["documents"][0][i]
                    metadata = results["metadatas"][0][i]
                    
                    integrity_fail = False
                    if verify_integrity:
                        stored_checksum = metadata.get("checksum")
                        actual_checksum = hashlib.sha256(content.encode()).hexdigest()
                        if stored_checksum != actual_checksum:
                            integrity_fail = True
                    
                    output.append({
                        "content": content,
                        "metadata": metadata,
                        "id": results["ids"][0][i],
                        "distance": results["distances"][0][i],
                        "integrity_fail": integrity_fail
                    })
                return output
            except Exception:
                return []
        else:
            # Corpus-wide search in Chroma is harder (requires listing collections)
            return []
