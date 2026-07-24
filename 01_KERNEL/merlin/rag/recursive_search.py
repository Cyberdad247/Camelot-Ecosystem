# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
recursive_search.py

Implements the Recursive Search & Reflection Engine for Chronos.
Allows the system to critique its own retrieval results and generate follow-up queries.
"""

import json
import logging
import re
from typing import Any, Dict, List

from integrations.merlin_haystack_generator import MerlinGenerator

logger = logging.getLogger(__name__)


class ReflectionEngine:
    """
    Analyzes RAG results and determines if further searching is needed.
    """

    def __init__(self):
        self.evaluator = MerlinGenerator(mode="Reasoning")  # Use reasoning mode for critique

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

        context_preview = "\n".join([get_content(d)[:200] + "..." for d in documents[:3]])

        prompt = f"""
        [SYSTEM: REFLECTION_AGENT]
        Analyze if the provided documents are sufficient to answer the user query.
        
        Query: {query}
        
        Retrieved Documents (Preview):
        {context_preview}
        
        Task:
        1. Rate coverage (0-10).
        2. Identify MISSING information.
        3. Determine if we need more searches (True/False).
        
        Output JSON format:
        {{
            "score": <int>,
            "missing": "<description>",
            "needs_recursion": <bool>
        }}
        """

        try:
            # Call actual LLM for critique
            response = self.evaluator.run(prompt=prompt)
            reply = response.get("replies", [""])[0]

            # Attempt to extract JSON from the reply
            json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", reply, re.DOTALL)
            if json_match:
                reply_json_str = json_match.group(1)
            else:
                # Fallback to finding any dictionary-like structure
                dict_match = re.search(r"(\{.*?\})", reply, re.DOTALL)
                reply_json_str = dict_match.group(1) if dict_match else reply

            try:
                result = json.loads(reply_json_str)
                return {
                    "score": int(result.get("score", 0)),
                    "missing": str(result.get("missing", "Parse Error")),
                    "needs_recursion": bool(result.get("needs_recursion", False)),
                }
            except json.JSONDecodeError:
                logger.error(f"Failed to parse LLM response as JSON: {reply}")
                # Fallback heuristic if JSON parsing fails
                score = 10
                missing = "None"
                needs_recursion = False

                if len(documents) < 2:
                    score = 5
                    missing = "Low document count"
                    needs_recursion = True

                return {"score": score, "missing": missing, "needs_recursion": needs_recursion}

        except Exception as e:
            logger.error(f"Reflection failed: {e}")
            return {"score": 0, "missing": "Error", "needs_recursion": False}

    def generate_followup(self, original_query: str, missing_info: str) -> str:
        """
        Generate a new, more specific search query based on missing info.
        """
        return f"{original_query} {missing_info}"
