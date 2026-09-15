# SPDX-License-Identifier: MIT
"""jcode AST & Polyglot CLI Executor Helper.

Parses source code into structured AST symbol manifests and dispatches
kinetic zero-context-bleed refactoring directives.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Dict, List


def parse_python_ast(source_code: str) -> Dict[str, Any]:
    """Extract classes, functions, and imports from python code."""
    try:
        tree = ast.parse(source_code)
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        imports = [
            n.names[0].name
            for n in ast.walk(tree)
            if isinstance(n, (ast.Import, ast.ImportFrom)) and n.names
        ]
        return {
            "valid": True,
            "classes": classes,
            "functions": functions,
            "imports": imports,
        }
    except SyntaxError as e:
        return {"valid": False, "error": str(e)}


if __name__ == "__main__":
    sample = """
import os
class Sentinel:
    def verify(self):
        return True
"""
    print(json.dumps(parse_python_ast(sample), indent=2))
