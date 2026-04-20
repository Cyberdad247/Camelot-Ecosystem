# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
[🔊] VOX_ANIMA v2.1 (The Living Voice)

PROSODY_MIRROR CORE:
Analyzes User Intent + Emotion to architect the Sonic Delivery.
Bridged into Camelot Kernel.
"""

from dataclasses import dataclass

from textblob import TextBlob


@dataclass
class VoiceState:
    style: str  # Base voice vector ID (neutral, deep, whisper)
    speed: float  # 0.5 to 2.0
    energy: float  # Intensity of the delivery
    texture: str  # Gravel, Silk, Static, Clear
    complexity: float  # Text complexity score for pacing


class VoxAnima:
    """
    Decides HOW a Knight should speak based on the provided context.
    Integrated into the UniversalKnight base class.
    """

    @staticmethod
    def analyze_and_adapt(user_text: str, current_persona_role: str) -> VoiceState:
        # 1. Sentiment Engine (Polarity & Subjectivity)
        try:
            blob = TextBlob(user_text)
            sentiment = blob.sentiment.polarity  # -1.0 to 1.0
            subjectivity = blob.sentiment.subjectivity  # 0.0 to 1.0
        except Exception:
            sentiment = 0.0
            subjectivity = 0.0

        # 2. Text Analysis for Pacing
        words = user_text.split()
        avg_word_len = sum(len(w) for w in words) / max(len(words), 1)
        complexity = min(avg_word_len / 10.0, 1.0)

        # 3. Default Mapping
        target_speed = 1.0 - (complexity * 0.2)
        target_style = "neutral"
        target_texture = "Clear"
        target_energy = 0.5 + (sentiment * 0.2)

        # 4. Emotional Branching (The Mirror)
        if sentiment < -0.4:
            target_style = "deep"
            target_speed *= 0.85
            target_texture = "Gravel"
        elif sentiment > 0.4:
            target_style = "neutral"
            target_speed *= 1.15
            target_texture = "Silk"

        if subjectivity > 0.7:
            target_style = "whisper"
            target_energy *= 0.7
            target_speed *= 0.9

        # 5. Knight-Specific Role Overrides
        role_map = {
            "Warden": {"texture": "Gravel", "style": "deep", "speed_mod": 0.8},
            "Interface": {"texture": "Silk", "style": "neutral", "speed_mod": 1.1},
            "Engineer": {"texture": "Clear", "style": "neutral", "speed_mod": 1.2},
            "Orchestrator": {"texture": "Static", "style": "deep", "speed_mod": 0.9},
            "AudioForge": {"texture": "Clear", "style": "neutral", "speed_mod": 1.0},
        }

        if current_persona_role in role_map:
            override = role_map[current_persona_role]
            target_texture = override["texture"]
            target_style = override["style"]
            target_speed *= override["speed_mod"]

        return VoiceState(
            style=target_style,
            speed=round(target_speed, 2),
            energy=round(target_energy, 2),
            texture=target_texture,
            complexity=round(complexity, 2),
        )