import pytest
from pydantic import ValidationError

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../02_FORGE/PORTAL_CORE/Modal/morgana")))

from morgana_core import MorganaRequest, morgana_brain_v2

def test_morgana_brain_v2_mock_mode():
    req = MorganaRequest(task="hello", mock_mode=True)
    res = morgana_brain_v2.local(req)
    assert res is not None
    assert "morgana" in res
    assert "[MOCK_REPLY]" in res["morgana"]

def test_morgana_brain_v2_empty_task():
    with pytest.raises(ValidationError):
        MorganaRequest(task="")

def test_morgana_brain_v2_long_task():
    with pytest.raises(ValidationError):
        MorganaRequest(task="a" * 10001)

def test_morgana_brain_v2_invalid_mode():
    with pytest.raises(ValidationError):
        MorganaRequest(task="hello", mode="INVALID_MODE")
