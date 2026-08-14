# SPDX-License-Identifier: MIT

"""Probe-runner for catalog check 080 lattice_yaml_consistency.

Verifies docs/architecture/lattice.yaml parses and subproject paths
exist on disk.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import yaml

from control_plane.preflight.probes.yaml_parses import check as yaml_parses_check


def main() -> int:
    args = sys.argv[1:]
    if "--path" not in args:
        sys.stderr.write(
            "lattice_run requires --path <lattice-yaml-path>\n"
        )
        return 2
    idx = args.index("--path")
    lattice_path = Path(args[idx + 1])

    # Step 1: verifies parses + top-level mapping.
    parse_ok, parse_msg = yaml_parses_check(lattice_path)
    if not parse_ok:
        payload = {
            "all_ok": False,
            "parse_ok": False,
            "parse_msg": parse_msg,
        }
        sys.stdout.write(json.dumps(payload, sort_keys=True) + "\n")
        return 1

    # Step 2: each subproject path must exist relative to lattice parent.
    data = yaml.safe_load(lattice_path.read_text())
    subprojects = data.get("subprojects", [])
    lattice_root = lattice_path.parent.parent  # docs/architecture/lattice.yaml -> repo root
    # Try multiple candidate roots (the lattice lives next to docs/architecture).
    candidate_bases = [
        lattice_root,                       # running from repo root
        lattice_root.parent,                # running from docs/architecture/..
        Path.cwd(),                         # cwd
    ]
    missing: list[str] = []
    for sp in subprojects:
        relpath = sp.get("path", "")
        for base in candidate_bases:
            if (base / relpath).exists():
                break
        else:
            missing.append(sp["id"])

    all_ok = parse_ok and not missing
    payload = {
        "all_ok": all_ok,
        "parse_ok": parse_ok,
        "subprojects_total": len(subprojects),
        "subprojects_missing": missing,
    }
    sys.stdout.write(json.dumps(payload, sort_keys=True) + "\n")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
