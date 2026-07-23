import pytest
import sys
import os

# Add regex_cleaner to sys.path so we can import main directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import phial_main, clean_json

def test_clean_json_markdown():
    raw = '```json\n{"key": "value"}\n```'
    assert clean_json(raw) == '{"key": "value"}'

def test_clean_json_raw():
    raw = '{"key": "value"}'
    assert clean_json(raw) == '{"key": "value"}'

def test_phial_main_success():
    raw = '```json\n{"status": "ok"}\n```'
    result = phial_main(raw)
    assert result == {"status": "success", "data": {"status": "ok"}}

def test_phial_main_invalid_json():
    raw = '```json\n{invalid json}\n```'
    result = phial_main(raw)
    assert result == {"status": "error", "message": "Invalid JSON"}
