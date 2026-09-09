# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import hashlib
import hmac
import json
import pytest
from control_plane.infra.vps_github_webhook import CamelotVPSWebhookHandler


def test_webhook_hmac_verification_and_deploy(tmp_path):
    secret = "test_webhook_secret_123"
    handler = CamelotVPSWebhookHandler(secret=secret, state_dir=tmp_path)

    payload = {
        "ref": "refs/heads/main",
        "after": "2219bbf9245f4a0749e92f875055fc9a0ad9c4b2",
        "repository": {
            "full_name": "Cyberdad247/Camelot-VPS",
            "html_url": "https://github.com/Cyberdad247/Camelot-VPS.git"
        }
    }
    payload_bytes = json.dumps(payload).encode("utf-8")

    # Generate valid signature
    valid_sig = "sha256=" + hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

    # 1. Process valid event
    receipt = handler.process_github_event(payload_bytes, valid_sig, event_type="push")
    assert receipt.verified is True
    assert receipt.build_status == "DEPLOYED"
    assert receipt.repository == "Cyberdad247/Camelot-VPS"
    assert receipt.commit_sha == "2219bbf9245f4a0749e92f875055fc9a0ad9c4b2"

    # 2. Process invalid signature (tampered)
    invalid_sig = "sha256=0000000000000000000000000000000000000000000000000000000000000000"
    bad_receipt = handler.process_github_event(payload_bytes, invalid_sig, event_type="push")
    assert bad_receipt.verified is False
    assert bad_receipt.build_status == "UNAUTHORIZED"
