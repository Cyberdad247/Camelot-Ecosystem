import unittest
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path("C:/Users/vizio/CAMELOT_OS")
sys.path.insert(0, str(PROJECT_ROOT))

import importlib.util
spec = importlib.util.spec_from_file_location("forensic_engine", str(PROJECT_ROOT / "01_KERNEL/iron_gate/forensic_engine.py"))
forensic_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(forensic_engine)
ForensicEngine = forensic_engine.ForensicEngine

class TestForensics(unittest.TestCase):
    def setUp(self):
        self.ledger_path = PROJECT_ROOT / "TEST_LEDGER.md"
        # Create a mock ledger with a specific "Scar"
        with open(self.ledger_path, "w", encoding="utf-8") as f:
            f.write("# 📖 TEST PROVENANCE LEDGER\n")
            f.write("| ID | Task Name | Author | Status | Notes |\n")
            f.write("| 001 | **Security Patch** | Sentinel | ✅ VERIFIED | Next.js RCE (CVE-2025-66478) patched. |\n")
            f.write("| 002 | **Failed Task** | LADY_M | ❌ FAILED | Module system/core.py crashed during deploy. |\n")
        
        self.engine = ForensicEngine(ledger_path=str(self.ledger_path))

    def tearDown(self):
        if self.ledger_path.exists():
            os.remove(self.ledger_path)

    def test_scar_indexing(self):
        """Verifies that the engine indexes scars correctly."""
        self.assertGreater(len(self.engine.scars), 0, "Should have indexed at least one scar.")
        self.assertTrue(any("RCE" in scar for scar in self.engine.scars))
        self.assertTrue(any("FAILED" in scar for scar in self.engine.scars))

    def test_analyze_impact_high_risk(self):
        """Verifies that a high risk score is returned for critical historical failures."""
        # Test context that should trigger the RCE scar
        impact = self.engine.analyze_impact("nextjs/app.py", "Deploy application")
        print(f"DEBUG: impact={impact}")
        print(f"DEBUG: scars={self.engine.scars}")
        self.assertGreaterEqual(impact["risk_score"], 0.8, "RCE should trigger high risk score.")
        self.assertTrue(any("RCE" in alert for alert in impact["alerts"]))

    def test_analyze_impact_remediation(self):
        """Verifies that remediation entries are counted."""
        # Test context matching 'system/core.py' and 'FAILED'
        impact = self.engine.analyze_impact("system/core.py", "Run core module")
        self.assertGreater(impact["relevant_count"], 0)
        self.assertTrue(any("remediation" in alert.lower() for alert in impact["alerts"]))

    def test_log_check(self):
        """Verifies that checks are logged to the ledger."""
        impact = {"risk_score": 0.5, "alerts": ["Test alert"], "relevant_count": 1}
        self.engine.log_check("test/path.py", "Test intent", impact)
        
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("| FORENSIC |", content)
            self.assertIn("Risk: 0.5", content)

if __name__ == "__main__":
    unittest.main()
