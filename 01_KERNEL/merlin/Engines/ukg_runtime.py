# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
UKG_EXEC_RUNTIME_v1
Universal Knowledge Glyph Runtime Execution Engine

Implements:
- r0-r5: Runtime execution contract
- DISTILL→ANCHOR→WEAVE cycle
- Hallucination resistance
- Deterministic reasoning (temp=0.0)
"""

import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

try:
    from .symbolect_transpiler.symbolect import SymbolectTranspiler
except (ImportError, ValueError):
    try:
        from Engines.symbolect_transpiler.symbolect import SymbolectTranspiler
    except ImportError:
        # Final fallback for direct execution / importlib
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), "symbolect_transpiler"))
        from symbolect import SymbolectTranspiler


class UKGRuntime:
    """
    Core UKG Runtime implementing closed-loop autonomous execution.
    
    Phases:
    r0 | RUNTIME | Init | {Load:UKG}
    r1 | RUNTIME | Ingest | {Any_Input}
    r2 | RUNTIME | Execute | {Loop:DISTILL->ANCHOR->WEAVE}
    r3 | RUNTIME | Persist | {Append:UKG}
    r4 | RUNTIME | Respond | {From:Minimal_Context}
    r5 | RUNTIME | Repeat | {Continuous:true}
    """
    
    def __init__(self, ukg_path: str = "01_KERNEL/memory/ukg_graph.json"):
        self.ukg_path = Path(ukg_path)
        self.graph = self._load_ukg()  # r0: Init
        self.hallucination_guard = True
        self.transpiler = SymbolectTranspiler()
        self.persona_library_path = Path("03_VAULT/knowledge/persona_library")
        
    def _load_ukg(self) -> Dict[str, Any]:
        """r0: Load UKG graph from persistent storage."""
        if not self.ukg_path.exists():
            return {
                "nodes": [],
                "edges": [],
                "metadata": {"version": "1.0", "type": "UKG_GRAPH"}
            }
        
        with open(self.ukg_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def execute(self, input_data: str, mode: str = "DIRECT") -> Dict[str, Any]:
        """
        r1-r5: Full execution cycle.
        
        Args:
            input_data: Raw user input or system event
            mode: DIRECT or LOWER (Model-Lowering Compression)
            
        Returns:
            TOON-compressed response or TAL Manifest
        """
        # r1: Ingest
        raw_input = input_data
        
        if mode == "LOWER":
            return self.lower_model(raw_input)
            
        # r2: Execute DISTILL→ANCHOR→WEAVE
        anchors = self._distill(raw_input)
        validated = self._anchor(anchors)
        response = self._weave(validated)
        
        # r3: Persist
        self._persist(validated, response)
        
        # r4: Respond (minimal context)
        return self._compress_response(response)

    def lower_model(self, raw_input: str) -> Dict[str, Any]:
        """
        [SINGULARITY] Model Lowering: Compresses heavy reasoning into a TAL Manifest.
        This allows 8B models to execute tasks from high-dimensional personas.
        """
        # 1. Distill anchors from raw input
        anchors = self._distill(raw_input)
        
        # 2. Synthesize a Persona Manifest using Merlin v2 TAL
        persona_role = anchors[0] if anchors else "General_Architect"
        tal_manifest = self.load_persona(persona_role) or self._merlin_tal_synthesis(persona_role)
        
        # 3. Create the Execution Payload (Compressed Logic)
        payload = {
            "root_id": tal_manifest["root"]["id"],
            "tal_manifest": tal_manifest,
            "anchors": anchors,
            "glyphs": self.transpiler.encode(", ".join(anchors))
        }
        
        return payload

    def _merlin_tal_synthesis(self, role: str) -> Dict[str, Any]:
        """
        🧙‍♂️ Merlin v2: Tree-structured Assembly Language (TAL) Synthesis.
        Transforms a role into a structured identity manifest.
        """
        # Detect bias based on role
        tone = "Technical/Kinetic" if any(x in role.lower() for x in ["engineer", "forge", "dev"]) else "Socratic/Analytical"
        symbols = "⚔️" if "security" in role.lower() or "sentinel" in role.lower() else "🧙‍♂️"
        
        tal_result = {
            "root": {
                "id": f"#{role.upper().replace(' ', '_')}",
                "mandate": "Uphold the Sovereign Kinetic Law.",
                "alignment": "Camelot_Singularity_Lattice"
            },
            "branch": {
                "lexicon": "Singularity_Dense",
                "tone": tone,
                "symbols": symbols
            },
            "leaf": [
                "Strict adherence to Titanium Laws",
                "Uses Symbolect for token reduction",
                "Cognitive Bias: Efficiency_First"
            ]
        }
        return tal_result

    def load_persona(self, role: str) -> Optional[Dict[str, Any]]:
        """Load a persona from the persistent library."""
        file_name = role.lower().replace(" ", "_") + ".jsonld"
        file_path = self.persona_library_path / file_name
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def list_persona_library(self) -> List[str]:
        """List all available personas in the library."""
        if not self.persona_library_path.exists():
            return []
        return [f.stem.replace("_", " ").title() for f in self.persona_library_path.glob("*.jsonld")]
    
    def _distill(self, raw_input: str) -> List[str]:
        """
        DISTILL: Extract invariant concepts from noisy input.
        
        Converts:
        "Can you help me implement the harmony gate for conflict detection?"
        
        To anchors:
        ["harmony_gate", "conflict_detection", "implementation"]
        """
        # Simple keyword extraction (upgrade to LLM later)
        keywords = []
        
        # Extract technical terms
        terms = raw_input.lower().split()
        technical_indicators = [
            "implement", "create", "build", "design", "fix", "debug",
            "harmony", "gate", "conflict", "detection", "assimilation",
            "oracle", "forge", "sentinel", "conductor", "hive", "symbolect"
        ]
        
        for term in terms:
            if term in technical_indicators or len(term) > 8:
                keywords.append(term.strip('.,!?'))
        
        return list(set(keywords))[:7]  # Max 7 anchors
    
    def _anchor(self, anchors: List[str]) -> List[Dict[str, Any]]:
        """
        ANCHOR: Validate anchors against UKG graph.
        
        Hallucination Guard: If anchor not in graph, return UNKNOWN.
        """
        validated = []
        
        for anchor in anchors:
            # Check if node exists in graph
            node = self._find_node(anchor)
            
            if node:
                validated.append({
                    "anchor": anchor,
                    "status": "KNOWN",
                    "node_id": node.get("id"),
                    "type": node.get("type", "CONCEPT")
                })
            else:
                if self.hallucination_guard:
                    validated.append({
                        "anchor": anchor,
                        "status": "UNKNOWN",
                        "action": "CREATE_NEW_NODE"
                    })
                else:
                    # Reject unknown anchors
                    validated.append({
                        "anchor": anchor,
                        "status": "REJECTED",
                        "reason": "NOT_IN_GRAPH"
                    })
        
        return validated
    
    def _weave(self, validated_anchors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        WEAVE: Construct response from validated anchors and graph context.
        
        Uses only KNOWN nodes to prevent hallucination.
        """
        known_nodes = [a for a in validated_anchors if a["status"] == "KNOWN"]
        unknown_nodes = [a for a in validated_anchors if a["status"] == "UNKNOWN"]
        
        # Build context from known nodes
        context = []
        for node_data in known_nodes:
            node = self._find_node(node_data["anchor"])
            if node:
                context.append({
                    "id": node["id"],
                    "type": node.get("type"),
                    "data": node.get("data", {})
                })
        
        return {
            "context": context,
            "known_count": len(known_nodes),
            "unknown_count": len(unknown_nodes),
            "unknown_anchors": [n["anchor"] for n in unknown_nodes],
            "deterministic": True,
            "temperature": 0.0
        }
    
    def _persist(self, validated: List[Dict], response: Dict) -> None:
        """
        r3: Persist new knowledge to UKG graph.
        
        Creates new nodes for UNKNOWN anchors.
        """
        for anchor_data in validated:
            if anchor_data["status"] == "UNKNOWN":
                # Create new node
                new_node = {
                    "id": f"node_{anchor_data['anchor']}",
                    "type": "CONCEPT",
                    "anchor": anchor_data["anchor"],
                    "data": {
                        "created_by": "UKG_RUNTIME",
                        "confidence": 0.5  # Low confidence for new nodes
                    }
                }
                self.graph["nodes"].append(new_node)
        
        # Save to disk
        with open(self.ukg_path, 'w', encoding='utf-8') as f:
            json.dump(self.graph, f, indent=2)
    
    def _compress_response(self, response: Dict) -> str:
        """
        r4: TOON compression for minimal token usage.
        
        Before: {"context": [...], "known_count": 3, "unknown_count": 1}
        After:  r4 | WEAVE | K:3 U:1 | {T:0.0}
        """
        k = response["known_count"]
        u = response["unknown_count"]
        t = response["temperature"]
        
        toon = f"r4 | WEAVE | K:{k} U:{u} | {{T:{t}}}"
        
        if u > 0:
            unknown = ",".join(response["unknown_anchors"])
            toon += f" | UNKNOWN:[{unknown}]"
        
        # Apply Symbolect Glyph Compression
        compressed = self.transpiler.encode(toon)
        return compressed
    
    def _find_node(self, anchor: str) -> Optional[Dict]:
        """Find node in graph by anchor/id."""
        for node in self.graph.get("nodes", []):
            if node.get("id") == f"node_{anchor}" or node.get("anchor") == anchor:
                return node
        return None
    
    def auto_repair(self) -> Dict[str, int]:
        """
        UKG_TESTING_AUTONOMY: Auto-repair graph.
        
        t5 | REPAIR | Merge | {Duplicate_Nodes}
        t6 | REPAIR | Prune | {Unused}
        t7 | REPAIR | Normalize | {Canonical}
        """
        stats = {
            "merged": 0,
            "pruned": 0,
            "normalized": 0
        }
        
        # t5: Merge duplicates
        seen = {}
        unique_nodes = []
        for node in self.graph.get("nodes", []):
            node_id = node.get("id")
            if node_id not in seen:
                seen[node_id] = True
                unique_nodes.append(node)
            else:
                stats["merged"] += 1
        
        self.graph["nodes"] = unique_nodes
        
        # t6: Prune orphans (nodes with no edges)
        connected_nodes = set()
        for edge in self.graph.get("edges", []):
            connected_nodes.add(edge.get("from"))
            connected_nodes.add(edge.get("to"))
        
        pruned_nodes = []
        for node in self.graph["nodes"]:
            if node.get("id") in connected_nodes or node.get("type") == "CORE":
                pruned_nodes.append(node)
            else:
                stats["pruned"] += 1
        
        self.graph["nodes"] = pruned_nodes
        
        # t7: Normalize (ensure all nodes have required fields)
        for node in self.graph["nodes"]:
            if "type" not in node:
                node["type"] = "CONCEPT"
                stats["normalized"] += 1
            if "data" not in node:
                node["data"] = {}
                stats["normalized"] += 1
        
        # Persist repairs
        with open(self.ukg_path, 'w', encoding='utf-8') as f:
            json.dump(self.graph, f, indent=2)
        
        return stats