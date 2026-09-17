#!/usr/bin/env python
"""
Test Knight Flash Memory integration.

Usage:
    python test_knight_memory.py [--search <query>]

Example:
    python test_knight_memory.py --search "Which knight handles security?"
"""
import asyncio
import sys
from pathlib import Path

# Add CAMELOT_OS to path
sys.path.insert(0, str(Path(__file__).parent))

from control_plane.agent_memory import (
    get_memory,
    log_dispatch,
    log_response,
    search,
    store_fact,
)


async def main() -> None:
    mem = get_memory()

    if not mem.client:
        print("❌ Agent Memory not initialized. Check AGENT_MEMORY_API_KEY env var.")
        return

    print("✓ Agent Memory initialized\n")

    # Log some example dispatches
    print("--- Logging Example Dispatches ---")

    await log_dispatch(
        terminal_id="sir_boris",
        prompt="Refactor this authentication module",
        system="You are an expert code architect",
        model="claude-sonnet-4-6"
    )
    print("✓ Logged dispatch: sir_boris (refactor)")

    await log_response(
        terminal_id="sir_boris",
        response="I'd recommend splitting this into three smaller modules...",
        latency_ms=234.5
    )
    print("✓ Logged response: sir_boris (234.5ms)")

    await log_dispatch(
        terminal_id="sir_sentinel",
        prompt="Audit this code for security vulnerabilities",
        system="You are a security expert",
        model="claude-haiku-4-5-20251001"
    )
    print("✓ Logged dispatch: sir_sentinel (audit)\n")

    # Store facts about capabilities
    print("--- Storing Knight Facts ---")

    facts = [
        ("sir_boris", "specializes in architecture review and code refactoring"),
        ("sir_sentinel", "focuses on security audits and vulnerability detection"),
        ("sir_helio", "handles large-context research and document analysis"),
        ("sir_ghost", "air-gapped, offline-only, zero-trust model"),
    ]

    for terminal_id, fact in facts:
        await store_fact(terminal_id, fact)
        print(f"✓ Stored fact: {terminal_id}")

    print()

    # Search examples
    print("--- Semantic Search ---\n")

    searches = [
        "Which knight handles security?",
        "What specializes in refactoring?",
        "Which model is air-gapped?",
    ]

    for query in searches:
        results = await search(query, limit=3)
        print(f"Query: {query}")
        if results:
            for i, result in enumerate(results, 1):
                text = result.get("text", "")[:100]
                score = result.get("score", 0)
                print(f"  {i}. {text}... (score: {score:.3f})")
        else:
            print("  (no results)")
        print()

    # Get session
    print("--- Session Retrieval ---\n")

    session = await mem.get_session("sir_boris")
    if session:
        events = session.get("events", [])
        print(f"sir_boris session: {len(events)} events")
        for event in events[:2]:
            role = event.get("role")
            content = event.get("content", [{}])[0].get("text", "")[:50]
            print(f"  - {role}: {content}...")
    else:
        print("(no session yet)")

    print("\n✓ Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
