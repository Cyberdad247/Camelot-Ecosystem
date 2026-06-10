# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import subprocess

from kernel.agora.knights.omni_knight import OmniKnight


class OpenCodeKnight(OmniKnight):
    """
    Sir OpenCode: The Kinetic Executor.
    Uses the OpenCode CLI to perform industrial-scale code changes.
    """

    def __init__(self, agent_id="PERCIVAL_OPEN"):
        # We inherit from OmniKnight but specialize for OpenCode
        super().__init__(agent_id=agent_id, default_role="Kinetic Master of the Terminal")
        self.cli_path = "opencode"  # Assumes globally installed

    async def execute_kinetic(self, task_prompt: str, plan_only: bool = True) -> str:
        """
        Executes a task via OpenCode CLI.
        """
        cmd = [self.cli_path, "run"]
        if plan_only:
            cmd.append("--plan")
        cmd.extend(["-p", task_prompt])

        try:
            print(f"🗡️ [OPENCODE] Executing Kinetic Task: {task_prompt[:50]}...")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=False,
            )
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                return f"❌ [OPENCODE] EXECUTION FAILED:\n{stderr}"

            return f"✅ [OPENCODE] TASK COMPLETE:\n{stdout}"

        except Exception as e:
            return f"❌ [OPENCODE] KINETIC ERROR: {str(e)}"

    def get_capabilities(self):
        return [
            "Industrial Refactoring",
            "Multi-File Search & Replace",
            "TUI Interactive Build",
            "Environment Diagnostics",
        ]