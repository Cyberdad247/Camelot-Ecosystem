# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
recursive_search.py

Implements the Recursive Search & Reflection Engine for Chronos.
Allows the system to critique its own retrieval results and generate follow-up queries.
"""

import json
import logging
from typing import Any, Dict, List

from integrations.merlin_haystack_generator import MerlinGenerator

logger = logging.getLogger(__name__)

class ReflectionEngine:
    """
    Analyzes RAG results and determines if further searching is needed.
    """
    
    def __init__(self):
        self.evaluator = MerlinGenerator(mode="Reasoning") # Use reasoning mode for critique

    def evaluate_coverage(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Critique the retrieved documents against the query.
        Returns a score (0-10) and missing information analysis.
        """
        if not documents:
            return {"score": 0, "missing": "No documents found.", "needs_recursion": True}

        # Context for evaluation
        # Helper to get content from dict or object
        def get_content(d):
            return d.get("content", "") if isinstance(d, dict) else getattr(d, "content", str(d))
            
        docs_text = "\n\n".join([f"Doc {i+1}: {get_content(d)[:200]}..." for i, d in enumerate(documents[:3])])
        
        prompt = f"""
Evaluate if the following documents provide enough information to answer the query.
Respond ONLY with a valid JSON object matching this schema:
{{
    "score": <int 0-10>,
    "missing": "<string detailing what information is missing, or 'None'>",
    "needs_recursion": <boolean>
}}

Query: {query}

Documents:
{docs_text}
"""
        
        try:
            result = self.evaluator.run(prompt=prompt)
            reply = result.get("replies", ["{}"])[0]

            # Clean up potential markdown formatting
            if reply.startswith("```json"):
                reply = reply[7:]
            if reply.endswith("```"):
                reply = reply[:-3]

            parsed = json.loads(reply.strip())

            # Ensure required keys exist
            return {
                "score": int(parsed.get("score", 5)),
                "missing": str(parsed.get("missing", "Parsing error")),
                "needs_recursion": bool(parsed.get("needs_recursion", True))
            }
            
        except Exception as e:
            logger.error(f"Reflection failed: {e}")
            
            # Fallback to simple heuristic
            score = 10
            missing = "None"
            needs_recursion = False
            
            if len(documents) < 2:
                score = 5
                missing = "Low document count"
                needs_recursion = True
            
            return {
                "score": score,
                "missing": missing,
                "needs_recursion": needs_recursion
            }

    def generate_followup(self, original_query: str, missing_info: str) -> str:
        """
        Generate a new, more specific search query based on missing info.
        """
        return f"{original_query} {missing_info}"