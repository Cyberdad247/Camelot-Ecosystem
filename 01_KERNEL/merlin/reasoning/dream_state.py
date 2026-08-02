# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
THE DREAM STATE (Serendipity Engine)
Background process that runs during Sovereign inactivity.
Performs Omega Learn (Ledger Mining) and Graph Permutation.
"""

import asyncio
import os
import time

# Resolve ledger path relative to CAMELOT_OS root
_KERNEL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_LEDGER = os.path.join(_KERNEL_DIR, "PROVENANCE_LEDGER.md")


class DreamStateEngine:
    """Background self-improvement engine with configurable cycle timing."""

    def __init__(self, cycle_seconds: int = 60, ledger_path: str = _DEFAULT_LEDGER):
        self.is_dreaming = False
        self.last_dream_time = 0.0
        self.cycle_seconds = cycle_seconds
        self.ledger_path = ledger_path
        self.cycles_completed = 0
        self.last_error: str | None = None

    async def enter_dream_state(self):
        """Activates background self-improvement protocols."""
        if self.is_dreaming:
            return

        print("[DREAM STATE] Sovereign Inactive. Entering Dream State...")
        self.is_dreaming = True

        while self.is_dreaming:
            # Phase 1: Omega Learn (Ledger Mining)
            await self._mine_ledger()

            # Phase 2: Graph Permutation
            await self._permutate_graph()

            self.cycles_completed += 1
            self.last_dream_time = time.time()

            # Wait for next cycle
            try:
                await asyncio.sleep(self.cycle_seconds)
            except asyncio.CancelledError:
                break

    async def _mine_ledger(self):
        """Mine successful patterns from the Provenance Ledger."""
        try:
            from reasoning.omega_learn import mine_ledger
            if os.path.isfile(self.ledger_path):
                mine_ledger(self.ledger_path)
                self.last_error = None
            else:
                self.last_error = f"Ledger not found: {self.ledger_path}"
        except Exception as e:
            self.last_error = f"Mining error: {e}"

    async def _permutate_graph(self):
        """Discover serendipitous connections in the knowledge graph."""
        try:
            # Future: integrate with Titan Omega graph permutation
            await asyncio.sleep(1)
        except Exception as e:
            self.last_error = f"Graph permutation error: {e}"

    def wake_up(self):
        """Signal the dream engine to stop after current cycle."""
        if self.is_dreaming:
            print("[DREAM STATE] Sovereign Active. Waking up...")
        self.is_dreaming = False
        self.last_dream_time = time.time()

    def status(self) -> dict:
        return {
            "dreaming": self.is_dreaming,
            "cycles": self.cycles_completed,
            "last_dream": self.last_dream_time,
            "last_error": self.last_error,
            "cycle_interval": self.cycle_seconds,
        }


# Singleton for the Kernel to manage
dream_engine = DreamStateEngine()