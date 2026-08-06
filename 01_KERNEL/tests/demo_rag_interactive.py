# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# SPDX-FileCopyrightText: 2026 Invisioned Marketing Inc.
# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-

"""
Interactive RAG Demo: Haystack-UKG with Merlin

Showcases the Phase 1 integration with real-time querying.
"""

import sys
from pathlib import Path

# Fix Python import paths
script_dir = Path(__file__).parent.absolute()
kernel_dir = script_dir.parent  # 01_KERNEL
camelot_root = kernel_dir.parent  # CAMELOT_OS root

sys.path.insert(0, str(kernel_dir))
sys.path.insert(0, str(camelot_root))

# Force UTF-8 on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from integrations.haystack_ukg_bridge import HaystackUKGBridge


def print_banner():
    """Print demo banner."""
    print("=" * 70)
    print("🏰 CAMELOT OS - HAYSTACK-UKG RAG DEMO")
    print("=" * 70)
    print("Phase 1: Semantic Knowledge Retrieval + Merlin Answer Generation")
    print("=" * 70)
    print()


def demo_query(bridge, question: str, top_k: int = 3):
    """Run a demo query and display results."""
    print(f"\n🔍 QUERY: {question}")
    print("-" * 70)
    
    # Query UKG
    result = bridge.query(question, top_k=top_k, generator_model="merlin")
    
    # Display retrieved documents
    print(f"\n📚 Retrieved {len(result['documents'])} relevant documents:")
    for i, doc in enumerate(result['documents'], 1):
        print(f"\n  {i}. Source: {doc['source']}")
        print(f"     Score: {doc['score']:.4f}" if doc['score'] else "     Score: N/A")
        print(f"     Content: {doc['content'][:150]}...")
    
    # Display Merlin's generated answer
    if result['answer']:
        print("\n🧙‍♂️ MERLIN'S ANSWER:")
        print("-" * 70)
        print(result['answer'])
        print("-" * 70)
        
        # Display metadata
        print("\n📊 METADATA:")
        print(f"  - Generator: {result['metadata']['generator']}")
        print(f"  - Retriever: {result['metadata']['retriever']}")
        print(f"  - Total Results: {result['metadata']['total_results']}")
    else:
        print("\n⚠️ No answer generated (retrieval-only mode)")
    
    print("\n" + "=" * 70)


def main():
    """Run interactive demo."""
    print_banner()
    
    # Initialize bridge with subset for faster demo
    print("⚙️  Initializing Haystack-UKG Bridge (100-node subset)...")
    bridge = HaystackUKGBridge(max_nodes=100)
    
    print(f"✅ Bridge ready with {bridge.document_store.count_documents()} UKG documents\n")
    
    # Demo queries
    demo_queries = [
        ("What is the Septem Regna architecture?", 3),
        ("Explain the role of Merlin Omega in Camelot OS", 3),
        ("What are the kinetic binaries in Layer 2?", 2),
    ]
    
    for question, top_k in demo_queries:
        demo_query(bridge, question, top_k)
        input("\nPress Enter to continue to next query...")
    
    print("\n🎉 Demo complete!")
    print("\nNext steps:")
    print("  1. Review generated answers for accuracy")
    print("  2. Test with full UKG (remove max_nodes limit)")
    print("  3. Proceed to Phase 2 (Persona Mining)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
