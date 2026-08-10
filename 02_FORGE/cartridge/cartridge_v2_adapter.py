# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Cartridge V1 -> V2 Adapter
==========================

Bridges the existing V1 cockpit cartridges (the seven React cartridges in
``02_FORGE/apps/pwa-cockpit/src/cartridges/``) into the V2 runtime hydrator
without re-bundling or re-signing.

The seven V1 cartridges are statically imported by
``src/cartridges/registry.tsx`` and are NOT packaged as ``.cartridge`` archives.
The runtime hydrator in ``src/lib/v2/cartridge-platform.ts`` therefore needs
a way to mount a V1 cartridge through the same V2 API as a fresh archive
without breaking the architecture test that requires the V1 trusted dynamic
catalog to stay intact.

The bridge strategy
-------------------
1. At Python registration time (e.g. in a deploy script or in the
   fabrication_engine), the operator calls ``upgrade_v1_manifest(v1)`` to
   produce a V2 CartridgeManifestV2. The V2 fields are filled with safe
   defaults:
     - ``hostApiVersion`` = ``V1_HOST_API_VERSION`` ("1")
     - ``publisher_id``   = "legacy-v1"
     - ``entry``          = the path the V1 trusted loader uses
     - ``sha256``         = ``V1_LEGACY_SHA256`` magic constant
     - ``routes``         = derived from the V1 ``id`` ("/cartridges/<id>")
     - ``resourceBudget`` = mirror of the V1 ``resource_budget``

2. At runtime, the browser hydrator recognises ``sha256 == V1_LEGACY_SHA256``
   and short-circuits the archive-verification path. The V1 cartridge props
   come from the existing V1 registry (``manifestFor``), and the V2 hydrator
   adapts them into a ``CartridgeManifestV2`` shape for the cockpit UI.

The signature from V1 is preserved unchanged. Because the V2 schema is a
superset of V1, ``CartridgeManifestV2.model_validate(v1_dict_with_v2_defaults)``
produces a valid V2 manifest that round-trips through
``cartridge_crypto.canonical_bytes`` and re-signs cleanly when the operator
upgrades to a real archive.
"""
from __future__ import annotations

from typing import Union

from .cartridge_schemas import (
    V1_HOST_API_VERSION,
    V1_LEGACY_SHA256,
    CartridgeManifest,
    CartridgeManifestV2,
    V2ResourceBudget,
    V2RouteEntry,
)


# Path conventions for the V1 trusted dynamic catalog. Mirrors
# `src/cartridges/registry.tsx` so the runtime hydrator can find the source
# without a separate index. The cockpit runtime trusts the static
# `trustedLoaders` map at this exact path; V1 cartridges do not have a
# variable entry path.
def _v1_entry_path(cartridge_id: str) -> str:
    return f"src/cartridges/{cartridge_id}/{cartridge_id}-cartridge.tsx"


def _v1_route(cartridge_id: str) -> V2RouteEntry:
    return V2RouteEntry(
        mount=f"/cartridges/{cartridge_id}",
        component=f"./{cartridge_id}-cartridge",
        prefetch=[],
    )


def _v1_resource_budget(v1: CartridgeManifest) -> V2ResourceBudget:
    return V2ResourceBudget(
        maxTokens=v1.resource_budget.max_tokens,
        maxMemoryMb=v1.resource_budget.max_memory_mb,
        maxLatencyMs=v1.resource_budget.max_latency_ms,
    )


def upgrade_v1_manifest(
    v1: Union[CartridgeManifest, dict],
    *,
    publisher_id: str = "legacy-v1",
) -> CartridgeManifestV2:
    """
    Build a V2 CartridgeManifestV2 from a V1 CartridgeManifest (or V1 dict).

    The result is a valid V2 manifest with:
      - Every V1 field preserved exactly (CartridgeManifestV2 inherits V1).
      - ``hostApiVersion`` = "1" so the runtime treats it as a legacy import.
      - ``publisher_id``   = "legacy-v1" (override for production publishers).
      - ``entry``          = the V1 trusted loader path.
      - ``sha256``         = V1_LEGACY_SHA256 (the magic constant).
      - ``routes``         = [ { mount: "/cartridges/<id>", component: "./<id>-cartridge" } ].
      - ``resourceBudget`` = camelCase mirror of the V1 ``resource_budget``.

    Raises ``ValueError`` if the V1 cartridge_id is missing (V1 mandates it).
    """
    if isinstance(v1, dict):
        v1_dict = v1
    else:
        v1_dict = v1.model_dump(mode="json")
    cartridge_id = v1_dict.get("cartridge_id")
    if not cartridge_id:
        raise ValueError("V1 manifest is missing required field 'cartridge_id'")

    # Build the V2-only fields.
    v2_only = {
        "hostApiVersion": V1_HOST_API_VERSION,
        "publisher_id": publisher_id,
        "entry": _v1_entry_path(cartridge_id),
        "sha256": V1_LEGACY_SHA256,
        "routes": [_v1_route(cartridge_id).model_dump(mode="json")],
    }

    # resourceBudget needs to mirror resource_budget.
    rb = v1_dict.get("resource_budget") or {}
    v2_only["resourceBudget"] = {
        "maxTokens": rb.get("max_tokens", 25000),
        "maxMemoryMb": rb.get("max_memory_mb", 512),
        "maxLatencyMs": rb.get("max_latency_ms", 600),
    }

    merged = {**v1_dict, **v2_only}
    return CartridgeManifestV2.model_validate(merged)


def is_legacy_v1(manifest: CartridgeManifestV2) -> bool:
    """True when this V2 manifest is a thin shim around a V1 cartridge."""
    return manifest.sha256 == V1_LEGACY_SHA256
