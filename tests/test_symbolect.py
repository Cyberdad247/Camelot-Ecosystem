import os
import sys

# Add 01_KERNEL to path for imports
sys.path.insert(0, os.path.abspath('01_KERNEL'))

from EXCALIBUR.shared.symbolect import decode_symbolect, encode_symbolect  # noqa: E402


def test_decode_symbolect_basic():
    """Test basic decoding of a string with valid symbols."""
    assert decode_symbolect("My 🧠 for the 🗺️") == "My thought for the plan"
    assert decode_symbolect("✅ for the 🔗") == "success for the integrate"


def test_decode_symbolect_no_symbols():
    """Test decoding a string that contains no symbols."""
    assert decode_symbolect("Just regular text here") == "Just regular text here"


def test_decode_symbolect_empty_string():
    """Test decoding an empty string."""
    assert decode_symbolect("") == ""


def test_decode_symbolect_multiple_symbols():
    """Test decoding a string with multiple identical and different symbols."""
    # Multiple identical
    assert decode_symbolect("🧠 🧠 🧠") == "thought thought thought"
    # Multiple different
    assert decode_symbolect("🧠 🗺️ ⚙️ ✅ ❌ 💡 🛡️ 📜 💻 🔗 ✔️") == "thought plan action success failure idea quest report system integrate validate"


def test_encode_symbolect_basic():
    """Test basic encoding of a string."""
    assert encode_symbolect("My thought for the plan") == "My 🧠 for the 🗺️"

def test_encode_symbolect_empty_string():
    """Test encoding an empty string."""
    assert encode_symbolect("") == ""
