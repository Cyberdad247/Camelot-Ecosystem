import sys
import importlib.util as _ilu
from pathlib import Path
from datetime import datetime

CAMELOT = Path(__file__).resolve().parents[1]

def _load_tools():
    # Use a well-defined mock module name to avoid conflicts
    name = "p8_open_notebook_tools"
    rel_path = CAMELOT / "01_KERNEL" / "agora" / "Squires" / "open_notebook" / "graphs" / "tools.py"

    cached = sys.modules.get(name)
    if cached is not None:
        return cached

    spec = _ilu.spec_from_file_location(name, rel_path)
    mod = _ilu.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

def test_get_current_timestamp_format():
    """Verify get_current_timestamp returns correctly formatted timestamp string."""
    tools = _load_tools()
    result = tools.get_current_timestamp.invoke({})

    assert isinstance(result, str)
    assert len(result) == 14
    assert result.isdigit()

    # Verify it can be parsed back into a datetime object
    try:
        parsed_time = datetime.strptime(result, "%Y%m%d%H%M%S")
        assert parsed_time is not None
    except ValueError as e:
        assert False, f"Timestamp format invalid: {e}"

def test_get_current_timestamp_freshness():
    """Verify get_current_timestamp generates a fresh, reasonably accurate timestamp."""
    tools = _load_tools()
    before = datetime.now()
    result = tools.get_current_timestamp.invoke({})

    parsed_time = datetime.strptime(result, "%Y%m%d%H%M%S")

    # Basic sanity checks for freshness
    assert parsed_time.year == before.year
    assert parsed_time.month == before.month
    assert parsed_time.day == before.day
