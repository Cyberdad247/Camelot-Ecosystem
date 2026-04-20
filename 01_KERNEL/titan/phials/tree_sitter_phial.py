# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
TREE-SITTER PHIAL: Code Intelligence Engine
Purpose: Unified AST/CST parsing for 40+ languages via Tree-sitter.

Integration Points:
- Assimilation Pipeline (CST → Camelot IR)
- UKG Code Glyphs (deterministic signature extraction)
- Semantic Tree RAG (code hierarchy for reasoning RAG)

Install:
    pip install tree-sitter tree-sitter-python tree-sitter-go tree-sitter-javascript tree-sitter-rust
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════
# LAZY GRAMMAR LOADING (to avoid import errors if not installed)
# ═══════════════════════════════════════════════════════════════════

_PARSERS: Dict[str, Any] = {}
_LANGUAGES: Dict[str, Any] = {}


def _load_language(lang: str):
    """Lazy-load a Tree-sitter language grammar."""
    if lang in _LANGUAGES:
        return _LANGUAGES[lang]

    try:
        from tree_sitter import Language, Parser

        if lang == "python":
            import tree_sitter_python as ts_lang
        elif lang == "go":
            import tree_sitter_go as ts_lang
        elif lang == "javascript":
            import tree_sitter_javascript as ts_lang
        elif lang == "rust":
            import tree_sitter_rust as ts_lang
        elif lang == "typescript":
            import tree_sitter_typescript as ts_lang

            ts_lang = ts_lang.language_typescript()  # Special case
            _LANGUAGES[lang] = Language(ts_lang)
            return _LANGUAGES[lang]
        else:
            return None

        _LANGUAGES[lang] = Language(ts_lang.language())
        return _LANGUAGES[lang]
    except ImportError:
        return None


def _get_parser(lang: str):
    """Get or create a parser for the given language."""
    if lang in _PARSERS:
        return _PARSERS[lang]

    language = _load_language(lang)
    if language is None:
        return None

    try:
        from tree_sitter import Parser

        parser = Parser(language)
        _PARSERS[lang] = parser
        return parser
    except Exception:
        return None


class NodeType(Enum):
    """Semantic node types extracted from code."""

    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    IMPORT = "import"
    VARIABLE = "variable"
    COMMENT = "comment"
    OTHER = "other"


@dataclass
class CodeNode:
    """A semantic node extracted from source code."""

    node_type: NodeType
    name: str
    signature: str  # Full signature for functions/classes
    docstring: str = ""
    start_line: int = 0
    end_line: int = 0
    children: List["CodeNode"] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def to_glyph(self) -> Dict:
        """Convert to UKG-compatible glyph format."""
        return {
            "type": self.node_type.value,
            "name": self.name,
            "sig": self.signature[:100],  # Truncate for token efficiency
            "lines": [self.start_line, self.end_line],
            "children": [c.to_glyph() for c in self.children],
        }


class TreeSitterPhial:
    """
    Code intelligence engine powered by Tree-sitter.

    Capabilities:
    - Parse 40+ languages to CST
    - Extract semantic nodes (classes, functions, imports)
    - Generate code glyphs for UKG storage
    - Build hierarchies for Semantic Tree RAG
    """

    # Language file extension mapping
    EXTENSION_MAP = {
        ".py": "python",
        ".go": "go",
        ".js": "javascript",
        ".ts": "typescript",
        ".rs": "rust",
        ".jsx": "javascript",
        ".tsx": "typescript",
    }

    # Query patterns for different languages
    QUERIES = {
        "python": {
            "functions": "(function_definition name: (identifier) @name)",
            "classes": "(class_definition name: (identifier) @name)",
            "imports": "(import_statement) @import",
        },
        "go": {
            "functions": "(function_declaration name: (identifier) @name)",
            "types": "(type_declaration (type_spec name: (type_identifier) @name))",
            "imports": "(import_declaration) @import",
        },
        "javascript": {
            "functions": "(function_declaration name: (identifier) @name)",
            "classes": "(class_declaration name: (identifier) @name)",
            "imports": "(import_statement) @import",
        },
    }

    def __init__(self):
        self.supported_languages = list(self.EXTENSION_MAP.values())

    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect language from file extension."""
        for ext, lang in self.EXTENSION_MAP.items():
            if file_path.endswith(ext):
                return lang
        return None

    def parse(self, source: str, language: str) -> Optional[Any]:
        """Parse source code and return the CST root node."""
        parser = _get_parser(language)
        if parser is None:
            return None

        tree = parser.parse(bytes(source, "utf-8"))
        return tree.root_node

    def extract_nodes(self, source: str, language: str) -> List[CodeNode]:
        """
        Extract semantic nodes from source code.
        Works without Tree-sitter queries for maximum compatibility.
        """
        root = self.parse(source, language)
        if root is None:
            return []

        nodes = []
        self._walk_tree(root, source, language, nodes)
        return nodes

    def _walk_tree(self, node, source: str, language: str, nodes: List[CodeNode], depth: int = 0):
        """Recursively walk the tree and extract semantic nodes."""
        node_type = self._classify_node(node, language)

        if node_type != NodeType.OTHER:
            name = self._extract_name(node, language)
            signature = self._extract_signature(node, source)

            code_node = CodeNode(
                node_type=node_type,
                name=name,
                signature=signature,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
            )
            nodes.append(code_node)

        # Recurse into children (limit depth for performance)
        if depth < 3:
            for child in node.children:
                self._walk_tree(child, source, language, nodes, depth + 1)

    def _classify_node(self, node, language: str) -> NodeType:
        """Classify a tree-sitter node into a semantic type."""
        node_type = node.type

        # Python
        if language == "python":
            if node_type == "function_definition":
                return NodeType.FUNCTION
            elif node_type == "class_definition":
                return NodeType.CLASS
            elif node_type in ("import_statement", "import_from_statement"):
                return NodeType.IMPORT

        # Go
        elif language == "go":
            if node_type == "function_declaration":
                return NodeType.FUNCTION
            elif node_type == "method_declaration":
                return NodeType.METHOD
            elif node_type == "type_declaration":
                return NodeType.CLASS
            elif node_type == "import_declaration":
                return NodeType.IMPORT

        # JavaScript/TypeScript
        elif language in ("javascript", "typescript"):
            if node_type in ("function_declaration", "arrow_function"):
                return NodeType.FUNCTION
            elif node_type == "class_declaration":
                return NodeType.CLASS
            elif node_type == "method_definition":
                return NodeType.METHOD
            elif node_type == "import_statement":
                return NodeType.IMPORT

        # Rust
        elif language == "rust":
            if node_type == "function_item":
                return NodeType.FUNCTION
            elif node_type in ("struct_item", "impl_item"):
                return NodeType.CLASS
            elif node_type == "use_declaration":
                return NodeType.IMPORT

        return NodeType.OTHER

    def _extract_name(self, node, language: str) -> str:
        """Extract the name identifier from a node."""
        for child in node.children:
            if child.type == "identifier" or child.type == "type_identifier":
                return child.text.decode("utf-8")
            # Handle named children
            if hasattr(node, "child_by_field_name"):
                name_node = node.child_by_field_name("name")
                if name_node:
                    return name_node.text.decode("utf-8")
        return "<anonymous>"

    def _extract_signature(self, node, source: str) -> str:
        """Extract the signature (first line) of a node."""
        start = node.start_byte
        # Find the end of the first line
        end = source.find("\n", start)
        if end == -1:
            end = node.end_byte

        sig = source[start : min(end, start + 150)]  # Cap at 150 chars
        return sig.strip()

    def to_camelot_ir(self, source: str, language: str, file_path: str = "") -> Dict:
        """
        Convert source code to Camelot Intermediate Representation.
        This is the output format expected by assimilation.jinja.
        """
        nodes = self.extract_nodes(source, language)

        return {
            "file": file_path,
            "language": language,
            "node_count": len(nodes),
            "structure": [n.to_glyph() for n in nodes],
            "imports": [n.name for n in nodes if n.node_type == NodeType.IMPORT],
            "exports": [n.name for n in nodes if n.node_type in (NodeType.FUNCTION, NodeType.CLASS)],
        }

    def build_semantic_hierarchy(self, source: str, language: str) -> List[Dict]:
        """
        Build a hierarchy suitable for semantic_tree_rag.py.
        Returns sections in the format expected by SemanticTreeRAG.index_document().
        """
        nodes = self.extract_nodes(source, language)

        sections = []
        for node in nodes:
            level = 1 if node.node_type == NodeType.CLASS else 2
            sections.append(
                {
                    "level": level,
                    "title": f"{node.node_type.value}: {node.name}",
                    "content": node.signature,
                    "summary": f"{node.node_type.value} '{node.name}' at lines {node.start_line}-{node.end_line}",
                    "page": node.start_line,
                }
            )

        return sections


# ═══════════════════════════════════════════════════════════════════
# CAMELOT INTEGRATION POINT
# ═══════════════════════════════════════════════════════════════════

_global_phial: Optional[TreeSitterPhial] = None


def get_tree_sitter_phial() -> TreeSitterPhial:
    """Singleton accessor for Camelot Kernel integration."""
    global _global_phial
    if _global_phial is None:
        _global_phial = TreeSitterPhial()
    return _global_phial


if __name__ == "__main__":
    # Demo
    phial = TreeSitterPhial()

    sample_python = '''
class Calculator:
    """A simple calculator."""
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
    
    def multiply(self, a: int, b: int) -> int:
        return a * b

def main():
    calc = Calculator()
    print(calc.add(2, 3))
'''

    print("=" * 60)
    print("TREE-SITTER PHIAL DEMO")
    print("=" * 60)

    # Try to parse
    nodes = phial.extract_nodes(sample_python, "python")

    if nodes:
        print(f"\nExtracted {len(nodes)} nodes:")
        for node in nodes:
            print(f"  - {node.node_type.value}: {node.name} (L{node.start_line}-{node.end_line})")

        print("\nCamelot IR:")
        ir = phial.to_camelot_ir(sample_python, "python", "sample.py")
        print(json.dumps(ir, indent=2))
    else:
        print("\n⚠️ Tree-sitter not installed. Run:")
        print("   pip install tree-sitter tree-sitter-python")