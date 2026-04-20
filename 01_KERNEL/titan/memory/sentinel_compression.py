# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Sentinel Compression: UKG Optimization Engine
Reduces memory footprint by extracting anchor tokens and pruning noise.
"""

import re
from collections import Counter
from typing import Any, Dict, List


class SentinelCompressor:
    """
    Implements Sentinel Compression for UKG nodes.
    Extracts high-salience "anchor tokens" and discards conversational fluff.
    """

    def __init__(self, anchor_threshold: float = 0.7):
        self.anchor_threshold = anchor_threshold

        # Noise patterns to filter
        self.noise_patterns = [
            r"\b(um|uh|like|you know|basically|actually)\b",
            r"\b(please|thank you|thanks|sorry)\b",
            r"\b(I think|I believe|maybe|perhaps)\b",
        ]

    def extract_anchor_tokens(self, text: str) -> List[str]:
        """
        Extract high-salience anchor tokens from text.
        Uses TF-IDF-like scoring to identify important terms.
        """
        # Remove noise patterns
        cleaned = text.lower()
        for pattern in self.noise_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        # Tokenize
        tokens = re.findall(r"\b\w+\b", cleaned)

        # Filter short tokens
        tokens = [t for t in tokens if len(t) > 3]

        # Count frequency
        freq = Counter(tokens)

        # Extract top N% as anchors
        total = len(tokens)
        threshold_count = int(total * self.anchor_threshold)

        anchors = [token for token, count in freq.most_common(threshold_count)]

        return anchors

    def compress_ukg_node(self, ukg_node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compress a UKG node by extracting anchors and pruning noise.
        """
        compressed = ukg_node.copy()

        # Extract anchors from text fields
        if "content" in ukg_node:
            anchors = self.extract_anchor_tokens(ukg_node["content"])
            compressed["anchor_tokens"] = anchors

            # Calculate compression ratio
            original_size = len(ukg_node["content"])
            compressed_size = len(" ".join(anchors))
            compression_ratio = 1 - (compressed_size / original_size)

            compressed["compression_ratio"] = compression_ratio
            compressed["original_size"] = original_size
            compressed["compressed_size"] = compressed_size

        return compressed

    def decompress_ukg_node(self, compressed_node: Dict[str, Any]) -> str:
        """
        Reconstruct approximate content from anchor tokens.
        Note: This is lossy compression - full fidelity not guaranteed.
        """
        if "anchor_tokens" not in compressed_node:
            return compressed_node.get("content", "")

        # Reconstruct from anchors
        reconstructed = " ".join(compressed_node["anchor_tokens"])

        return reconstructed


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    compressor = SentinelCompressor(anchor_threshold=0.3)

    # Example UKG node
    ukg_node = {
        "type": "ConversationNode",
        "id": "conv_001",
        "content": "Um, I think we should basically implement the KVzip compression, you know, because it provides like 3-4× memory reduction. Thank you for considering this.",
    }

    # Compress
    compressed = compressor.compress_ukg_node(ukg_node)

    print("=" * 60)
    print("SENTINEL COMPRESSION DEMO")
    print("=" * 60)
    print(f"Original: {ukg_node['content']}")
    print(f"Anchors: {compressed['anchor_tokens']}")
    print(f"Compression: {compressed['compression_ratio']:.1%}")
    print(f"Size: {compressed['original_size']} → {compressed['compressed_size']} bytes")

    # Decompress
    reconstructed = compressor.decompress_ukg_node(compressed)
    print(f"Reconstructed: {reconstructed}")