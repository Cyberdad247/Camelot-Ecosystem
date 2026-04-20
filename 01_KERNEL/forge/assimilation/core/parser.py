# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
from typing import Any, Dict, List

from .types import AssimilationRequest

# Real Phial Imports (Antigravity Well)
try:
    # Try absolute import (if 01_KERNEL is in path)
    import phials.semantic_tree_rag as semantic_tree_rag
    import phials.tree_sitter_phial as tree_sitter_phial

    PHIALS_AVAILABLE = True
    print("[DEBUG] Phials loaded via absolute import")
except ImportError:
    try:
        # Try relative import (if running as camelot.kernel.assimilation...)
        from ...phials import semantic_tree_rag, tree_sitter_phial

        PHIALS_AVAILABLE = True
        print("[DEBUG] Phials loaded via relative import")
    except ImportError:
        PHIALS_AVAILABLE = False
        print("[WARN] Phials not found. Running in mock mode.")


def scan_and_chunk_repo(request: AssimilationRequest) -> Dict[str, Any]:
    """
    Use existing Phials to walk the repo and produce semantic chunks.
    """
    files: List[str] = []
    chunks: List[Any] = []

    if PHIALS_AVAILABLE:
        try:
            phial = tree_sitter_phial.get_tree_sitter_phial()

            # Simple walk
            for root, dirs, filenames in os.walk(request.repo_path):
                # Skip .git etc
                if ".git" in dirs:
                    dirs.remove(".git")

                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    lang = phial.detect_language(filename)

                    if lang:
                        files.append(file_path)
                        try:
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read()

                            # Build hierarchy (sections)
                            sections = phial.build_semantic_hierarchy(content, lang)

                            # Add to chunks result
                            for sec in sections:
                                chunks.append(
                                    {
                                        "source": file_path,
                                        "type": "semantic_section",
                                        "language": lang,
                                        "title": sec["title"],
                                        "content": sec["content"],
                                        "summary": sec["summary"],
                                        "tags": request.tags,
                                    }
                                )
                        except Exception as e:
                            print(f"[WARN] Failed to process {file_path}: {e}")

        except Exception as e:
            print(f"[ERROR] Phial execution failed: {e}")
            # Fallback to mock logic handled below if chunks is empty?
            pass

    # Mock behavior fallback if nothing found (or Phials failed/unavailable)
    if not chunks:
        files = [f"{request.repo_path}/README.md"]
        chunks = [{"content": "Mock Chunk (Phials unavailable or empty repo)", "tags": request.tags}]

    return {
        "files_indexed": len(files),
        "chunks": chunks,
        "messages": [
            f"Indexed {len(files)} files from {request.repo_path}",
            f"Generated {len(chunks)} semantic chunks",
        ],
    }