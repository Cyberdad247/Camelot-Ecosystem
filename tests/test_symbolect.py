import os
import sys

# Adjust path to import 01_KERNEL modules
sys.path.insert(0, os.path.abspath('01_KERNEL'))
from EXCALIBUR.shared.symbolect import decode_symbolect, encode_symbolect  # noqa: E402


def test_encode_symbolect_basic():
    text = "My thought for the plan"
    encoded = encode_symbolect(text)
    assert encoded == "My 🧠 for the 🗺️"

def test_decode_symbolect_basic():
    text = "My 🧠 for the 🗺️"
    decoded = decode_symbolect(text)
    assert decoded == "My thought for the plan"

def test_symbolect_reversibility():
    text = "The system will integrate the idea for the quest and report success or failure of the action, then validate."
    encoded = encode_symbolect(text)
    decoded = decode_symbolect(encoded)
    assert decoded == text

def test_encode_no_symbols():
    text = "Just a normal string with no matching words"
    assert encode_symbolect(text) == text

def test_decode_no_symbols():
    text = "Just a normal string with no matching emojis"
    assert decode_symbolect(text) == text

def test_empty_string():
    assert encode_symbolect("") == ""
    assert decode_symbolect("") == ""

def test_multiple_occurrences():
    text = "thought thought thought"
    encoded = encode_symbolect(text)
    assert encoded == "🧠 🧠 🧠"
    assert decode_symbolect(encoded) == text
