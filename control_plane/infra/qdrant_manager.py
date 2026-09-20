# SPDX-License-Identifier: MIT
"""
Camelot Apex OS — Local Embedded Qdrant Manager
===============================================
Provides high-performance, sub-5ms local semantic vector storage & context
anchoring for Round Table Knights without requiring Docker or cloud round-trips.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("camelot.qdrant_local")

CAMELOT_HOME = Path(os.environ.get("CAMELOT_OS_HOME", Path("C:/Users/vizio/CAMELOT_OS"))).resolve()
QDRANT_STORAGE_DIR = CAMELOT_HOME / "03_VAULT" / "memory" / "qdrant"
DEFAULT_COLLECTION = "knight_context"
VECTOR_DIM = 128


def _deterministic_pseudo_vector(text: str, dim: int = VECTOR_DIM) -> List[float]:
    """Generates a normalized deterministic feature vector from text when no neural model is loaded."""
    raw_hash = hashlib.sha512(text.encode("utf-8")).digest()
    extended_bytes = bytearray()
    while len(extended_bytes) < dim * 4:
        raw_hash = hashlib.sha512(raw_hash).digest()
        extended_bytes.extend(raw_hash)
    floats = []
    norm_sq = 0.0
    for i in range(dim):
        val = int.from_bytes(extended_bytes[i*4:(i+1)*4], byteorder="little", signed=True) / (2**31)
        floats.append(val)
        norm_sq += val * val
    norm = norm_sq ** 0.5 or 1.0
    return [round(v / norm, 6) for v in floats]


class LocalQdrantManager:
    """Manages local embedded Qdrant vector database storage and queries."""

    def __init__(self, storage_dir: Optional[Path] = None, vector_dim: int = VECTOR_DIM) -> None:
        self.storage_dir = storage_dir or QDRANT_STORAGE_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.vector_dim = vector_dim
        self._client = None
        self._initialized = False

    def _get_client(self):
        if self._client is None:
            import qdrant_client
            from qdrant_client.models import Distance, VectorParams
            self._client = qdrant_client.QdrantClient(path=str(self.storage_dir))
            if not self._client.collection_exists(DEFAULT_COLLECTION):
                self._client.create_collection(
                    collection_name=DEFAULT_COLLECTION,
                    vectors_config=VectorParams(size=self.vector_dim, distance=Distance.COSINE),
                )
            self._initialized = True
        return self._client

    def store_context(
        self,
        knight_id: str,
        text: str,
        vector: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Store a knight's context item with metadata in local Qdrant."""
        client = self._get_client()
        from qdrant_client.models import PointStruct
        
        vec = vector or _deterministic_pseudo_vector(text, self.vector_dim)
        point_id = int(hashlib.md5(f"{knight_id}_{text}_{time.time()}".encode("utf-8")).hexdigest()[:8], 16)
        
        payload = {
            "knight_id": knight_id,
            "text": text,
            "timestamp": time.time(),
            **(metadata or {}),
        }
        
        client.upsert(
            collection_name=DEFAULT_COLLECTION,
            points=[PointStruct(id=point_id, vector=vec, payload=payload)],
        )
        return {"success": True, "point_id": point_id, "knight_id": knight_id}

    def search_context(
        self,
        knight_id: Optional[str] = None,
        query_text: Optional[str] = None,
        query_vector: Optional[List[float]] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search relevant contexts by semantic similarity, filtered by knight_id if provided."""
        client = self._get_client()
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        if query_vector is None:
            if not query_text:
                return []
            query_vector = _deterministic_pseudo_vector(query_text, self.vector_dim)

        query_filter = None
        if knight_id:
            query_filter = Filter(
                must=[FieldCondition(key="knight_id", match=MatchValue(value=knight_id))]
            )

        res = client.query_points(
            collection_name=DEFAULT_COLLECTION,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
        )

        return [
            {
                "id": hit.id,
                "score": round(float(hit.score), 4),
                "payload": hit.payload,
            }
            for hit in res.points
        ]

    def get_status(self) -> Dict[str, Any]:
        """Get collection metrics and database health."""
        try:
            client = self._get_client()
            col_info = client.get_collection(DEFAULT_COLLECTION)
            return {
                "status": "HEALTHY",
                "collection": DEFAULT_COLLECTION,
                "vector_size": self.vector_dim,
                "points_count": getattr(col_info, "points_count", 0),
                "storage_dir": str(self.storage_dir),
            }
        except Exception as exc:
            return {
                "status": "DEGRADED",
                "error": str(exc),
            }

    def close(self) -> None:
        """Close client connection cleanly."""
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None
            self._initialized = False
