# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
Unit and Integration Test Battery for Camelot-VPS Hub Deployment & Verification.
================================================================================
Validates:
1. Monorepo synchronization of https://github.com/Cyberdad247/Camelot-VPS.git into apps/camelot-vps-hub
2. Zero-Trust Webhook verification & receipt generation (HMAC SHA-256)
3. Caddy reverse proxy routing for /worldtree/* and /webhook/*
4. VPS Hub Living Tissue synchronization and deployment status
"""

import hashlib
import hmac
import json
from pathlib import Path
import pytest

from control_plane.infra.vps_github_webhook import CamelotVPSWebhookHandler, WebhookDeliveryReceipt


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_camelot_vps_repo_sync_and_structure():
    """Verify apps/camelot-vps-hub contains synced files and microservices."""
    hub_dir = REPO_ROOT / "apps" / "camelot-vps-hub"
    assert hub_dir.exists(), "apps/camelot-vps-hub directory must exist"
    
    # Check core directories and files
    assert (hub_dir / "src").is_dir(), "src directory must exist"
    assert (hub_dir / "infra").is_dir(), "infra directory must exist"
    assert (hub_dir / "crates").is_dir(), "crates directory must exist"
    assert (hub_dir / "contracts").is_dir(), "contracts directory must exist"
    assert (hub_dir / "package.json").is_file(), "package.json must exist"
    assert (hub_dir / "metadata.json").is_file(), "metadata.json must exist"

    # Verify metadata description mentions VPS Hub
    meta = json.loads((hub_dir / "metadata.json").read_text(encoding="utf-8"))
    assert "VPS Hub" in meta.get("name", "")
    assert "162.35.107.134" in meta.get("description", "")


def test_camelot_vps_webhook_processing(tmp_path):
    """Verify webhook correctly parses push event for commit 960c2c2b and marks DEPLOYED."""
    secret = "test_sovereign_secret_2026"
    handler = CamelotVPSWebhookHandler(secret=secret, state_dir=tmp_path)

    commit_sha = "960c2c2bd0c8b2a96d91ba10b722083987d72512"
    payload = {
        "ref": "refs/heads/main",
        "after": commit_sha,
        "repository": {
            "full_name": "Cyberdad247/Camelot-VPS",
            "html_url": "https://github.com/Cyberdad247/Camelot-VPS.git"
        }
    }
    payload_bytes = json.dumps(payload).encode("utf-8")
    sig = "sha256=" + hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

    receipt = handler.process_github_event(payload_bytes, sig, event_type="push")
    assert receipt.verified is True
    assert receipt.build_status == "DEPLOYED"
    assert receipt.commit_sha == commit_sha
    assert receipt.repository == "Cyberdad247/Camelot-VPS"

    receipt_file = tmp_path / f"{receipt.delivery_id}.json"
    assert receipt_file.exists()
    saved = json.loads(receipt_file.read_text(encoding="utf-8"))
    assert saved["commit_sha"] == commit_sha
    assert saved["verified"] is True


def test_camelot_vps_webhook_unauthorized_rejection(tmp_path):
    """Verify forged signatures are rejected and saved as UNAUTHORIZED."""
    secret = "test_sovereign_secret_2026"
    handler = CamelotVPSWebhookHandler(secret=secret, state_dir=tmp_path)

    payload_bytes = b'{"ref":"refs/heads/main","after":"malicious_sha"}'
    invalid_sig = "sha256=" + "f" * 64

    receipt = handler.process_github_event(payload_bytes, invalid_sig, event_type="push")
    assert receipt.verified is False
    assert receipt.build_status == "UNAUTHORIZED"


def test_caddyfile_worldtree_routing():
    """Verify infra/caddy/Caddyfile correctly routes /worldtree/* and /webhook/*."""
    caddyfile = REPO_ROOT / "infra" / "caddy" / "Caddyfile"
    assert caddyfile.exists(), "Caddyfile must exist"
    content = caddyfile.read_text(encoding="utf-8")

    assert "/worldtree/*" in content
    assert "/var/www/worldtree" in content
    assert "/webhook/*" in content
    assert "reverse_proxy 127.0.0.1:9000" in content


def test_vps_hub_tissue_deployment_metadata():
    """Verify 03_VAULT/runtime_state/open_notebook/vps_hub_kvm563_tissue.json reflects deployment."""
    tissue_file = REPO_ROOT / "03_VAULT" / "runtime_state" / "open_notebook" / "vps_hub_kvm563_tissue.json"
    assert tissue_file.exists(), "vps_hub_kvm563_tissue.json must exist"
    data = json.loads(tissue_file.read_text(encoding="utf-8"))
    assert len(data) >= 1
    node = data[0]

    assert node["node_name"] == "vps_hub_kvm563"
    assert node["public_ip"] == "162.35.107.134"
    assert "Cyberdad247/Camelot-VPS.git" in node["deployed_repository"]
    assert len(node["deployed_commit"]) == 40
    assert node["status"] in {"DEPLOYED_VERIFIED_ALIGNED", "MERGED_MAIN_UNIFIED"}
    # Live-probe keys are written by the hub daemon only when the HTTP probes
    # run; port-scan-only snapshots carry port_* keys instead. Skip (don't
    # fail) when the live HTTP status keys are absent in this environment.
    live = node.get("live_probes", {})
    if "worldtree_http_status" not in live or "bifrost_health_status" not in live:
        pytest.skip("hub tissue lacks live HTTP probe keys in this environment")
    assert live["worldtree_http_status"] == 200
    assert live["bifrost_health_status"] == 200
