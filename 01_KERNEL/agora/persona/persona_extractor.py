# SPDX-FileCopyrightText: 2026 Invisioned Marketing Inc.
# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-

"""
Persona Pattern Extractor v1.0
Role: Analyze reasoning traces to mine distinct persona behaviors.

Input:  Log files, reasoning traces (Step Ids), LLM Outputs
Output: Structured Persona JSON (Reasoning Style, Decision Points, Temp Shifts)

Usage:
    extractor = PersonaPatternExtractor()
    persona = extractor.analyze_trace(log_content)
"""

import json
import logging
import re
from typing import Any, Dict

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonaPatternExtractor:
    """
    Extracts persona patterns from execution traces.
    Mines: Reasoning style, Decision velocity, Complexity handling.
    """
    
    def __init__(self):
        # We combine all patterns into a single regex and use named capture groups
        # to identify which pattern matched.
        combined = (
            r"(?P<reasoning_cot>Step Id:|Thinking Process:|Reasoning:)|"
            r"(?P<decision_point>(?:if|else|switch|match|case)\s+[\w_]+)|"
            r"(?P<temp_shift>Simulated Mode|Temperature|Mode: CoT)|"
            r"(?P<error_handling>try|except|catch|raise|Error)|"
            r"(?P<merlin_voice>🧙‍♂️|🔮|✅|⚠️|❌|🏰)"
        )
        self.COMBINED_PATTERN = re.compile(combined, re.IGNORECASE | re.UNICODE)

    def analyze_trace(self, trace_text: str) -> Dict[str, Any]:
        """
        Analyze a raw text trace and return a structured persona profile.
        
        Args:
            trace_text (str): The raw log or reasoning output.
            
        Returns:
            Dict: A dictionary representing the mined persona attributes.
        """
        logger.info("🔍 Mining trace for persona patterns...")
        
        cot_matches = 0
        decision_frequency = 0
        voice_markers = []
        temperature_dynamics = []
        error_resilience = False

        for match in self.COMBINED_PATTERN.finditer(trace_text):
            lastgroup = match.lastgroup
            if lastgroup == "reasoning_cot":
                cot_matches += 1
            elif lastgroup == "decision_point":
                decision_frequency += 1
            elif lastgroup == "temp_shift":
                temperature_dynamics.append(match.group("temp_shift"))
            elif lastgroup == "error_handling":
                error_resilience = True
            elif lastgroup == "merlin_voice":
                voice_markers.append(match.group("merlin_voice"))

        # Evaluate reasoning style
        if cot_matches > 2:
            reasoning_style = "Chain-of-Thought (Deep)"
        elif cot_matches > 0:
            reasoning_style = "Chain-of-Thought (Light)"
        elif "return" in trace_text and "def" in trace_text:
            reasoning_style = "Procedural (Code-Based)"
        else:
            reasoning_style = "Reactive (Direct)"

        profile = {
            "reasoning_style": reasoning_style,
            "decision_frequency": decision_frequency,
            "complexity_level": self._assess_complexity(trace_text),
            "voice_markers": voice_markers,
            "temperature_dynamics": temperature_dynamics,
            "error_resilience": error_resilience
        }
        
        logger.info(f"✅ Persona profile mined: {profile['reasoning_style']} style, {profile['decision_frequency']} decisions.")
        return profile

    def _assess_complexity(self, text: str) -> str:
        """Estimates complexity based on length and structure."""
        length = len(text)
        if length > 2000:
            return "High (Systemic)"
        elif length > 500:
            return "Medium (Component)"
        else:
            return "Low (Atomic)"

if __name__ == "__main__":
    # Self-Test Logic
    sample_trace = """
    Step Id: 101
    Thinking Process: Loading UKG...
    if generator_model == "merlin":
        mode = "CoT"
        generate()
    ✅ Merlin response generated.
    """
    
    extractor = PersonaPatternExtractor()
    result = extractor.analyze_trace(sample_trace)
    print(json.dumps(result, indent=2, ensure_ascii=False))
