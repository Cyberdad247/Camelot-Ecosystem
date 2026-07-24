import importlib.util
import sys
from pathlib import Path

# Need to import a module starting with a number
_KERNEL = Path(__file__).resolve().parent.parent / "01_KERNEL"
spec = importlib.util.spec_from_file_location("symbolect", _KERNEL / "EXCALIBUR" / "shared" / "symbolect.py")
symbolect = importlib.util.module_from_spec(spec)
sys.modules["symbolect"] = symbolect
spec.loader.exec_module(symbolect)


def test_encode_symbolect():
    # Happy path test
    text = "My thought for the plan"
    encoded = symbolect.encode_symbolect(text)
    assert encoded == "My 🧠 for the 🗺️"

    # Test all symbols
    text2 = "system action success failure idea quest report integrate validate"
    encoded2 = symbolect.encode_symbolect(text2)
    assert encoded2 == "💻 ⚙️ ✅ ❌ 💡 🛡️ 📜 🔗 ✔️"

    # Edge cases
    assert symbolect.encode_symbolect("") == ""
    assert symbolect.encode_symbolect("no matching words here") == "no matching words here"


def test_decode_symbolect():
    # Happy path test
    encoded = "My 🧠 for the 🗺️"
    decoded = symbolect.decode_symbolect(encoded)
    assert decoded == "My thought for the plan"

    # Test all symbols
    encoded2 = "💻 ⚙️ ✅ ❌ 💡 🛡️ 📜 🔗 ✔️"
    decoded2 = symbolect.decode_symbolect(encoded2)
    assert decoded2 == "system action success failure idea quest report integrate validate"

    # Edge cases
    assert symbolect.decode_symbolect("") == ""
    assert symbolect.decode_symbolect("no matching symbols here") == "no matching symbols here"


def test_encode_decode_loop():
    # Loop should be identical
    original = "a system thought is an idea for an action plan"
    encoded = symbolect.encode_symbolect(original)
    decoded = symbolect.decode_symbolect(encoded)
    assert original == decoded
