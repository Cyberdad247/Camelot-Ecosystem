"""OMEGA Defense Nexus Phase 4 acceptance tests — CompressionNexus."""
import sys
import gzip
import json
import importlib.util as _ilu
from pathlib import Path
import pytest

CAMELOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMELOT))

spec = _ilu.spec_from_file_location(
    "compression_nexus",
    CAMELOT / "control_plane" / "infra" / "compression_nexus.py",
)
_mod = _ilu.module_from_spec(spec)
sys.modules["compression_nexus"] = _mod
spec.loader.exec_module(_mod)

CompressionNexus = _mod.CompressionNexus


# ── Helpers ───────────────────────────────────────────────────────────────────

_BIG_CONTEXT = "\n".join(
    [
        "## IDENTITY",
        "I am CAMELOT-OS.",
        "",
        "## RANDOM_SECTION",
    ]
    + [f"line {i}" for i in range(200)]   # >1500 tok equivalent
)

_SMALL_CONTEXT = "## IDENTITY\nShort text.\n"


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_compress_context_large():
    cn = CompressionNexus(hermes_enabled=False)
    result = cn.compress_context(_BIG_CONTEXT, tok_target=100)
    assert result.compressed_tok_est < result.original_tok_est
    assert result.ratio > 0
    assert "## IDENTITY" in result.text
    assert "I am CAMELOT-OS." in result.text  # priority section kept verbatim


def test_compress_context_small_passthrough():
    cn = CompressionNexus(hermes_enabled=False)
    result = cn.compress_context(_SMALL_CONTEXT)
    # Small text should pass through unchanged
    assert result.original_chars == result.compressed_chars
    assert result.ratio == 0.0
    assert result.text == _SMALL_CONTEXT


def test_compress_memory_gzip_roundtrip():
    cn = CompressionNexus(hermes_enabled=False)
    data = {"key": "value", "numbers": list(range(50)), "nested": {"a": 1, "b": 2}}
    result = cn.compress_memory(data)
    assert result.original_bytes > 0
    assert result.compressed_bytes > 0
    assert result.codec in ("gzip", "msgpack", "msgpack+lz4")
    # Roundtrip
    recovered = cn.decompress_memory(result.data, result.codec)
    assert recovered == data


def test_compress_memory_reduces_size():
    cn = CompressionNexus(hermes_enabled=False)
    # Highly repetitive data should compress well
    data = {"items": ["repeated_value"] * 100}
    result = cn.compress_memory(data)
    assert result.ratio > 0.3, f"Expected >30% compression, got {result.ratio:.1%}"


def test_audit_disk_finds_large_files(tmp_path):
    """audit_disk reports files above 500 KB threshold."""
    small = tmp_path / "small.txt"
    small.write_bytes(b"x" * 100)
    large = tmp_path / "large.bin"
    large.write_bytes(b"y" * (600 * 1024))   # 600 KB

    cn = CompressionNexus(hermes_enabled=False)
    result = cn.audit_disk(scan_root=tmp_path)
    assert result.scanned_files == 2
    assert len(result.large_files) == 1
    assert result.large_files[0]["size_kb"] == pytest.approx(600.0, abs=1.0)
    assert result.potential_savings_kb > 0


def test_audit_disk_empty_dir(tmp_path):
    cn = CompressionNexus(hermes_enabled=False)
    result = cn.audit_disk(scan_root=tmp_path)
    assert result.scanned_files == 0
    assert result.large_files == []


def test_pack_file(tmp_path):
    src = tmp_path / "sample.json"
    payload = {"hello": "sovereign", "data": list(range(100))}
    src.write_text(json.dumps(payload), encoding="utf-8")

    cn = CompressionNexus(hermes_enabled=False)
    dest = cn.pack_file(src, remove_original=False)

    assert dest.exists()
    assert dest.suffix == ".gz"
    # Decompress and verify content
    with gzip.open(dest, "rb") as f:
        recovered = json.loads(f.read().decode("utf-8"))
    assert recovered == payload
    assert src.exists()   # original preserved when remove_original=False
