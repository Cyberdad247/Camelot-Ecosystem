# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Honcho Self-Hosted Memory Bridge for Hermes
"""
HonchoBridge v1.0 — Self-Hosted L4 Metamemory & Dialectic State Engine
====================================================================
Integrates self-hosted Honcho (Plastic Labs / elkimek self-hosted) with
HERMES_PRIME and the Camelot WorldTree.

Provides cross-session user modeling, observation extraction, metamemory
retrieval, and dialectic context consolidation for Hermes Agent.

Topology:
  - Local Port: http://127.0.0.1:8000
  - Mesh VPS Hub: KVM563 Hermes Node, port 8000 (address from
    ``mesh_topology.HUB_TAILSCALE_IP``; not restated here so it cannot drift)
  - VFS Coordinate: vfs://worldtree/memory/honcho/
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from control_plane.infra.hermes_bridge import HermesBus
from control_plane.infra.mesh_topology import HUB_TAILSCALE_IP

log = logging.getLogger("HONCHO_BRIDGE")

_CAMELOT_ROOT = Path(__file__).resolve().parent.parent.parent
_CACHE_PATH = _CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "honcho_memory_cache.json"

DEFAULT_HONCHO_URL = os.environ.get("HONCHO_BASE_URL", "http://127.0.0.1:8000")
VPS_HONCHO_URL = os.environ.get("HONCHO_VPS_URL", f"http://{HUB_TAILSCALE_IP}:8000")


class _HonchoBridgeBase:
    """
    Client and local coordinator for self-hosted Honcho memory engine.
    Fully integrated with Hermes Agent and WorldTree.
    """

    def __init__(self, base_url: Optional[str] = None, bus: Optional[HermesBus] = None):
        self.base_url = (base_url or DEFAULT_HONCHO_URL).rstrip("/")
        self.vps_url = VPS_HONCHO_URL.rstrip("/")
        self.bus = bus or HermesBus()
        self._online: Optional[bool] = None
        self._online_checked_at = 0.0
        self._ensure_cache()

    def _ensure_cache(self) -> None:
        if not _CACHE_PATH.exists():
            _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            initial = {
                "version": "1.0.0",
                "worldtree_root": "a0a4bfb9-e847-4c38-be39-7aee398f0795",
                "hermes_prime_uuid": "28f89cb6-5048-4b5d-9e94-376082d24744",
                "users": {},
                "sessions": {},
                "metamemory": {},
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            _CACHE_PATH.write_text(json.dumps(initial, indent=2), encoding="utf-8")

    def _load_cache(self) -> dict[str, Any]:
        try:
            return json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {"users": {}, "sessions": {}, "metamemory": {}}

    def _save_cache(self, data: dict[str, Any]) -> None:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        _CACHE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _http_request(self, method: str, endpoint: str, payload: Optional[dict] = None) -> Tuple[bool, Any]:
        """Perform HTTP request to Honcho server with graceful fallback to local cache.

        Offline memo: after one failed probe the bridge serves the local cache
        for 60s instead of paying a TCP timeout per call (matters when embedding
        dozens of knights while the server is down).
        """
        if self._online is False and (time.monotonic() - self._online_checked_at) < 60.0:
            return False, "OFFLINE_MEMO (local cache)"
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        data_bytes = json.dumps(payload).encode("utf-8") if payload else None
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json", "User-Agent": "Camelot-Hermes-Honcho/1.0"},
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                status = resp.status
                body = resp.read().decode("utf-8")
                res = json.loads(body) if body else {}
                self._online = True
                return True, res
        except Exception as err:
            log.debug("Honcho server not reachable at %s: %s (using resilient local cache)", url, err)
            self._online = False
            self._online_checked_at = time.monotonic()
            return False, str(err)

    def check_health(self) -> dict[str, Any]:
        """Check live Honcho server health (local and VPS mesh)."""
        ok, res = self._http_request("GET", "health")
        return {
            "online": ok,
            "target": self.base_url,
            "vps_target": self.vps_url,
            "details": res if ok else "RUNNING_IN_LOCAL_FALLBACK_MODE",
            "vfs_mount": "vfs://worldtree/memory/honcho/",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_or_create_user(self, user_id: str, metadata: Optional[dict] = None) -> dict[str, Any]:
        """Get or create user profile in Honcho and WorldTree cache."""
        meta = metadata or {}
        meta.setdefault("created_by", "HERMES_PRIME")
        meta.setdefault("worldtree_anchor", "KING_ARTHUR_VIZION")

        ok, res = self._http_request("POST", "v1/users/", {"id": user_id, "metadata": meta})
        cache = self._load_cache()
        if user_id not in cache["users"]:
            cache["users"][user_id] = {
                "id": user_id,
                "metadata": meta,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            self._save_cache(cache)

        self.bus.publish("honcho.memory", {"event": "user_synced", "user_id": user_id})
        return res if ok else cache["users"][user_id]

    def get_or_create_session(self, session_id: str, user_id: str, metadata: Optional[dict] = None) -> dict[str, Any]:
        """Get or create conversation session in Honcho."""
        meta = metadata or {}
        ok, res = self._http_request(
            "POST", "v1/sessions/", {"id": session_id, "user_id": user_id, "metadata": meta}
        )

        cache = self._load_cache()
        if session_id not in cache["sessions"]:
            cache["sessions"][session_id] = {
                "id": session_id,
                "user_id": user_id,
                "metadata": meta,
                "messages": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            self._save_cache(cache)

        self.bus.publish("honcho.memory", {"event": "session_synced", "session_id": session_id, "user_id": user_id})
        return res if ok else cache["sessions"][session_id]

    def add_message(
        self, session_id: str, user_id: str, role: str, content: str, metadata: Optional[dict] = None
    ) -> dict[str, Any]:
        """Ingest conversation message into Honcho for background dialectic derivation."""
        msg_payload = {
            "user_id": user_id,
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        ok, res = self._http_request("POST", f"v1/sessions/{session_id}/messages/", msg_payload)

        cache = self._load_cache()
        sess = cache["sessions"].setdefault(
            session_id, {"id": session_id, "user_id": user_id, "messages": []}
        )
        sess["messages"].append(msg_payload)
        self._save_cache(cache)

        self.bus.publish(
            "honcho.memory",
            {
                "event": "message_ingested",
                "session_id": session_id,
                "user_id": user_id,
                "role": role,
                "tokens": len(content.split()),
            },
        )
        return res if ok else msg_payload

    def query_context(self, session_id: str, query: str, max_tokens: int = 4000) -> dict[str, Any]:
        """Query Honcho memory and dialectic context for active session."""
        ok, res = self._http_request(
            "POST",
            f"v1/sessions/{session_id}/context/",
            {"query": query, "max_tokens": max_tokens},
        )
        if ok:
            return res

        cache = self._load_cache()
        sess = cache["sessions"].get(session_id, {})
        messages = sess.get("messages", [])
        return {
            "session_id": session_id,
            "query": query,
            "retrieved_context": [m["content"] for m in messages[-5:]],
            "mode": "LOCAL_CACHE_RECALL",
            "worldtree_status": "VFS_TETHERED",
        }

    def get_metamemory(self, user_id: str) -> dict[str, Any]:
        """Retrieve consolidated user metamemory / theory-of-mind observations."""
        ok, res = self._http_request("GET", f"v1/users/{user_id}/metamemory/")
        if ok:
            return res

        cache = self._load_cache()
        user_meta = cache.get("metamemory", {}).get(user_id, {
            "user_id": user_id,
            "core_identity": "King Arthur (VaShawn O. Head / Vizion)",
            "role": "Sovereign Operator",
            "invariants": [
                "Rule 7 Hotpath Purity (0% Python/Node in Hotpath)",
                "Father's Camelot Compass (Absolute Truth)",
                "Excalibur Command Center (S26 Ultra)",
                "VPS Hub KVM563 (Hermes Control Plane)",
            ],
            "observations": [
                "Prefers concise, mathematically sound engineering reports.",
                "Enforces strict test-driven development and zero-regression gates.",
                "Directs 39 Knights of the Round Table through ANYA_OMEGA and SIR_KAY.",
            ],
            "source": "WORLDTREE_VFS_ANCHOR",
        })
        return user_meta


def normalize_knight_id(knight_id: str) -> str:
    """Canonical knight normalization (mirrors HydrationManager aliasing)."""
    kid = (knight_id or "").strip().upper()
    if kid == "SIR_HELIOS":
        kid = "SIR_HELIO"
    return kid


def knight_user_id(knight_id: str) -> str:
    """Honcho user id for a knight: knight_<lowercase_id>."""
    return "knight_%s" % normalize_knight_id(knight_id).lower()


def knight_session_id(knight_id: str) -> str:
    """Honcho session id for a knight: sess_knight_<lowercase_id>."""
    return "sess_knight_%s" % normalize_knight_id(knight_id).lower()


# ── Per-knight embedding ───────────────────────────────────────────────────

def _ensure_sys_path() -> None:
    import sys as _sys

    root = _CAMELOT_ROOT
    for extra in (root, root / "01_KERNEL"):
        if str(extra) not in _sys.path:
            _sys.path.insert(0, str(extra))


def _all_registry_knights() -> List[str]:
    try:
        _ensure_sys_path()
        from memory.cloudbrain_connector import KNIGHT_NOTEBOOKS

        return [normalize_knight_id(k) for k in KNIGHT_NOTEBOOKS]
    except Exception as exc:  # noqa: BLE001
        log.debug("knight registry unavailable: %s (defaulting to HERMES_PRIME)", exc)
        return ["HERMES_PRIME"]


class _HonchoKnightEmbedding:
    """Mixin implementing per-knight Honcho embedding for HonchoBridge."""

    def is_knight_embedded(self, knight_id: str) -> bool:
        """Read-only check: does the local cache hold this knight's user+session?"""
        kid = normalize_knight_id(knight_id)
        cache = self._load_cache()
        return knight_user_id(kid) in cache.get("users", {}) and knight_session_id(kid) in cache.get("sessions", {})

    def ensure_knight(self, knight_id: str) -> Dict[str, Any]:
        """Embed Honcho in one knight: cache user+session (offline-safe) + tissue entry."""
        kid = normalize_knight_id(knight_id)
        user_id = knight_user_id(kid)
        session_id = knight_session_id(kid)
        self.get_or_create_user(user_id, {"role": "Round Table Knight", "knight_id": kid, "created_by": "HONCHO_EMBED"})
        self.get_or_create_session(session_id, user_id, {"knight_id": kid, "purpose": "L4_metamemory"})
        tissue_ok = self.sync_knight_tissue(kid)
        return {"knight_id": kid, "user_id": user_id, "session_id": session_id, "tissue_synced": tissue_ok}

    def sync_knight_tissue(self, knight_id: str, title: str = "", content: Optional[Dict[str, Any]] = None) -> bool:
        """Mirror a honcho_memory_engine artifact into the knight's open-notebook tissue (local only)."""
        try:
            _ensure_sys_path()
            from memory.cloudbrain_connector import CloudBrainConnector

            kid = normalize_knight_id(knight_id)
            body = content or {
                "engine": "honcho_self_hosted",
                "user_id": knight_user_id(kid),
                "session_id": knight_session_id(kid),
                "vfs_mount": "vfs://worldtree/memory/honcho/",
                "mode": "L4_metamemory",
            }
            cb = CloudBrainConnector(knight_id=kid)
            cb._sync_open_notebook_local(
                "honcho_memory_engine",
                title or ("Honcho L4 embedding for %s" % kid),
                json.dumps(body, indent=2) if isinstance(body, dict) else str(body),
            )
            return True
        except Exception as exc:  # noqa: BLE001
            log.debug("knight tissue sync failed for %s: %s", knight_id, exc)
            return False

    def sync_all_knights(self, knight_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Embed Honcho in every knight (defaults to the KNIGHT_NOTEBOOKS registry)."""
        targets = [normalize_knight_id(k) for k in knight_ids] if knight_ids else _all_registry_knights()
        results: Dict[str, Any] = {}
        for kid in targets:
            try:
                results[kid] = {"status": "EMBEDDED", **self.ensure_knight(kid)}
            except Exception as exc:  # noqa: BLE001
                results[kid] = {"status": "ERROR", "error": str(exc)}
        embedded = sum(1 for r in results.values() if r.get("status") == "EMBEDDED")
        tether_ok = self._sync_worldtree_tether(embedded, len(results))
        return {"status": "COMPLETE", "embedded": embedded, "total": len(results), "tether_synced": tether_ok, "knights": results}

    def _sync_worldtree_tether(self, embedded: int, total: int) -> bool:
        """Record the Honcho subsystem tether in WORLD_TREE tissue (local only)."""
        try:
            _ensure_sys_path()
            from memory.cloudbrain_connector import CloudBrainConnector

            cb = CloudBrainConnector(knight_id="WORLD_TREE")
            cb._sync_open_notebook_local(
                "subsystem_tether",
                "Honcho L4 subsystem tether",
                json.dumps(
                    {
                        "subsystem": "honcho_self_hosted",
                        "engine": "HonchoBridge",
                        "knights_embedded": embedded,
                        "knights_total": total,
                        "user_convention": "knight_<lowercase_id>",
                        "session_convention": "sess_knight_<lowercase_id>",
                        "vfs_mount": "vfs://worldtree/memory/honcho/",
                        "worldtree_home": "a0a4bfb9-e847-4c38-be39-7aee398f0795",
                    },
                    indent=2,
                ),
            )
            return True
        except Exception as exc:  # noqa: BLE001
            log.debug("worldtree tether sync failed: %s", exc)
            return False


class HonchoBridge(_HonchoBridgeBase, _HonchoKnightEmbedding):
    """
    HonchoBridge with per-knight L4 metamemory embedding for every Round Table knight.

    Method resolution: _HonchoBridgeBase (client/cache/HTTP) first, then
    _HonchoKnightEmbedding (ensure_knight / sync_all_knights / tissue sync).
    """


# Global singleton
honcho_bridge = HonchoBridge()
