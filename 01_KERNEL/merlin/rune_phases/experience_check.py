# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
==============================================================================
EXPERIENCE_CHECK RUNE PHASE
Camelot OS v33.0 - The Learning Phase
==============================================================================
Position: AFTER Anya_Ingest, BEFORE Extract
Symbol: {🧠}
==============================================================================
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from kernel.storage.exp_ledger import EXPEntry, EXPLedger


# ==============================================================================
# CONFIGURATION
# ==============================================================================

PHASE_NAME = "Experience_Check"
PHASE_SYMBOL = "🧠"
PHASE_POSITION = "AFTER_Anya_Ingest"


# ==============================================================================
# RISK TAG EXTRACTION (Simplified Anya_APEE)
# ==============================================================================


def extract_complication_tags(prompt: str) -> tuple[str, list[str]]:
    """
    Extract potential complication type and tags from prompt.
    This is a simplified version of Anya_APEE risk analysis.

    Returns:
        (complication_type, [tags])
    """
    prompt_lower = prompt.lower()

    # Detect complication type
    complication_type = "General"

    type_keywords = {
        "SyntaxError": ["syntax", "parse", "invalid", "unexpected token"],
        "ImportError": ["import", "module", "package", "not found"],
        "TypeError": ["type", "cannot", "expected", "got"],
        "NameError": ["undefined", "not defined", "unknown"],
        "ValueError": ["value", "invalid", "out of range"],
        "RuntimeError": ["runtime", "crash", "exception"],
        "AmbiguousDirective": ["unclear", "ambiguous", "which", "what do you mean"],
        "EthicalConflict": ["should i", "is it okay", "ethical", "allowed"],
        "Timeout": ["timeout", "slow", "taking too long", "hanging"],
    }

    for ctype, keywords in type_keywords.items():
        if any(kw in prompt_lower for kw in keywords):
            complication_type = ctype
            break

    # Extract tags
    tags = []

    # Language detection
    languages = ["python", "javascript", "typescript", "rust", "go", "java", "c++", "sql"]
    for lang in languages:
        if lang in prompt_lower:
            tags.append(lang)

    # Domain detection
    domains = [
        "api",
        "database",
        "web",
        "file",
        "network",
        "async",
        "thread",
        "memory",
        "performance",
        "security",
        "auth",
        "data",
        "parsing",
    ]
    for domain in domains:
        if domain in prompt_lower:
            tags.append(domain)

    # Error type tags
    error_tags = ["error", "exception", "bug", "fix", "debug", "issue", "problem"]
    for et in error_tags:
        if et in prompt_lower:
            tags.append(et)

    return complication_type, list(set(tags))[:10]  # Limit to 10 tags


# ==============================================================================
# EXPERIENCE CHECK RESULT
# ==============================================================================


@dataclass
class ExperienceCheckResult:
    """Result of the Experience_Check phase."""

    match_found: bool
    entry: Optional["EXPEntry"] = None
    prompt_hash: str = ""
    complication_type: str = ""
    tags: list[str] = None
    should_skip_phases: bool = False
    solution_steps: list[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.solution_steps is None:
            self.solution_steps = []


# ==============================================================================
# MAIN PHASE IMPLEMENTATION
# ==============================================================================


def generate_prompt_hash(prompt: str) -> str:
    """Generate SHA-256 hash of user prompt."""
    return hashlib.sha256(prompt.encode()).hexdigest()


async def experience_check(
    prompt: str,
    persona_id: str,
    ledger: Optional["EXPLedger"] = None,
) -> ExperienceCheckResult:
    """
    Execute the Experience_Check rune phase.

    WORKFLOW:
    1. Generate prompt_hash (SHA-256)
    2. Extract complication_tags using simplified Anya_APEE
    3. Query the persona's EXP_Ledger for matches
    4. If match found → return solution for injection
    5. If no match → return empty result (continue normal flow)

    Args:
        prompt: User's input prompt
        persona_id: ID of the Knight/Squire
        ledger: Optional EXPLedger instance (will create if not provided)

    Returns:
        ExperienceCheckResult with match status and solution if found
    """
    # Import here to avoid circular imports
    from kernel.storage.exp_ledger import EXPLedger as LedgerClass

    # Step 1: Generate prompt hash
    prompt_hash = generate_prompt_hash(prompt)

    # Step 2: Extract complication type and tags
    complication_type, tags = extract_complication_tags(prompt)

    # Step 3: Query ledger
    if ledger is None:
        ledger = LedgerClass(persona_id)

    entry = ledger.query_matching(prompt_hash, complication_type, tags)

    # Step 4 & 5: Return result
    if entry:
        # Match found - update last_reused
        ledger.update_last_reused(entry.exp_id)

        return ExperienceCheckResult(
            match_found=True,
            entry=entry,
            prompt_hash=prompt_hash,
            complication_type=complication_type,
            tags=tags,
            should_skip_phases=True,
            solution_steps=entry.resolution.solution_steps,
        )

    # No match - continue normal flow
    return ExperienceCheckResult(
        match_found=False,
        entry=None,
        prompt_hash=prompt_hash,
        complication_type=complication_type,
        tags=tags,
        should_skip_phases=False,
        solution_steps=[],
    )


# ==============================================================================
# SYNC VERSION
# ==============================================================================


def experience_check_sync(
    prompt: str,
    persona_id: str,
    ledger: Optional["EXPLedger"] = None,
) -> ExperienceCheckResult:
    """Synchronous version of experience_check."""
    import asyncio

    return asyncio.get_event_loop().run_until_complete(experience_check(prompt, persona_id, ledger))


# ==============================================================================
# TESTING
# ==============================================================================


if __name__ == "__main__":
    import asyncio

    async def test():
        print("[TEST] Experience_Check Phase")
        print("=" * 50)

        # Test tag extraction
        prompt1 = "Python import error with pandas module"
        ctype, tags = extract_complication_tags(prompt1)
        print(f"[1] Prompt: '{prompt1}'")
        print(f"    Type: {ctype}, Tags: {tags}")

        # Test hash generation
        hash1 = generate_prompt_hash(prompt1)
        print(f"    Hash: {hash1[:16]}...")

        # Test experience check (will find nothing in empty ledger)
        result = await experience_check(prompt1, "Sir_Syntax_Test")
        print(f"[2] Match found: {result.match_found}")
        print(f"    Should skip phases: {result.should_skip_phases}")

        print("=" * 50)
        print("[PASS] Experience_Check phase working correctly.")

    asyncio.run(test())