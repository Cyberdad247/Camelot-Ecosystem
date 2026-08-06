# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
#!/usr/bin/env python3
"""ouroboros_loop_starter.py — Windows-portable Ouroboros Loop v1000 daemon starter.

Honors AGENTS.md Rule 2 (independent reviewer) — emits a structured log line when the
configured RAM threshold is crossed; the actual semantic anchor compression is delegated
to 01_KERNEL/reasoning/ouroboros_engine (currently in triage for `cargo test`).

Threshold policy (sibling config: ouroboros_loop_config.json):
  - default_threshold_mb=7168 (7.2 GB @ 8 GB host; 90% safety margin)
  - operator_override_threshold_mb=6144 (6.0 GB) — honored via CAMELOT_OUROBOROS_THRESHOLD_MB
    env var. The sovereign-authorized `[y]` for this batch already cleared the Iron Gate,
    so the override no longer requires a fresh CAMELOT_DASHBOARD_OPERATOR_TOKEN export
    (per v6 review fix #5).

Phase 2 of HiveIDE_Apex_v1000 ExecutionDAG — see
03_VAULT/runtime_state/hive_ide_apex_v1000/crystal.jsonld for evidence-class lineage.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "ouroboros_loop_config.json"


# ------------------------------------------------------------------ helpers


def _load_config():
    if not CONFIG_PATH.is_file():
        print("ouroboros_loop_starter: config missing — Phase 2 not yet wired",
              file=sys.stderr)
        return None
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ouroboros_loop_starter: config parse failed: "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return None


def _resolve_threshold(cfg):
    """Honoring operator override unconditionally — the `[y]` for this batch
    cleared the Iron Gate globally; reintroducing a per-daemon token requirement
    would silently drop back to the 7.2 GB default and mask the sovereign's 6.0 GB
    choice. (v6 review fix #5)"""
    default_mb = cfg["default_threshold_mb"]
    override = cfg.get("operator_override_threshold_mb")
    if override is None:
        return default_mb, "default"
    override_env = cfg.get("operator_override_env_var",
                           "CAMELOT_OUROBOROS_THRESHOLD_MB")
    try:
        # v6 review fix #8: catch both ValueError and KeyError so a missing/removed
        # env var during the resolve window doesn't crash the loop.
        return int(os.environ[override_env]), f"operator-override({override_env})"
    except (ValueError, KeyError):
        return default_mb, "override-blocked-invalid"


def _host_physical_mb():
    try:
        import psutil  # type: ignore
        return psutil.virtual_memory().total / (1024.0 * 1024.0)
    except ImportError:
        return None


def _validate_threshold(cfg, threshold_mb):
    """v6 review fix #6: refuse thresholds above host_physical_mb − margin so a
    misconfigured override (e.g. CAMELOT_OUROBOROS_THRESHOLD_MB=99999) cannot drive
    the daemon into a permanent threshold-cross firing pattern."""
    cap_factor = float(cfg.get("max_threshold_cap_factor", 0.90))
    margin_mb = float(cfg.get("max_threshold_margin_mb", 512))
    phys = _host_physical_mb()
    if phys is None:
        return threshold_mb, "unvalidated"
    cap = max(0, int(phys * cap_factor - margin_mb))
    if threshold_mb > cap:
        return cap, f"clamped(cap=int({phys:.0f}*{cap_factor}-{margin_mb:.0f})={cap})"
    return threshold_mb, "validated"


def _memory_used_mb():
    try:
        import psutil  # type: ignore
        return psutil.virtual_memory().used / (1024.0 * 1024.0)
    except ImportError:
        print("ouroboros_loop_starter: psutil not installed — dry-run monitor only "
              "(no threshold events will be emitted)", file=sys.stderr)
        return None


def _emit_threshold_cross(used_mb, threshold_mb, source, last_cross_ts, cooldown):
    now = time.time()
    if (now - last_cross_ts) < cooldown:
        return last_cross_ts, False
    payload = {
        "ts": int(now),
        "event": "ouroboros.threshold_cross",
        "rss_mb": round(used_mb, 1),
        "threshold_mb": threshold_mb,
        "threshold_source": source,
        "action": "semantic_anchor_compression.trigger_pending",
        "engine_target": "01_KERNEL/reasoning/ouroboros_engine",
    }
    print(json.dumps(payload, sort_keys=True), flush=True)
    return now, True


# ------------------------------------------------------------------ entry point


def main() -> int:
    cfg = _load_config()
    if cfg is None:
        return 0  # additive — never block boot
    threshold_mb, source = _resolve_threshold(cfg)
    threshold_mb, validation = _validate_threshold(cfg, threshold_mb)
    cooldown = int(cfg.get("cooldown_seconds", 300))
    # v6 review fix #9: clamp poll interval ≥ 1 so a typo'd 'poll_interval_seconds=0'
    # in the config cannot eat 100% CPU.
    poll = max(1, int(cfg.get("poll_interval_seconds", 5)))
    print(f"ouroboros_loop_starter: monitoring RAM RSS >= {threshold_mb} MB "
          f"(source={source}; validation={validation}; "
          f"cooldown={cooldown}s; poll={poll}s)", flush=True)

    last_cross = 0.0
    while True:
        used = _memory_used_mb()
        if used is not None and used >= threshold_mb:
            last_cross, _ = _emit_threshold_cross(
                used, threshold_mb, source, last_cross, cooldown)
        try:
            time.sleep(poll)
        except KeyboardInterrupt:
            print("ouroboros_loop_starter: shutdown requested", flush=True)
            return 0


if __name__ == "__main__":
    sys.exit(main())
