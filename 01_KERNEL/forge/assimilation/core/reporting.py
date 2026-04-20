# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
from typing import Any, Dict

from .types import AssimilationRequest


def generate_assimilation_report(
    request: AssimilationRequest,
    scan_result: Dict[str, Any],
    graph_result: Dict[str, Any],
    skills_result: Dict[str, Any],
) -> str:
    """
    Render ASSIMILATIONREPORT.md using prompts/assimilation.jinja.
    """
    safe_path = request.repo_path.replace("\\", "_").replace("/", "_").replace(":", "")
    report_path = f"Nano-Knights/ASSIMILATIONREPORT_{safe_path}.md"

    # Check output dir
    output_dir = os.path.dirname(report_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Content Generation (Simple Template)
    content = f"""# 🛡️ ASSIMILATION REPORT
**Target:** `{request.repo_path}`
**Origin:** {request.origin}
**Tags:** {request.tags}

## 📊 Summary
- **Files Scanned:** {scan_result.get('files_indexed', 0)}
- **Semantic Chunks:** {len(scan_result.get('chunks', []))}
- **Knowledge Graph Nodes:** {graph_result.get('graph_nodes_created', 0)}
- **Skills Registered:** {skills_result.get('skills_registered', 0)}

## 📝 Messages
{chr(10).join(f"- {m}" for m in scan_result.get('messages', []))}

---
**[SIR FORGE]:** "The context is siphoned."
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    return report_path