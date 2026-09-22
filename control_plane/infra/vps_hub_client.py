# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""Cybertronia VPS hub bridge — CloudBrain <-> authority-plane integration.

The Camelot-VPS hub (Cyberdad247/Camelot-VPS, ``main``) is the active control,
trust, evidence, and coordination plane: Sentinel -> Excalibur -> Gideon ->
Arthur -> Ledger. This module is the CAMELOT_OS-side bridge to it:

- **Endpoint table** for every hub service (ports from the hub ``.env.example``).
- **Vendored hub contracts** (``control_plane/dispatch/vps_hub_contracts/``,
  pinned by git blob SHA in ``MANIFEST.json``) with offline validation.
- **Builders** for hub-shaped artifacts: context packets
  (``camelot-context-packet/1``), receipt drafts (``receipt/2``), and
  CloudBrain lease scopes (``cloudbrain://notebooklm/<workspace>/<notebook>``).

Offline-safe by default. Live TCP contact with the hub happens only when
``live=True`` (``--live``). Draft builders emit clearly-marked LOCAL DRAFT
artifacts with zeroed hashes/signatures: structurally valid, never
submittable — the hub verifies Ed25519 and the hash chain itself.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from control_plane.infra.mesh_topology import HUB_PUBLIC_IP, HUB_TAILSCALE_IP
except Exception:  # noqa: BLE001 — standalone fallback, never hard-fail import
    HUB_TAILSCALE_IP = "100.110.180.18"
    HUB_PUBLIC_IP = "162.35.107.134"

_CAMELOT_ROOT = Path(__file__).resolve().parent.parent.parent
CONTRACTS_DIR = _CAMELOT_ROOT / "control_plane" / "dispatch" / "vps_hub_contracts"
MANIFEST_PATH = CONTRACTS_DIR / "MANIFEST.json"

HUB_SOURCE_REPO = "Cyberdad247/Camelot-VPS"
HUB_SOURCE_BRANCH = "main"

# Service -> hub port + purpose. Ports from the hub `.env.example` (main).
# All hub services bind loopback on the hub itself; from the mesh they are
# reached over the tailnet address (never the public WAN for mesh traffic).
ENDPOINTS: Dict[str, Dict[str, Any]] = {
    "bifrost": {"port": 3000, "purpose": "Go transport admission (signed bifrost/1 envelopes; admission is not authority)"},
    "receipt": {"port": 3001, "purpose": "Signed receipt ledger (append-only hash chain)"},
    "vfs": {"port": 3003, "purpose": "VFS Guardian preflight + signed vfs-attestation"},
    "node-agent": {"port": 3010, "purpose": "Governed Wasmtime executor (lease + attestation required)"},
    "gideon": {"port": 3011, "purpose": "Evidence verifier (PASS/FAIL/INCONCLUSIVE/QUARANTINE, formalProof=false)"},
    "state": {"port": 3012, "purpose": "Authoritative workspace state spine (RECEIPTED checked vs ledger)"},
    "arthur": {"port": 3013, "purpose": "Final completion/promotion resolution (no effect execution)"},
    "epoch": {"port": 3014, "purpose": "Twin-Brain authority-epoch fencer + signed epoch certificates"},
    "cloudbrain": {"port": 3015, "purpose": "CloudBrain retrieval broker (cloudbrain:retrieve lease required)"},
    "notebooklm-mcp": {"port": 8484, "purpose": "NotebookLM MCP sidecar (loopback-only, non-authority provider)"},
    "shadow": {"port": 4190, "purpose": "Shadow Subspace executor (server-side bearer token, fail-closed R6)"},
}

ZERO_SHA256 = "sha256:" + "0" * 64
ZERO_ED25519_SIG = "ed25519:" + "0" * 128
ZERO_PUBKEY = "0" * 64


# ── Contracts ────────────────────────────────────────────────────────────────

def contract_inventory() -> Dict[str, Any]:
    """Vendored hub contract schemas + pin manifest (offline)."""
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"status": "ERROR", "error": "MANIFEST.json unreadable: %s" % exc}
    schemas = sorted(p.name for p in CONTRACTS_DIR.glob("*.schema.json"))
    return {
        "status": "VENDORED",
        "source_repo": manifest.get("source_repo", HUB_SOURCE_REPO),
        "branch": manifest.get("branch", HUB_SOURCE_BRANCH),
        "fetched_at": manifest.get("fetched_at"),
        "contract_count": len(schemas),
        "schemas": schemas,
        "pins": manifest.get("files", {}),
    }


def _load_schema(schema_name: str) -> Dict[str, Any]:
    filename = schema_name if schema_name.endswith(".schema.json") else schema_name + ".schema.json"
    path = CONTRACTS_DIR / filename
    if not path.is_file():
        raise ValueError("unknown hub contract: %s (vendored: %s)" % (schema_name, sorted(p.name for p in CONTRACTS_DIR.glob("*.schema.json"))))
    return json.loads(path.read_text(encoding="utf-8"))


def _validator_for(schema: Dict[str, Any]):
    """Draft 2020-12 validator with an offline registry built from vendored $ids.

    Resolves the hub's remote `$ref`s (e.g. context-packet -> actor) and
    relative `$ref`s (wasm-execution -> ./vfs-attestation) without network.
    Fail-closed: unresolvable refs raise instead of passing.
    """
    import jsonschema
    from referencing import Registry, Resource
    import referencing.jsonschema

    resources: List[Tuple[str, Any]] = []
    for path in CONTRACTS_DIR.glob("*.schema.json"):
        try:
            contents = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        schema_id = contents.get("$id")
        if not schema_id:
            continue
        resources.append(
            (schema_id, Resource(contents=contents, specification=referencing.jsonschema.DRAFT202012))
        )
    registry = Registry().with_resources(resources)
    validator_cls = jsonschema.validators.validator_for(schema)
    return validator_cls(schema, registry=registry, format_checker=jsonschema.FormatChecker())


def validate_artifact(schema_name: str, artifact: Dict[str, Any]) -> Dict[str, Any]:
    """Validate an artifact dict against a vendored hub contract (offline)."""
    try:
        schema = _load_schema(schema_name)
    except ValueError as exc:
        return {"ok": False, "schema": schema_name, "errors": [str(exc)]}
    try:
        validator = _validator_for(schema)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "schema": schema_name, "errors": ["validator build failed: %s" % exc]}
    errors = sorted(validator.iter_errors(artifact), key=lambda e: list(e.path))
    return {
        "ok": not errors,
        "schema": schema.get("$id", schema_name),
        "errors": ["%s: %s" % ("/".join(str(p) for p in e.path) or "<root>", e.message) for e in errors],
    }


# ── Builders (LOCAL DRAFT artifacts — structurally valid, never submittable) ──

def cloudbrain_lease_scope(workspace: str, notebook: str) -> str:
    """Hub CloudBrain retrieval lease scope: cloudbrain://notebooklm/<workspace>/<notebook>."""
    return "cloudbrain://notebooklm/%s/%s" % (workspace, notebook)


def build_context_packet(
    tenant_id: str,
    task_id: str,
    retrieval_lease_id: str,
    sections: List[Dict[str, Any]],
    compiled_by_actor_id: str = "hermes_prime",
    correlation_id: Optional[str] = None,
    packet_id: Optional[str] = None,
    hard_max_tokens: int = 8192,
    signature: str = ZERO_ED25519_SIG,
) -> Dict[str, Any]:
    """Draft ``camelot-context-packet/1`` packet (LOCAL DRAFT, unsigned).

    NotebookLM content travels as ``l2_evidence`` sections: evidence, never
    authority — the hub compiler, not this builder, decides what is trusted.
    """
    total = sum(int(s.get("tokens", 0)) for s in sections)
    return {
        "schema_version": "camelot-context-packet/1",
        "packet_id": packet_id or ("pkt_%s" % uuid.uuid4().hex[:12]),
        "tenant_id": tenant_id,
        "correlation_id": correlation_id or ("cor_%s" % uuid.uuid4().hex[:12]),
        "task_id": task_id,
        "retrieval_lease_id": retrieval_lease_id,
        "compiled_by": {"id": compiled_by_actor_id, "role": "context_compiler"},
        "sections": sections,
        "total_input_tokens": total,
        "hard_max_tokens": hard_max_tokens,
        "signature": signature,
    }


def build_receipt_draft(
    tenant_id: str,
    workspace_id: str,
    mission_id: str,
    task_id: str,
    actor_id: str,
    action_type: str,
    resource_uri: str,
    authority_epoch: int = 1,
    sequence: int = 0,
    receipt_id: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Draft ``receipt/2`` receipt (LOCAL DRAFT — zeroed hashes/signature)."""
    return {
        "schemaVersion": "receipt/2",
        "receiptId": receipt_id or str(uuid.uuid4()),
        "sequence": sequence,
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        "tenantId": tenant_id,
        "workspaceId": workspace_id,
        "missionId": mission_id,
        "taskId": task_id,
        "actorId": actor_id,
        "actionType": action_type,
        "resourceUri": resource_uri,
        "manifestHash": ZERO_SHA256,
        "capabilityLeaseId": None,
        "approvalId": None,
        "vfsAttestationId": None,
        "gideonVerdictId": None,
        "arthurResolutionId": None,
        "resultHash": ZERO_SHA256,
        "authorityEpoch": authority_epoch,
        "parentReceiptHash": None,
        "receiptHash": ZERO_SHA256,
        "signerPublicKey": ZERO_PUBKEY,
        "signature": ZERO_ED25519_SIG,
    }


# ── Status ───────────────────────────────────────────────────────────────────

def _tcp_probe(host: str, port: int, timeout: float = 2.0) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def hub_status(live: bool = False) -> Dict[str, Any]:
    """Hub bridge status. Offline by default; TCP probes only when live=True."""
    inventory = contract_inventory()
    for _extra_path in (_CAMELOT_ROOT, _CAMELOT_ROOT / "01_KERNEL"):
        if str(_extra_path) not in sys.path:
            sys.path.insert(0, str(_extra_path))
    try:
        from memory.cloudbrain_connector import KNIGHT_NOTEBOOKS
        knight_nodes = len(KNIGHT_NOTEBOOKS)
    except Exception as exc:  # noqa: BLE001
        KNIGHT_NOTEBOOKS = {}
        knight_nodes = 0
        cloudbrain_error = str(exc)
    else:
        cloudbrain_error = ""
    endpoints = [
        {"service": name, "host": HUB_TAILSCALE_IP, "port": spec["port"], "purpose": spec["purpose"]}
        for name, spec in ENDPOINTS.items()
    ]
    probes: List[Dict[str, Any]] = []
    if live:
        for entry in endpoints:
            is_open = _tcp_probe(entry["host"], entry["port"])
            probes.append({"service": entry["service"], "port": entry["port"], "open": is_open})
    return {
        "action": "vps_hub_status",
        "status": "OK",
        "mode": "LIVE" if live else "OFFLINE",
        "hub": {
            "node": "cybertronia",
            "tailscale_ip": HUB_TAILSCALE_IP,
            "public_ip": HUB_PUBLIC_IP,
            "source_repo": HUB_SOURCE_REPO,
            "authority_chain": "sentinel -> excalibur -> gideon -> arthur -> ledger",
        },
        "contracts": inventory,
        "endpoints": endpoints,
        "live_probes": probes,
        "cloudbrain": {
            "knight_nodes": knight_nodes,
            "lease_scope_format": "cloudbrain://notebooklm/<workspace>/<notebook>",
            "error": cloudbrain_error,
        },
    }


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Cybertronia VPS hub bridge (offline-safe; --live opts into TCP probes)")
    parser.add_argument("--status", action="store_true", help="Print hub bridge status as JSON")
    parser.add_argument("--live", action="store_true", help="Probe hub TCP ports (default: offline)")
    parser.add_argument("--validate", nargs=2, metavar=("SCHEMA", "FILE"), help="Validate a JSON file against a vendored hub contract")
    parser.add_argument("--lease-scope", nargs=2, metavar=("WORKSPACE", "NOTEBOOK"), help="Print a CloudBrain lease scope URI")
    args = parser.parse_args(argv)
    if args.validate:
        schema_name, file_path = args.validate
        try:
            artifact = json.loads(Path(file_path).read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"ok": False, "schema": schema_name, "errors": ["unreadable file: %s" % exc]}, indent=2))
            return 2
        result = validate_artifact(schema_name, artifact)
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1
    if args.lease_scope:
        print(cloudbrain_lease_scope(args.lease_scope[0], args.lease_scope[1]))
        return 0
    result = hub_status(live=args.live)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
