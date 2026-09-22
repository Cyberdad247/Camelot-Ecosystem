# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Unit tests for the Cybertronia VPS hub bridge (offline-safe; no network).
"""
import hashlib
import json
import unittest

from control_plane.infra.vps_hub_client import (
    CONTRACTS_DIR,
    ENDPOINTS,
    build_context_packet,
    build_receipt_draft,
    cloudbrain_lease_scope,
    contract_inventory,
    hub_status,
    validate_artifact,
)


def _blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


class TestVpsHubContracts(unittest.TestCase):
    def test_manifest_pins_match_files(self):
        manifest = json.loads((CONTRACTS_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["source_repo"], "Cyberdad247/Camelot-VPS")
        self.assertEqual(manifest["branch"], "main")
        self.assertGreaterEqual(manifest["contract_count"], 11)
        for name, pin in manifest["files"].items():
            data = (CONTRACTS_DIR / name).read_bytes()
            self.assertEqual(_blob_sha(data), pin["blob_sha"], "contract drift: %s" % name)

    def test_inventory(self):
        inv = contract_inventory()
        self.assertEqual(inv["status"], "VENDORED")
        self.assertGreaterEqual(inv["contract_count"], 11)
        self.assertIn("receipt.schema.json", inv["schemas"])
        self.assertIn("context-packet.schema.json", inv["schemas"])


class TestVpsHubValidation(unittest.TestCase):
    def test_receipt_draft_validates(self):
        draft = build_receipt_draft(
            tenant_id="tenant_demo",
            workspace_id="workspace_demo",
            mission_id="mission_demo",
            task_id="task_demo",
            actor_id="hermes_prime",
            action_type="cloudbrain.retrieve",
            resource_uri="cloudbrain://notebooklm/workspace_demo/HERMES_PRIME",
        )
        result = validate_artifact("receipt", draft)
        self.assertTrue(result["ok"], "errors: %s" % result["errors"])

    def test_receipt_missing_field_fails(self):
        draft = build_receipt_draft(
            tenant_id="tenant_demo",
            workspace_id="workspace_demo",
            mission_id="mission_demo",
            task_id="task_demo",
            actor_id="hermes_prime",
            action_type="cloudbrain.retrieve",
            resource_uri="cloudbrain://notebooklm/workspace_demo/HERMES_PRIME",
        )
        del draft["signature"]
        result = validate_artifact("receipt", draft)
        self.assertFalse(result["ok"])
        self.assertTrue(result["errors"])

    def test_context_packet_validates_with_actor_ref(self):
        packet = build_context_packet(
            tenant_id="tenant_demo",
            task_id="task_demo",
            retrieval_lease_id="rl_demo123",
            sections=[{"kind": "l2_evidence", "content_ref": "notebooklm://HERMES_PRIME/note/1", "tokens": 120}],
        )
        result = validate_artifact("context-packet", packet)
        self.assertTrue(result["ok"], "errors: %s" % result["errors"])

    def test_unknown_schema_fails_closed(self):
        result = validate_artifact("nope", {})
        self.assertFalse(result["ok"])


class TestVpsHubBridge(unittest.TestCase):
    def test_lease_scope_format(self):
        self.assertEqual(
            cloudbrain_lease_scope("ws1", "HERMES_PRIME"),
            "cloudbrain://notebooklm/ws1/HERMES_PRIME",
        )

    def test_endpoint_table_ports(self):
        self.assertEqual(ENDPOINTS["receipt"]["port"], 3001)
        self.assertEqual(ENDPOINTS["state"]["port"], 3012)
        self.assertEqual(ENDPOINTS["epoch"]["port"], 3014)
        self.assertEqual(ENDPOINTS["cloudbrain"]["port"], 3015)

    def test_status_offline_by_default(self):
        status = hub_status()
        self.assertEqual(status["status"], "OK")
        self.assertEqual(status["mode"], "OFFLINE")
        self.assertEqual(status["live_probes"], [])
        self.assertIn("sentinel -> excalibur -> gideon -> arthur -> ledger", status["hub"]["authority_chain"])
        self.assertGreater(status["cloudbrain"]["knight_nodes"], 30)


if __name__ == "__main__":
    unittest.main()
