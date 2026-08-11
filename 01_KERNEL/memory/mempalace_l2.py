import hashlib
import hmac
import os
import re
import sys
from pathlib import Path
from typing import Any, Optional
import logging

logger = logging.getLogger("MemPalaceL2")

# Shipped in the repository for a long time as the fallback HMAC key. A secret
# that is public is not a secret: anyone with the source could compute any
# tenant's salted IDs. Kept here only so it can be recognised and refused.
_INSECURE_DEFAULT_SECRET = "OMEGA_DEER_CORE_FIX_2026"


class MemPalaceSecretError(RuntimeError):
    """MEMPALACE_SECRET is missing, or set to the known-public default."""


def _canonical(*parts: str) -> bytes:
    """Length-prefixed framing for a tuple of strings.

    Concatenating fields directly makes the boundary between them ambiguous, so
    distinct tuples can share one encoding — ``("a", "bc")`` and ``("ab", "c")``
    both become ``b"abc"``. That produced genuine cross-tenant collisions in both
    the salted-ID HMAC and the collection name. A 4-byte big-endian length before
    each field makes the encoding injective.
    """
    out = bytearray()
    for part in parts:
        raw = part.encode("utf-8")
        out += len(raw).to_bytes(4, "big")
        out += raw
    return bytes(out)

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
        self._secret = self._resolve_secret()
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

    @staticmethod
    def _resolve_secret() -> bytes:
        """Return the HMAC key, refusing to fall back to a public value.

        Set ``MEMPALACE_SECRET``. For local development and tests, set
        ``MEMPALACE_ALLOW_INSECURE_SECRET=1`` to accept the historical default
        explicitly — the index is keyed by this value, so it must be stable
        across restarts and cannot simply be randomised per process.
        """
        secret = os.environ.get("MEMPALACE_SECRET")

        if secret and secret != _INSECURE_DEFAULT_SECRET:
            return secret.encode()

        if secret == _INSECURE_DEFAULT_SECRET:
            raise MemPalaceSecretError(
                "MEMPALACE_SECRET is set to the historical default that ships in "
                "this repository, so it provides no tenant isolation. Generate a "
                "fresh secret (e.g. `python -c \"import secrets;"
                "print(secrets.token_urlsafe(32))\"`)."
            )

        if os.environ.get("MEMPALACE_ALLOW_INSECURE_SECRET") == "1":
            logger.warning(
                "MEMPALACE_SECRET unset and MEMPALACE_ALLOW_INSECURE_SECRET=1 — "
                "using the public default key. Cache IDs are forgeable by anyone "
                "with the source. Never do this outside development."
            )
            return _INSECURE_DEFAULT_SECRET.encode()

        raise MemPalaceSecretError(
            "MEMPALACE_SECRET is not set. L2 memory keys tenant-scoped cache IDs "
            "with it, so starting without one would silently remove tenant "
            "isolation. Set MEMPALACE_SECRET, or set "
            "MEMPALACE_ALLOW_INSECURE_SECRET=1 for local development."
        )

    def _get_collection_name(self, wing: str, room: str, tenant_id: str = "default") -> str:
        """Map wing/room/tenant to a unique, valid ChromaDB collection name.

        The readable slug is advisory only; uniqueness comes from the digest over
        the length-prefixed triple. The previous scheme joined the fields with
        ``_`` and then rewrote separators, so ``tenant="acme", wing="sec_ops"``
        and ``tenant="acme_sec", wing="ops"`` mapped to the *same* collection —
        two tenants sharing one index.

        Note: this changes collection names, so an index built by an earlier
        version is not read by this one and must be re-ingested.
        """
        digest = hashlib.sha256(_canonical(tenant_id, wing, room)).hexdigest()[:16]
        slug = re.sub(r"[^0-9A-Za-z]+", "_", f"{tenant_id}_{wing}_{room}").strip("_")[:40]
        slug = slug.rstrip("_")
        # ChromaDB requires 3-63 chars, starting and ending alphanumeric.
        return f"{slug}_{digest}" if slug else f"mp_{digest}"

    def _generate_salted_id(self, content: str, tenant_id: str) -> str:
        """Generate a salted HMAC-SHA256 ID over the length-prefixed inputs."""
        return hmac.new(
            self._secret, _canonical(tenant_id, content), hashlib.sha256
        ).hexdigest()

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
                # We map tenant_id to knight_id conceptually. Default to SIR_BORIS if "default"
                knight_id = tenant_id if tenant_id != "default" else "SIR_BORIS"
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
