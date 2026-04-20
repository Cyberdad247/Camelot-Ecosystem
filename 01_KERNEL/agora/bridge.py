# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from kernel.agora.knights.opencode_knight import OpenCodeKnight
from kernel.security.warden import warden


class ExcaliburBridge:
    """
    ⚔️ THE EXCALIBUR BRIDGE
    Bridges the Strategic Brain (Merlin) with the Kinetic Hand (OpenCode).
    Handles high-velocity code manipulation tasks.
    """

    def __init__(self):
        self.knight = OpenCodeKnight()

    async def fast_refactor(self, intent: str, context_details: str = "") -> str:
        """
        Executes an industrial-scale refactor.
        """
        print(f"🗡️ [BRIDGE] Actuating Excalibur for intent: {intent[:50]}...")

        # 1. Security Check (Warden)
        warden.verify_permission(
            agent_id="EXCALIBUR_BRIDGE",
            resource_type="system_api",
            action="EXECUTE_BRIDGE",
            target="opencode",
            trust_level="KERNEL",
        )

        # 2. Hand-off to OpenCode Knight
        # Multi-file refactors often require a prompt that includes context
        full_prompt = f"{intent}\n\n[ADDITIONAL_CONTEXT]:\n{context_details}"

        # We use a non-dry run for the bridge by default if confirmed or for simulation
        result = await self.knight.execute_kinetic(full_prompt, plan_only=False)

        return result


# Singleton
bridge = ExcaliburBridge()