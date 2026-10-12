# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
CLARITY_CORE v1.0.0 — SQUIRE TOKENPRESS
=======================================
Payload & Inter-Agent Context Compression Engine for Camelot-OS.
Enforces Symbolect Dialogue Law and token economy:
  - Triple-QFT Symbolect token reduction & expansion
  - Sub-millisecond Zstandard binary compression with zlib fallback
  - Transparent encoding/decoding for JSON-RPC, AST cache, and multi-knight transcripts.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Optional, Tuple, Union

try:
    import zstandard as zstd
    _HAS_ZSTD = True
except ImportError:
    import zlib
    _HAS_ZSTD = False

LOG = logging.getLogger("SquireTokenPress")

# Canonical Magic Headers
MAGIC_ZSTD = b"CQZ1"
MAGIC_ZLIB = b"CQG1"
MAGIC_SYMBOLECT = b"CQS1"

# Triple-QFT Symbolect High-Frequency Vocabulary (1:1 Bijection)
SYMBOLECT_LEXICON: Dict[str, str] = {
    "ANYA_IS_THE_GATE": "⟐ANYA_GATE⟐",
    "PROVENANCE_LEDGER.md": "⟐PROV_LEDGER_MD⟐",
    "PROVENANCE_LEDGER": "⟐PROV_LEDGER⟐",
    "CYBERTRONIA": "⟐CYBERTRONIA⟐",
    "MERLIN_OMEGA": "⟐MERLIN_Ω⟐",
    "SIR_HELIOS": "⟐SIR_HELIOS⟐",
    "SIR_LUCAS": "⟐SIR_LUCAS⟐",
    "SIR_BORIS": "⟐SIR_BORIS⟐",
    "SIR_SENTINEL": "⟐SIR_SENTINEL⟐",
    "SIR_CODEX": "⟐SIR_CODEX⟐",
    "BIFROST_GATEWAY": "⟐BIFROST⟐",
    "TAILSCALE_MESH": "⟐TS_MESH⟐",
    "Warp Gate Keypass": "⟐WARP_KEYPASS⟐",
    "warp_gate_keypass": "⟐WARP_KEYPASS_LOWER⟐",
    "03_VAULT/runtime_state": "⟐VAULT_RT⟐",
    "04_KINETIC": "⟐KINETIC_04⟐",
    "01_KERNEL": "⟐KERNEL_01⟐",
    "02_FORGE": "⟐FORGE_02⟐",
    "control_plane": "⟐CTRL_PLANE⟐",
    "vfs://worldtree": "⟐VFS_TREE⟐",
    "Samsung Galaxy S26 Ultra": "⟐EXCALIBUR_S26⟐",
    "SM-S948U": "⟐EXCALIBUR_MODEL⟐",
}

# Reverse mapping for expansion
REVERSE_SYMBOLECT_LEXICON: Dict[str, str] = {v: k for k, v in SYMBOLECT_LEXICON.items()}


class SquireTokenPress:
    """Inter-agent compression squire combining symbolic substitution with modern LZ algorithms."""

    def __init__(self, level: int = 3) -> None:
        self.level = level
        if _HAS_ZSTD:
            self._cctx = zstd.ZstdCompressor(level=self.level)
            self._dctx = zstd.ZstdDecompressor()
        else:
            self._cctx = None
            self._dctx = None

    @staticmethod
    def compress_symbolect(text: str) -> str:
        """Applies Symbolect token reduction to high-frequency Camelot phrases."""
        if not text:
            return text
        compressed = text
        for term, glyph in SYMBOLECT_LEXICON.items():
            compressed = compressed.replace(term, glyph)
        return compressed

    @staticmethod
    def expand_symbolect(text: str) -> str:
        """Expands Symbolect glyphs back to their canonical natural-language representations."""
        if not text:
            return text
        expanded = text
        for glyph, term in REVERSE_SYMBOLECT_LEXICON.items():
            expanded = expanded.replace(glyph, term)
        return expanded

    def compress_payload(
        self,
        data: Union[str, bytes, Dict[str, Any], list],
        symbolect_first: bool = True,
    ) -> bytes:
        """
        Compresses arbitrary payloads (dict, str, or bytes) into a sealed binary envelope.
        Format: [4-byte magic] + [compressed bytes]
        """
        raw_bytes: bytes

        if isinstance(data, (dict, list)):
            serialized = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
            if symbolect_first:
                serialized = self.compress_symbolect(serialized)
            raw_bytes = serialized.encode("utf-8")
        elif isinstance(data, str):
            processed = self.compress_symbolect(data) if symbolect_first else data
            raw_bytes = processed.encode("utf-8")
        elif isinstance(data, bytes):
            raw_bytes = data
        else:
            raw_bytes = str(data).encode("utf-8")

        if _HAS_ZSTD and self._cctx:
            compressed = self._cctx.compress(raw_bytes)
            return MAGIC_ZSTD + compressed
        else:
            import zlib
            compressed = zlib.compress(raw_bytes, level=self.level)
            return MAGIC_ZLIB + compressed

    def decompress_payload(self, blob: bytes, parse_json: bool = True) -> Any:
        """Decompresses a sealed binary envelope back into string, dict, or bytes."""
        if len(blob) < 4:
            raise ValueError(f"Invalid TokenPress blob length: {len(blob)} bytes")

        magic = blob[:4]
        payload = blob[4:]

        if magic == MAGIC_ZSTD:
            if not _HAS_ZSTD:
                raise RuntimeError("Zstandard package required to decompress CQZ1 payload")
            raw_bytes = self._dctx.decompress(payload)
        elif magic == MAGIC_ZLIB:
            import zlib
            raw_bytes = zlib.decompress(payload)
        elif magic == MAGIC_SYMBOLECT:
            raw_bytes = payload
        else:
            raise ValueError(f"Unrecognized TokenPress magic header: {magic!r}")

        # Decode string and expand Symbolect
        try:
            decoded_text = raw_bytes.decode("utf-8")
            expanded_text = self.expand_symbolect(decoded_text)
            if parse_json:
                try:
                    return json.loads(expanded_text)
                except json.JSONDecodeError:
                    return expanded_text
            return expanded_text
        except UnicodeDecodeError:
            return raw_bytes

    def get_metrics(
        self,
        original: Union[str, bytes, Dict[str, Any], list],
        compressed: bytes,
    ) -> Dict[str, Any]:
        """Calculates compression ratios and space savings."""
        if isinstance(original, (dict, list)):
            orig_len = len(json.dumps(original, separators=(",", ":")).encode("utf-8"))
        elif isinstance(original, str):
            orig_len = len(original.encode("utf-8"))
        else:
            orig_len = len(original)

        comp_len = len(compressed)
        ratio = round(orig_len / comp_len, 2) if comp_len > 0 else 1.0
        savings_pct = round((1.0 - (comp_len / orig_len)) * 100.0, 1) if orig_len > 0 else 0.0

        return {
            "original_bytes": orig_len,
            "compressed_bytes": comp_len,
            "ratio": f"{ratio}:1",
            "savings_pct": savings_pct,
            "algorithm": "zstd" if compressed.startswith(MAGIC_ZSTD) else "zlib",
        }
