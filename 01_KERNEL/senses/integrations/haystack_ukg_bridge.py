# SPDX-FileCopyrightText: 2026 Invisioned Marketing Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Haystack-UKG Bridge Module

Integrates Haystack's RAG pipeline with Camelot's Universal Knowledge Glyph (UKG).
Converts UKG JSON-LD nodes to Haystack Documents for semantic retrieval.

Architecture:
    UKG (JSON-LD) → HaystackUKGBridge → Haystack Pipeline → RAG Queries

Components:
    - Document Store: In-memory (development) / Vector DB (production)
    - Retriever: BM25 (keyword) + potential vector search
    - Generator: Integrated with Merlin API (vs external LLM)

Usage:
    >>> bridge = HaystackUKGBridge("03_VAULT/UKG/UKG_MEMORY.jsonld")
    >>> result = bridge.query("What is the empire map structure?")
    >>> print(result['answer'])
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# Haystack imports (conditional - graceful degradation if not installed)
try:
    from haystack import Document, Pipeline
    from haystack.components.generators import OpenAIGenerator
    from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
    from haystack.document_stores.in_memory import InMemoryDocumentStore
    HAYSTACK_AVAILABLE = True
except ImportError:
    HAYSTACK_AVAILABLE = False
    # Define stub classes for type hints
    class Pipeline:
        pass
    class Document:
        pass
    class InMemoryDocumentStore:
        pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HaystackUKGBridge:
    """
    Bridge between Haystack RAG Pipeline and Camelot UKG.
    
    Maps UKG nodes to Haystack Documents for semantic retrieval.
    Provides RAG-enhanced knowledge access across the Septem Regna.
    
    Attributes:
        ukg_path: Path to UKG JSON-LD file
        document_store: Haystack document store (in-memory or vector DB)
        max_nodes: Maximum UKG nodes to load (for testing/performance)
    """
    
    def __init__(
        self, 
        ukg_path: str = "03_VAULT/UKG/UKG_MEMORY.jsonld",
        max_nodes: Optional[int] = None,
        use_vector_search: bool = False
    ):
        """
        Initialize the Haystack-UKG bridge.
        
        Args:
            ukg_path: Path to UKG JSON-LD file (relative or absolute)
            max_nodes: Limit nodes loaded (None = all). Use 100 for testing.
            use_vector_search: Enable vector embeddings (requires API keys)
        """
        if not HAYSTACK_AVAILABLE:
            raise ImportError(
                "Haystack not installed. Install with: pip install haystack-ai"
            )
        
        self.ukg_path = Path(ukg_path)
        self.max_nodes = max_nodes
        self.use_vector_search = use_vector_search
        
        logger.info("🔮 Initializing Haystack-UKG Bridge...")
        logger.info(f"   UKG Path: {self.ukg_path}")
        logger.info(f"   Max Nodes: {max_nodes or 'ALL'}")
        
        # Load UKG graph
        self.ukg = self._load_ukg()
        
        # Initialize document store
        self.document_store = InMemoryDocumentStore()
        
        # Populate with UKG nodes
        self._populate_document_store()
        
        logger.info(f"✅ Bridge initialized with {len(self.document_store.filter_documents())} documents")
    
    def _load_ukg(self) -> Dict[str, Any]:
        """
        Load UKG graph from JSON-LD file.
        
        Returns:
            Parsed UKG dictionary with 'nodes' key
            
        Raises:
            FileNotFoundError: If UKG file doesn't exist
            json.JSONDecodeError: If UKG file is malformed
        """
        if not self.ukg_path.exists():
            raise FileNotFoundError(
                f"UKG file not found: {self.ukg_path}\n"
                f"Expected location: 03_VAULT/UKG/UKG_MEMORY.jsonld"
            )
        
        logger.info(f"📖 Loading UKG from {self.ukg_path}...")
        
        with open(self.ukg_path, 'r', encoding='utf-8') as f:
            ukg_data = json.load(f)
        
        # Validate structure
        if "nodes" not in ukg_data:
            raise ValueError(
                "Invalid UKG format: missing 'nodes' key. "
                "Expected JSON-LD structure with nodes array."
            )
        
        total_nodes = len(ukg_data.get("nodes", []))
        logger.info(f"   Total UKG nodes: {total_nodes}")
        
        # Apply max_nodes limit if specified
        if self.max_nodes:
            ukg_data["nodes"] = ukg_data["nodes"][:self.max_nodes]
            logger.info(f"   Limited to: {len(ukg_data['nodes'])} nodes")
        
        return ukg_data
    
    def _populate_document_store(self) -> None:
        """
        Convert UKG nodes to Haystack Documents and populate store.
        
        Transformation:
            UKG KnowledgeArtifact → Haystack Document
            - content: content_summary (text to search)
            - meta: source, hash, timestamp, status
        """
        documents = []
        
        for idx, node in enumerate(self.ukg.get("nodes", [])):
            # Only process KnowledgeArtifacts (skip other node types)
            if node.get("@type") != "KnowledgeArtifact":
                continue
            
            # Extract content (use summary for searching)
            content = node.get("content_summary", "")
            
            # Skip empty nodes
            if not content or len(content.strip()) < 10:
                continue
            
            # Create Haystack Document
            doc = Document(
                content=content,
                meta={
                    "source": node.get("source", "unknown"),
                    "hash": node.get("hash", ""),
                    "assimilated_at": node.get("assimilated_at", 0),
                    "status": node.get("status", "unknown"),
                    "node_id": idx  # Track original position
                }
            )
            
            documents.append(doc)
        
        # Write to document store
        if documents:
            self.document_store.write_documents(documents)
            logger.info(f"✅ Populated DocumentStore with {len(documents)} UKG artifacts")
        else:
            logger.warning("⚠️ No valid KnowledgeArtifacts found in UKG")
    
    def create_rag_pipeline(self, generator_model: str = "merlin") -> Pipeline:
        """
        Create a RAG pipeline using UKG as knowledge base.
        """
        pipeline = Pipeline()
        
        # Add retriever component (BM25 keyword search)
        retriever = InMemoryBM25Retriever(document_store=self.document_store)
        pipeline.add_component("retriever", retriever)
        
        # Add generator component
        if generator_model == "merlin":
            try:
                from integrations.merlin_haystack_generator import MerlinGenerator
                generator = MerlinGenerator(mode="CoT")  # Chain-of-Thought reasoning
                pipeline.add_component("generator", generator)
                logger.info("✅ Merlin generator integrated (CoT mode)")
            except ImportError as e:
                logger.warning(
                    f"⚠️ Merlin generator import failed: {e}. "
                    "Falling back to retriever-only mode."
                )
        
        elif generator_model == "openai":
            generator = OpenAIGenerator(model="gpt-4")
            pipeline.add_component("generator", generator)
            pipeline.connect("retriever.documents", "generator.documents")
        else:
            raise ValueError(
                f"Unknown generator model: {generator_model}. "
                f"Supported: 'merlin', 'openai'"
            )
        
        return pipeline
    
    def retrieve_documents(self, query: str, top_k: int = 5) -> List[Any]:
        """
        Execute only the retrieval stage (useful for recursive search).
        """
        try:
            retriever = InMemoryBM25Retriever(document_store=self.document_store)
            pipeline = Pipeline()
            pipeline.add_component("retriever", retriever)
            
            result = pipeline.run({
                "retriever": {"query": query, "top_k": top_k}
            })
            return result.get("retriever", {}).get("documents", [])
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return []

    def query(
        self, 
        question: str, 
        top_k: int = 5,
        generator_model: str = "merlin",
        prompt_template: str = None,
        documents: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Query UKG using RAG pipeline with optional Persona support.
        
        Args:
            question: Natural language query
            top_k: Number of documents
            generator_model: Model to use ("merlin")
            prompt_template: Optional custom prompt for the generator
        """
        logger.info(f"🔍 Querying UKG: '{question}'")
        
        if not prompt_template:
            prompt_template = "Based on these documents:\n\n{{documents}}\n\nQuestion: {{query}}"
        
        if documents is None:
            # STAGE 1: Retriever
            retriever_pipeline = Pipeline()
            retriever = InMemoryBM25Retriever(document_store=self.document_store)
            retriever_pipeline.add_component("retriever", retriever)
            
            retriever_results = retriever_pipeline.run({
                "retriever": {"query": question, "top_k": top_k}
            })
            
            retrieved_docs = retriever_results.get("retriever", {}).get("documents", [])
        else:
            retrieved_docs = documents
        
        # STAGE 2: Generator
        if generator_model == "merlin" and retrieved_docs:
            try:
                from integrations.merlin_haystack_generator import MerlinGenerator
                generator = MerlinGenerator(mode="CoT")
                
                gen_result = generator.run(
                    prompt=prompt_template,
                    documents=retrieved_docs,
                    query=question
                )
                
                generated_answer = gen_result.get("replies", [None])[0]
                generator_meta = gen_result.get("meta", [{}])[0]
                
                response = {
                    "question": question,
                    "documents": [
                        {
                            "content": doc.content[:500],
                            "source": doc.meta.get("source", "unknown"),
                            "score": doc.score
                        } for doc in retrieved_docs
                    ],
                    "answer": generated_answer,
                    "metadata": {
                        "retriever": "BM25",
                        "generator": generator_model,
                        "total_results": len(retrieved_docs),
                        "generator_meta": generator_meta
                    }
                }
            except Exception as e:
                logger.error(f"❌ Generator failed: {e}")
                generator_model = None
        
        # Fallback / Output
        if generator_model != "merlin" or not retrieved_docs:
            response = {
                "question": question,
                "documents": [
                    {
                        "content": doc.content[:500],
                        "source": doc.meta.get("source", "unknown"),
                        "score": doc.score
                    } for doc in retrieved_docs
                ],
                "answer": None,
                "metadata": {
                    "retriever": "BM25",
                    "generator": None,
                    "total_results": len(retrieved_docs)
                }
            }
        
        logger.info(f"✅ Retrieved {len(response['documents'])} relevant documents")
        if response['answer']:
            logger.info(f"✅ Generated answer ({len(response['answer'])} chars)")
        
        return response

# Convenience functions
def quick_query(question: str, max_nodes: int = 100) -> Dict[str, Any]:
    bridge = HaystackUKGBridge(max_nodes=max_nodes)
    return bridge.query(question)

if __name__ == "__main__":
    print("🏰 Camelot OS - Haystack UKG Bridge Test\n")
    try:
        result = quick_query("empire map structure", max_nodes=50)
        print(f"Question: {result['question']}")
        print(f"\nRetrieved {len(result['documents'])} documents:")
        for i, doc in enumerate(result['documents'][:3], 1):
            print(f"\n{i}. Source: {doc['source']}")
            print(f"   Content: {doc['content'][:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
