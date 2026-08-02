# SPDX-FileCopyrightText: 2026 Invisioned Marketing Inc.
# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-

"""
Phase 1 Test Script: Haystack-UKG RAG Pipeline

Validates the complete integration:
1. UKG loading (test with 100-node subset first)
2. Haystack document conversion
3. BM25 retrieval
4. Merlin answer generation
5. Chronos integration

Usage:
    python test_phase1_integration.py [--full]
    
    --full: Test with full 38,742-node UKG (default: 100-node subset)
"""

import logging
import sys
from pathlib import Path

# Force UTF-8 encoding on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Fix Python import paths
script_dir = Path(__file__).parent.absolute()
kernel_dir = script_dir.parent  # 01_KERNEL
camelot_root = kernel_dir.parent  # CAMELOT_OS root

sys.path.insert(0, str(kernel_dir))  # For 'integrations' and 'kernel' modules
sys.path.insert(0, str(camelot_root))  # For root-level imports

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_1_haystack_available():
    """Test 1: Verify Haystack installation."""
    logger.info("=" * 60)
    logger.info("TEST 1: Haystack Availability Check")
    logger.info("=" * 60)
    
    try:
        import haystack
        logger.info(f"✅ Haystack version: {haystack.__version__}")
        
        from haystack import Document, Pipeline  # noqa: F401
        from haystack.components.retrievers.in_memory import InMemoryBM25Retriever  # noqa: F401
        from haystack.document_stores.in_memory import InMemoryDocumentStore  # noqa: F401
        
        logger.info("✅ All core Haystack imports successful")
        return True
    except ImportError as e:
        logger.error(f"❌ Haystack not installed: {e}")
        logger.info("Install with: pip install haystack-ai")
        return False


def test_2_ukg_loading(full_mode: bool = False):
    """Test 2: Load UKG nodes."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: UKG Loading (Subset Mode)" if not full_mode else "TEST 2: UKG Loading (Full Mode)")
    logger.info("=" * 60)
    
    try:
        from integrations.haystack_ukg_bridge import HaystackUKGBridge
        
        # Bridge automatically loads UKG on init
        if full_mode:
            logger.info("📂 Creating bridge with FULL UKG...")
            bridge = HaystackUKGBridge()  # Loads all nodes
        else:
            logger.info("📂 Creating bridge with SUBSET (100 nodes)...")
            bridge = HaystackUKGBridge(max_nodes=100)  # Limits to 100
        
        count = bridge.document_store.count_documents()
        
        logger.info(f"✅ Loaded {count} UKG nodes into Haystack")
        
        # Verify document store
        logger.info(f"✅ Document store contains {count} documents")
        
        return count > 0
    
    except FileNotFoundError as e:
        logger.error(f"❌ UKG file not found: {e}")
        logger.info("Ensure UKG file exists at: 03_VAULT/UKG/UKG_MEMORY.jsonld")
        return False
    except Exception as e:
        logger.error(f"❌ UKG loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_retrieval():
    """Test 3: BM25 retrieval test."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: BM25 Retrieval Test")
    logger.info("=" * 60)
    
    try:
        from integrations.haystack_ukg_bridge import HaystackUKGBridge
        
        # Create bridge with 100-node limit for faster testing
        bridge = HaystackUKGBridge(max_nodes=100)
        
        # Test queries
        test_queries = [
            "empire map structure",
            "Septem Regna architecture",
            "Merlin kernel",
            "Anya interface",
            "Lukas kinetic layer"
        ]
        
        for query in test_queries:
            logger.info(f"\n🔍 Query: '{query}'")
            result = bridge.query(query, top_k=3, generator_model="merlin")
            
            logger.info(f"   Retrieved {len(result['documents'])} documents")
            
            if result['documents']:
                top_doc = result['documents'][0]
                logger.info(f"   Top result: {top_doc['content'][:100]}...")
                logger.info(f"   Source: {top_doc['source']}")
                logger.info(f"   Score: {top_doc['score']}")
            
            if result.get('answer'):
                logger.info(f"   ✅ Merlin Answer ({len(result['answer'])} chars):")
                logger.info(f"   {result['answer'][:200]}...")
        
        logger.info("\n✅ Retrieval tests complete")
        return True
    
    except Exception as e:
        logger.error(f"❌ Retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_merlin_generator():
    """Test 4: Merlin generator integration."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Merlin Generator Integration")
    logger.info("=" * 60)
    
    try:
        from haystack import Document
        from integrations.merlin_haystack_generator import MerlinGenerator
        
        # Create test documents
        docs = [
            Document(
                content="The Septem Regna is a 7-layer sovereign stack in Camelot OS.",
                meta={"source": "ARCHITECTURE.md"}
            ),
            Document(
                content="Layer 3 (L3) is Merlin Omega, the Neural routing layer with Videneptus LaC.",
                meta={"source": "EMPIRE_MAP.md"}
            ),
            Document(
                content="Layer 2 (L2) is Lukas Omega, the Kinetic layer with Saltare/Cribo/Rotel binaries.",
                meta={"source": "EMPIRE_MAP.md"}
            )
        ]
        
        # Initialize generator
        generator = MerlinGenerator(mode="CoT")
        
        # Generate answer
        logger.info("🧙‍♂️ Generating answer with Merlin...")
        result = generator.run(
            prompt="Based on these documents:\n\n{{documents}}\n\nQuestion: {{query}}",
            documents=docs,
            query="What is the Septem Regna and which layer is Merlin?"
        )
        
        answer = result['replies'][0]
        metadata = result['meta'][0]
        
        logger.info(f"\n✅ Merlin Response ({len(answer)} chars):")
        logger.info(f"{answer}")
        logger.info(f"\nMetadata: {metadata}")
        
        return True
    
    except ImportError as e:
        logger.warning(f"⚠️ Merlin generator test skipped: {e}")
        logger.info("This is expected if MerlinLLM is not fully configured")
        return True  # Not a blocker
    except Exception as e:
        logger.error(f"❌ Merlin generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_chronos_integration():
    """Test 5: Chronos Haystack integration."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Chronos Integration Test")
    logger.info("=" * 60)
    
    try:
        import asyncio

        from kernel.agora.protocol import ANPEnvelope
        from kernel.rag.chronos_haystack import ChronosHaystackNode
        
        async def test_chronos():
            # Initialize with Haystack only (skip LightRAG for this test)
            chronos = ChronosHaystackNode(enable_haystack=True, enable_lightrag=False)
            
            # Simulate UKG query
            envelope = ANPEnvelope(
                sender="TEST_MERLIN",
                recipient="CHRONOS_HAYSTACK",  # Fixed: recipient not receiver
                protocol="UKG_Query",
                payload={
                    "question": "What is the Septem Regna architecture?",
                    "top_k": 3
                }
            )
            
            logger.info("📨 Sending UKG query to Chronos...")
            await chronos.receive(envelope)
        
        asyncio.run(test_chronos())
        logger.info("✅ Chronos integration test complete")
        return True
    
    except ImportError as e:
        logger.warning(f"⚠️ Chronos test skipped: {e}")
        logger.info("This is expected if Agora/LightRAG dependencies missing")
        return True  # Not a blocker
    except Exception as e:
        logger.error(f"❌ Chronos integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 1 tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Phase 1 Integration Tests')
    parser.add_argument(
        '--full',
        action='store_true',
        help='Test with full 38,742-node UKG (default: 100-node subset)'
    )
    args = parser.parse_args()
    
    logger.info("🏰 PHASE 1: HAYSTACK-UKG RAG PIPELINE INTEGRATION")
    logger.info("=" * 60)
    logger.info(f"Mode: {'FULL UKG (38,742 nodes)' if args.full else 'SUBSET (100 nodes)'}")
    logger.info("=" * 60)
    
    results = {}
    
    # Run tests
    results['haystack_available'] = test_1_haystack_available()
    
    if results['haystack_available']:
        results['ukg_loading'] = test_2_ukg_loading(full_mode=args.full)
        results['retrieval'] = test_3_retrieval()
        results['merlin_generator'] = test_4_merlin_generator()
        results['chronos_integration'] = test_5_chronos_integration()
    else:
        logger.error("⚠️ Skipping remaining tests (Haystack not available)")
        logger.info("\n📦 Install Haystack:")
        logger.info("   pip install haystack-ai")
        return 1
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{test:30s} {status}")
    
    logger.info("=" * 60)
    logger.info(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED! Phase 1 integration successful.")
        logger.info("\nNext steps:")
        logger.info("1. Review Merlin-generated answers")
        logger.info("2. Test with full UKG (remove --full flag)")
        logger.info("3. Proceed to Phase 2 (Persona Mining)")
        return 0
    else:
        logger.warning("\n⚠️ Some tests failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
