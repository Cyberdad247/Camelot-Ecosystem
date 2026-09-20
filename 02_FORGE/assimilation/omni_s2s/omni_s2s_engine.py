# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Omni Speech-to-Speech (S2S) Assimilation Engine.
=================================================
Synthesizes:
- mini-sglang & sglang-omni: RadixAudioCache & chunked audio prefill
- AgoraAI_ChatBotApp & AgoraAi: Agora RTC SD-RTN channel bridge
- Camelot Humanistic Prosody & Multivoice Router

Domain: CAMELOT-OS Omni S2S Nexus
Forged by: SIR_SONUS (Multivoice Audio Director) & SIR_CODEX & SIR_HELIO
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import struct
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

CAMELOT_HOME = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(CAMELOT_HOME))

from radix_audio_cache import RadixAudioCache
from agora_rtc_bridge import AgoraRTCBridge, AgoraRTCConfig

# Import VocalPatternAnalyzer from humanistic_voice assimilation
try:
    hv_dir = CAMELOT_HOME / "02_FORGE" / "assimilation" / "humanistic_voice"
    if str(hv_dir) not in sys.path:
        sys.path.insert(0, str(hv_dir))
    from vocal_pattern_analyzer import VocalPatternAnalyzer  # type: ignore
except ImportError:
    VocalPatternAnalyzer = None

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [OMNI_S2S] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("omni_s2s_engine")


@dataclass
class S2STurnResult:
    status: str
    channel_name: str
    turn_index: int
    active_knight: str
    input_text: str
    response_text: str
    radix_cache_hit_tokens: int
    radix_total_tokens: int
    radix_cache_hit_rate: float
    estimated_ttfa_ms: float
    prosody_summary: Dict[str, Any]
    agora_transport_stats: Dict[str, Any]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class OmniS2SEngine:
    """End-to-end Omni Speech-to-Speech Engine with Radix prefix caching and Agora RTC."""

    # Common system prompt prefix tokens (represented as integer token IDs)
    SYSTEM_PREFIX_TOKENS = list(range(1001, 1065))  # 64 tokens of base instructions

    def __init__(self, channel_name: str = "camelot_omni_s2s"):
        self.radix_cache = RadixAudioCache(max_cached_tokens=16384)
        self.agora_bridge = AgoraRTCBridge(AgoraRTCConfig(channel_name=channel_name))
        self.analyzer = VocalPatternAnalyzer() if VocalPatternAnalyzer else None
        self.turn_history_tokens: List[int] = list(self.SYSTEM_PREFIX_TOKENS)
        self.turn_counter = 0

        # Pre-seed system prefix in Radix Tree
        self.radix_cache.insert_sequence(
            self.SYSTEM_PREFIX_TOKENS,
            kv_data={"type": "SYSTEM_INSTRUCTIONS", "kv_ptr": "0xKV_SYSTEM"},
            is_audio=False,
        )
        self.agora_bridge.join_channel(channel_name)

    def process_speech_turn(
        self,
        pcm_bytes: bytes,
        transcript_hint: str = "Status update",
        knight_id: str = "reya_companion",
    ) -> S2STurnResult:
        """Processes an incoming audio turn through Agora, Radix Cache, and Multivoice S2S."""
        self.turn_counter += 1
        t_start = time.perf_counter()

        # 1. Ingest via Agora RTC Bridge
        agora_in = self.agora_bridge.push_audio_frame(pcm_bytes)

        # 2. Vocal Pattern Analysis
        prosody_info = {}
        if self.analyzer:
            report = self.analyzer.analyze_audio_chunk(pcm_bytes, transcript_hint)
            prosody_info = report.to_dict()

        # 3. Simulate continuous audio/text tokenization
        # e.g., 25 tokens per second of speech + text token hashes
        audio_dur_sec = len(pcm_bytes) / (2 * 16000) if len(pcm_bytes) >= 2 else 0.5
        audio_tokens = [int(10000 + (hash(transcript_hint) + i) % 5000) for i in range(max(4, int(audio_dur_sec * 25)))]
        
        # Build full sequence for this turn including conversation history
        full_turn_sequence = list(self.turn_history_tokens) + audio_tokens

        # 4. RadixAttention Prefix Cache Lookup (mini-sglang / sglang-omni)
        matched_node, matched_count = self.radix_cache.match_prefix(full_turn_sequence)
        
        # Compute hit rate for this turn
        hit_rate = (matched_count / len(full_turn_sequence) * 100.0) if full_turn_sequence else 0.0

        # 5. Insert new delta tokens into Radix Tree for future turns
        self.radix_cache.insert_sequence(
            full_turn_sequence,
            kv_data={"turn": self.turn_counter, "knight": knight_id},
            is_audio=True,
        )

        # Update turn history with latest turn tokens
        self.turn_history_tokens.extend(audio_tokens)

        # 6. Generate Response
        response_text = self._generate_response(transcript_hint, knight_id, prosody_info)

        # 7. TTFA calculation:
        # Base latency = 140ms. If Radix matched >50 tokens, save 40-70ms.
        time_saved_ms = min(80.0, (matched_count / len(full_turn_sequence)) * 75.0) if full_turn_sequence else 0.0
        ttfa_ms = max(45.0, 145.0 - time_saved_ms)

        # 8. Push simulated outbound audio packet to Agora RTC
        out_pcm = pcm_bytes[:640] if len(pcm_bytes) >= 640 else b"\x00" * 640
        self.agora_bridge.pull_egress_frame(out_pcm)

        return S2STurnResult(
            status="S2S_TURN_COMPLETED",
            channel_name=self.agora_bridge.config.channel_name,
            turn_index=self.turn_counter,
            active_knight=knight_id,
            input_text=transcript_hint,
            response_text=response_text,
            radix_cache_hit_tokens=matched_count,
            radix_total_tokens=len(full_turn_sequence),
            radix_cache_hit_rate=round(hit_rate, 1),
            estimated_ttfa_ms=round(ttfa_ms, 1),
            prosody_summary=prosody_info,
            agora_transport_stats=self.agora_bridge.get_stats(),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def _generate_response(self, text: str, knight_id: str, prosody: Dict[str, Any]) -> str:
        is_urgent = prosody.get("is_urgent", False)
        urgency_note = " Priority expedited." if is_urgent else ""

        if "boris" in knight_id:
            return f"Boris responding.{urgency_note} Grid blueprint validated for '{text}'."
        elif "codex" in knight_id:
            return f"Codex execution.{urgency_note} Rust WASM compiled for '{text}'."
        elif "merlin" in knight_id:
            return f"Merlin System 2.{urgency_note} Radix-cached DAG resolved for '{text}'."
        else:
            return f"Reya here.{urgency_note} Connected over Agora RTC for '{text}'."


# Module singleton
_engine_instance: Optional[OmniS2SEngine] = None


def get_omni_s2s_engine() -> OmniS2SEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = OmniS2SEngine()
    return _engine_instance


def main():
    parser = argparse.ArgumentParser(description="CAMELOT-OS Omni S2S Engine")
    parser.add_argument("--test", action="store_true", help="Run multi-turn S2S test")
    parser.add_argument("--knight", type=str, default="reya_companion", help="Active Knight persona")
    parser.add_argument("--turns", type=int, default=3, help="Number of turns to simulate")
    args = parser.parse_args()

    engine = get_omni_s2s_engine()

    # Generate synthetic 16kHz audio
    samples = [int(1500 * math.sin(2 * math.pi * 220 * i / 16000)) for i in range(8000)]
    pcm_bytes = struct.pack(f"<{len(samples)}h", *samples)

    prompts = [
        "First turn: connect to satellite uplink",
        "Second turn: report telemetry on port 3001",
        "Third turn: lock down the fortress perimeter",
    ]

    for i in range(min(args.turns, len(prompts))):
        res = engine.process_speech_turn(pcm_bytes, prompts[i], args.knight)
        print(f"\n--- Turn {res.turn_index} ---")
        print(f"Hit Rate: {res.radix_cache_hit_rate}% ({res.radix_cache_hit_tokens}/{res.radix_total_tokens} tokens)")
        print(f"TTFA: {res.estimated_ttfa_ms}ms")
        print(f"Response: {res.response_text}")


if __name__ == "__main__":
    main()
