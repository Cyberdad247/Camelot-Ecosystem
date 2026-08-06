import sys
import os

sys.path.insert(0, os.path.abspath("01_KERNEL")) # noqa: E402

from EXCALIBUR.shared.symbolect import decode_symbolect, encode_symbolect

def test_decode_symbolect_basic():
    """Test basic decoding."""
    encoded = "My 🧠 for the 🗺️"
    expected = "My thought for the plan"
    assert decode_symbolect(encoded) == expected

def test_decode_symbolect_no_symbols():
    """Test decoding a string with no symbols."""
    text = "Just a normal string with no symbols."
    assert decode_symbolect(text) == text

def test_decode_symbolect_all_symbols():
    """Test decoding each symbol."""
    encoded = "🧠 🗺️ ⚙️ ✅ ❌ 💡 🛡️ 📜 💻 🔗 ✔️"
    expected = "thought plan action success failure idea quest report system integrate validate"
    assert decode_symbolect(encoded) == expected

def test_decode_symbolect_multiple_occurrences():
    """Test decoding multiple occurrences of the same symbol."""
    encoded = "🧠 and 🧠"
    expected = "thought and thought"
    assert decode_symbolect(encoded) == expected

def test_decode_symbolect_adjacent_symbols():
    """Test decoding adjacent symbols."""
    encoded = "🧠🗺️⚙️"
    expected = "thoughtplanaction"
    assert decode_symbolect(encoded) == expected

def test_encode_symbolect_basic():
    """Test basic encoding."""
    text = "My thought for the plan"
    expected = "My 🧠 for the 🗺️"
    assert encode_symbolect(text) == expected

def test_encode_decode_roundtrip():
    """Test that encoding then decoding returns the original string."""
    original = "This plan is a thought out action."
    encoded = encode_symbolect(original)
    decoded = decode_symbolect(encoded)
    assert decoded == original
