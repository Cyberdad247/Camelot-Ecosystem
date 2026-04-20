# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import re
from typing import Dict, List


class SymbolectTranspiler:
    """
    A Transpiler for the Symbolect Language - A symbolic logic shorthand for AI reasoning.
    """

    def __init__(self):
        # Core Symbol Map (The "Rosetta Stone" of the system)
        self.symbol_map: Dict[str, str] = {
            "->": "implies",
            "<-": "derived_from",
            "==": "equivalent_to",
            "!=": "not_equivalent_to",
            "&&": "and",
            "||": "or",
            ">>": "process_flow_to",
            "<<": "process_flow_from",
            "[?]": "query",
            "[!]": "alert",
            "[*]": "insight",
            "[@]": "reference",
            "{...}": "context_block",
            "<...>": "variable",
            "#": "entity_tag",
            "🌙": "dark_mode",
            "🛡️": "security_constraint",
            "🧩": "component",
            "📦": "state_storage",
            "🔄": "lifecycle_loop",
            "🔮": "strategic_plan",
            "🔥": "performance_optimize",
            "⚡": "kinetic_execution",
            "👤": "human_in_the_loop",
            "✅": "verified"
        }

        self.reverse_map = {v: k for k, v in self.symbol_map.items()}

    def encode(self, text: str) -> str:
        """
        Compresses natural language into Symbolect shorthand where possible.
        This is a rudimentary implementation relying on key phrases.
        """
        encoded_text = text
        for symbol, meaning in self.reverse_map.items():
            # Basic replacement - in a real system this would be NLP based
            # avoiding partial word matches would require regex boundaries
            pattern = re.compile(r"\b" + re.escape(meaning) + r"\b", re.IGNORECASE)
            encoded_text = pattern.sub(symbol, encoded_text)

        return encoded_text

    def decode(self, symbolect_code: str) -> str:
        """
        Expands Symbolect shorthand into readable natural language (or structured JSON).
        """
        decoded_text = symbolect_code
        for symbol, meaning in self.symbol_map.items():
            decoded_text = decoded_text.replace(symbol, f" [{meaning}] ")

        return " ".join(decoded_text.split())  # Clean up whitespace

    def parse_to_graph(self, symbolect_code: str) -> List[Dict]:
        """
        Parses simple "A -> B" type logic into a graph structure.
        """
        lines = symbolect_code.split("\n")
        graph = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Simple relation parser
            if "->" in line:
                parts = line.split("->")
                if len(parts) == 2:
                    graph.append({"source": parts[0].strip(), "target": parts[1].strip(), "relation": "implies"})
            elif ">>" in line:
                parts = line.split(">>")
                if len(parts) == 2:
                    graph.append({"source": parts[0].strip(), "target": parts[1].strip(), "relation": "process_flow"})

        return graph


# Example Usage if run directly
if __name__ == "__main__":
    transpiler = SymbolectTranspiler()

    sample_logic = """
    User_Input >> NLP_Processor
    NLP_Processor -> Intent_Classification
    Intent_Classification == "Purchase" -> Trigger_Checkout
    """

    print("--- Original Symbolect ---")
    print(sample_logic)

    print("\n--- Decoded ---")
    print(transpiler.decode(sample_logic))

    print("\n--- Graph Structure ---")
    print(transpiler.parse_to_graph(sample_logic))