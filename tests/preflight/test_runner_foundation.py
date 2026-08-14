# SPDX-License-Identifier: MIT

"""TDD-first tests for runner.load_catalog (slice #1 Task 3).

Validates:
- YAML files in checks_dir are parsed by CheckSpec.from_yaml_text.
- Specs are returned sorted by `sequence` ascending.
- Duplicate sequences raise CatalogError.
- A single malformed YAML raises CatalogError with bundled error info.
- Empty dir returns [] (no exceptions).
"""
from pathlib import Path
import pytest
from control_plane.preflight import runner

SYNTHETIC_YAML_A = """
sequence: 10
id: a_check
display_name: A
command_type: shell
command: ["python", "-c", "print('a')"]
""".strip()

SYNTHETIC_YAML_B = """
sequence: 5
id: b_check
display_name: B
command_type: shell
command: ["python", "-c", "print('b')"]
""".strip()

SYNTHETIC_YAML_C = """
sequence: 20
id: c_check
display_name: C
command_type: shell
command: ["python", "-c", "print('c')"]
""".strip()


def test_load_catalog_sorts_by_sequence(tmp_path: Path):
    """Files are read regardless of filename order; sorted by sequence."""
    (tmp_path / "b.yaml").write_text(SYNTHETIC_YAML_B)
    (tmp_path / "a.yaml").write_text(SYNTHETIC_YAML_A)
    (tmp_path / "c.yaml").write_text(SYNTHETIC_YAML_C)
    specs = runner.load_catalog(tmp_path)
    assert [s.sequence for s in specs] == [5, 10, 20]
    assert [s.id for s in specs] == ["b_check", "a_check", "c_check"]


def test_load_catalog_rejects_duplicate_sequence(tmp_path: Path):
    """Two specs sharing sequence raise CatalogError (no silent shadowing)."""
    (tmp_path / "a.yaml").write_text(SYNTHETIC_YAML_A)
    dup_yaml = SYNTHETIC_YAML_A.replace(
        "id: a_check", "id: dup_check"
    ).replace(
        "display_name: A", "display_name: DUP"
    )
    (tmp_path / "b.yaml").write_text(dup_yaml)
    with pytest.raises(runner.CatalogError) as exc:
        runner.load_catalog(tmp_path)
    assert "duplicated" in str(exc.value).lower() or "sequence" in str(exc.value).lower()


def test_load_catalog_propagates_parse_error(tmp_path: Path):
    """Malformed YAML triggers CatalogError bundling per-file errors."""
    (tmp_path / "bad.yaml").write_text("not a yaml mapping: [")
    with pytest.raises(runner.CatalogError) as exc:
        runner.load_catalog(tmp_path)
    # Bundled per-file error info present.
    msg = str(exc.value).lower()
    assert ("bad" in msg or "yaml" in msg)


def test_load_catalog_missing_dir_raises_catalog_error(tmp_path: Path):
    """A nonexistent checks_dir raises CatalogError (run() can't proceed)."""
    nonexistent = tmp_path / "no_such_dir"
    with pytest.raises(runner.CatalogError):
        runner.load_catalog(nonexistent)


def test_load_catalog_empty_dir_returns_empty_list(tmp_path: Path):
    """Empty dir -> [] (caller decides whether to halt)."""
    assert runner.load_catalog(tmp_path) == []
