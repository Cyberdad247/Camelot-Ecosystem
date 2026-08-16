#!/usr/bin/env python3
"""
Camelot-OS — published contract family meta-validation harness.

Meta-validates every schema in `packages/contracts/` against the JSON Schema
**Draft 2020-12** meta-schema (the dialect the §11 catalog mandates) and checks
the `index.json` catalog for conformance. This is the mechanical check behind
the PURGE_PREP.md claim "all meta-validated 2020-12".

Checks performed:
  1. Dialect declaration — every `*.schema.json` must declare
     `$schema: https://json-schema.org/draft/2020-12/schema`.
  2. Meta-validation — every schema document must itself be a *valid* JSON
     Schema under the 2020-12 meta-schema (keyword names, types, formats,
     required/properties consistency, etc.).
  3. Catalog conformance — `index.json` must list exactly the schema files on
     disk (no orphans, no missing), with matching `$id` URIs.
  4. JSON well-formedness — every catalog entry is parseable JSON.

The meta-schema is bundled with `jsonschema` (Draft202012Validator.META_SCHEMA),
so the check runs fully offline. The schemas are self-contained (no `$ref`),
so no external resolution is needed.

Usage:  python harness/contracts/validate_contract_schemas.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

# Windows consoles default to cp1252, which cannot encode the ✓/✗ glyphs used
# in output. Force UTF-8 (with replacement fallback) so the harness never
# crashes on print, regardless of the active console codepage.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = ROOT / "packages" / "contracts"
INDEX = CONTRACTS_DIR / "index.json"

DIALECT = "https://json-schema.org/draft/2020-12/schema"


def main() -> int:
    failures: list[str] = []
    schema_files = sorted(CONTRACTS_DIR.glob("*.schema.json"))
    meta = Draft202012Validator.META_SCHEMA
    meta_validator = Draft202012Validator(meta)

    print("=" * 72)
    print(f"Meta-validation — {len(schema_files)} schemas vs Draft 2020-12 meta-schema")
    print("=" * 72)

    for f in schema_files:
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  [FAIL] {f.name}: not valid JSON ({e})")
            failures.append(f"{f.name}: JSON parse")
            continue

        # 1. Dialect declaration
        if doc.get("$schema") != DIALECT:
            print(f"  [FAIL] {f.name}: $schema is {doc.get('$schema')!r}, "
                  f"expected {DIALECT!r}")
            failures.append(f"{f.name}: wrong dialect")
            continue

        # 2. Meta-validation against the 2020-12 meta-schema
        errors = sorted(meta_validator.iter_errors(doc), key=lambda e: list(e.path))
        if errors:
            print(f"  [FAIL] {f.name}: {len(errors)} meta-validation error(s)")
            for e in errors[:5]:
                print(f"         ✗ {'/'.join(str(p) for p in e.path)}: {e.message}")
            failures.append(f"{f.name}: meta-validation ({len(errors)} errors)")
        else:
            print(f"  [PASS] {f.name}")

    # 3. Catalog conformance (index.json ↔ files on disk)
    print("\n" + "=" * 72)
    print("Catalog conformance — index.json vs packages/contracts/")
    print("=" * 72)
    catalog = json.loads(INDEX.read_text(encoding="utf-8"))
    listed = {entry["file"]: entry for entry in catalog["schemas"]}
    on_disk = {f.name for f in schema_files}

    if catalog.get("$schema") != DIALECT:
        print(f"  [FAIL] index.json: $schema is {catalog.get('$schema')!r}, "
              f"expected {DIALECT!r}")
        failures.append("index.json: wrong dialect")

    for name in sorted(on_disk - set(listed)):
        print(f"  [FAIL] {name}: on disk but missing from index.json catalog")
        failures.append(f"{name}: missing from catalog")
    for name in sorted(set(listed) - on_disk):
        print(f"  [FAIL] {name}: listed in index.json but missing on disk")
        failures.append(f"{name}: listed but not on disk")

    for name in sorted(set(listed) & on_disk):
        expected_id = f"https://camelot-os/schemas/{name}"
        if listed[name].get("$id") != expected_id:
            print(f"  [FAIL] {name}: catalog $id {listed[name].get('$id')!r} != "
                  f"{expected_id!r}")
            failures.append(f"{name}: catalog $id mismatch")
        else:
            print(f"  [PASS] {name}: catalog entry + $id OK")

    print("\n" + "=" * 72)
    if failures:
        print(f"✗ {len(failures)} problem(s):")
        for f in failures:
            print(f"    - {f}")
        return 1
    print(f"✓ ALL {len(schema_files)} schemas meta-validate as JSON Schema "
          f"Draft 2020-12; catalog conformance OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
