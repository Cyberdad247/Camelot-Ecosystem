# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Phial: Regex Cleaner
A specialized tool for cleaning structured data from LLM outputs.
Input: Raw string
Output: JSON-compliant structure
"""

import json
import re


def clean_json(text: str) -> str:
    """Extract and repair JSON from Markdown fenced blocks"""
    pattern = r"```json\s*(\{.*?\})\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)

    # Fallback: Find raw JSON object
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        return match.group(1)

    return "{}"


def phial_main(raw_input: str) -> dict:
    """Main entrypoint for the Phial"""
    cleaned = clean_json(raw_input)
    try:
        data = json.loads(cleaned)
        return {"status": "success", "data": data}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON"}


if __name__ == "__main__":
    import sys

    # Read from stdio in production
    if len(sys.argv) > 1:
        inp = sys.argv[1]
    else:
        inp = '```json\n{"key": "value"}\n```'

    print(phial_main(inp))