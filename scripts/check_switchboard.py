#!/usr/bin/env python3
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "control_plane"))
from switchboard import probe_all, get_manifest

asyncio.run(probe_all())
manifest = get_manifest()
terminals = manifest.get("terminals", {})

hdr = "{:<20} {:<10} {:<16} {:<12} {}".format("KNIGHT", "COST_TIER", "STATUS", "PROBE_PORT", "NOTES")
print(hdr)
print("-" * 90)
for tid, t in sorted(terminals.items()):
    flag = "  <-- VERIFY" if tid == "sir_codex" else ""
    row = "{:<20} {:<10} {:<16} {:<12} {}{}".format(
        tid,
        t["cost_tier"],
        t["status"],
        str(t["probe_port"]),
        t["notes"][:40],
        flag,
    )
    print(row)
