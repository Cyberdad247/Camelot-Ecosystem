# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
swarm_tools_v2.py

Defines the Tool Capabilities for the Titan Swarm (Merlin/Chronos).
Implements safe wrappers for file I/O, search, and execution.
Follows the Iron Gate protocol.
"""

import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SwarmTools:
    """
    Registry of executable actions for the Titan Swarm.
    """
    
    @staticmethod
    def get_definitions() -> List[Dict[str, Any]]:
        """
        Returns OpenAI-compatible tool definitions.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge",
                    "description": "Search the UKG (Universal Knowledge Glyph) for conceptual information.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query."}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read content of a file from the repository.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Relative path to file."}
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_memory",
                    "description": "Save a critical insight to Long-Term Memory (UKG).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "The insight to store."},
                            "tags": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["content"]
                    }
                }
            }
        ]

    # --- Execution Handlers ---

    @staticmethod
    def execute_tool(tool_name: str, args: Dict[str, Any], context: Any = None) -> str:
        """
        Safely executes a tool by name.
        """
        logger.info(f"🛠️ Executing Tool: {tool_name} with {args}")
        
        try:
            if tool_name == "search_knowledge":
                if context and hasattr(context, "query"):
                    # Use the bridge if context is passed (e.g. Chronos reference)
                    return str(context.query(args["query"]))
                return "Error: Search context not available."

            elif tool_name == "read_file":
                path = args.get("file_path", "")
                # Simple path validation (Iron Gate lite)
                if ".." in path or path.startswith(("/", "\\")):
                    return "Error: Invalid path (Path Traversal detected)."
                
                full_path = os.path.abspath(path)
                if not os.path.exists(full_path):
                    return f"Error: File not found: {path}"
                
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read()

            elif tool_name == "write_memory":
                # Mock memory write (Phase 4 integration point)
                content = args.get("content", "")
                tags = args.get("tags", [])
                logger.info(f"💾 [MEMORY] Storing: {content[:50]}... Tags: {tags}")
                return "Success: Written to Memory Buffer."

            else:
                return f"Error: Unknown tool {tool_name}"
                
        except Exception as e:
            logger.error(f"Tool Execution Failed: {e}")
            return f"Error: {str(e)}"