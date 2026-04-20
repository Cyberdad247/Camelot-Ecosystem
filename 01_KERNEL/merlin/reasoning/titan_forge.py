# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json
import os


class TitanForge:
    """
    TITAN FORGE v2.0: Context Compiler
    Prepares a high-density 'Forge Envelope' for OpenCode execution.
    """

    @staticmethod
    def compile_forge_envelope(intent, target_files):
        """
        Gathers files and metadata into a single block of context.
        """
        print(f"⚒️ [FORGE] Compiling Context for: {intent[:50]}...")

        envelope = {"intent": intent, "timestamp": "2026-01-20", "files": []}

        for file_path in target_files:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    envelope["files"].append({"path": file_path, "content": f.read()})
            else:
                print(f"⚠️ [FORGE] File missing: {file_path}")

        # Inject Sovereign DNA
        envelope["dna"] = {"version": "100.3.0", "laws": ["Antigravity", "Resonance"]}

        output_path = "04_DEVELOPMENT/build/forge_envelope.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(envelope, f, indent=2)

        print(f"✅ [FORGE] Envelope Ready: {output_path}")
        return output_path