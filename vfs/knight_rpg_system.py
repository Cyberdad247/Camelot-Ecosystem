# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — RPG Knight Progression & SkillGraph System
"""
RPG System for Camelot-OS Knights:
- Progression: Level (1-100), XP, Mana, Class, SkillGraph (S1-S5)
- OCEAN Personality Vectors & Runic Alignments
- Grants XP upon verified task completion, TDD audit passes, and GEP evolution
"""

from __future__ import annotations

import json
import logging
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

LOG = logging.getLogger("KnightRPG")
CAMELOT_ROOT = Path(__file__).resolve().parent.parent

# ── Complete Knight Class Matrix ──────────────────────────────────────────────
KNIGHT_CLASSES: Dict[str, Dict[str, Any]] = {
    "KING_ARTHUR":     {"class": "Sovereign Lord",    "primary_stat": "Authority",    "base_rune": "ᛟ"},
    "SIR_BORIS":       {"class": "Crucible Master",   "primary_stat": "Architecture", "base_rune": "ᚨ"},
    "SIR_ALEX":        {"class": "DAG Tactician",     "primary_stat": "Planning",     "base_rune": "ᚨ"},
    "SIR_FORGE":       {"class": "Kinetic Paladin",   "primary_stat": "Execution",    "base_rune": "ᚠ"},
    "SIR_CODEX":       {"class": "Cybernetic Knight", "primary_stat": "Velocity",     "base_rune": "ᚠ"},
    "SIR_SENTINEL":    {"class": "Iron Shield",       "primary_stat": "Security",     "base_rune": "ᛜ"},
    "SIR_DEBUG":       {"class": "Alchemical Doctor", "primary_stat": "Self-Healing",  "base_rune": "ᛞ"},
    "SIR_GHOST":       {"class": "Shadow Spectre",    "primary_stat": "Air-Gap Privacy","base_rune": "ᛜ"},
    "LADY_APIS":       {"class": "Knowledge Scout",   "primary_stat": "Research",     "base_rune": "ᚱ"},
    "MERLIN_OMEGA":    {"class": "Archmage Reasoner", "primary_stat": "Deep Thinking", "base_rune": "ᚱ"},
    "SIR_HELIO":       {"class": "Vocal Bard",        "primary_stat": "Realtime Audio", "base_rune": "ᚢ"},
    "SIR_SONUS":       {"class": "Harmonic Weaver",   "primary_stat": "Phonetics",    "base_rune": "ᚢ"},
    "LADY_MNEMOSYNE":  {"class": "Memory Chronicler", "primary_stat": "Swarm Governance","base_rune": "ᛗ"},
    "ANYA_QUANTUM_MANTRA":{"class": "Quantum Alchemist","primary_stat": "Token Compression","base_rune": "ᛗ"},
    "SIR_HEIMDALL":    {"class": "Bifrost Guardian",  "primary_stat": "mTLS Transport","base_rune": "ᛜ"},
    "SIR_GALAHAD":     {"class": "Pure Verifier",     "primary_stat": "Integrity",    "base_rune": "ᚨ"},
    "SIR_ALCHEMIST":   {"class": "Code Optimizer",    "primary_stat": "Refactoring",  "base_rune": "ᚠ"},
    "SIR_HERMES":      {"class": "Swift Messenger",   "primary_stat": "Telemetry",    "base_rune": "ᚱ"},
    "SIR_RUSTCLAW":    {"class": "Kernel Specialist", "primary_stat": "Bare-Metal Rust","base_rune": "ᚠ"},
    "SIR_STITCH":      {"class": "Cartridge Weaver",  "primary_stat": "Hot-Swap Packages","base_rune": "ᚨ"},
    "LADY_SPARKLE":    {"class": "UI Virtuoso",       "primary_stat": "Aesthetics",   "base_rune": "ᚠ"},
    "SIR_SCAVENGER":   {"class": "Orphan Purger",     "primary_stat": "Garbage Collection","base_rune": "ᚦ"},
}


class KnightRPGSystem:
    """Manages progression, XP calculation, levels, and SkillGraph tiers for Knights."""

    def __init__(self):
        self.rpg_db_path = CAMELOT_ROOT / "vfs" / "knight_rpg_database.json"
        self.roster: Dict[str, Dict[str, Any]] = self._load_or_init_db()

    def _load_or_init_db(self) -> Dict[str, Dict[str, Any]]:
        if self.rpg_db_path.exists():
            try:
                with open(self.rpg_db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # Initialize all Knights with default Level 1 stats
        db = {}
        for knight_id, meta in KNIGHT_CLASSES.items():
            db[knight_id] = {
                "knight_id": knight_id,
                "title": meta["class"],
                "level": 10,  # Base veteran level for Core Knights
                "xp": 1000,
                "xp_to_next_level": 1500,
                "primary_stat": meta["primary_stat"],
                "rune": meta["base_rune"],
                "skill_graph_tier": "S3 Contextual",
                "ocean_vector": {
                    "openness": 0.85,
                    "conscientiousness": 0.95,
                    "extraversion": 0.30,
                    "agreeableness": 0.60,
                    "neuroticism": 0.05
                },
                "tasks_completed": 0,
                "last_active": datetime.now(timezone.utc).isoformat()
            }
        return db

    def save_db(self):
        with open(self.rpg_db_path, "w", encoding="utf-8") as f:
            json.dump(self.roster, f, indent=2, ensure_ascii=False)

    def award_xp(self, knight_id: str, xp_amount: int, task_name: str) -> Dict[str, Any]:
        """Award XP to a Knight and trigger Level-Up / SkillGraph evolution."""
        if knight_id not in self.roster:
            # Auto-register new knight
            self.roster[knight_id] = {
                "knight_id": knight_id,
                "title": "Knight of Camelot",
                "level": 1,
                "xp": 0,
                "xp_to_next_level": 100,
                "primary_stat": "Kinetic",
                "rune": "ᚠ",
                "skill_graph_tier": "S1 Atomic",
                "tasks_completed": 0,
                "last_active": datetime.now(timezone.utc).isoformat()
            }

        k = self.roster[knight_id]
        k["xp"] += xp_amount
        k["tasks_completed"] += 1
        k["last_active"] = datetime.now(timezone.utc).isoformat()

        leveled_up = False
        while k["xp"] >= k["xp_to_next_level"]:
            k["level"] += 1
            k["xp_to_next_level"] = int(k["xp_to_next_level"] * 1.5)
            leveled_up = True

        # Update SkillGraph Tier based on Level
        lvl = k["level"]
        if lvl >= 50:
            k["skill_graph_tier"] = "S5 Sovereign"
        elif lvl >= 35:
            k["skill_graph_tier"] = "S4 Strategic"
        elif lvl >= 20:
            k["skill_graph_tier"] = "S3 Contextual"
        elif lvl >= 10:
            k["skill_graph_tier"] = "S2 Composite"
        else:
            k["skill_graph_tier"] = "S1 Atomic"

        self.save_db()
        LOG.info(f"⚔️ [{knight_id}] +{xp_amount} XP for '{task_name}' (Level: {k['level']} | Tier: {k['skill_graph_tier']})")
        return {"knight_id": knight_id, "level": k["level"], "leveled_up": leveled_up, "tier": k["skill_graph_tier"]}

    def get_roster_summary(self) -> str:
        lines = [
            "╔═══════════════════════════════════════════════════════╗",
            "║       CAMELOT-OS KNIGHT RPG PROGRESSION ROSTER        ║",
            "╚═══════════════════════════════════════════════════════╝",
            ""
        ]
        for kid, data in self.roster.items():
            lines.append(f"  [{data['rune']} {kid:<22}] Lvl {data['level']:<2} | {data['skill_graph_tier']:<14} | Stat: {data['primary_stat']}")
        return "\n".join(lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    rpg = KnightRPGSystem()
    rpg.award_xp("SIR_FORGE", 500, "VFS Token Reduction Build")
    rpg.award_xp("LADY_MNEMOSYNE", 750, "Worldtree SQUIRE_BRIEF Sweep")
    print(rpg.get_roster_summary())
