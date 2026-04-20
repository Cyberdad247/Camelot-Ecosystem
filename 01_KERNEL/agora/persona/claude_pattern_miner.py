# SPDX-FileCopyrightText: 2026 Invisioned Marketing Inc.
# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-

"""
Golden Pattern Analyzer v1.0 (Claude Pattern Miner)
Role: Analyze high-quality 'Golden Traces' to extract prompt engineering templates.

Input:  List of prompt/response pairs (Golden Traces).
Output: Reusable prompt templates (System Context, Task Def, Constraint, Output).

Usage:
    miner = GoldenPatternAnalyzer()
    template = miner.extract_template(prompt, response)
"""

import re
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoldenPatternAnalyzer:
    """
    Extracts underlying prompt structures from successful interactions.
    Identify: System Context blocks, Task definitions, Constraints.
    """
    
    def __init__(self):
        self.MARKERS = {
            "system_context": re.compile(r"(\[SYSTEM_ACTIVATE\]:|Role:|Identity:)", re.IGNORECASE),
            "task_def": re.compile(r"(Task:|Objective:|Goal:)", re.IGNORECASE),
            "constraints": re.compile(r"(Constraint:|Rule:|Warning:|Note:)", re.IGNORECASE),
            "output_format": re.compile(r"(Output:|Format:|Return:)", re.IGNORECASE)
        }

    def extract_template(self, prompt_text: str, response_text: str) -> Dict[str, Any]:
        """
        Derive a reusable template from a golden prompt/response pair.
        """
        logger.info("✨ Mining Golden Pattern from prompt...")
        
        template = {
            "context_marker": self._find_marker(prompt_text, "system_context"),
            "task_marker": self._find_marker(prompt_text, "task_def"),
            "constraint_marker": self._find_marker(prompt_text, "constraints"),
            "output_marker": self._find_marker(prompt_text, "output_format"),
            "response_analysis": {
                "length": len(response_text),
                "structure": "Structured Checkpoint/Log" if "Step Id" in response_text else "Free Text"
            }
        }
        
        logger.info(f"✅ Template extracted with {len([k for k,v in template.items() if v])} active components.")
        return template

    def _find_marker(self, text: str, key: str) -> bool:
        """True if the prompt explicitly uses this structural marker."""
        return bool(self.MARKERS[key].search(text))

if __name__ == "__main__":
    miner = GoldenPatternAnalyzer()
    sample_prompt = """
    [SYSTEM_ACTIVATE]: Code Audit
    Task: Audit this file.
    Constraint: No emojis.
    Output: JSON only.
    """
    sample_response = "{ 'status': 'audited' }"
    
    print(json.dumps(miner.extract_template(sample_prompt, sample_response), indent=2))
