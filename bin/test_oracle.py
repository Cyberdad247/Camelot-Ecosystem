"""Ω₃ Oracle dispatch test — routes a synth request through CloudServiceRouter.

Exercises the full path:
    _plan_cloud_service(intent)
        -> CloudServiceRequest(NOTEBOOKLM_SYNTHESIZE)
            -> CloudServiceRouter._notebooklm_synthesize
                -> notebooklm_bridge.synthesize
                    -> notebooklm-py RPC -> Cloud Brain
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

HOME = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS"))
os.environ["CAMELOT_OS_HOME"] = str(HOME)

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Make control_plane importable regardless of cwd.
sys.path.insert(0, str(HOME))

from control_plane.cloud_services import (  # noqa: E402
    CloudServiceName,
    CloudServiceRequest,
    CloudServiceRouter,
)


async def main() -> int:
    router = CloudServiceRouter()
    fails: list[str] = []

    async def step(label: str, service: CloudServiceName, payload: dict | None = None) -> bool:
        req = CloudServiceRequest(service=service, payload=payload or {})
        res = await router.invoke(req)
        marker = "OK" if res.success else "FAIL"
        print(f"[{marker}] {label}")
        if not res.success:
            print(f"    error: {res.error}")
            fails.append(label)
            return False
        summary = res.result
        if isinstance(summary, dict):
            keys = {k: (str(v)[:80] if not isinstance(v, (list, dict)) else f"<{type(v).__name__} len={len(v)}>")
                    for k, v in summary.items() if k != "items" and k != "sources"}
            if summary.get("items"):
                keys["items"] = f"<list len={len(summary['items'])}>"
            if summary.get("sources"):
                keys["sources"] = f"<list len={len(summary['sources'])}>"
            print(f"    {keys}")
        return True

    print("=== Ω₃ end-to-end smoke test ===")
    await step("NOTEBOOKLM_HEALTH", CloudServiceName.NOTEBOOKLM_HEALTH)
    await step("NOTEBOOKLM_SOURCES_LIST", CloudServiceName.NOTEBOOKLM_SOURCES_LIST)
    await step("NOTEBOOKLM_STUDIO_LIST(audio)",
               CloudServiceName.NOTEBOOKLM_STUDIO_LIST, {"artifact_type": "audio"})
    await step("NOTEBOOKLM_STUDIO_LIST(report)",
               CloudServiceName.NOTEBOOKLM_STUDIO_LIST, {"artifact_type": "report"})
    await step("NOTEBOOKLM_RESEARCH_POLL", CloudServiceName.NOTEBOOKLM_RESEARCH_POLL)
    # Synthesis last (slowest) — small question to keep it fast.
    await step(
        "NOTEBOOKLM_SYNTHESIZE",
        CloudServiceName.NOTEBOOKLM_SYNTHESIZE,
        {"query": "Name the Bifrost gate's three layers in one line.", "use_cache": False},
    )
    print("=== done ===")
    if fails:
        print(f"FAILED: {fails}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
