#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Camelot-OS Symbolect Transpiler & Runic Dispatcher
==================================================
Deterministic compiler implementing Triple-QFT context compression,
Renormalization Group (RG) flow, ambiguity scoring, and runic dispatch.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Optional

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# Standard Symbolect Glyph Registry
GLYPH_REGISTRY = {
    "COGNITION": "🧠",
    "KINETIC": "⚡",
    "DIALOGUE": "💬",
    "FORAGE": "🧲",
    "TEST": "🧪",
    "EVOLVE": "📈",
    "DEPLOY": "🏆",
    "SHIELD": "🛡️",
    "STRUCTURE": "🏗️",
    "MEMORY": "📜",
    "ORACLE": "🔮",
    "SOVEREIGN": "⚜️",
}

# Standard Runic Dispatch Mappings
RUNIC_DISPATCH_MAP = {
    "//PLAN": {"knight": "merlin_omega", "mode": "ORACLE", "priority": 3, "description": "ToT strategic planning"},
    "//THINK": {"knight": "merlin_omega", "mode": "ORACLE", "priority": 3, "description": "Deep GoT/ToT reasoning chain"},
    "//FORGE": {"knight": "sir_forge", "mode": "KINETIC", "priority": 2, "description": "Kinetic build + compile"},
    "//SWARM": {"knight": "sir_boris", "mode": "SWARM", "priority": 2, "description": "Full hive parallel debug/vote"},
    "//CARTRIDGE_VERIFY": {"knight": "merlin_omega", "mode": "ORACLE", "priority": 1, "description": "Crucible schema verification"},
    "//ASSIMILATE_REPO": {"knight": "merlin_omega", "mode": "ORACLE", "priority": 1, "description": "Branch-isolated repository assimilation"},
    "//SCAN": {"knight": "squire_colony", "mode": "SENTINEL", "priority": 2, "description": "CLARITY_CORE codebase scan"},
    "//STATUS": {"knight": "sir_boris", "mode": "ORACLE", "priority": 1, "description": "Live system status + port probes"},
    "//HEAL": {"knight": "sir_debug", "mode": "FORGE", "priority": 2, "description": "PIV self-healing loop"},
    "//MOTO_EDGE_BUS": {"knight": "sir_heimdall", "mode": "SENTINEL", "priority": 1, "description": "Moto edge bus probe, drain, and signed dispatch (:8096)"},
    "//QTSCRCPY": {"knight": "sir_heimdall", "mode": "KINETIC", "priority": 1, "description": "QtScrcpy kinetic bridge audit, device orchestration, and ADB screen injection"},
    "//VALIDATE_SPEC": {"knight": "hermes_prime", "mode": "SENTINEL", "priority": 1, "description": "Formal specification, 36 schemas, and authority closure validation"},
    "//OWL": {"knight": "merlin_omega", "mode": "ORACLE", "priority": 1, "description": "Strigiform Owl ToT optimization"},
    "Omega_Merlin": {"knight": "merlin_omega", "mode": "ORACLE", "priority": 1, "description": "Direct Merlin Omega dispatch"},
    "Omega_THINK": {"knight": "merlin_omega", "mode": "ORACLE", "priority": 3, "description": "Deep GoT/DoT reasoning chain"},
    "Omega_GLYPH": {"knight": "merlin_omega", "mode": "ORACLE", "priority": 1, "description": "NPE TCoT formal verification"},
    "Omega_COMPRESS": {"knight": "merlin_omega", "mode": "ORACLE", "priority": 1, "description": "SAC->CCF->QFT compression"},
    "Omega_ORACLE": {"knight": "merlin_omega", "mode": "ORACLE", "priority": 1, "description": "Oracle Hypervisor broadcast"},
    "Omega_MOTO_EDGE": {"knight": "sir_heimdall", "mode": "SENTINEL", "priority": 1, "description": "Moto Edge Bus signed outbox and telemetry drain (:8096)"},
    "Omega_QTSCRCPY": {"knight": "sir_heimdall", "mode": "KINETIC", "priority": 1, "description": "QtScrcpy mobile kinetic bridge and ADB device control"},
    "Omega_SPEC_VALIDATE": {"knight": "hermes_prime", "mode": "SENTINEL", "priority": 1, "description": "Formal specification, 36 schemas, and authority closure validation"},
}

NOISE_PATTERNS = [
    r"\bcan you please\b",
    r"\bcould you please\b",
    r"\bcould you\b",
    r"\bcan you\b",
    r"\bi was wondering if\b",
    r"\bi would like you to\b",
    r"\bplease\b",
    r"\bthank you\b",
    r"\bhelpful assistant\b",
    r"\bwould be great\b",
    r"\bi need help with\b",
]

VAGUE_TERMS = ["something", "stuff", "things", "fix it", "make it work", "make it better", "help me"]


class TripleQFTTranspiler:
    """
    Implements Context-as-a-Compiler with Triple-QFT Logic:
    1. Physics: Renormalization Group Flow (noise extraction)
    2. Pedagogy: Ambiguity verification (QFT stop sequence gate)
    3. Engineering: Semantic Anchor Compression (SAC) into Symbolect tokens
    """

    def __init__(self, fallback_anchors: Optional[List[str]] = None):
        self.fallback_anchors = fallback_anchors or ["Omnicompetent", "Savant", "Orthogonal", "Symmetry"]

    def renormalize_physics(self, text: str) -> str:
        """Strip conversational fluff and isolate the relevant physical signal."""
        cleansed = text.strip()
        for pattern in NOISE_PATTERNS:
            cleansed = re.sub(pattern, "", cleansed, flags=re.IGNORECASE)
        # Collapse repeated whitespace
        cleansed = re.sub(r"\s+", " ", cleansed).strip()
        return cleansed

    def pedagogy_qft_check(self, intent: str) -> Dict[str, Any]:
        """
        Evaluate ambiguity score to prevent Type III errors.
        Ambiguity threshold > 20 triggers a HALT stop sequence.
        """
        ambiguity_score = 0
        missing_vars: List[str] = []
        lower_intent = intent.lower()

        for term in VAGUE_TERMS:
            if term in lower_intent:
                ambiguity_score += 25
                missing_vars.append(f"Vague descriptor: '{term}'")

        words = [w for w in intent.split() if len(w.strip()) > 0]
        if len(words) < 3:
            ambiguity_score += 40
            missing_vars.append("Missing explicit target subject or action scope")

        if ambiguity_score > 20:
            return {
                "status": "HALT",
                "ambiguity_score": ambiguity_score,
                "missing_variables": missing_vars,
                "clarification_prompts": [
                    f"Define the concrete target and boundary for: '{intent}'",
                    "Specify required inputs, output artifacts, and formats.",
                    "Declare hardware or latency constraints (e.g. 8GB ceiling, SLA).",
                ],
            }

        return {"status": "PASS", "ambiguity_score": ambiguity_score}

    def quantize_engineering(self, intent: str) -> List[str]:
        """Quantize intent into high-density semantic anchors."""
        raw_tokens = [w.strip(".,:;!?()[]{}\"'") for w in intent.split()]
        anchors = [t for t in raw_tokens if len(t) > 3 and t.lower() not in {"with", "from", "that", "this", "have"}]

        # Inject structural anchors if token density is sparse
        if len(anchors) < 4:
            for fallback in self.fallback_anchors:
                if fallback not in anchors:
                    anchors.append(fallback)
                if len(anchors) >= 4:
                    break

        return anchors

    def compile(self, raw_prompt: str, glyph_operator: str = "|🧠⊗(⚡💬)⟩") -> Dict[str, Any]:
        """Execute full Triple-QFT compilation pipeline."""
        signal = self.renormalize_physics(raw_prompt)
        qft = self.pedagogy_qft_check(signal)

        if qft["status"] == "HALT":
            return {
                "status": "AMBIGUITY_HALT",
                "ambiguity_score": qft["ambiguity_score"],
                "missing_variables": qft["missing_variables"],
                "clarification_prompts": qft["clarification_prompts"],
                "signal": signal,
            }

        anchors = self.quantize_engineering(signal)
        anchor_body = "|".join(anchors)
        symbolect_expression = f"{glyph_operator} ⟨Omega:{anchor_body}⟩"

        # Calculate token reduction metrics (approximate word-level tokens)
        original_words = len(raw_prompt.split())
        compiled_words = len(anchors) + 1
        reduction_pct = max(0.0, round((1.0 - (compiled_words / max(1, original_words))) * 100, 2))

        return {
            "status": "RADIANT",
            "original_prompt": raw_prompt,
            "signal": signal,
            "anchor_tokens": anchors,
            "symbolect": symbolect_expression,
            "reduction_percentage": f"{reduction_pct}%",
            "governing_knight": "MERLIN_OMEGA",
        }

    def decode(self, symbolect_str: str) -> Dict[str, Any]:
        """Parse and extract semantic anchors from a symbolect string."""
        match = re.search(r"⟨Omega:([^⟩]+)⟩", symbolect_str)
        if not match:
            return {"status": "INVALID_SYNTAX", "error": "No valid ⟨Omega:...⟩ anchor block found"}

        anchors = match.group(1).split("|")
        return {
            "status": "VALID",
            "anchors": anchors,
            "anchor_count": len(anchors),
            "glyph_operator": symbolect_str.split("⟨")[0].strip() if "⟨" in symbolect_str else "",
        }


class RunicDispatcher:
    """Detects and formats runic command dispatch packets."""

    @staticmethod
    def detect(command_line: str) -> Optional[Dict[str, Any]]:
        """Identify runic prefix (`//` or `Omega_`) and extract task directives."""
        stripped = command_line.strip()

        # Check Omega_ runes
        for rune, meta in RUNIC_DISPATCH_MAP.items():
            if rune.startswith("Omega_") and (stripped == rune or stripped.startswith(f"{rune} ")):
                task = stripped[len(rune):].strip()
                return {
                    "rune": rune,
                    "task": task,
                    "knight": meta["knight"],
                    "mode": meta["mode"],
                    "priority": meta["priority"],
                    "description": meta["description"],
                }

        # Check // runes
        if stripped.startswith("//"):
            parts = stripped.split(" ", 1)
            rune = parts[0].upper()
            task = parts[1].strip() if len(parts) > 1 else ""
            meta = RUNIC_DISPATCH_MAP.get(rune, {
                "knight": "sir_boris",
                "mode": "AGENTIC",
                "priority": 2,
                "description": "Standard sovereign dispatch",
            })
            return {
                "rune": rune,
                "task": task,
                "knight": meta["knight"],
                "mode": meta["mode"],
                "priority": meta["priority"],
                "description": meta["description"],
            }

        return None


class SymbolectDecompiler:
    """Decompiles and visualizes Dirac bra-ket Symbolect expressions into plain English."""

    GLYPH_EXPLANATIONS = {
        "🧠": ("COGNITION", "High-level strategic reasoning and intent distillation"),
        "⚡": ("KINETIC", "Direct deterministic execution and code compilation"),
        "💬": ("DIALOGUE", "Inter-agent dialogue and conversational synchronization"),
        "🧲": ("FORAGE", "VFS and repository search / document harvesting"),
        "🧪": ("TEST", "Verification and regression test suite execution"),
        "📈": ("EVOLVE", "Self-evolving skill distillation and parameter refinement"),
        "🏆": ("DEPLOY", "Production release and endpoint promotion"),
        "🛡️": ("SHIELD", "Sir Heimdall zero-trust perimeter enforcement"),
        "🏗️": ("STRUCTURE", "Monorepo scaffolding and directory hierarchy"),
        "📜": ("MEMORY", "Tripartite memory access (World Tree / Open-Notebook)"),
        "🔮": ("ORACLE", "Merlin Omega formal proof and Tree-of-Thought search"),
        "⚜️": ("SOVEREIGN", "King Arthur / Royal Sovereign directive"),
    }

    @classmethod
    def decompile(cls, symbolect_expression: str) -> Dict[str, Any]:
        """Parses a Symbolect string and returns an intuitive plain-English breakdown."""
        glyphs_found = []
        for g, (cat, desc) in cls.GLYPH_EXPLANATIONS.items():
            if g in symbolect_expression:
                glyphs_found.append({"glyph": g, "category": cat, "meaning": desc})

        # Extract anchor tokens from ⟨Omega: ...⟩
        anchor_match = re.search(r"⟨Omega:\s*([^⟩]+)⟩", symbolect_expression)
        anchors = []
        if anchor_match:
            anchors = [a.strip() for a in anchor_match.group(1).split("⊗") if a.strip()]

        # Estimate compression metrics
        estimated_raw_words = len(anchors) * 7 + len(glyphs_found) * 5
        symbolect_token_estimate = max(2, len(anchors) + len(glyphs_found))
        savings_pct = max(0.0, round((1.0 - (symbolect_token_estimate / max(1, estimated_raw_words))) * 100, 1))

        # Plain English summary
        operations = [item["meaning"] for item in glyphs_found]
        plain_english = (
            f"Sovereign intent compressed via Dirac bra-ket: Performs "
            f"{', and '.join(operations) if operations else 'symbolic operations'} "
            f"anchored on key operational tokens: [{', '.join(anchors)}]."
        )

        return {
            "symbolect_expression": symbolect_expression,
            "plain_english_summary": plain_english,
            "detected_glyphs": glyphs_found,
            "anchor_tokens": anchors,
            "token_metrics": {
                "estimated_raw_words": estimated_raw_words,
                "symbolect_tokens": symbolect_token_estimate,
                "token_reduction_pct": f"{savings_pct}%",
            },
            "status": "DECOMPILED_TRANSPARENT",
        }

    @classmethod
    def visualize(cls, symbolect_expression: str) -> str:
        """Returns a formatted ASCII visualization of the Dirac expression."""
        data = cls.decompile(symbolect_expression)
        lines = [
            "╔════════════════════════════════════════════════════════════════════════════╗",
            "║ 🔮 CAMELOT-OS SYMBOLECT DECOMPILER & VISUALIZER                           ║",
            "╠════════════════════════════════════════════════════════════════════════════╣",
            f"║ Expression : {symbolect_expression:<60} ║",
            f"║ Reduction  : {data['token_metrics']['token_reduction_pct']} token savings (≈{data['token_metrics']['estimated_raw_words']} words -> {data['token_metrics']['symbolect_tokens']} tokens){' ' * 13} ║",
            "╟────────────────────────────────────────────────────────────────────────────╢",
            "║ Operational Glyphs:                                                        ║",
        ]
        for g in data["detected_glyphs"]:
            lines.append(f"║   • {g['glyph']} [{g['category']:<10}]: {g['meaning'][:52]:<52} ║")
        lines.extend([
            "╟────────────────────────────────────────────────────────────────────────────╢",
            "║ Anchored Tokens:                                                           ║",
            f"║   {', '.join(data['anchor_tokens']):<72} ║",
            "╟────────────────────────────────────────────────────────────────────────────╢",
            "║ Plain English Meaning:                                                     ║",
            f"║   {data['plain_english_summary'][:72]:<72} ║",
            "╚════════════════════════════════════════════════════════════════════════════╝",
        ])
        return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Camelot-OS Symbolect Transpiler & Runic Dispatcher")
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand to execute")

    compile_parser = subparsers.add_parser("compile", help="Transpile prompt into Symbolect anchor expression")
    compile_parser.add_argument("prompt", type=str, help="Raw prompt string to compile")
    compile_parser.add_argument("--glyph", type=str, default="|🧠⊗(⚡💬)⟩", help="Custom initial glyph operator")

    decode_parser = subparsers.add_parser("decode", help="Decode and extract anchors from Symbolect expression")
    decode_parser.add_argument("expression", type=str, help="Symbolect string containing ⟨Omega:...⟩")

    decompile_parser = subparsers.add_parser("decompile", help="Decompile Symbolect into plain English & metrics")
    decompile_parser.add_argument("expression", type=str, help="Symbolect expression (e.g. '|🧠⊗(⚡💬)⟩')")

    visualize_parser = subparsers.add_parser("visualize", help="Render ASCII visualization of Symbolect expression")
    visualize_parser.add_argument("expression", type=str, help="Symbolect expression")

    route_parser = subparsers.add_parser("route", help="Detect runic command and format dispatch packet")
    route_parser.add_argument("command", type=str, help="Full runic command string (e.g. '//PLAN build auth')")

    args = parser.parse_args()
    transpiler = TripleQFTTranspiler()

    if args.subcommand == "compile":
        result = transpiler.compile(args.prompt, glyph_operator=args.glyph)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if result["status"] == "AMBIGUITY_HALT":
            sys.exit(1)

    elif args.subcommand == "decode":
        result = transpiler.decode(args.expression)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.subcommand == "decompile":
        result = SymbolectDecompiler.decompile(args.expression)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.subcommand == "visualize":
        print(SymbolectDecompiler.visualize(args.expression))

    elif args.subcommand == "route":
        result = RunicDispatcher.detect(args.command)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"status": "NO_RUNE_DETECTED", "input": args.command}, indent=2))
            sys.exit(2)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

