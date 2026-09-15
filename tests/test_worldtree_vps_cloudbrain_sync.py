# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Unit tests for WorldTree CloudBrain & VPS Hub Sync Engine.
"""
import json
import unittest

from control_plane.runners.worldtree_vps_cloudbrain_sync import (
    WorldTreeCloudBrainVPSSync,
    WORLDTREE_HOME_ID,
    HERMES_PRIME_UUID,
    MAX_VERSION,
    OPEN_NOTEBOOK_DIR,
)


class TestWorldTreeCloudBrainVPSSync(unittest.TestCase):
    def setUp(self):
        self.engine = WorldTreeCloudBrainVPSSync()

    def test_sync_vps_hub_to_worldtree(self):
        res = self.engine.sync_vps_hub_to_worldtree()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["worldtree_home"], WORLDTREE_HOME_ID)
        self.assertEqual(res["hermes_prime_node"], HERMES_PRIME_UUID)
        self.assertEqual(res["version"], MAX_VERSION)
        self.assertGreaterEqual(res["tethered_knights"], 36)

        tissue_file = OPEN_NOTEBOOK_DIR / "vps_hub_kvm563_tissue.json"
        self.assertTrue(tissue_file.exists())
        data = json.loads(tissue_file.read_text(encoding="utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(data[0]["host_server"], "KVM563")
        self.assertEqual(data[0]["assigned_knight"], "HERMES_PRIME")
        vps_tailscale_ip = data[0]["tailscale_ip"]
        cliproxy_link = data[0]["inference_links"]["cliproxy_sie"]
        self.assertEqual(cliproxy_link["selector"], "cliproxy:default")
        self.assertEqual(cliproxy_link["governing_knight"], "HERMES_PRIME")
        self.assertEqual(cliproxy_link["vps_node"], "vps_hub_kvm563")
        bifrost_bridge = cliproxy_link["bifrost_bridge"]
        self.assertEqual(bifrost_bridge["module"], "control_plane/dispatch/bifrost.py")
        self.assertEqual(bifrost_bridge["gateway_url"], f"http://{vps_tailscale_ip}:3001")
        self.assertEqual(bifrost_bridge["mesh_bridge_url"], f"http://{vps_tailscale_ip}:8095")
        self.assertEqual(bifrost_bridge["co_governors"], ["HERMES_PRIME", "SIR_HEIMDALL"])
        self.assertFalse(bifrost_bridge["auth"]["secret_values_serialized"])
        self.assertFalse(cliproxy_link["secret_values_serialized"])


if __name__ == "__main__":
    unittest.main()
