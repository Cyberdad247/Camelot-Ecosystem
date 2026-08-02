#!/usr/bin/env bash
# CAMELOT_OS/bin/pre_flight.sh — PR #5 (gate-of-gates) for Mnemosyne wiring.
#
# Operator-invariant from 2026-07-14 directive (Phase 2):
#   "*Write the pre-flight.js or pre-flight.sh script that automatically scans
#    the local directory, generates the file tree, and compares it against the
#    NotebookLM master schema before allowing any other agentic actions.*"
#
# Behavior:
#   - Walks $REPO_ROOT recursively
#   - Generates a file tree JSON (path, kind, size_bytes, mtime_unix, sig_sha256)
#   - Loads master schema at docs/schemas/notebooklm_master_schema.json
#   - Classifies drift into 3 categories:
#       critical drift   → exit 2  (Heimdall veto; control_plane / pyproject)
#       general drift    → exit 1  (operator block; supernumerary files)
#       bootstrap drift  → exit 3  (operator re-bootstrap required)
#       no drift         → exit 0
#   - Structured STDERR log emitted ONLY on failure (avoid log spam)
#
# Pre-conditions (handled gracefully):
#   - Master schema MUST exist (else exit 2; pre-flight refuses to run blind)
#   - python3 with json+hashlib stdlib (gate-tested by CONTROL_PLANE pre-req)
#
# Usage:
#   bash CAMELOT_OS/bin/pre_flight.sh \
#        [REPO_ROOT]                # default: cwd
#        [OUT_JSON]                 # default: $REPO_ROOT/03_VAULT/runtime_state/notebooklm_tree_latest.json
#        [SCHEMA_FILE]              # default: $REPO_ROOT/docs/schemas/notebooklm_master_schema.json
#
# Returns:
#   0  matches schema (proceed)
#   1  general drift (operator block; usually extra files)
#   2  critical drift (Heimdall veto; missing core control_plane files / pyproject)
#   3  bootstrap drift (.env.appwrite example present but live .env.appwrite missing; manual re-bootstrap required)

set -eo pipefail

# ── Argument parsing ────────────────────────────────────────────────────────────
REPO_ROOT="${1:-$(pwd)}"
OUT_JSON="${2:-$REPO_ROOT/03_VAULT/runtime_state/notebooklm_tree_latest.json}"
SCHEMA_FILE="${3:-$REPO_ROOT/docs/schemas/notebooklm_master_schema.json}"

# ── Resolve REPO_ROOT to absolute path (handles symlinks + relative paths) ───
REPO_ROOT="$(cd "$REPO_ROOT" 2>/dev/null && pwd || echo "$REPO_ROOT")"
OUT_JSON="$(cd "$(dirname "$OUT_JSON")" 2>/dev/null && pwd)/$(basename "$OUT_JSON")"
SCHEMA_FILE="$(cd "$(dirname "$SCHEMA_FILE")" 2>/dev/null && pwd)/$(basename "$SCHEMA_FILE")"

# ── Pre-requisite checks (early-out with critical-drift if prerequisites missing) ──
# Detect a usable Python interpreter (Windows-friendly: try python3, then python, then py).
PYTHON=$(command -v python3 || command -v python || command -v py)
[ -n "$PYTHON" ] || {
    echo 'pre_flight CRITICAL: no usable Python interpreter found (tried python3, python, py)' >&2
    exit 2
}
# Gate: refuse Python <3.6 (f-strings used in heredoc; python2 f-string SyntaxError would be opaque)
"$PYTHON" -c "import sys; sys.exit(0 if sys.version_info >= (3,6) else 1)" 2>/dev/null || {
    PYVER=$("$PYTHON" --version 2>&1)
    echo "pre_flight CRITICAL: Python >=3.6 required (got $PYVER)" >&2
    exit 2
}
[ -f "$SCHEMA_FILE" ] || {
    echo "pre_flight CRITICAL: master schema not found at $SCHEMA_FILE (refusing to run blind)" >&2
    exit 2
}

# ── Inline Python: walk tree → load schema → classify drift → emit JSON ────────
# (runs as a direct child of bash, not via $() capture — exit code propagates cleanly)
"$PYTHON" - "$REPO_ROOT" "$OUT_JSON" "$SCHEMA_FILE" << 'PYEOF'
import hashlib, json, os, re, sys, time
from pathlib import Path

REPO_ROOT = Path(sys.argv[1]).resolve()
OUT_JSON = Path(sys.argv[2])
SCHEMA_FILE = Path(sys.argv[3])

# ── Walk constraints (matches D1 + D7 risk mitigations) ──────────────────────
SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", "data", "99_ARCHIVE", "99_HISTORY",
    ".ruff_cache", ".pytest_cache", ".pytest_temp",
    ".worktrees", "node_modules", "target", ".cargo",
}
INCLUDE_EXTS = {
    ".py", ".sh", ".ts", ".tsx", ".js", ".mjs", ".cjs",
    ".md", ".yml", ".yaml", ".toml", ".json", ".lock",
    ".txt", ".cfg", ".ini",
    ".env",  # dev-secret files with .env suffix (e.g. stray_untracked_secret.env)
}
# Special-case filenames with NO suffix that are still relevant for gate enforcement.
# `Path(".env").suffix` returns "", so the INCLUDE_EXTS check above would skip them.
INCLUDE_BASENAMES = {".env"}
CACHE_DIR_FRAGMENT = "runtime_state/notebooklm_cache"
SIZE_CAP_BYTES = 1_048_576  # 1 MB

# ── Walk tree ────────────────────────────────────────────────────────────────
tree = []
ext_counts = {}
for root, dirs, files in os.walk(REPO_ROOT):
    # In-place filter (don't descend into skipped dirs)
    dirs[:] = sorted(
        d for d in dirs
        if d not in SKIP_DIRS
        and not d.startswith(".")
        and not d.startswith("_")
    )
    # Skip cache directory entirely
    if CACHE_DIR_FRAGMENT in root.replace("\\", "/"):
        continue

    # Add an entry for each kept directory (helps drift detection on missing dirs)
    if root != str(REPO_ROOT):
        rel = os.path.relpath(root, REPO_ROOT).replace("\\", "/")
        tree.append({
            "path": rel,
            "kind": "dir",
            "size_bytes": 0,
            "mtime_unix": os.path.getmtime(root),
            "signature_sha256": None,
        })

    for name in sorted(files):
        if name not in INCLUDE_BASENAMES and Path(name).suffix.lower() not in INCLUDE_EXTS:
            continue
        fpath = Path(root) / name
        rel_path = fpath.relative_to(REPO_ROOT).as_posix()
        try:
            stat = fpath.stat()
        except OSError:
            continue
        size = stat.st_size
        ext_counts[Path(name).suffix.lower()] = ext_counts.get(Path(name).suffix.lower(), 0) + 1
        # 1 MB cap on sha256 (D7 Risk B mitigation)
        sig = None
        if 0 < size <= SIZE_CAP_BYTES:
            try:
                sig = hashlib.sha256(fpath.read_bytes()).hexdigest()
            except OSError:
                sig = None
        elif size > SIZE_CAP_BYTES:
            sig = "<size-cap:file-too-large>"
        tree.append({
            "path": rel_path,
            "kind": "file",
            "size_bytes": size,
            "mtime_unix": stat.st_mtime,
            "signature_sha256": sig,
        })

# ── Load master schema ──────────────────────────────────────────────────────
with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
    master = json.load(f)

# ── D3 drift-classifier ──────────────────────────────────────────────────────
required_files = master.get("required_files", [])
required_paths_re = [re.compile(p) for p in master.get("required_paths", [])]
allowed_paths_re = [re.compile(p) for p in master.get("allowed_paths_regex", [])]
forbidden_paths_re = [re.compile(p) for p in master.get("forbidden_paths", [])]
thresholds = master.get("thresholds", {})

live_paths = {entry["path"] for entry in tree if entry["kind"] == "file"}

critical_drift = []
general_drift = []
bootstrap_drift = []

# 1. Required files (path equality; kind sanity)
for req in required_files:
    rel = req.get("path", "").lstrip("/")
    if not rel:
        continue
    expected_kind = req.get("kind", "")
    if rel not in live_paths:
        critical_drift.append(f"missing required file: {rel}")
        continue
    # Kind sanity (file vs dir)
    live = next((e for e in tree if e["path"] == rel), None)
    if live and live["kind"] != "file":
        critical_drift.append(f"required path not a file: {rel}")

# 2. Required path regex coverage (D2 — patterns must have ≥1 match)
for pattern_re in required_paths_re:
    matches = [p for p in live_paths if pattern_re.search(p)]
    if not matches:
        critical_drift.append(f"required path pattern unmatched: {pattern_re.pattern}")

# 3. Forbidden path patterns (e.g. untracked .env files)
forbidden_hits = []
for pattern_re in forbidden_paths_re:
    hits = [p for p in live_paths if pattern_re.search(p)]
    forbidden_hits.extend(hits)
if forbidden_hits:
    general_drift.append(
        f"forbidden paths detected (likely untracked secrets / leftovers): {forbidden_hits}"
    )

# 4. Supermumerary files (extra files not in schema) — general-drift
schema_paths = {req.get("path", "").lstrip("/") for req in required_files}
# A file is "schema-allowed" if it matches any required_path regex, any allowed_paths_regex,
# OR is in schema_paths explicitly. allowed_paths_regex lets the schema tolerate common
# types (e.g. control_plane/*.py anywhere) without flagging bulk-realism as drift —
# required_paths still enforces the named anchors as critical.
allowed_via_regex = set()
for pattern_re in required_paths_re + allowed_paths_re:
    allowed_via_regex.update(p for p in live_paths if pattern_re.search(p))
allowed_full = schema_paths | allowed_via_regex
extras = sorted(p for p in live_paths if p not in allowed_full)
# Don't flag files that are obviously expected to exist (gate-friendly ignore zones)
IGNORE_BASENAMES = {
    "__init__.py", "package.json", "package-lock.json", "tsconfig.json",
    "pyproject.toml", "README.md", "gitignore", ".gitignore",
    "Dockerfile", "Makefile",
}
extras_filtered = [
    p for p in extras
    if Path(p).name not in IGNORE_BASENAMES  # type: ignore
    and not p.endswith(".pyc")
    and ".pytest_cache" not in p
    and "runtime_state" not in p  # runtime_state is intentionally self-tracked
]
if extras_filtered:
    general_drift.append(
        f"supernumerary files outside schema: {len(extras_filtered)} (first 5: {extras_filtered[:5]})"
    )

# 5. Bootstrap drift (D3): example present but live missing (operator re-bootstrap required)
# Resolve relative to repo root (one-shot, supports both layouts)
def repo_rel(p):
    """Try p against REPO_ROOT directly, then under CAMELOT_OS/ subdir.
    Returns the relative path string if the file exists, else None.
    Handles both pre-flight invocations:
      A) REPO_ROOT == $VIZIO_HOME/CAMELOT_OS   -> finds ".env.appwrite.example"
      B) REPO_ROOT == $VIZIO_HOME              -> finds "CAMELOT_OS/.env.appwrite.example"
    """
    p = p.lstrip("/")
    for cand_rel in (p, f"CAMELOT_OS/{p}"):
        try:
            if (REPO_ROOT / cand_rel).is_file():
                return cand_rel
        except OSError:
            continue
    return None

example_rel = repo_rel(".env.appwrite.example")
live_rel    = repo_rel(".env.appwrite")
if example_rel and not live_rel:
    bootstrap_drift.append(
        f"example env present (at {example_rel}) but live {live_rel or '.env.appwrite'} missing — operator must run bash CAMELOT_OS/bin/appwrite_bootstrap.sh"
    )

# 6. Threshold sanity (D2)
min_python = thresholds.get("min_python_files", 0)
python_files = ext_counts.get(".py", 0)
if min_python and python_files < min_python:
    # Reclassified to general_drift: a low python file count implies operator attention
    # (structural truncation) but is NOT a Heimdall veto — required_files already enforces
    # canonical module presence. Threshold exists as a quality-floor not a hard fail.
    general_drift.append(
        f"python file count {python_files} below threshold {min_python}"
    )

# ── Build output ────────────────────────────────────────────────────────────
drift = {
    "matches_schema": not (critical_drift or general_drift or bootstrap_drift),
    "critical": critical_drift,
    "general": general_drift,
    "bootstrap": bootstrap_drift,
}

output = {
    "schema_version": master.get("schema_version"),
    "tier": master.get("tier"),
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "repo_root": str(REPO_ROOT),
    "stats": {
        "files_total": len([e for e in tree if e["kind"] == "file"]),
        "files_python": ext_counts.get(".py", 0),
        "files_shell": ext_counts.get(".sh", 0),
        "files_typescript": ext_counts.get(".ts", 0) + ext_counts.get(".tsx", 0),
        "files_markdoc": ext_counts.get(".md", 0),
        "files_yaml": ext_counts.get(".yml", 0) + ext_counts.get(".yaml", 0),
        "files_toml": ext_counts.get(".toml", 0),
        "files_json": ext_counts.get(".json", 0),
    },
    "tree": tree,
    "drift": drift,
}

# ── Persist tree JSON (safe makedirs) ────────────────────────────────────────
OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

# Decide exit code (D3 classification)
if drift["bootstrap"]:
    sys.exit(3)
if drift["critical"]:
    sys.exit(2)
if drift["general"]:
    sys.exit(1)
sys.exit(0)
PYEOF
PY_EXIT=$?

# ── Structured STDERR log ONLY on drift (avoid log spam in clean case) ─────────
if [ $PY_EXIT -ne 0 ]; then
    TS=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date +%Y-%m-%dT%H:%M:%SZ)
    echo "{\"event\":\"pre_flight_drift_detected\",\"exit_code\":$PY_EXIT,\"report\":\"$OUT_JSON\",\"timestamp\":\"$TS\"}" >&2
fi

exit $PY_EXIT
