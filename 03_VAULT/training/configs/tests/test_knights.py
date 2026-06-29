"""Tests for knight modules."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_coder_path_traversal():
    """CRITICAL: Verify path traversal is blocked."""
    from knights.coder import SirForge
    knight = SirForge()
    # Attempt traversal — should return None
    result = knight._write_file("../../etc/passwd", "malicious")
    assert result is None


def test_coder_path_traversal_dotdot():
    from knights.coder import SirForge
    knight = SirForge()
    result = knight._write_file("../../../tmp/evil.py", "bad")
    assert result is None


def test_coder_execute_template():
    from knights.coder import SirForge
    knight = SirForge()
    intent = {"intent": "BUILD", "domain": "CODE", "complexity": 2}
    result = knight.execute("create an api route for users", intent, write=False)
    assert result["status"] == "success"
    assert "api_route" in result["output"].lower() or "template" in result["output"].lower()


def test_coder_clean_name():
    from knights.coder import SirForge
    knight = SirForge()
    assert knight._clean_name("hello") == "Hello"
    assert knight._clean_name("") == "Module"
    assert knight._clean_name(None) == "Module"
    assert knight._clean_name("a!b@c") == "Abc"


def test_all_knights_load():
    """Verify all knight modules can be imported."""
    from knights.base import BaseKnight
    import importlib
    knights_dir = os.path.join(os.path.dirname(__file__), "..", "knights")
    loaded = 0
    for f in os.listdir(knights_dir):
        if f.startswith("_") or not f.endswith(".py") or f == "base.py":
            continue
        mod = importlib.import_module(f"knights.{f[:-3]}")
        for attr in dir(mod):
            obj = getattr(mod, attr)
            if isinstance(obj, type) and issubclass(obj, BaseKnight) and obj is not BaseKnight:
                instance = obj()
                assert instance.name
                assert instance.specialty
                loaded += 1
    assert loaded >= 4  # We have at least 4 knights
