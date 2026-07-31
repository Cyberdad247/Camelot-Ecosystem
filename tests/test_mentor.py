import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath('01_KERNEL'))
# noqa: E402
from EXCALIBUR.system.MENTOR import check_system_integrity


def test_check_system_integrity_all_exist():
    with patch('EXCALIBUR.system.MENTOR.os.path.exists') as mock_exists:
        mock_exists.return_value = True
        result = check_system_integrity()
        assert result is True

def test_check_system_integrity_missing_files():
    with patch('EXCALIBUR.system.MENTOR.os.path.exists') as mock_exists:
        mock_exists.side_effect = lambda x: False if "titan_protocol.md" in x else True
        result = check_system_integrity()
        assert result is False
