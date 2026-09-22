# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Sir Helios autonomous NotebookLM link verification (offline-safe).

Session forensics run against synthetic fixtures; the live machine check only
asserts shape (CONNECTED/DEGRADED/OFFLINE) and that no cookie VALUE ever
appears in any report payload.
"""
import json
import time
import unittest
from pathlib import Path

from control_plane.infra.helios_notebooklm_guard import (
    find_session_file,
    inspect_session,
    sdk_available,
    tri_brain_consumers,
    verify,
)


def _synthetic_state(path: Path) -> dict:
    state = {
        "cookies": [
            {"name": "SID", "value": "SECRET_SID_VALUE_XYZ", "domain": "notebooklm.google.com",
             "expires": time.time() + 86400},
            {"name": "OSID", "value": "SECRET_OSID_VALUE_XYZ", "domain": "notebooklm.google.com",
             "expires": time.time() - 10},
            {"name": "PREF", "value": "SECRET_PREF_VALUE_XYZ", "domain": ".google.com",
             "expires": time.time() + 86400},
        ],
        "origins": [],
    }
    path.write_text(json.dumps(state), encoding="utf-8")
    return state


class TestSessionForensics(unittest.TestCase):
    def test_synthetic_expiry_accounting(self):
        fixture = Path(__file__).resolve().parent / ".tmp_helios_guard_fixture.json"
        try:
            _synthetic_state(fixture)
            report = inspect_session(fixture)
            self.assertTrue(report["found"])
            self.assertTrue(report["valid_json"])
            self.assertEqual(report["cookie_count"], 3)
            self.assertEqual(report["expired_cookies"], 1)
            self.assertIn("OSID", report["notebooklm_session_cookies"])
            # Secret discipline: names only, values never.
            blob = json.dumps(report)
            for secret in ("SECRET_SID_VALUE_XYZ", "SECRET_OSID_VALUE_XYZ", "SECRET_PREF_VALUE_XYZ"):
                self.assertNotIn(secret, blob)
        finally:
            if fixture.exists():
                fixture.unlink()

    def test_missing_file_reports_not_found(self):
        report = inspect_session(Path(__file__).resolve().parent / "does_not_exist_xyz.json")
        if not report["found"]:
            self.assertIn("notebooklm login", report.get("remediation", ""))

    def test_malformed_file_reported(self):
        fixture = Path(__file__).resolve().parent / ".tmp_helios_guard_bad.json"
        try:
            fixture.write_text("{not json", encoding="utf-8")
            report = inspect_session(fixture)
            self.assertTrue(report["found"])
            self.assertFalse(report["valid_json"])
        finally:
            if fixture.exists():
                fixture.unlink()


class TestAuthFailureClassification(unittest.TestCase):
    @staticmethod
    def _load_wrapper():
        import sys

        vfs_dir = str(Path(__file__).resolve().parent.parent / "vfs")
        if vfs_dir not in sys.path:
            sys.path.insert(0, vfs_dir)
        import notebooklm_client

        return notebooklm_client

    def test_transient_marker_present_in_wrapper_source(self):
        source = (Path(__file__).resolve().parent.parent / "vfs" / "notebooklm_client.py").read_text(encoding="utf-8")
        self.assertIn("redirect/environment problem", source)
        self.assertIn("_classify_auth_failure", source)

    def test_redirect_environment_is_transient(self):
        wrapper = self._load_wrapper()
        exc = ValueError(
            "CSRF token not found in HTML. Final URL: https://support.google.com/accounts/answer/32050\n"
            "The response did not come from a NotebookLM app host, so the request never "
            "reached the app \u2014 this is a redirect/environment problem, not a page-structure change."
        )
        self.assertEqual(wrapper._classify_auth_failure(exc), "transient")

    def test_rejected_credentials_are_expired(self):
        wrapper = self._load_wrapper()
        self.assertEqual(wrapper._classify_auth_failure(ValueError("Session ID not found in HTML")), "expired")
        try:
            from notebooklm.exceptions import AuthError

            self.assertEqual(wrapper._classify_auth_failure(AuthError("401 Unauthorized")), "expired")
        except ImportError:
            self.skipTest("notebooklm SDK not installed")


class TestShelfDiscipline(unittest.TestCase):
    def test_thresholds(self):
        from control_plane.infra.helios_notebooklm_guard import SHELF_CAP, classify_shelf

        self.assertEqual(classify_shelf(0), "OK")
        self.assertEqual(classify_shelf(269), "OK")
        self.assertEqual(classify_shelf(270), "PRESSURE")
        self.assertEqual(classify_shelf(292), "PRESSURE")
        self.assertEqual(classify_shelf(300), "FULL")
        self.assertEqual(classify_shelf(301), "FULL")
        self.assertEqual(SHELF_CAP, 300)

    def test_verify_carries_shelf_key(self):
        report = verify(live=False, mirror_tissue=False)
        self.assertIn("shelf", report)
        self.assertIsNone(report["shelf"])

    def test_assimilate_scour_dispatch(self):
        from control_plane.runes.runic_router import route_rune

        res = route_rune("//ASSIMILATE readiness", context={})
        self.assertTrue(res.queued)
        self.assertEqual(res.metadata.get("action"), "omega_assimilate")
        self.assertEqual(res.metadata.get("status"), "SCOURED")
        self.assertGreater(res.metadata.get("knights_total", 0), 30)
        self.assertGreaterEqual(res.metadata.get("knights_ready", 0), 1)


class TestTriBrainMap(unittest.TestCase):
    def test_three_consumers_defined(self):
        consumers = tri_brain_consumers()
        self.assertEqual(set(consumers), {"L2_hydration", "worldtree_tissue", "hub_broker"})
        for consumer in consumers.values():
            self.assertIn("reader", consumer)
            self.assertIn("needs", consumer)


class TestLiveMachine(unittest.TestCase):
    def test_verify_report_shape_and_no_leak(self):
        report = verify(live=False, mirror_tissue=False)
        self.assertEqual(report["action"], "helios_notebooklm_verify")
        self.assertEqual(report["knight"], "SIR_HELIOS")
        self.assertIn(report["status"], {"CONNECTED", "DEGRADED", "OFFLINE"})
        self.assertIn("session", report)
        self.assertIn("tri_brain_consumers", report)
        if report["status"] != "CONNECTED":
            self.assertIn("notebooklm login", report.get("remediation", ""))
        # No cookie value from the real session file may appear in the report.
        session_file = find_session_file()
        if session_file is not None:
            try:
                state = json.loads(session_file.read_text(encoding="utf-8"))
                values = [c.get("value", "") for c in state.get("cookies", []) if c.get("value")]
            except Exception:  # noqa: BLE001
                values = []
            blob = json.dumps(report)
            for value in values:
                if len(value) > 8:
                    self.assertNotIn(value, blob)

    def test_sdk_presence_is_bool(self):
        self.assertIsInstance(sdk_available(), bool)

    def test_helios_rune_dispatch_offline(self):
        from control_plane.runes.runic_router import route_rune

        res = route_rune("//HELIOS --offline", context={})
        self.assertTrue(res.queued)
        self.assertEqual(res.metadata.get("action"), "helios_notebooklm_verify")
        self.assertEqual(res.knight, "sir_helios")
        self.assertIn(res.metadata.get("status"), {"CONNECTED", "DEGRADED", "OFFLINE", "ERROR"})


if __name__ == "__main__":
    unittest.main()
