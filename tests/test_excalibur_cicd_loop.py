# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Unit tests for Excalibur Autonomous CI/CD & WorldTree Loop runner.
"""
import unittest

from control_plane.runners.excalibur_cicd_loop import (
    ExcaliburAutonomousLoop,
    load_schedule_state,
)


class TestExcaliburCICDLoop(unittest.TestCase):
    def setUp(self):
        self.loop = ExcaliburAutonomousLoop()

    def test_load_and_save_schedule_state(self):
        state = load_schedule_state()
        self.assertTrue(state.active_version)
        self.assertIsNotNone(state.next_daily_run_utc)
        self.assertIsNotNone(state.next_quarterly_run_utc)

    def test_status_report_structure(self):
        status = self.loop.get_status_report()
        self.assertEqual(status["loop_name"], "Excalibur_Autonomous_CICD_WorldTree_Sync")
        self.assertIn("active_version", status)
        self.assertIn("next_daily_run", status)
        self.assertIn("next_quarterly_run", status)
        self.assertIn("total_daily_cycles", status)
        self.assertIn("active_snapshots", status)

    def test_run_daily_cycle(self):
        res = self.loop.run_daily_cycle()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["cadence"], "DAILY")
        self.assertTrue(res["snapshot_id"].startswith("excalibur_cicd_"))
        self.assertGreater(res["tethered_knights"], 0)

    def test_markdown_log_generation(self):
        from control_plane.runners.excalibur_cicd_loop import LOG_MD_PATH, DOCS_LOG_MD_PATH, LOGS_LOG_MD_PATH
        self.assertTrue(LOG_MD_PATH.exists())
        self.assertTrue(DOCS_LOG_MD_PATH.exists())
        self.assertTrue(LOGS_LOG_MD_PATH.exists())
        content = LOG_MD_PATH.read_text(encoding="utf-8")
        self.assertIn("Excalibur Command Center — Autonomous CI/CD & Cron Telemetry Log", content)
        self.assertIn("Autonomous Execution Telemetry & Analysis", content)
        self.assertIn("v1000.54-EXCALIBUR-A", content)


if __name__ == "__main__":
    unittest.main()
