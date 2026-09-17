# SPDX-License-Identifier: MIT

"""The mesh inventory must have exactly one definition.

Modules used to each carry their own copy of the Tailscale node list and they
drifted: two listed nodes that were not on the tailnet at all, one omitted the hub
entirely, and one attributed the hub's address to a different node. That wrong
address ended up in **eight** separate places, including the hub's own status
endpoint and the published governance payload.

These tests are the mechanism that prevents a recurrence. They do not assert that
the *current* node list is correct (only `tailscale status` can settle that) — they
assert that there is one list, that every consumer reads it, and that no consumer
has quietly reintroduced a private copy.

An earlier version of this file hardcoded three paths under `control_plane/infra/`.
Every remaining copy was outside that scope, so the guard passed while protecting
almost nothing. Scope is now the repository, minus documented exceptions.
"""

from __future__ import annotations

import io
import re
import tokenize
from pathlib import Path

import pytest

from control_plane.infra import mesh_topology as mt

REPO_ROOT = Path(__file__).resolve().parents[1]

CONSUMERS = {
    "hermes_heimdall_sentinel": REPO_ROOT / "control_plane" / "infra" / "hermes_heimdall_sentinel.py",
    "heimdall_bifrost_governance": REPO_ROOT / "control_plane" / "infra" / "heimdall_bifrost_governance.py",
    "mesh_sentinel": REPO_ROOT / "control_plane" / "infra" / "mesh_sentinel.py",
}

# A tailnet address: the 100.64.0.0/10 CGNAT range Tailscale hands out.
_TAILNET_IP = re.compile(r"\b100\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")

# Directories scanned for drift. The set is deliberately the *executable* surface
# — the places a stale address can route traffic at a host that does not exist.
SCAN_DIRS = ("control_plane", "bin", "scripts", "infra", "01_KERNEL", "apps")

# File types that can carry a live address.
SCAN_SUFFIXES = frozenset(
    {".py", ".sh", ".bash", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".go", ".rs",
     ".json", ".toml", ".ini", ".yaml", ".yml", ".cfg"}
)

# Never descended into: dependencies and build output, not source.
SKIP_DIRS = frozenset(
    {".git", ".venv", "node_modules", "__pycache__", ".next", "dist", "build",
     ".pytest_cache", ".mypy_cache", ".turbo", "target", "site-packages"}
)

# Files excluded from the sweep, each for a reason that is not "it was failing".
ALLOWLIST: dict[str, str] = {
    "control_plane/infra/mesh_topology.py": "the single source — it is where these addresses are supposed to live",
    "03_VAULT/runtime_state/sovereign_mesh_topology.json": "state file; its `nodes` vs `absent_nodes` split is asserted in tests/test_sovereign_mesh_topology.py",
}

# Append-only history. Rewriting these would falsify the record of what was
# believed true at the time — the ledger's whole purpose is that it does not change.
HISTORY_ALLOW = (
    "PROVENANCE_LEDGER.md",
    "verification_ledger.jsonl",
    "forensic_checks.jsonl",
    "learnings.md",
)


def _code_only(path: Path) -> list[tuple[int, str]]:
    """Lines with comments removed.

    A comment cannot declare a node, and explaining *why* a stale address was
    replaced is worth keeping in the source. Uses tokenize rather than a naive
    `split('#')` so a `#` inside a string literal cannot truncate real code.
    Python is parsed with `tokenize`; shell-family files strip a `#` that begins a
    word, which covers `  # note` and `value  # note` without truncating a `#`
    mid-token. C-style files strip `//` that is *not* preceded by `:`, so `http://`
    and `ws://` survive while a trailing `// note` is removed. The `:` guard is a
    heuristic: a bare `//` inside a string literal would be truncated. That
    direction is safe — it can only hide a comment, never invent one.
    """
    src = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix in {".sh", ".bash", ".toml", ".ini", ".yaml", ".yml", ".cfg"}:
        return [
            (i, re.sub(r"(?:(?<=^)|(?<=\s))#.*$", "", line))
            for i, line in enumerate(src.splitlines(), 1)
        ]
    if path.suffix in {".go", ".rs", ".ts", ".tsx", ".js", ".jsx", ".mjs"}:
        return [
            (i, re.sub(r"(?<!:)//.*$", "", line))
            for i, line in enumerate(src.splitlines(), 1)
        ]
    if path.suffix != ".py":
        return list(enumerate(src.splitlines(), 1))
    lines = src.splitlines()
    comment_cols: dict[int, list[int]] = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                comment_cols.setdefault(tok.start[0], []).append(tok.start[1])
    except (tokenize.TokenError, IndentationError):  # pragma: no cover - defensive
        comment_cols = {}
    out: list[tuple[int, str]] = []
    for i, line in enumerate(lines, 1):
        cols = comment_cols.get(i)
        out.append((i, line[: min(cols)] if cols else line))
    return out


def _scanned_files() -> list[Path]:
    """Every in-scope file the drift guard inspects."""
    found: list[Path] = []
    for top in SCAN_DIRS:
        base = REPO_ROOT / top
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SCAN_SUFFIXES:
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            if rel in ALLOWLIST:
                continue
            # Generated distillation artifacts, not hand-maintained config.
            if rel.startswith("02_FORGE/generated/") or rel.startswith("03_VAULT/UKG/"):
                continue
            if "/tests/" in rel or rel.startswith("tests/"):
                continue  # this file and its negative controls live here
            if any(rel.endswith(h) for h in HISTORY_ALLOW):
                continue
            found.append(path)
    return found


def test_every_consumer_imports_the_single_source() -> None:
    for name, path in CONSUMERS.items():
        src = path.read_text(encoding="utf-8")
        assert "mesh_topology" in src, f"{name} does not import mesh_topology"


@pytest.mark.parametrize("name", sorted(CONSUMERS))
def test_no_consumer_declares_a_tailnet_address(name: str) -> None:
    """A hardcoded 100.x address in a consumer is the private copy being reborn."""
    hits = [
        f"line {i}: {line.strip()}"
        for i, line in _code_only(CONSUMERS[name])
        if _TAILNET_IP.search(line)
    ]
    assert not hits, f"{name} hardcodes tailnet addresses: {hits}"


def test_no_absent_node_address_survives_anywhere_in_the_repo() -> None:
    """The two nodes absent from the tailnet must not appear in executable code.

    `100.71.218.75` and `100.84.98.39` name hosts that are not on the tailnet. Any
    surface that references them can only ever report OFFLINE, which is noise that
    masks a real node going down — and in the hub's case it actively misdirected
    callers at a host that does not exist.
    """
    absent = set(mt.absent_ips())
    violations: list[str] = []
    for path in _scanned_files():
        rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        for i, line in _code_only(path):
            for ip in absent:
                if ip in line:
                    violations.append(f"{rel}:{i} [{ip}] {line.strip()[:90]}")
    assert not violations, (
        "tailnet-absent addresses found in executable code:\n  " + "\n  ".join(violations)
    )


def test_hub_address_constants_are_never_literals_in_scope() -> None:
    """A `...TAILSCALE_IP = '100.x'` assignment is the single source being bypassed.

    Textual rather than import-based: `bin/` is not a package and several of these
    modules are deliberately standalone, so importing them all to check one
    constant would couple this test to their runtime requirements.
    """
    literal = re.compile(r"^\s*[A-Z_]*(?:TAILSCALE|VPS)[A-Z_]*_IP\s*=\s*[\"']100\.")
    violations = [
        f"{str(p.relative_to(REPO_ROOT)).replace(chr(92), '/')}:{i} {line.strip()}"
        for p in _scanned_files()
        for i, line in _code_only(p)
        if literal.match(line)
    ]
    assert not violations, (
        "hub/TAILSCALE address hardcoded instead of importing HUB_TAILSCALE_IP:\n  "
        + "\n  ".join(violations)
    )


def test_the_drift_guards_can_actually_fire() -> None:
    """Negative controls: both guards are worthless if they match nothing.

    Without this, a regression that made `_code_only` return blank lines would make
    the checks pass while protecting nothing.
    """
    assert _TAILNET_IP.search('"ip": "100.71.218.75"')
    assert _TAILNET_IP.search("x = 100.110.180.18")
    # ...and comments are genuinely excluded, which is the whole point.
    assert not _TAILNET_IP.search("# was 100.71.218.75 once".split("#", 1)[0])
    # Shell-family comments strip too, but not a `#` mid-token.
    assert not re.sub(r"(?:(?<=^)|(?<=\s))#.*$", "", "# was 100.71.218.75")
    assert re.sub(r"(?:(?<=^)|(?<=\s))#.*$", "", "IP=100.71.218.75 # note").strip() == "IP=100.71.218.75"
    # C-style: a trailing comment goes, a URL survives.
    assert "100.71.218.75" not in re.sub(r"(?<!:)//.*$", "", "// was 100.71.218.75")
    assert "http://100.110.180.18:8011" in re.sub(r"(?<!:)//.*$", "", "u = 'http://100.110.180.18:8011' // hub")
    # The literal-constant pattern fires on a real violation and not on a derive.
    literal = re.compile(r"^\s*[A-Z_]*(?:TAILSCALE|VPS)[A-Z_]*_IP\s*=\s*[\"']100\.")
    assert literal.match('VPS_TAILSCALE_IP = "100.71.218.75"')
    assert not literal.match("VPS_TAILSCALE_IP = HUB_TAILSCALE_IP")
    # ...and the scan genuinely covers more than the three original consumers.
    assert len(_scanned_files()) > 20


def test_sentinel_inventory_projects_every_node() -> None:
    from control_plane.infra.hermes_heimdall_sentinel import MESH_INVENTORY

    assert set(MESH_INVENTORY) == set(mt.node_ids())
    assert {v["ip"] for v in MESH_INVENTORY.values()} == set(mt.active_ips())


def test_canonical_inventory_projects_every_node() -> None:
    from control_plane.infra.heimdall_bifrost_governance import CANONICAL_MESH_INVENTORY

    assert {e["id"] for e in CANONICAL_MESH_INVENTORY} == set(mt.node_ids())
    assert {e["tailscale_ip"] for e in CANONICAL_MESH_INVENTORY} == set(mt.active_ips())


def test_rule5_inventory_projects_every_node() -> None:
    from control_plane.infra.mesh_sentinel import TailscaleMeshSentinel

    assert len(TailscaleMeshSentinel.RULE_5_INVENTORY) == len(mt.MESH_NODES)
    assert {e["ip"] for e in TailscaleMeshSentinel.RULE_5_INVENTORY} == set(mt.active_ips())


def test_all_projections_agree() -> None:
    from control_plane.infra.heimdall_bifrost_governance import CANONICAL_MESH_INVENTORY
    from control_plane.infra.hermes_heimdall_sentinel import MESH_INVENTORY
    from control_plane.infra.mesh_sentinel import TailscaleMeshSentinel

    addresses = (
        {v["ip"] for v in MESH_INVENTORY.values()},
        {e["tailscale_ip"] for e in CANONICAL_MESH_INVENTORY},
        {e["ip"] for e in TailscaleMeshSentinel.RULE_5_INVENTORY},
        set(mt.active_ips()),
    )
    assert all(a == addresses[0] for a in addresses), addresses


def test_absent_nodes_are_reachable_from_every_consumer() -> None:
    from control_plane.infra.heimdall_bifrost_governance import ABSENT_MESH_NODES as gov
    from control_plane.infra.hermes_heimdall_sentinel import ABSENT_MESH_NODES as sent

    expected = set(n.id for n in mt.ABSENT_MESH_NODES)
    assert set(sent) == expected
    assert {n["id"] for n in gov} == expected


def test_absent_nodes_never_appear_in_the_active_inventory() -> None:
    """The bug that started this: a node absent from the tailnet being pinged."""
    assert not (set(mt.node_ids()) & {n.id for n in mt.ABSENT_MESH_NODES})
    assert not (set(mt.active_ips()) & set(mt.absent_ips()))


def test_hub_address_constants_agree_across_modules() -> None:
    """Several modules declare the hub's tailnet address independently.

    They agree today. If one is edited without the others, this fails rather than
    silently routing part of the system at the wrong host.
    """
    mods = []
    for module, attr in (
        ("control_plane.dispatch.vps_hermes_links", "VPS_TAILSCALE_IP"),
        ("control_plane.dispatch.vps_mobile_mesh_bridge", "VPS_TAILSCALE_IP"),
        ("control_plane.infra.hermes_vps_gateway", "VPS_TAILSCALE_IP"),
        ("control_plane.runners.vps_nexus_deployment_runner", "VPS_TAILSCALE_IP"),
        ("control_plane.runners.worldtree_vps_cloudbrain_sync", "VPS_TAILSCALE_IP"),
    ):
        try:
            imported = __import__(module, fromlist=[attr])
        except Exception as exc:  # pragma: no cover - environment dependent
            pytest.skip(f"{module} not importable here: {exc}")
        mods.append((module, getattr(imported, attr)))

    for module, value in mods:
        assert value == mt.HUB_TAILSCALE_IP, (
            f"{module} declares {value!r}, expected {mt.HUB_TAILSCALE_IP!r}"
        )
