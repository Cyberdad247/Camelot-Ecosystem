# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Symbolect - Symbol Compression System
Assimilated from CC_v32_Kingdom

Provides text compression via symbolic encoding for:
- Memory efficiency
- Compact logs
- Cryptic communication
"""

SYMBOL_MAP = {
    "thought": "🧠",
    "plan": "🗺️",
    "action": "⚙️",
    "success": "✅",
    "failure": "❌",
    "idea": "💡",
    "quest": "🛡️",
    "report": "📜",
    "system": "💻",
    "integrate": "🔗",
    "validate": "✔️",
}

REVERSE_SYMBOL_MAP = {v: k for k, v in SYMBOL_MAP.items()}


def encode_symbolect(text: str) -> str:
    """
    Encode text into Symbolect (symbol compression).

    Args:
        text: Plain text string

    Returns:
        Symbolect-encoded string

    Example:
        >>> encode_symbolect("My thought for the plan")
        "My 🧠 for the 🗺️"
    """
    encoded_text = text
    for word, symbol in SYMBOL_MAP.items():
        # Replace whole words only
        encoded_text = encoded_text.replace(word, symbol)
    return encoded_text


def decode_symbolect(symbolect_text: str) -> str:
    """
    Decode Symbolect back to plain text.

    Args:
        symbolect_text: Symbolect-encoded string

    Returns:
        Decoded plain text

    Example:
        >>> decode_symbolect("My 🧠 for the 🗺️")
        "My thought for the plan"
    """
    decoded_text = symbolect_text
    for symbol, word in REVERSE_SYMBOL_MAP.items():
        decoded_text = decoded_text.replace(symbol, word)
    return decoded_text