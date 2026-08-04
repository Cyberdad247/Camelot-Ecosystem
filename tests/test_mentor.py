import os
import sys
from unittest.mock import mock_open, patch

sys.path.insert(0, os.path.abspath('01_KERNEL')) # noqa: E402

from EXCALIBUR.system import MENTOR


@patch("EXCALIBUR.system.MENTOR.datetime")
@patch("builtins.open", new_callable=mock_open)
@patch("builtins.print")
def test_log_to_ledger_default_status(mock_print, mock_file, mock_datetime):
    mock_datetime.now.return_value.isoformat.return_value = "2023-10-27T10:00:00"

    MENTOR.log_to_ledger("SYSTEM_BOOT")

    expected = "| 2023-10-27T10:00:00 | MENTOR_Omega | SYSTEM_BOOT | SUCCESS |"

    mock_file.assert_called_once_with(MENTOR.LEDGER_PATH, "a", encoding="utf-8")
    mock_file().write.assert_called_once_with("\n" + expected)
    mock_print.assert_called_once_with(expected)

@patch("EXCALIBUR.system.MENTOR.datetime")
@patch("builtins.open", new_callable=mock_open)
@patch("builtins.print")
def test_log_to_ledger_custom_status(mock_print, mock_file, mock_datetime):
    mock_datetime.now.return_value.isoformat.return_value = "2023-10-27T10:05:00"

    MENTOR.log_to_ledger("AUTH_CHECK", status="FAILED")

    expected = "| 2023-10-27T10:05:00 | MENTOR_Omega | AUTH_CHECK | FAILED |"

    mock_file.assert_called_once_with(MENTOR.LEDGER_PATH, "a", encoding="utf-8")
    mock_file().write.assert_called_once_with("\n" + expected)
    mock_print.assert_called_once_with(expected)
