#!/usr/bin/env python3
"""CI sanity check: enforce parity between the EXCALIBUR PyInstaller
smoke's CRLF pre-check `watched` literal and the dorny/paths-filter
`excalibur-paths` list inside `.github/workflows/verify_os.yml`.

Both lists live in the same workflow file but in two different blocks:
  * a Python tuple OR list embedded in a YAML heredoc, and
  * a YAML literal-block scalar under `with.filters`.

It's easy for a contributor to update one block and forget the other,
which would silently let:

  * CRLF contamination slip past the pre-build gate (literal grew
    in dorny block, not CRLF block) — producing a confusing
    60-seconds-into-the-build BOM/CRLF import error in fastapi/uvicorn.

  * Build changes slip past CI (CRLF literal grew without dorny block
    being updated) — producing a stale skipped smoke on a real change.

This script extracts both lists from `.github/workflows/verify_os.yml`
and asserts SET EQUALITY between them. Mismatch exits non-zero with a
precise diagnostic.

Exit codes:
    0 — sets are equal (parity holds)
    1 — sets differ OR have duplicates OR are missing entries
    2 — workflow YAML or expected blocks could not be parsed

Self-test:
    --self-test writes synthetic workflow YAMLs to a temp dir,
    exercises four cases (divergent / matching / missing-CRLF-step /
    list-literal rewrite), and verifies the script catches each.
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

import yaml


WORKFLOW = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "verify_os.yml"
JOB_ID = "excalibur-pyinstaller-smoke"
CRLF_STEP_NAME = "Enforce LF line endings on smoke-affected files"
DORNY_FILTER_GROUP = "excalibur-paths"


def fail(msg: str) -> "None":
    print(f"[FAIL] excalibur_filter_parity: {msg}", file=sys.stderr)
    sys.exit(1)


def ok(msg: str) -> "None":
    print(f"[OK]   excalibur_filter_parity: {msg}")


# ---------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------


def _load_yaml_doc(path: Path) -> dict:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        fail(f"cannot parse {path}: {e}")


def _find_step(job: dict, *, name: str | None = None, id_: str | None = None) -> dict:
    for s in (job.get("steps") or []):
        if id_ is not None and isinstance(s, dict) and s.get("id") == id_:
            return s
        if name is not None and isinstance(s, dict) and s.get("name") == name:
            return s
    label = f"`id: {id_}`" if id_ else f"`name: {name}`"
    fail(f"step {label} not found in job `{JOB_ID}`")


def _extract_watched_strings(run: str) -> list[str]:
    """Extract single- AND double-quoted strings inside the watched literal.

    Accepts BOTH `watched = (...)` (tuple) and `watched = [...]` (list)
    literal forms — Python permits either for a static collection, and
    contributors reasonably refactor between them. The close delimiter
    matches whichever opening brace the regex hit. The current heredoc
    has no nested parens/brackets, so non-greedy matching is safe.
    """
    # Strip Python `# ...` comments before regex extraction so a path
    # literal containing `]` (e.g., `data/output/2026]`) cannot confuse
    # the close-delimiter match, AND so a `# 'phantom'` comment near the
    # tuple doesn't get slurped as a real entry. This mirrors the
    # pre-commit regex strip in scripts/check_filter_parity.py.
    run_no_comments = re.sub(r"#.*", "", run)
    # The char class `[\(\[]` opens with either `(` or `[`; the closing
    # class `[\])]` likewise closes with the matching brace.
    tuple_match = re.search(r"watched\s*=\s*[[\(](.*?)[\])]", run_no_comments, re.DOTALL)
    if tuple_match is None:
        fail(
            "CRLF step `run:` does not contain a `watched = (...)` tuple "
            "or `watched = [...]` list literal"
        )
    body = tuple_match.group(1)
    # Capture either single- or double-quoted paths; flatten the alternation.
    raw = re.findall(r"'([^']+)'|\"([^\"]+)\"", body)
    if not raw:
        fail(
            "CRLF step `watched` literal has no quoted entries "
            "(mix of str literals? stray comments inside? check heredoc)"
        )
    return [single or double for single, double in raw]


def _extract_watched_tuple(crlf_step: dict) -> list[str]:
    run = crlf_step.get("run")
    if not isinstance(run, str):
        fail("CRLF step `run:` is not a string")
    return _extract_watched_strings(run)


def _extract_dorny_paths(job: dict) -> list[str]:
    """Extract the dorny/paths-filter `excalibur-paths` list (YAML literal)."""
    filter_step = None
    for s in (job.get("steps") or []):
        if isinstance(s, dict) and s.get("id") == "filter":
            filter_step = s
            break
    if filter_step is None:
        fail("step `id: filter` not found in job `excalibur-pyinstaller-smoke`")

    filters_text = (filter_step.get("with") or {}).get("filters")
    if not isinstance(filters_text, str):
        fail("`with.filters` in step `id: filter` is not a string")

    try:
        filters_doc = yaml.safe_load(filters_text)
    except yaml.YAMLError as e:
        fail(f"cannot re-parse `with.filters` literal-block scalar: {e}")

    if not isinstance(filters_doc, dict):
        fail("`with.filters` mini-document did not parse to a dict")

    paths = filters_doc.get(DORNY_FILTER_GROUP)
    if not isinstance(paths, list):
        fail(f"`{DORNY_FILTER_GROUP}` is not a list")
    if not all(isinstance(p, str) for p in paths):
        fail(f"`{DORNY_FILTER_GROUP}` contains non-string entries")
    return paths


def _duplicates(items: list[str]) -> list[str]:
    return sorted(p for p, c in Counter(items).items() if c > 1)


# ---------------------------------------------------------------------------
# Core check
# ---------------------------------------------------------------------------


def check(document_path: Path) -> tuple[set[str], set[str]]:
    """Returns (watched_set, dorny_set) for downstream validation.

    Raises ``SystemExit(1)`` on parse failure or duplicates. The caller
    decides what to do with the sets (parity, divergence report, etc.).
    """
    doc = _load_yaml_doc(document_path)
    if not isinstance(doc, dict):
        fail(f"{document_path} did not parse to a dict")

    job = (doc.get("jobs") or {}).get(JOB_ID)
    if not isinstance(job, dict):
        fail(f"job `{JOB_ID}` not found in {document_path}")

    # Catches the case where the CRLF step is removed entirely (refactor).
    crlf_step = _find_step(job, name=CRLF_STEP_NAME)
    watched_list = _extract_watched_tuple(crlf_step)
    dorny_list = _extract_dorny_paths(job)

    # Dup detection on BOTH sides; set equality would mask this otherwise.
    for label, items in (("watched", watched_list), ("dorny", dorny_list)):
        dups = _duplicates(items)
        if dups:
            fail(
                f"{label} list has duplicate entries "
                f"(would be masked by set equality):\n  "
                + "\n  ".join(f"{p!r}" for p in dups)
            )

    return set(watched_list), set(dorny_list)


def _report_divergence(watched: set[str], dorny: set[str]) -> "None":
    diff_lines = []
    only_in_watched = sorted(watched - dorny)
    only_in_dorny = sorted(dorny - watched)
    if only_in_watched:
        diff_lines.append("  in CRLF `watched = (...)` but NOT in dorny filter:")
        diff_lines.extend(f"    - {p!r}" for p in only_in_watched)
    if only_in_dorny:
        diff_lines.append("  in dorny filter but NOT in CRLF `watched = (...)`:")
        diff_lines.extend(f"    - {p!r}" for p in only_in_dorny)
    fail(
        "EXCALIBUR smoke's CRLF pre-check and dorny/paths-filter are\n"
        "OUT OF SYNC. Update the matching block in\n"
        f"  {WORKFLOW}\n"
        "so both lists contain exactly the same paths.\n"
        + "\n".join(diff_lines)
    )


def enforce_parity(document_path: Path) -> tuple[set[str], set[str]]:
    """Run `check()` then assert set equality. Fail loudly on divergence.

    Used by both `main()` and `_run_self_test()` so the same gate runs in
    production and in synthetic-test mode.
    """
    watched, dorny = check(document_path)
    if watched != dorny:
        _report_divergence(watched, dorny)
    return watched, dorny


def main() -> "None":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run a synthetic-divergence self-test and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        _run_self_test()
        return

    if not WORKFLOW.exists():
        fail(f"{WORKFLOW} not found; expected at the repo root")

    watched, dorny = enforce_parity(WORKFLOW)
    ok(
        f"CRLF step lists {len(watched)} unique entries; "
        f"dorny filter lists {len(dorny)} unique entries"
    )

    print(
        f"[PASS] excalibur_filter_parity: CRLF tuple/list and dorny filter "
        f"both contain exactly {len(watched)} paths in lock-step"
    )


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


_PARITY_TEMPLATE = """\
name: synthetic
on: [push]
jobs:
  excalibur-pyinstaller-smoke:
    runs-on: ubuntu-latest
    steps:
      - name: checkout
        run: echo checkout
      - name: Enforce LF line endings on smoke-affected files
        run: |
          python -c "
          watched = (
            {watched_quoted}
          )
          "
      - name: Detect changes
        id: filter
        uses: dorny/paths-filter@v3
        with:
          filters: |
            excalibur-paths:
{dorny_yaml_paths_indented}
"""


_LIST_LITERAL_TEMPLATE = """\
name: synthetic
on: [push]
jobs:
  excalibur-pyinstaller-smoke:
    runs-on: ubuntu-latest
    steps:
      - name: checkout
        run: echo checkout
      - name: Enforce LF line endings on smoke-affected files
        run: |
          python -c "
          watched = [
            'm.py',
            'n.py'
          ]
          "
      - name: Detect changes
        id: filter
        uses: dorny/paths-filter@v3
        with:
          filters: |
            excalibur-paths:
              - 'm.py'
              - 'n.py'
"""


_NO_CRLF_STEP_TEMPLATE = """\
name: synthetic
on: [push]
jobs:
  excalibur-pyinstaller-smoke:
    runs-on: ubuntu-latest
    steps:
      - name: checkout
        run: echo checkout
      - name: Detect changes
        id: filter
        uses: dorny/paths-filter@v3
        with:
          filters: |
            excalibur-paths:
              - 'a.py'
              - 'b.py'
"""


def _build_synthetic_yaml(watched: list[str], dorny: list[str]) -> str:
    quoted = ",\n            ".join(f"'{p}'" for p in watched)
    indented = "\n".join(f"              - '{p}'" for p in dorny)
    return _PARITY_TEMPLATE.format(
        watched_quoted=quoted,
        dorny_yaml_paths_indented=indented,
    )


def _run_self_test() -> None:
    # Case 1: divergent (extra path in CRLF literal, missing from dorny).
    print("== self-test: divergent case ==")
    bad_yaml_text = _build_synthetic_yaml(
        ["a.py", "b.py", "c.py"], ["a.py", "b.py"]
    )
    _expect_failure(bad_yaml_text, label="divergent")

    # Case 2: matching sets (parity holds).
    print("== self-test: matching case ==")
    good_watched = sorted(["x.py", "y.py", "z.py"])
    good_dorny = sorted(["x.py", "y.py", "z.py"])
    good_yaml_text = _build_synthetic_yaml(good_watched, good_dorny)
    _expect_pass(good_yaml_text, label="matching", expected_size=3)

    # Case 3: CRLF step removed entirely (refactor scenario).
    print("== self-test: missing CRLF step ==")
    _expect_failure(_NO_CRLF_STEP_TEMPLATE, label="missing-CRLF-step")

    # Case 4: contributor refactored `watched = (...)` to `watched = [...]`;
    # the regex still extracts the same 2 paths and parity holds.
    print("== self-test: list-literal rewrite ([...] instead of (...)) ==")
    _expect_pass(_LIST_LITERAL_TEMPLATE, label="list-literal", expected_size=2)

    print("[PASS] excalibur_filter_parity: self-test passed")


def _with_synthetic_yaml(yaml_text: str) -> tuple[Path, tempfile.TemporaryDirectory]:
    td = tempfile.TemporaryDirectory()
    path = Path(td.name) / "verify_os.yml"
    path.write_text(yaml_text, encoding="utf-8")
    return path, td


def _expect_failure(yaml_text: str, *, label: str) -> None:
    path, td = _with_synthetic_yaml(yaml_text)
    try:
        try:
            enforce_parity(path)
        except SystemExit as e:
            if e.code != 1:
                print(f"[self-test] FAIL ({label}): exited {e.code}, want 1")
                sys.exit(2)
            print(f"[self-test] OK ({label}): correctly failed with exit 1")
            return
        print(f"[self-test] FAIL ({label}): expected failure but check passed")
        sys.exit(2)
    finally:
        td.cleanup()


def _expect_pass(yaml_text: str, *, label: str, expected_size: int) -> None:
    path, td = _with_synthetic_yaml(yaml_text)
    try:
        watched, dorny = enforce_parity(path)
        if len(watched) != expected_size or len(dorny) != expected_size:
            print(
                f"[self-test] FAIL ({label}): unexpected set sizes "
                f"{len(watched)}/{len(dorny)}, want {expected_size}/{expected_size}"
            )
            sys.exit(2)
        print(f"[self-test] OK ({label}): correctly saw parity ({expected_size} paths)")
    finally:
        td.cleanup()


if __name__ == "__main__":
    main()
