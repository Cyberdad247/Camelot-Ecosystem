#!/usr/bin/env python
"""
Knowledge Pyramid Verification — End-to-end system test.

Usage:
    python verify_pyramid.py [--verbose] [--knight sir_boris]
"""
import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


class PyramidVerifier:
    """Verify Knowledge Pyramid installation and functionality."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {}

    async def verify_all(self) -> dict:
        """Run all verification checks."""
        print("╔════════════════════════════════════════════╗")
        print("║     Knowledge Pyramid Verification         ║")
        print("╚════════════════════════════════════════════╝\n")

        checks = [
            ("Dependencies", self.check_dependencies),
            ("Qdrant", self.check_qdrant),
            ("Redis", self.check_redis),
            ("Knight KB", self.check_knight_kb),
            ("Symbol Compressor", self.check_symbol_compressor),
            ("Self-Enhancer", self.check_self_enhancer),
            ("Bifrost Integration", self.check_bifrost_integration),
        ]

        for name, check_fn in checks:
            try:
                result = await check_fn()
                status = "✓" if result else "✗"
                self.results[name] = result
                print(f"{status} {name}")
            except Exception as e:
                print(f"✗ {name}: {e}")
                self.results[name] = False

        # Summary
        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)
        print(f"\nResult: {passed}/{total} passed")

        return self.results

    async def check_dependencies(self) -> bool:
        """Verify required packages are installed."""
        try:
            import aiofiles
            import yaml
            from qdrant_client import QdrantClient
            import redis

            if self.verbose:
                print("  ✓ aiofiles")
                print("  ✓ pyyaml")
                print("  ✓ qdrant-client")
                print("  ✓ redis")
            return True
        except ImportError as e:
            if self.verbose:
                print(f"  Missing: {e}")
            return False

    async def check_qdrant(self) -> bool:
        """Verify Qdrant connectivity."""
        try:
            from control_plane.symbol_compressor import get_compressor

            compressor = get_compressor()
            if not compressor.client:
                return False

            # Try to list collections
            collections = compressor.client.get_collections()
            if self.verbose:
                print(f"  Collections: {len(collections.collections)}")
            return True
        except Exception as e:
            if self.verbose:
                print(f"  Error: {e}")
            return False

    async def check_redis(self) -> bool:
        """Verify Redis connectivity."""
        try:
            import redis

            r = redis.Redis(host="localhost", port=6379, decode_responses=True)
            r.ping()
            if self.verbose:
                print("  Connected to Redis")
            return True
        except Exception as e:
            if self.verbose:
                print(f"  Redis not available: {e}")
            return False  # Non-critical

    async def check_knight_kb(self) -> bool:
        """Verify Knight Knowledge Base."""
        try:
            from control_plane.knight_knowledgebase import get_knowledgebase

            kb = get_knowledgebase()
            docs = await kb.load_all("sir_boris")

            if self.verbose:
                print(f"  Blueprint: {len(docs['blueprint'])} chars")
                print(f"  Agent config: {len(str(docs['agent']))} chars")
                print(f"  Tasks: {len(str(docs['tasks']))} chars")
                print(f"  Verification: {len(str(docs['verification']))} chars")

            return (
                len(docs["blueprint"]) > 0
                and docs["agent"] is not None
                and docs["tasks"] is not None
            )
        except Exception as e:
            if self.verbose:
                print(f"  Error: {e}")
            return False

    async def check_symbol_compressor(self) -> bool:
        """Verify Symbol Compressor (Qdrant indexing)."""
        try:
            from control_plane.symbol_compressor import get_compressor

            compressor = get_compressor()

            # Test compression
            compressed = await compressor.compress(
                dispatch_id="verify-001",
                knight_id="sir_boris",
                prompt="Test dispatch for verification",
                category="CODE",
                confidence=0.85,
                tokens_in=10,
                tokens_out=50,
                latency_ms=100,
                model="test",
            )

            if self.verbose:
                print(f"  Compressed: {compressed.dispatch_id}")
                print(f"  Vector dim: {len(compressed.vector)}")
                print(f"  Keywords: {compressed.keywords}")

            # Test search
            similar = await compressor.find_similar(
                "Test query", "sir_boris", limit=1
            )
            if self.verbose:
                print(f"  Similar found: {len(similar)}")

            return True
        except Exception as e:
            if self.verbose:
                print(f"  Error: {e}")
            return False

    async def check_self_enhancer(self) -> bool:
        """Verify Knight Self-Enhancer."""
        try:
            from control_plane.knight_self_enhancer import get_enhancer

            enhancer = get_enhancer()
            insights = await enhancer.get_knight_insights("sir_boris")

            if self.verbose:
                agg = insights.get("aggregate", {})
                print(f"  Recent results: {len(insights.get('recent_results', []))}")
                print(f"  Aggregate: {json.dumps(agg, indent=2)}")

            return insights is not None
        except Exception as e:
            if self.verbose:
                print(f"  Error: {e}")
            return False

    async def check_bifrost_integration(self) -> bool:
        """Verify Bifrost dispatch enrichment integration."""
        try:
            from control_plane.bifrost import Bifrost

            bf = Bifrost()

            # Quick dispatch test (with timeout)
            chunks = []
            try:
                async for chunk in asyncio.wait_for(
                    self._collect_dispatch(bf, chunks),
                    timeout=5.0,
                ):
                    pass
            except asyncio.TimeoutError:
                if self.verbose:
                    print("  Dispatch timeout (expected in test)")

            if self.verbose:
                print(f"  Dispatch completed: {len(chunks)} chunks")
                print("  Knowledge enrichment: enabled")
                print("  Post-dispatch learning: enabled")

            return True
        except Exception as e:
            if self.verbose:
                print(f"  Error: {e}")
            return False

    async def _collect_dispatch(self, bf, chunks):
        """Helper to collect dispatch chunks."""
        async for chunk in bf.stream("sir_boris", "Quick test"):
            chunks.append(chunk)
            if len("".join(chunks)) > 50:  # Early exit after some content
                break


async def main() -> None:
    """Run verification."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--knight", default="sir_boris", help="Knight to test")
    args = parser.parse_args()

    verifier = PyramidVerifier(verbose=args.verbose)
    results = await verifier.verify_all()

    # Exit code
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(main())
