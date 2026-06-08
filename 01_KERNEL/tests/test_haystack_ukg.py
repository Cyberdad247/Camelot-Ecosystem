# SPDX-FileCopyrightText: 2026 Invisioned Marketing Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test Suite for Haystack-UKG Bridge

Validates RAG pipeline integration with Camelot's Universal Knowledge Glyph.

Test Categories:
    1. UKG Loading: File parsing, validation, node filtering
    2. Document Conversion: UKG → Haystack Document transformation
    3. Retrieval: BM25 search, ranking, top-k selection
    4. Query Interface: End-to-end RAG queries
    5. Error Handling: Missing files, malformed JSON, edge cases

Usage:
    # Run all tests
    pytest test_haystack_ukg.py -v
    
    # Run specific test
    pytest test_haystack_ukg.py::test_ukg_loading -v
    
    # Quick smoke test
    python test_haystack_ukg.py
"""

import sys
from pathlib import Path
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the bridge (with graceful handling if Haystack not installed)
try:
    from integrations.haystack_ukg_bridge import HaystackUKGBridge, HAYSTACK_AVAILABLE
except ImportError as e:
    print(f"❌ Failed to import HaystackUKGBridge: {e}")
    print("Make sure you're running from 01_KERNEL directory")
    sys.exit(1)


# Skip all tests if Haystack not installed
pytestmark = pytest.mark.skipif(
    not HAYSTACK_AVAILABLE, 
    reason="Haystack not installed (pip install haystack-ai)"
)


class TestUKGLoading:
    """Test UKG file loading and parsing."""
    
    def test_load_valid_ukg(self):
        """Should successfully load valid UKG JSON-LD file."""
        bridge = HaystackUKGBridge(
            ukg_path="03_VAULT/UKG/UKG_MEMORY.jsonld",
            max_nodes=10  # Limit for faster testing
        )
        
        assert bridge.ukg is not None
        assert "nodes" in bridge.ukg
        assert len(bridge.ukg["nodes"]) <= 10
    
    def test_max_nodes_limit(self):
        """Should respect max_nodes parameter."""
        max_nodes = 5
        bridge = HaystackUKGBridge(max_nodes=max_nodes)
        
        # Loaded nodes should not exceed limit
        assert len(bridge.ukg["nodes"]) <= max_nodes
    
    def test_missing_ukg_file(self):
        """Should raise FileNotFoundError for missing UKG file."""
        with pytest.raises(FileNotFoundError):
            HaystackUKGBridge(ukg_path="nonexistent/path.jsonld")
    
    def test_malformed_ukg(self, tmp_path):
        """Should raise ValueError for UKG without 'nodes' key."""
        # Create malformed UKG file
        malformed_ukg = tmp_path / "malformed.jsonld"
        malformed_ukg.write_text('{"@context": "test"}')  # Missing 'nodes'
        
        with pytest.raises(ValueError, match="missing 'nodes' key"):
            HaystackUKGBridge(ukg_path=str(malformed_ukg))


class TestDocumentConversion:
    """Test UKG → Haystack Document transformation."""
    
    def test_knowledge_artifacts_converted(self):
        """Should convert KnowledgeArtifacts to Haystack Documents."""
        bridge = HaystackUKGBridge(max_nodes=50)
        
        # Get all documents from store
        docs = bridge.document_store.filter_documents()
        
        # Should have at least some documents
        assert len(docs) > 0, "No documents in store"
        
        # Check document structure
        first_doc = docs[0]
        assert hasattr(first_doc, 'content')
        assert hasattr(first_doc, 'meta')
        assert 'source' in first_doc.meta
    
    def test_empty_nodes_skipped(self):
        """Should skip nodes with empty or minimal content."""
        bridge = HaystackUKGBridge(max_nodes=100)
        
        # Count original nodes vs converted documents
        original_artifacts = sum(
            1 for node in bridge.ukg["nodes"] 
            if node.get("@type") == "KnowledgeArtifact"
        )
        
        docs = bridge.document_store.filter_documents()
        
        # Some nodes should be filtered (empty content, etc.)
        # Converted docs <= original artifacts
        assert len(docs) <= original_artifacts
    
    def test_metadata_preservation(self):
        """Should preserve UKG metadata in Haystack Documents."""
        bridge = HaystackUKGBridge(max_nodes=10)
        docs = bridge.document_store.filter_documents()
        
        if docs:
            doc = docs[0]
            
            # Required metadata fields
            assert 'source' in doc.meta
            assert 'hash' in doc.meta
            assert 'assimilated_at' in doc.meta
            assert 'status' in doc.meta
            assert 'node_id' in doc.meta


class TestRetrieval:
    """Test BM25 retrieval and ranking."""
    
    def test_basic_retrieval(self):
        """Should retrieve relevant documents for query."""
        bridge = HaystackUKGBridge(max_nodes=100)
        
        # Test query
        result = bridge.query("empire map", top_k=5)
        
        assert result is not None
        assert "documents" in result
        assert len(result["documents"]) <= 5  # Respects top_k
    
    def test_top_k_parameter(self):
        """Should return exactly top_k documents (or fewer if not enough)."""
        bridge = HaystackUKGBridge(max_nodes=20)
        
        # Query with different top_k values
        result_3 = bridge.query("test", top_k=3)
        result_10 = bridge.query("test", top_k=10)
        
        assert len(result_3["documents"]) <= 3
        assert len(result_10["documents"]) <= 10
    
    def test_no_results_for_nonsense_query(self):
        """Should handle queries with no matching results."""
        bridge = HaystackUKGBridge(max_nodes=50)
        
        # Extremely unlikely query
        result = bridge.query("xyzabc123nonsensequery999", top_k=5)
        
        # Should return empty or very few results
        assert "documents" in result
        # Note: BM25 may still return some results even for gibberish


class TestQueryInterface:
    """Test end-to-end query functionality."""
    
    def test_query_response_structure(self):
        """Should return properly structured query response."""
        bridge = HaystackUKGBridge(max_nodes=50)
        result = bridge.query("Camelot OS architecture")
        
        # Required fields
        assert "question" in result
        assert "documents" in result
        assert "metadata" in result
        
        # Question should match input
        assert result["question"] == "Camelot OS architecture"
        
        # Metadata should have retriever info
        assert "retriever" in result["metadata"]
        assert "top_k" in result["metadata"]
    
    def test_document_truncation(self):
        """Should truncate long document content in response."""
        bridge = HaystackUKGBridge(max_nodes=50)
        result = bridge.query("test", top_k=3)
        
        if result["documents"]:
            doc = result["documents"][0]
            # Content should be truncated to ~500 chars
            assert len(doc["content"]) <= 600  # Allow some margin


class TestStatistics:
    """Test statistics and introspection methods."""
    
    def test_get_stats(self):
        """Should return comprehensive statistics."""
        bridge = HaystackUKGBridge(max_nodes=50)
        stats = bridge.get_stats()
        
        # Required stat fields
        assert "total_documents" in stats
        assert "ukg_path" in stats
        assert "document_store_type" in stats
        assert "status_breakdown" in stats
        
        # Total documents should match
        docs = bridge.document_store.filter_documents()
        assert stats["total_documents"] == len(docs)
    
    def test_status_breakdown(self):
        """Should categorize documents by status."""
        bridge = HaystackUKGBridge(max_nodes=100)
        stats = bridge.get_stats()
        
        breakdown = stats["status_breakdown"]
        
        # Should be a dictionary with status counts
        assert isinstance(breakdown, dict)
        
        # Total should match document count
        total_in_breakdown = sum(breakdown.values())
        assert total_in_breakdown == stats["total_documents"]


class TestErrorHandling:
    """Test error cases and edge conditions."""
    
    def test_invalid_generator_model(self):
        """Should raise ValueError for unknown generator model."""
        bridge = HaystackUKGBridge(max_nodes=10)
        
        with pytest.raises(ValueError, match="Unknown generator model"):
            bridge.create_rag_pipeline(generator_model="invalid_model")
    
    def test_empty_query(self):
        """Should handle empty query string."""
        bridge = HaystackUKGBridge(max_nodes=10)
        
        # Empty query should not crash
        result = bridge.query("", top_k=5)
        assert result is not None


# Smoke test for quick validation
def smoke_test():
    """Quick smoke test without pytest."""
    print("🏰 Camelot OS - Haystack UKG Bridge Smoke Test\n")
    
    if not HAYSTACK_AVAILABLE:
        print("❌ Haystack not installed. Install with:")
        print("   pip install haystack-ai")
        return False
    
    try:
        print("1. Initializing bridge (max 50 nodes)...")
        bridge = HaystackUKGBridge(max_nodes=50)
        print(f"   ✅ Loaded {len(bridge.document_store.filter_documents())} documents")
        
        print("\n2. Testing query: 'empire map structure'...")
        result = bridge.query("empire map structure", top_k=3)
        print(f"   ✅ Retrieved {len(result['documents'])} documents")
        
        if result['documents']:
            print(f"\n   Top result:")
            doc = result['documents'][0]
            print(f"   - Source: {doc['source']}")
            print(f"   - Content: {doc['content'][:150]}...")
        
        print("\n3. Getting statistics...")
        stats = bridge.get_stats()
        print(f"   ✅ Total documents: {stats['total_documents']}")
        print(f"   ✅ Status breakdown: {stats['status_breakdown']}")
        
        print("\n✅ All smoke tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Smoke test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run smoke test when executed directly
    success = smoke_test()
    sys.exit(0 if success else 1)
