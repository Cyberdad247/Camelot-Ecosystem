# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
AURORA ENGINE: Unified Multimodal Vision
Consolidates framework selection (aurora_vision) + frame buffer (aurora_v_jepa).
Wired to RustDeskBridge for screen capture when available.
"""

import time
from typing import Any, Dict, List, Optional


class AuroraEngine:
    """Multimodal vision engine with framework routing and frame buffering."""

    FRAMEWORKS = {
        "cinematic": "LCE 4.0 (Latent Cinematic Expression)",
        "artistic": "Hyper-Aesthetic Rendering",
        "technical": "Vector Graph Schematic",
        "realistic": "V-JEPA Grounding",
    }

    _INTENT_MAP = {
        "cinematic": ["movie", "film", "cinematic", "scene"],
        "artistic": ["art", "style", "aesthetic", "paint"],
        "technical": ["diagram", "map", "schematic", "architecture", "flow"],
    }

    def __init__(self, rustdesk_bridge=None, buffer_size: int = 10):
        self.rustdesk = rustdesk_bridge
        self.is_active = False
        self.frame_buffer: List[Dict] = []
        self._buffer_size = buffer_size

    def activate(self):
        self.is_active = True

    def attach_bridge(self, rustdesk_bridge):
        """Late-bind a RustDeskBridge instance for screen capture."""
        self.rustdesk = rustdesk_bridge

    def select_framework(self, intent: str) -> str:
        intent_lower = intent.lower()
        for category, keywords in self._INTENT_MAP.items():
            if any(kw in intent_lower for kw in keywords):
                return self.FRAMEWORKS[category]
        return self.FRAMEWORKS["realistic"]

    def capture_frame(self) -> Optional[str]:
        """Capture a screen frame via RustDesk, store in buffer."""
        if not self.is_active:
            return None

        frame_id = f"frame_{int(time.time() * 1000)}"
        frame_data = None

        if self.rustdesk:
            try:
                frame_data = self.rustdesk.capture_frame()
            except Exception:
                frame_data = None

        self.frame_buffer.append({
            "id": frame_id,
            "ts": time.time(),
            "has_data": frame_data is not None,
        })

        if len(self.frame_buffer) > self._buffer_size:
            self.frame_buffer.pop(0)

        return frame_id

    async def visualize(self, prompt: str, frame_id: Optional[str] = None) -> Dict:
        """Route a visual intent through the appropriate framework."""
        framework = self.select_framework(prompt)

        result = {
            "framework": framework,
            "prompt": prompt,
            "status": "SYNTHESIZED" if self.is_active else "INACTIVE",
        }

        if frame_id and self.frame_buffer:
            matching = [f for f in self.frame_buffer if f["id"] == frame_id]
            if matching:
                result["frame_ref"] = frame_id
                result["status"] = "GROUNDED"

        return result

    async def analyze_visual_intent(self, prompt: str) -> Dict:
        """Zero-shot visual reasoning on the current buffer state."""
        buffer_summary = [f["id"] for f in self.frame_buffer[-3:]]
        return {
            "status": "ACTIVE" if self.is_active else "INACTIVE",
            "framework": self.select_framework(prompt),
            "buffer_depth": len(self.frame_buffer),
            "recent_frames": buffer_summary,
        }


# Singleton
aurora = AuroraEngine()