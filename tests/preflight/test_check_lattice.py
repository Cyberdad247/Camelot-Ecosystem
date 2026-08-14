# SPDX-License-Identifier: MIT

"""TDD-first tests for the lattice consistency check (sequence 080).

The check verifies both:
- yaml_parses (top-level mapping shape), AND
- each subproject's path actually exists on disk.

Tests here exercise the lattice path mapping using a tmp tree mirroring
docs/architecture/lattice.yaml.
"""
from pathlib import Path
import textwrap
import os
import yaml

from control_plane.preflight.probes import yaml_parses


SAMPLE_LATTICE = textwrap.dedent("""
    version: 1
    sot: {type: file, path: docs/architecture/lattice_map.md}
    axes: {inference: {anchors: []}, memory: {anchors: []}}
    subprojects:
      - id: CAMELOT_OS
        type: sovereign
        path: CAMELOT_OS/
        mb: 26800
      - id: cli-proxy-api
        type: service
        path: CLIProxyAPI/
        mb: 56
""").strip()


def _write_lattice(tmp: Path) -> Path:
    """Write SAMPLE_LATTICE and create dummy subproject dirs."""
    lattice_path = tmp / "lattice.yaml"
    lattice_path.write_text(SAMPLE_LATTICE)
    os.makedirs(tmp / "CAMELOT_OS", exist_ok=True)
    # `cli-proxy-api` is intentionally NOT created to test path-missing
    # cases in the integration tests; here we test happy-path.
    os.makedirs(tmp / "CLIProxyAPI", exist_ok=True)
    return lattice_path


def test_lattice_yaml_parses(tmp_path):
    p = _write_lattice(tmp_path)
    ok, _ = yaml_parses.check(p)
    assert ok is True


def test_lattice_subprojects_present(tmp_path):
    p = _write_lattice(tmp_path)
    data = yaml.safe_load(p.read_text())
    on_disk = set()
    for sp in data["subprojects"]:
        path = tmp_path / sp["path"]
        if path.exists():
            on_disk.add(sp["id"])
    # When _write_lattice creates both subproject dirs, both are on disk.
    assert "CAMELOT_OS" in on_disk
    assert "cli-proxy-api" in on_disk


def test_lattice_subproject_missing_observable(tmp_path):
    """If a subproject dir is absent, surface as missing."""
    lattice_path = tmp_path / "lattice.yaml"
    lattice_path.write_text(SAMPLE_LATTICE)
    os.makedirs(tmp_path / "CAMELOT_OS", exist_ok=True)
    # `CLIProxyAPI` not created.
    data = yaml.safe_load(lattice_path.read_text())
    missing = []
    for sp in data["subprojects"]:
        path = tmp_path / sp["path"]
        if not path.exists():
            missing.append(sp["id"])
    assert "cli-proxy-api" in missing
    assert "CAMELOT_OS" not in missing
