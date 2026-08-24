# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

import re


class ChunkKVPolicy:
    """Linguistic-Aware KV Pruning Policy (ChunkKV)."""

    def prune(self, text: str) -> str:
        """Prune text while preserving complete linguistic structures (sentences)."""
        # Find the last full sentence boundary (. ! ?)
        match = re.search(r'(.*[.!?])', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()
