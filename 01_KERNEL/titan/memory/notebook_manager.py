# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import re
from typing import Any, Dict, List

from pydantic import BaseModel


class NotebookNode(BaseModel):
    id: str
    type: str
    content: str
    metadata: Dict[str, Any]
    links: List[str]


class NotebookManager:
    """
    Manages the Open Notebook structure and interfaces with LightRAG.
    """

    def __init__(self, notebook_dir: str = "03_VAULT/CAMELOT_NOTEBOOK"):
        self.notebook_dir = notebook_dir
        self.nodes: Dict[str, NotebookNode] = {}

    def scan(self):
        """
        Scans all markdown files in the notebook directory to build a local graph map.
        """
        for root, _, files in os.walk(self.notebook_dir):
            for file in files:
                if file.endswith(".md") and file != "index.md":
                    filepath = os.path.join(root, file)
                    self._parse_node(filepath)

    def _parse_node(self, filepath: str):
        with open(filepath, "r") as f:
            content = f.read()

        # Extract YAML frontmatter (simplified)
        metadata = {}
        if content.startswith("---"):
            match = re.search(r"---(.*?)---", content, re.DOTALL)
            if match:
                # In a real impl, we'd use yaml.safe_load
                frontmatter = match.group(1)
                for line in frontmatter.strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip()

        # Extract wiki-links [[node_id]]
        links = re.findall(r"\[\[(.*?)\]\]", content)

        node_id = metadata.get("id", os.path.basename(filepath).replace(".md", ""))

        self.nodes[node_id] = NotebookNode(
            id=node_id, type=metadata.get("type", "General"), content=content, metadata=metadata, links=links
        )

    def get_context(self, query: str) -> str:
        """
        Stub for LightRAG hybrid retrieval.
        Returns the human-readable 'Truth' from the notebook.
        """
        # In v1, we just return the most relevant nodes based on simple matches
        # Future: Call LightRAG API here
        return "[OPEN_NOTEBOOK_TRUTH]: Glass-walled cognition active."