# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Tier 3 Modal entrypoint (blueprint-compatible)
#
# Equivalent to the blueprint's:
#     cd cloud_orchestrator && modal deploy modal_brain.py
#
# This file is a THIN wrapper around the existing Morgana Modal stack
# under 02_FORGE/PORTAL_CORE/Modal/morgana/, fronted by the
# SmartCostController so no job can exceed the fiduciary caps.
#
# DO NOT modal deploy this until:
#   1. Modal tokens at ~/.modal.toml have been rotated in modal.com
#   2. SmartCostController ledger path is writable (vault .secure dir)
#   3. Vault .secure/ is confirmed gitignored
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "02_FORGE" / "PORTAL_CORE" / "Modal"))
sys.path.insert(0, str(_REPO / "02_FORGE" / "PORTAL_CORE" / "Modal" / "morgana"))

from security import cost_gate  # noqa: E402


@cost_gate(estimated_usd=0.12, label="modal.morgana_core.invoke")
def invoke_morgana_core(prompt: str):
    """Cost-gated facade over the existing morgana_core module."""
    import morgana_core  # type: ignore
    if hasattr(morgana_core, "invoke"):
        return morgana_core.invoke(prompt)
    if hasattr(morgana_core, "run"):
        return morgana_core.run(prompt)
    raise RuntimeError(
        "morgana_core has neither invoke() nor run(); "
        "inspect 02_FORGE/PORTAL_CORE/Modal/morgana/morgana_core.py"
    )


@cost_gate(estimated_usd=0.08, label="modal.tasha_voice.invoke")
def invoke_tasha_voice(text: str):
    """Cost-gated facade over tasha_voice_agent."""
    import tasha_voice_agent  # type: ignore
    if hasattr(tasha_voice_agent, "synthesize"):
        return tasha_voice_agent.synthesize(text)
    raise RuntimeError("tasha_voice_agent.synthesize not found")


if __name__ == "__main__":
    from security import SmartCostController
    print("SmartCostController status:", SmartCostController().status())
