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

import re
import json
import logging
from typing import Dict, List, Any

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonaPatternExtractor:
    """
    Extracts persona patterns from execution traces.
    Mines: Reasoning style, Decision velocity, Complexity handling.
    """
    
    def __init__(self):
        # Patterns to mine
        self.PATTERNS = {
            "reasoning_cot": re.compile(r"(Step Id:|Thinking Process:|Reasoning:)", re.IGNORECASE),
            "decision_point": re.compile(r"(if|else|switch|match|case)\s+[\w_]+", re.IGNORECASE),
            "temp_shift": re.compile(r"(Simulated Mode|Temperature|Mode: CoT)", re.IGNORECASE),
            "error_handling": re.compile(r"(try|except|catch|raise|Error)", re.IGNORECASE),
            "merlin_voice": re.compile(r"(🧙‍♂️|🔮|✅|⚠️|❌|🏰)", re.UNICODE)
        }

    def analyze_trace(self, trace_text: str) -> Dict[str, Any]:
        """
        Analyze a raw text trace and return a structured persona profile.
        
        Args:
            trace_text (str): The raw log or reasoning output.
            
        Returns:
            Dict: A dictionary representing the mined persona attributes.
        """
        logger.info("🔍 Mining trace for persona patterns...")
        
        profile = {
            "reasoning_style": self._detect_reasoning_style(trace_text),
            "decision_frequency": len(self.PATTERNS["decision_point"].findall(trace_text)),
            "complexity_level": self._assess_complexity(trace_text),
            "voice_markers": self.PATTERNS["merlin_voice"].findall(trace_text),
            "temperature_dynamics": self._detect_temp_shifts(trace_text),
            "error_resilience": len(self.PATTERNS["error_handling"].findall(trace_text)) > 0
        }
        
        logger.info(f"✅ Persona profile mined: {profile['reasoning_style']} style, {profile['decision_frequency']} decisions.")
        return profile

    def _detect_reasoning_style(self, text: str) -> str:
        """Determines if the trace is Chain-of-Thought, Reactive, or Procedural."""
        cot_matches = len(self.PATTERNS["reasoning_cot"].findall(text))
        if cot_matches > 2:
            return "Chain-of-Thought (Deep)"
        elif cot_matches > 0:
            return "Chain-of-Thought (Light)"
        elif "return" in text and "def" in text:
            return "Procedural (Code-Based)"
        else:
            return "Reactive (Direct)"

    def _assess_complexity(self, text: str) -> str:
        """Estimates complexity based on length and structure."""
        length = len(text)
        if length > 2000:
            return "High (Systemic)"
        elif length > 500:
            return "Medium (Component)"
        else:
            return "Low (Atomic)"

    def _detect_temp_shifts(self, text: str) -> List[str]:
        """Finds explicit mentions of mode or temperature changes."""
        return self.PATTERNS["temp_shift"].findall(text)

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
