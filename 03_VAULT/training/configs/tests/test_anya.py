"""Tests for the Anya intent compiler."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from anya import compile_intent


def test_basic_compile():
    result = compile_intent("build a login page")
    assert "intent" in result
    assert "domain" in result
    assert "complexity" in result
    assert isinstance(result["complexity"], int)
    assert 1 <= result["complexity"] <= 5


def test_runic_command():
    result = compile_intent("//PLAN deploy auth service")
    assert result["runic"] is True


def test_non_runic():
    result = compile_intent("create a component")
    assert result["runic"] is False


def test_empty_input():
    result = compile_intent("")
    assert result is not None
    assert "intent" in result


def test_long_input():
    result = compile_intent("x" * 5000)
    assert result is not None
    assert isinstance(result["complexity"], int)
