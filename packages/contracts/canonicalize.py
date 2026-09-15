# SPDX-License-Identifier: MIT
"""RFC 8785 JSON Canonicalization Scheme (JCS) implementation for Camelot-OS contracts.

Provides deterministic, byte-for-byte reproducible JSON serialization
across Rust, Go, TypeScript, and Python environments.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any


def canonicalize_json(data: Any) -> str:
    """Serialize data into a deterministic RFC 8785 canonical JSON string."""
    if data is None:
        return "null"
    if isinstance(data, bool):
        return "true" if data else "false"
    if isinstance(data, (int, float)):
        if isinstance(data, float):
            if math.isnan(data) or math.isinf(data):
                raise ValueError("NaN and Infinity are not permitted in RFC 8785 JSON")
            # ECMAScript number formatting for integer-equivalent floats
            if data.is_integer():
                return str(int(data))
        return str(data)
    if isinstance(data, str):
        # json.dumps provides standard JSON string escaping
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    if isinstance(data, (list, tuple)):
        items = [canonicalize_json(item) for item in data]
        return "[" + ",".join(items) + "]"
    if isinstance(data, dict):
        # Sort keys lexicographically by UTF-16 code units
        def utf16_sort_key(key: str) -> list[int]:
            return [ord(c) for c in key.encode("utf-16-be").decode("utf-16-be")]

        sorted_keys = sorted(data.keys(), key=utf16_sort_key)
        pairs = [
            json.dumps(k, ensure_ascii=False, separators=(",", ":")) + ":" + canonicalize_json(data[k])
            for k in sorted_keys
        ]
        return "{" + ",".join(pairs) + "}"
    raise TypeError(f"Object of type {type(data)} is not JSON serializable")


def sha256_canonical(data: Any) -> str:
    """Return SHA-256 hex digest of the RFC 8785 canonical serialization."""
    canonical_bytes = canonicalize_json(data).encode("utf-8")
    return hashlib.sha256(canonical_bytes).hexdigest()
