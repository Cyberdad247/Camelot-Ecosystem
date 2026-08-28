# SPDX-License-Identifier: MIT

"""Tests for CAMELOT_NON_INTERACTIVE env-var activation (CI gate)."""

import os
from unittest.mock import patch

from control_plane.cli.iron_gate import _check_iron_gate, set_non_interactive


class TestNonInteractiveEnvVar:
    """Verify the CAMELOT_NON_INTERACTIVE env-var path."""

    def setup_method(self):
        """Reset module-level flag before each test."""
        set_non_interactive(False)

    def teardown_method(self):
        """Clean up env var and flag after each test."""
        set_non_interactive(False)
        os.environ.pop("CAMELOT_NON_INTERACTIVE", None)

    def test_env_var_true_enables_non_interactive(self):
        """CAMELOT_NON_INTERACTIVE=true should activate non-interactive mode."""
        with patch.dict(os.environ, {"CAMELOT_NON_INTERACTIVE": "true"}):
            result = _check_iron_gate("delete all files")
            assert result is False

    def test_env_var_case_insensitive(self):
        """CAMELOT_NON_INTERACTIVE=TRUE should also work."""
        with patch.dict(os.environ, {"CAMELOT_NON_INTERACTIVE": "TRUE"}):
            result = _check_iron_gate("deploy to production")
            assert result is False

    def test_env_var_false_allows_interactive(self):
        """CAMELOT_NON_INTERACTIVE=false should not activate."""
        with patch.dict(os.environ, {"CAMELOT_NON_INTERACTIVE": "false"}):
            # Low-risk intent passes regardless
            result = _check_iron_gate("list files")
            assert result is True

    def test_env_var_not_set_allows_interactive(self):
        """No env var set should default to interactive mode."""
        os.environ.pop("CAMELOT_NON_INTERACTIVE", None)
        # Low-risk intent passes regardless
        result = _check_iron_gate("help me")
        assert result is True

    def test_programmatic_override_takes_priority(self):
        """set_non_interactive(True) should work even without the env var."""
        os.environ.pop("CAMELOT_NON_INTERACTIVE", None)
        set_non_interactive(True)
        result = _check_iron_gate("delete everything")
        assert result is False
