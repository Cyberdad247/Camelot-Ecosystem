# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Ω_NANO_FORGE: The Knight Factory (v1.0)
Generates lightweight, single-binary agents based on a Manifest.
"""

import json
import os
from typing import Any, Dict


class NanoForge:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(base_dir, "dist", "nano_knights")
        self.templates_dir = os.path.join(base_dir, "templates")

        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def load_manifest(self, manifest_path: str) -> Dict[str, Any]:
        with open(manifest_path, "r") as f:
            return json.load(f)

    def forge_knight(self, manifest: Dict[str, Any]):
        knight_id = manifest["id"]
        print(f"[FORGE] Igniting Anvil for Knight: {knight_id}...")

        # 1. Select Template (Python default for now)
        template_path = os.path.join(self.templates_dir, "knight_python.py.tpl")

        # 2. Render Code
        with open(template_path, "r") as f:
            template_code = f.read()

        # Basic substitution (Jinja2 overkill for v1)
        knight_code = template_code.replace("{{KNIGHT_ID}}", knight_id)
        knight_code = knight_code.replace("{{OWNER}}", manifest["governance"]["owner"])

        print(f"[DEBUG] knight_code snippet: {knight_code[:100]}")

        # 3. Write Output
        output_path = os.path.join(self.output_dir, f"{knight_id}.py")
        with open(output_path, "w") as f:
            f.write(knight_code)

        print(f"[FORGE] Knight Cast Successfully: {output_path}")
        return output_path


if __name__ == "__main__":
    # Test Forge
    forge = NanoForge()
    # Dummy manifest
    test_manifest = {"id": "knight_scout_01", "governance": {"owner": "Sir_Test"}}
    # Create dummy template for test logic removed to use real template
    # if not os.path.exists(forge.templates_dir):
    #     os.makedirs(forge.templates_dir)
    # with open(os.path.join(forge.templates_dir, "knight_python.py.tpl"), "w") as f:
    #     f.write("# Knight: {{KNIGHT_ID}}\n# Owner: {{OWNER}}\nprint('I serve.')")

    forge.forge_knight(test_manifest)