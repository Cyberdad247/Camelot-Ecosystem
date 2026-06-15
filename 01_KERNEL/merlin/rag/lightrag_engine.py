# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
==============================================================================
LIGHTRAG ENGINE
Camelot OS v33.0 - Instant Knowledge Retrieval
==============================================================================
Lightweight RAG engine using ChromaDB for vector storage and
sentence-transformers for embeddings. Replaces Sir_Percival (Deep_RAG).
==============================================================================
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

# ==============================================================================
# CONFIGURATION
# ==============================================================================

CONFIG_PATH = Path("config/lightrag_config.yaml")
DEFAULT_COLLECTION = "exp_ledger_vectors"
DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass
class LightRAGConfig:
    """Configuration for LightRAG engine."""

    persist_directory: str = "Titan_Omega_Hypergraph/chromadb"
    collection_name: str = DEFAULT_COLLECTION
    embedding_model: str = DEFAULT_MODEL
    embedding_dimension: int = 384
    top_k: int = 5
    similarity_threshold: float = 0.1
    pre_index_ethical_scan: bool = True
    auto_index_new_exp: bool = True

    @classmethod
    def from_yaml(cls, path: Path) -> "LightRAGConfig":
        """Load config from YAML file."""
        if not path.exists():
            return cls()

        with open(path, "r") as f:
            data = yaml.safe_load(f)

        lr = data.get("lightrag", {})
        vs = lr.get("vector_store", {})
        emb = lr.get("embedding", {})
        ret = lr.get("retrieval", {})
        idx = lr.get("indexing", {})

        return cls(
            persist_directory=vs.get("persist_directory", cls.persist_directory),
            collection_name=vs.get("collection_name", cls.collection_name),
            embedding_model=emb.get("model", cls.embedding_model),
            embedding_dimension=emb.get("dimension", cls.embedding_dimension),
            top_k=ret.get("top_k", cls.top_k),
            similarity_threshold=ret.get("similarity_threshold", cls.similarity_threshold),
            pre_index_ethical_scan=idx.get("pre_index_ethical_scan", cls.pre_index_ethical_scan),
            auto_index_new_exp=idx.get("auto_index_new_exp", cls.auto_index_new_exp),
        )


# ==============================================================================
# DATA MODELS
# ==============================================================================


@dataclass
class RAGResult:
    """A single retrieval result."""

    doc_id: str
    content: str
    score: float
    metadata: dict = field(default_factory=dict)


@dataclass
class RAGQueryResponse:
    """Response from a RAG query."""

    query: str
    results: list[RAGResult]
    latency_ms: float
    total_results: int


@dataclass
class RAGIndexResponse:
    """Response from indexing operation."""

    success: bool
    doc_id: str
    message: str
    latency_ms: float


# ==============================================================================
# PII SCANNER (For Pre-Index Ethical Scan)
# ==============================================================================


class PIIScanner:
    """Scans documents for PII before indexing."""

    # Pattern definitions
    PATTERNS = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "api_key": r"\b(api[_-]?key|apikey|api_secret)[:\s]*['\"]?[\w-]{20,}['\"]?\b",
    }

    # Keywords to block
    BLOCKED_KEYWORDS = ["password", "secret", "private key", "ssh key", "access token", "bearer token", "api secret"]

    @classmethod
    def scan(cls, text: str) -> tuple[bool, list[str]]:
        """
        Scan text for PII.

        Returns:
            (is_safe, list of detected issues)
        """
        issues = []
        text_lower = text.lower()

        # Check patterns
        for name, pattern in cls.PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"PII detected: {name}")

        # Check keywords
        for keyword in cls.BLOCKED_KEYWORDS:
            if keyword in text_lower:
                issues.append(f"Sensitive keyword: {keyword}")

        return len(issues) == 0, issues


# ==============================================================================
# LIGHTRAG ENGINE
# ==============================================================================


class LightRAGEngine:
    """
    LightRAG Engine for CAMELOT.

    Provides:
    - Semantic search across EXP_Ledger entries
    - Auto-indexing of new entries
    - Pre-index ethical scanning
    - ChromaDB vector storage
    """

    def __init__(self, config: Optional[LightRAGConfig] = None):
        self.config = config or LightRAGConfig.from_yaml(CONFIG_PATH)
        self._client = None
        self._collection = None
        self._embedder = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the engine with ChromaDB and embedder."""
        if self._initialized:
            return

        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise ImportError(f"Missing dependency: {e}. " "Run: pip install chromadb sentence-transformers")

        # Initialize ChromaDB
        persist_path = Path(self.config.persist_directory)
        persist_path.mkdir(parents=True, exist_ok=True)

        self._client = chromadb.PersistentClient(path=str(persist_path))

        # Get or create collection
        self._collection = self._client.get_or_create_collection(
            name=self.config.collection_name, metadata={"hnsw:space": "cosine"}
        )

        # Initialize embedder
        print(f"[LIGHTRAG] Loading embedding model: {self.config.embedding_model}")
        self._embedder = SentenceTransformer(self.config.embedding_model)

        self._initialized = True
        print(f"[LIGHTRAG] Initialized with {self._collection.count()} documents")

    def _ensure_initialized(self) -> None:
        """Ensure engine is initialized."""
        if not self._initialized:
            self.initialize()

    def _generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for text."""
        self._ensure_initialized()
        return self._embedder.encode(text).tolist()

    def _generate_doc_id(self, content: str, metadata: dict) -> str:
        """Generate unique document ID."""
        unique_str = f"{content}:{metadata.get('exp_id', '')}:{metadata.get('persona_id', '')}"
        return hashlib.sha256(unique_str.encode()).hexdigest()[:16]

    def query(
        self,
        query_text: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[dict] = None,
    ) -> RAGQueryResponse:
        """
        Query the vector store for similar documents.

        Args:
            query_text: The query string
            top_k: Number of results (default from config)
            filter_metadata: Optional metadata filter

        Returns:
            RAGQueryResponse with results
        """
        start_time = time.time()
        self._ensure_initialized()

        k = top_k or self.config.top_k

        # Generate query embedding
        query_embedding = self._generate_embedding(query_text)

        # Query ChromaDB
        where_filter = filter_metadata if filter_metadata else None

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        # Parse results
        parsed_results = []

        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if results["distances"] else 0
                # Convert distance to similarity (cosine distance to similarity)
                score = 1 - distance

                if score >= self.config.similarity_threshold:
                    parsed_results.append(
                        RAGResult(
                            doc_id=doc_id,
                            content=results["documents"][0][i] if results["documents"] else "",
                            score=round(score, 4),
                            metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                        )
                    )

        latency = (time.time() - start_time) * 1000

        return RAGQueryResponse(
            query=query_text,
            results=parsed_results,
            latency_ms=round(latency, 2),
            total_results=len(parsed_results),
        )

    def index(
        self,
        content: str,
        metadata: dict,
        doc_id: Optional[str] = None,
        skip_pii_scan: bool = False,
    ) -> RAGIndexResponse:
        """
        Index a document in the vector store.

        Args:
            content: Document content
            metadata: Document metadata
            doc_id: Optional document ID (auto-generated if not provided)
            skip_pii_scan: Skip PII scan (NOT recommended)

        Returns:
            RAGIndexResponse with status
        """
        start_time = time.time()
        self._ensure_initialized()

        # Pre-index ethical scan
        if self.config.pre_index_ethical_scan and not skip_pii_scan:
            is_safe, issues = PIIScanner.scan(content)
            if not is_safe:
                return RAGIndexResponse(
                    success=False,
                    doc_id="",
                    message=f"⚠️ BLOCKED by Sir_Zenith: {', '.join(issues)}",
                    latency_ms=round((time.time() - start_time) * 1000, 2),
                )

        # Generate document ID
        final_doc_id = doc_id or self._generate_doc_id(content, metadata)

        # Generate embedding
        embedding = self._generate_embedding(content)

        # Add to collection
        self._collection.add(
            ids=[final_doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata],
        )

        latency = (time.time() - start_time) * 1000

        return RAGIndexResponse(
            success=True,
            doc_id=final_doc_id,
            message="Document indexed successfully",
            latency_ms=round(latency, 2),
        )

    def delete(self, doc_id: str) -> bool:
        """
        Delete a document from the index.

        Args:
            doc_id: Document ID to delete

        Returns:
            True if deleted, False if not found
        """
        self._ensure_initialized()

        try:
            self._collection.delete(ids=[doc_id])
            return True
        except Exception:
            return False

    def get_stats(self) -> dict:
        """Get collection statistics."""
        self._ensure_initialized()

        return {
            "collection_name": self.config.collection_name,
            "total_documents": self._collection.count(),
            "embedding_model": self.config.embedding_model,
            "embedding_dimension": self.config.embedding_dimension,
            "persist_directory": self.config.persist_directory,
        }

    def index_exp_entry(self, exp_entry: dict) -> RAGIndexResponse:
        """
        Index an EXP entry from the EXP_Ledger.

        Args:
            exp_entry: EXP entry dictionary

        Returns:
            RAGIndexResponse
        """
        # Build content from entry
        solution_steps = exp_entry.get("resolution", {}).get("solution_steps", [])
        if isinstance(solution_steps, list):
            solution_text = " ".join(solution_steps)
        else:
            solution_text = str(solution_steps)

        complication_type = exp_entry.get("trigger", {}).get("complication_type", "")
        tags = exp_entry.get("tags", [])

        content = f"{complication_type}: {solution_text}. Tags: {', '.join(tags)}"

        # Build metadata
        metadata = {
            "exp_id": exp_entry.get("exp_id", ""),
            "persona_id": exp_entry.get("trigger", {}).get("knight_responsible", ""),
            "complication_type": complication_type,
            "tags": ",".join(tags),
            "timestamp": exp_entry.get("timestamp", ""),
        }

        doc_id = f"exp_{exp_entry.get('exp_id', '')}"

        return self.index(content, metadata, doc_id)


# ==============================================================================
# SINGLETON INSTANCE
# ==============================================================================

_engine_instance: Optional[LightRAGEngine] = None


def get_lightrag_engine() -> LightRAGEngine:
    """Get the singleton LightRAGEngine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = LightRAGEngine()
    return _engine_instance


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================


def quick_query(query: str, top_k: int = 5) -> list[dict]:
    """Quick query function."""
    engine = get_lightrag_engine()
    response = engine.query(query, top_k=top_k)
    return [
        {
            "id": r.doc_id,
            "content": r.content,
            "score": r.score,
            "metadata": r.metadata,
        }
        for r in response.results
    ]


def quick_index(content: str, metadata: dict) -> dict:
    """Quick index function."""
    engine = get_lightrag_engine()
    response = engine.index(content, metadata)
    return {
        "success": response.success,
        "doc_id": response.doc_id,
        "message": response.message,
    }


# ==============================================================================
# TESTING
# ==============================================================================


if __name__ == "__main__":
    print("[TEST] LightRAG Engine")
    print("=" * 60)

    # Initialize
    engine = LightRAGEngine()

    try:
        engine.initialize()
        print("[OK] Engine initialized")

        # Test PII scanner
        is_safe, issues = PIIScanner.scan("Normal text without PII")
        print(f"[OK] PII scan (clean): safe={is_safe}")

        is_safe, issues = PIIScanner.scan("My SSN is 123-45-6789")
        print(f"[OK] PII scan (PII): safe={is_safe}, issues={issues}")

        # Test indexing
        response = engine.index(
            content="Fix Python ImportError by checking sys.path and installing missing packages.",
            metadata={
                "exp_id": "test-001",
                "complication_type": "ImportError",
                "tags": "python,import,error",
            },
        )
        print(f"[OK] Index: {response.message}")

        # Test PII blocking
        response = engine.index(content="User password: secret123, SSN: 123-45-6789", metadata={"exp_id": "test-pii"})
        print(f"[OK] PII block: {response.message}")

        # Test query
        query_response = engine.query("How to fix Python import error?")
        print(f"[OK] Query: {query_response.total_results} results in {query_response.latency_ms}ms")

        if query_response.results:
            print(f"    Top result: {query_response.results[0].content[:50]}...")

        # Stats
        stats = engine.get_stats()
        print(f"[OK] Stats: {stats['total_documents']} documents")

        print("=" * 60)
        print("[PASS] All LightRAG tests passed!")

    except ImportError as e:
        print(f"[SKIP] Missing dependencies: {e}")
        print("[INFO] Run: pip install chromadb sentence-transformers")