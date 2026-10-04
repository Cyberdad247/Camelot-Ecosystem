# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Unit tests for Squire TokenPress payload & Symbolect compression."""

from __future__ import annotations

import pytest
from squires.tokenpress import SquireTokenPress, MAGIC_ZSTD, MAGIC_ZLIB


def test_tokenpress_symbolect_substitution():
    press = SquireTokenPress()
    raw = "All commands must pass ANYA_IS_THE_GATE on CYBERTRONIA before writing to PROVENANCE_LEDGER.md"
    compressed = press.compress_symbolect(raw)
    assert "⟐ANYA_GATE⟐" in compressed
    assert "⟐CYBERTRONIA⟐" in compressed
    assert "⟐PROV_LEDGER_MD⟐" in compressed
    assert "ANYA_IS_THE_GATE" not in compressed

    expanded = press.expand_symbolect(compressed)
    assert expanded == raw


def test_tokenpress_payload_compression_roundtrip_string():
    press = SquireTokenPress()
    original_text = "Camelot-OS node telemetry verification from SIR_HELIOS at vfs://worldtree." * 20
    blob = press.compress_payload(original_text)
    assert isinstance(blob, bytes)
    assert blob[:4] in (MAGIC_ZSTD, MAGIC_ZLIB)
    assert len(blob) < len(original_text)

    restored = press.decompress_payload(blob)
    assert restored == original_text


def test_tokenpress_payload_compression_roundtrip_dict():
    press = SquireTokenPress()
    payload = {
        "knight": "SIR_HELIOS",
        "node": "CYBERTRONIA",
        "gate": "ANYA_IS_THE_GATE",
        "ledger": "PROVENANCE_LEDGER.md",
        "mesh": "TAILSCALE_MESH",
        "metrics": [1.0, 2.5, 3.8, 4.2] * 10,
    }
    blob = press.compress_payload(payload)
    assert isinstance(blob, bytes)
    assert len(blob) > 4

    metrics = press.get_metrics(payload, blob)
    assert metrics["savings_pct"] > 0
    assert metrics["algorithm"] in ("zstd", "zlib")

    restored = press.decompress_payload(blob)
    assert isinstance(restored, dict)
    assert restored["knight"] == "SIR_HELIOS"
    assert restored["gate"] == "ANYA_IS_THE_GATE"
    assert restored["metrics"] == payload["metrics"]
