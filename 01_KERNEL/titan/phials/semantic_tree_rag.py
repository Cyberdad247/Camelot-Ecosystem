# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
SEMANTIC TREE RAG PHIAL: Reasoning-Based Retrieval
Extracted from: VectifyAI/PageIndex architecture
Purpose: Replace vector similarity search with LLM-driven tree traversal.
         Eliminates embedding cost entirely, trades for inference.

Key Insight: "Structure before Similarity"
- Documents are parsed into hierarchical semantic trees (like a smart TOC).
- Retrieval is performed via LLM reasoning over tree nodes, not vector distance.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional


class NodeType(Enum):
    DOCUMENT = "document"
    SECTION = "section"
    PARAGRAPH = "paragraph"
    LEAF = "leaf"


@dataclass
class SemanticNode:
    """A node in the semantic tree."""

    id: str
    title: str
    summary: str  # LLM-generated summary for reasoning
    node_type: NodeType
    content: str = ""  # Full content (only for leaf nodes)
    children: List["SemanticNode"] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    page_ref: Optional[int] = None

    def to_toc_entry(self, depth: int = 0) -> str:
        """Format as table-of-contents entry for LLM reasoning."""
        indent = "  " * depth
        children_str = "\n".join(c.to_toc_entry(depth + 1) for c in self.children)
        result = f"{indent}- [{self.id}] {self.title}: {self.summary}"
        if children_str:
            result += f"\n{children_str}"
        return result


class SemanticTreeRAG:
    """
    Reasoning-based RAG engine inspired by PageIndex.

    Instead of:
        query → embed → vector_search → top-k chunks

    We do:
        query → LLM(tree_toc, query) → selected_nodes → LLM(nodes, query) → answer

    This trades embedding cost for inference cost, but provides:
        - Better explainability (we know WHY a section was selected)
        - No chunk boundary issues
        - Works with any LLM (no embedding model needed)
    """

    def __init__(self, llm_fn: Callable[[str], str] = None):
        """
        Args:
            llm_fn: Function that takes a prompt string and returns LLM response.
                    If None, uses a mock for testing.
        """
        self.llm_fn = llm_fn or self._mock_llm
        self.trees: Dict[str, SemanticNode] = {}  # doc_id -> root node

    def _mock_llm(self, prompt: str) -> str:
        """Mock LLM for testing."""
        return json.dumps({"selected_nodes": ["node_1"], "reasoning": "Mock selection"})

    def index_document(self, doc_id: str, sections: List[Dict]) -> SemanticNode:
        """
        Build semantic tree from document sections.

        Args:
            doc_id: Unique document identifier.
            sections: List of dicts with keys: title, content, level (1-4)

        Returns:
            Root SemanticNode of the built tree.
        """
        root = SemanticNode(id=f"{doc_id}_root", title=doc_id, summary="Document root", node_type=NodeType.DOCUMENT)

        # Simple tree builder: group by level
        current_parents = {0: root}

        for i, sec in enumerate(sections):
            level = sec.get("level", 1)
            node = SemanticNode(
                id=f"{doc_id}_sec_{i}",
                title=sec.get("title", f"Section {i}"),
                summary=sec.get("summary", sec.get("content", "")[:100] + "..."),
                node_type=NodeType.SECTION if level < 3 else NodeType.LEAF,
                content=sec.get("content", ""),
                page_ref=sec.get("page"),
            )

            # Find parent at level - 1
            parent_level = max(0, level - 1)
            parent = current_parents.get(parent_level, root)
            parent.children.append(node)
            current_parents[level] = node

        self.trees[doc_id] = root
        return root

    def generate_toc(self, doc_id: str) -> str:
        """Generate table-of-contents string for LLM reasoning."""
        if doc_id not in self.trees:
            return ""
        return self.trees[doc_id].to_toc_entry()

    def query(self, query: str, doc_ids: List[str] = None, max_nodes: int = 5) -> Dict:
        """
        Perform reasoning-based retrieval.

        Returns:
            {
                "selected_nodes": [SemanticNode, ...],
                "reasoning": str,
                "context": str  # Combined content for answer generation
            }
        """
        # Build combined TOC
        target_docs = doc_ids or list(self.trees.keys())
        combined_toc = "\n\n".join(f"## {doc_id}\n{self.generate_toc(doc_id)}" for doc_id in target_docs)

        # Phase 1: LLM selects relevant nodes
        selection_prompt = f"""You are a document navigation expert.
Given the following document structure (table of contents with node IDs):

{combined_toc}

USER QUERY: {query}

Select the {max_nodes} most relevant nodes to answer this query.
Respond in JSON format:
{{"selected_nodes": ["node_id_1", "node_id_2", ...], "reasoning": "Brief explanation"}}
"""
        selection_response = self.llm_fn(selection_prompt)

        try:
            selection = json.loads(selection_response)
        except json.JSONDecodeError:
            selection = {"selected_nodes": [], "reasoning": "Parse error"}

        # Phase 2: Gather selected node content
        selected_nodes = []
        for doc_id in target_docs:
            selected_nodes.extend(self._find_nodes_by_ids(self.trees[doc_id], selection.get("selected_nodes", [])))

        context = "\n\n---\n\n".join(f"[{n.id}] {n.title}\n{n.content}" for n in selected_nodes)

        return {"selected_nodes": selected_nodes, "reasoning": selection.get("reasoning", ""), "context": context}

    def _find_nodes_by_ids(self, node: SemanticNode, ids: List[str]) -> List[SemanticNode]:
        """Recursively find nodes by ID."""
        found = []
        if node.id in ids:
            found.append(node)
        for child in node.children:
            found.extend(self._find_nodes_by_ids(child, ids))
        return found


# ═══════════════════════════════════════════════════════════════════
# CAMELOT INTEGRATION POINT
# ═══════════════════════════════════════════════════════════════════

_global_tree_rag: Optional[SemanticTreeRAG] = None


def get_tree_rag(llm_fn: Callable[[str], str] = None) -> SemanticTreeRAG:
    """Singleton accessor for Camelot Kernel integration."""
    global _global_tree_rag
    if _global_tree_rag is None:
        _global_tree_rag = SemanticTreeRAG(llm_fn=llm_fn)
    return _global_tree_rag


if __name__ == "__main__":
    # Quick demo
    rag = SemanticTreeRAG()

    # Index a mock document
    sections = [
        {"level": 1, "title": "Introduction", "content": "This is the intro.", "summary": "Overview of the topic."},
        {"level": 2, "title": "Background", "content": "Historical context here.", "summary": "Historical background."},
        {"level": 2, "title": "Methods", "content": "We used method X and Y.", "summary": "Methodology details."},
        {"level": 1, "title": "Results", "content": "Key finding: X increased by 50%.", "summary": "Main findings."},
    ]
    rag.index_document("paper_001", sections)

    print("Generated TOC:")
    print(rag.generate_toc("paper_001"))

    print("\nQuery result:")
    result = rag.query("What methods were used?", ["paper_001"])
    print(f"Reasoning: {result['reasoning']}")
    print(f"Selected: {[n.id for n in result['selected_nodes']]}")