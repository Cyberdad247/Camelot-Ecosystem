# SPDX-FileCopyrightText: 2026 Invisioned Marketing Inc.
# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-

"""
Persona Evolution Engine (Phase 2 Core)
Role: Continuously evolve system personas by mining logs and updating UKG.

Integration:
  - PersonaPatternExtractor (A)
  - GoldenPatternAnalyzer (B)
  - UKG Schema (C)

Usage:
    engine = PersonaEvolutionEngine()
    engine.evolve_persona('test_phase1_integration.log')
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

# Local imports
try:
    from .persona_extractor import PersonaPatternExtractor
    from .claude_pattern_miner import GoldenPatternAnalyzer
except ImportError:
    # Handle direct execution
    from persona_extractor import PersonaPatternExtractor
    from claude_pattern_miner import GoldenPatternAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonaEvolutionEngine:
    """
    Orchestrates the persona mining -> evolution -> storage loop.
    """
    
    def __init__(self, ukg_path: str = "03_VAULT/UKG/UKG_MEMORY.jsonld"):
        self.ukg_path = Path(ukg_path)
        self.extractor = PersonaPatternExtractor()
        self.miner = GoldenPatternAnalyzer()
        logger.info("🧬 Persona Evolution Engine initialized.")

    def evolve_persona(self, log_content: str) -> Dict[str, Any]:
        """
        Mine a log for persona traits and return the evolved profile.
        """
        logger.info("🔄 Evolving Persona from trace...")
        
        # 1. Mine Reasoning Style
        reasoning_profile = self.extractor.analyze_trace(log_content)
        
        # 2. Mine Prompt Patterns (simulated from log content as 'prompt')
        pattern_profile = self.miner.extract_template(log_content[:500], log_content)
        
        # 3. Create Evolved Persona Object
        evolved_persona = {
            "@type": "PersonaProfile",
            "identity_hash": "MERLIN_EVOLVED_V2",
            "reasoning_style": reasoning_profile["reasoning_style"],
            "decision_frequency": reasoning_profile["decision_frequency"],
            "complexity_handling": reasoning_profile["complexity_level"],
            "golden_patterns": {
                "context_usage": pattern_profile["context_marker"],
                "constraint_adherence": pattern_profile["constraint_marker"]
            },
            "status": "EVOLVED"
        }
        
        logger.info(f"✨ Persona evolved: {evolved_persona['reasoning_style']} | Decisions: {evolved_persona['decision_frequency']}")
        return evolved_persona

if __name__ == "__main__":
    # Test with sample log
    sample_log = """
    [SYSTEM_ACTIVATE]: Test
    Step Id: 1
    Thinking Process: Analysis complete.
    if error: raise Exception()
    """
    
    engine = PersonaEvolutionEngine()
    result = engine.evolve_persona(sample_log)
    print(json.dumps(result, indent=2))
