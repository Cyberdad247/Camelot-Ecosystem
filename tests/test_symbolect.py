import sys
import os

sys.path.insert(0, os.path.abspath('01_KERNEL'))

from EXCALIBUR.shared.symbolect import encode_symbolect, decode_symbolect  # noqa: E402

def test_encode_symbolect_happy_path():
    assert encode_symbolect("My thought for the plan") == "My 🧠 for the 🗺️"
    assert encode_symbolect("A great success") == "A great ✅"

def test_encode_symbolect_empty():
    assert encode_symbolect("") == ""

def test_encode_symbolect_substring_not_replaced():
    # 'thought' is a word, but 'thoughtful' should not be replaced
    assert encode_symbolect("My thoughtful action") == "My thoughtful ⚙️"

def test_decode_symbolect_happy_path():
    assert decode_symbolect("My 🧠 for the 🗺️") == "My thought for the plan"
    assert decode_symbolect("A great ✅") == "A great success"

def test_decode_symbolect_empty():
    assert decode_symbolect("") == ""
