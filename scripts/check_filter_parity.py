#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""CI sanity check: enforce pre-commit <-> dorny filter parity for the
infra-purge-rollback gate.

Reads both:
  * `.pre-commit-config.yaml` -- extracts hook `infra-purge-rollback-verify`
    `files:` block (Python extended-regex via `(?x)`).
  * `.github/workflows/verify_os.yml` -- extracts job `infra-purge-rollback`
    step `id: filter` `with.filters` literal-block scalar (which is itself
    a YAML mini-document under `infra-purge:`).

Asserts that the two describe the same set of paths, modulo the documented
translation rules:

  * Python regex `99_ARCHIVE/infra_purge_backup/.*\\.py` -> dorny glob
    `99_ARCHIVE/infra_purge_backup/**/*.py` (recursion via globstar).
  * Python regex `01_KERNEL/(memory|merlin)/(...|...)\\.py` -> one
    dorny line per matched filename (dorny lacks OR-alternation).
  * Other alternatives are literal-path one-to-one.
  * Comments inside the regex block are stripped before comparison.

Exits 0 on parity, 1 on any mismatch with a precise diagnostic.
"""
import re
import sys

import yaml

PRE_COMMIT = ".pre-commit-config.yaml"
WORKFLOW = ".github/workflows/verify_os.yml"
HOOK_ID = "infra-purge-rollback-verify"
JOB_ID = "infra-purge-rollback"
STEP_ID = "filter"
INFRA_PURGE_GROUP = "infra-purge"

# Translation table: 1:1 mirror between pre-commit regex and dorny filter.
# Mirrors the rules documented under `.github/workflows/verify_os.yml`
# Stage 8's drift-warning comment block (Option-b alignment, 2026-06-22).
TRANSLATION_TABLE = [
    {
        "name": "99_ARCHIVE infra_purge_backup recursive py",
        "regex_canonical": r"99_ARCHIVE/infra_purge_backup/.*\.py",
        "dorny_paths": ["99_ARCHIVE/infra_purge_backup/**/*.py"],
    },
    {
        "name": "01_KERNEL/memory rollback stores",
        "regex_canonical": (
            r"01_KERNEL/memory/"
            r"(redis_store|qdrant_store|local_store|local_sovereign_store|agent_memory)"
            r"\.py"
        ),
        "dorny_paths": [
            "01_KERNEL/memory/redis_store.py",
            "01_KERNEL/memory/qdrant_store.py",
            "01_KERNEL/memory/local_store.py",
            "01_KERNEL/memory/local_sovereign_store.py",
            "01_KERNEL/memory/agent_memory.py",
        ],
    },
    {
        "name": "01_KERNEL/merlin rollback consumers",
        "regex_canonical": (
            r"01_KERNEL/merlin/(merlin_omega|rag/chronos_haystack)\.py"
        ),
        "dorny_paths": [
            "01_KERNEL/merlin/merlin_omega.py",
            "01_KERNEL/merlin/rag/chronos_haystack.py",
        ],
    },
    {
        "name": "chimera_unified_kernel registry",
        "regex_canonical": r"01_KERNEL/config/registry/chimera_unified_kernel\.json",
        "dorny_paths": ["01_KERNEL/config/registry/chimera_unified_kernel.json"],
    },
    {
        "name": "boot_sequence",
        "regex_canonical": r"control_plane/boot_sequence\.py",
        "dorny_paths": ["control_plane/boot_sequence.py"],
    },
    {
        "name": "awaken",
        "regex_canonical": r"bin/awaken\.py",
        "dorny_paths": ["bin/awaken.py"],
    },
    {
        "name": "dependency manifest",
        "regex_canonical": r"(requirements\.txt|pyproject\.toml)",
        "dorny_paths": ["requirements.txt", "pyproject.toml"],
    },
    {
        "name": "plan doc",
        "regex_canonical": r"docs/plans/IMPLEMENTATION_INFRA_PURGE\.md",
        "dorny_paths": ["docs/plans/IMPLEMENTATION_INFRA_PURGE.md"],
    },
]


def fail(msg: str) -> "None":
    print(f"[FAIL] filter_parity: {msg}", file=sys.stderr)
    sys.exit(1)


def ok(msg: str) -> "None":
    print(f"[OK]   filter_parity: {msg}")


def load_precommit_regex_flat() -> str:
    """Load .pre-commit-config.yaml, locate the hook regex block,
    strip Python-style comments, flatten whitespace.
    """
    with open(PRE_COMMIT, "r", encoding="utf-8") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            fail(f"cannot parse {PRE_COMMIT}: {e}")

    hook = None
    for repo in config.get("repos", []) or []:
        for h in repo.get("hooks", []) or []:
            if h.get("id") == HOOK_ID:
                hook = h
                break
        if hook is not None:
            break
    if hook is None:
        fail(f"hook `id: {HOOK_ID}` not found in {PRE_COMMIT}")

    files = hook.get("files")
    if not isinstance(files, str):
        fail(
            f"hook `{HOOK_ID}` `files:` is not a string "
            f"(got {type(files).__name__})"
        )

    # Pre-commit's regex uses `(?x)` extended mode which permits
    # whitespace AND `# comment` lines inside the pattern. Strip the
    # comments first, then collapse whitespace.
    no_comments = re.sub(r"#.*", "", files)
    flat = re.sub(r"\s+", "", no_comments)
    return flat


def load_dorny_paths() -> list:
    """Load the workflow, locate the dorny filter step, re-parse the
    `filters:` literal-block scalar as a YAML mini-document, and pull
    the `infra-purge:` path list.
    """
    with open(WORKFLOW, "r", encoding="utf-8") as f:
        try:
            doc = yaml.safe_load(f)
        except yaml.YAMLError as e:
            fail(f"cannot parse {WORKFLOW}: {e}")

    job = doc.get("jobs", {}).get(JOB_ID)
    if job is None:
        fail(f"job `{JOB_ID}` not found in {WORKFLOW}")

    filter_step = None
    for s in job.get("steps", []) or []:
        if isinstance(s, dict) and s.get("id") == STEP_ID:
            filter_step = s
            break
    if filter_step is None:
        fail(f"step with `id: {STEP_ID}` not found in job `{JOB_ID}`")

    filters_text = filter_step.get("with", {}).get("filters")
    if not isinstance(filters_text, str):
        fail(
            f"`with.filters` in step `{STEP_ID}` is not a string "
            f"(got {type(filters_text).__name__})"
        )

    # Re-parse the literal-block scalar as a YAML mini-document so we
    # don't have to regex-extract quote-form paths (which would miss
    # double-quoted or unquoted entries).
    try:
        filters_doc = yaml.safe_load(filters_text)
    except yaml.YAMLError as e:
        fail(
            f"cannot re-parse `with.filters` literal-block scalar in "
            f"{WORKFLOW}: {e}"
        )
    if not isinstance(filters_doc, dict):
        fail(
            f"filters mini-document did not parse to a dict "
            f"(got {type(filters_doc).__name__})"
        )

    paths = filters_doc.get(INFRA_PURGE_GROUP)
    if not isinstance(paths, list):
        fail(
            f"filter group `{INFRA_PURGE_GROUP}` is not a list "
            f"(got {type(paths).__name__})"
        )
    return paths


def main() -> "None":
    flat_regex = load_precommit_regex_flat()
    dorny_paths = load_dorny_paths()

    # Surface dorny-side duplicate entries explicitly. The set-based
    # set-equality check below would mask them otherwise.
    if len(dorny_paths) != len(set(dorny_paths)):
        from collections import Counter

        counts = Counter(dorny_paths)
        dups = sorted(p for p, c in counts.items() if c > 1)
        fail(
            "dorny filter has duplicate entries (set equality below "
            "would mask this):\n  " + "\n  ".join(dups)
        )

    # Build the union of expected dorny paths from the translation table,
    # enforcing that no path is claimed by multiple categories.
    expected_dorny: set = set()
    for entry in TRANSLATION_TABLE:
        for p in entry["dorny_paths"]:
            if p in expected_dorny:
                fail(
                    f"translation table has a duplicate dorny path `{p}` "
                    f"(claimed by `{entry['name']}` and earlier category)"
                )
            expected_dorny.add(p)

    # 1. Each canonical regex alternative must appear as a substring
    #    of the flattened pre-commit regex.
    for entry in TRANSLATION_TABLE:
        flat_canonical = re.sub(r"\s+", "", entry["regex_canonical"])
        if flat_canonical not in flat_regex:
            fail(
                f"pre-commit regex is missing canonical alternative "
                f"`{flat_canonical}` for category `{entry['name']}`"
            )
    ok(
        f"all {len(TRANSLATION_TABLE)} translation categories' canonical "
        f"regex alternatives present in pre-commit config"
    )

    # 2. Set equality between actual dorny paths and expected dorny paths.
    actual_dorny: set = set(dorny_paths)

    extra = actual_dorny - expected_dorny
    if extra:
        fail(
            "dorny filter contains paths not in any translation category:\n  "
            + "\n  ".join(sorted(extra))
        )

    missing = expected_dorny - actual_dorny
    if missing:
        fail(
            f"translation table requires these dorny paths not present "
            f"in workflow `{JOB_ID}` step `{STEP_ID}` "
            f"filter group `{INFRA_PURGE_GROUP}`:\n  "
            + "\n  ".join(sorted(missing))
        )

    ok(
        f"all {len(actual_dorny)} dorny paths trace to exactly one "
        f"translation category; no orphans, no missing"
    )

    print("[PASS] filter_parity: pre-commit and dorny filters are aligned")


if __name__ == "__main__":
    main()
