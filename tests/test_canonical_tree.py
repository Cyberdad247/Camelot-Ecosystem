# SPDX-License-Identifier: MIT
"""Every operational file must agree on ONE Camelot-OS checkout.

WHY THIS TEST EXISTS

The hub carried two checkouts whose names differ only by case. The filesystem is
case-sensitive, so they were genuinely different directories at different commits:

    /opt/Camelot-Ecosystem   990300d1   stale bootstrap clone   (now RETIRED)
    /opt/camelot-ecosystem   canonical checkout

The stale one was not obviously broken, which is why it survived. What made it dangerous
was that it was still WIRED IN:

* `camelot-vps-mesh.service` ran from it, via an `ExecStart` naming a module that does not
  exist in that tree. The service was only alive because a drop-in pointed its
  WorkingDirectory elsewhere — one `systemctl edit --full` from a unit that could not start.
* `CAMELOT_OS_HOME` named it, so the live process carried a path to a tree its own code was
  not loaded from. Inert for today's modules, but `control_plane.dispatch.bifrost` and its
  siblings DO read that variable — any future import of one of them would resolve against a
  directory that no longer exists.
* `vps_hub_bootstrap.sh` installed units FROM it, and its `pull --ff-only origin main` was a
  no-op on a tree checked out to `feat/cloudbrain-zero-login-autonomous`. That combination is
  how the hub came to carry a `--loop 60` unit upstream had already replaced.

A single stale path in a single unit file is enough to reintroduce all of it, so this test
enumerates every operational file rather than spot-checking.

THE PROSE PROBLEM

Comments are excluded everywhere here. A guard must be able to NAME the thing it guards
against, and `camelot-hermes-prime.service` documents the retired path by name in a comment
explaining why it was abandoned. Earlier guards in this codebase were trained on full-line
comments only and stayed silent when a mutation appended its marker to the end of a live
line, so `_directive_lines` strips inline comments too.

Consequently the rule for the retired path is narrow but exact: it may appear in prose, and
it may be DECLARED once per file as a variable assignment, but never as a live setting.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_TREE = "/opt/camelot-ecosystem"
RETIRED_TREE = "/opt/Camelot-Ecosystem"

UNIT_DIR = REPO_ROOT / "infra/systemd"

# Files permitted to DECLARE the retired path, because naming their subject is their job.
DECLARATION_ALLOWLIST = {
    "scripts/vps_hub_bootstrap.sh",  # declares it once so its guards can reference it
    "scripts/ops/retire-uppercase-tree.sh",  # the migration whose subject it is
}

# A whole-line assignment: NAME="..." or NAME="${NAME:-...}"
_DECLARATION = re.compile(rf"^[A-Za-z_][A-Za-z0-9_]*=")


def _operational_files() -> list[Path]:
    """Files that are read by systemd or executed by a shell on the hub."""
    found: set[Path] = set()
    found.update(p for p in UNIT_DIR.glob("*") if p.is_file())
    found.update(p for p in (REPO_ROOT / "scripts").rglob("*.sh") if p.is_file())
    return sorted(found)


def _directive_lines(path: Path) -> list[tuple[int, str]]:
    """(lineno, code) pairs — comments removed, full-line and inline alike."""
    out: list[tuple[int, str]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        out.append((lineno, re.split(r"\s#", raw, maxsplit=1)[0]))
    return out


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def test_the_scan_is_not_vacuous() -> None:
    """Globs that match nothing would make every assertion below silently pass."""
    files = _operational_files()
    units = [p for p in files if p.parent == UNIT_DIR]
    scripts = [p for p in files if p.suffix == ".sh"]
    assert len(units) > 15, f"only {len(units)} unit files found"
    assert len(scripts) > 15, f"only {len(scripts)} scripts found"
    assert any(p.name == "vps_hub_bootstrap.sh" for p in files)


def test_no_operational_file_uses_the_retired_tree_as_a_setting() -> None:
    offenders: list[str] = []
    for path in _operational_files():
        rel = _rel(path)
        for lineno, code in _directive_lines(path):
            if RETIRED_TREE not in code:
                continue
            if rel in DECLARATION_ALLOWLIST and _DECLARATION.match(code.strip()):
                continue  # a declaration, not a setting
            offenders.append(f"{rel}:{lineno}: {code.strip()}")
    assert not offenders, (
        "these lines name the retired checkout as a live setting:\n  "
        + "\n  ".join(offenders)
    )


def test_the_retired_tree_is_declared_at_most_once_per_file() -> None:
    """Each allowed file must name it once, so a guard reads as a guard.

    A guard that spells out its own subject four times cannot be distinguished from a
    dependency on it — which is exactly how the retired tree stayed load-bearing.
    """
    for name in sorted(DECLARATION_ALLOWLIST):
        path = REPO_ROOT / name
        assert path.is_file(), f"allow-listed file is missing: {name}"
        declares = [
            (lineno, code)
            for lineno, code in _directive_lines(path)
            if RETIRED_TREE in code
        ]
        assert len(declares) == 1, (
            f"{name} should declare the retired path exactly once, "
            f"found {len(declares)}: {declares}"
        )
        assert _DECLARATION.match(declares[0][1].strip()), (
            f"{name}:{declares[0][0]} is not a declaration: {declares[0][1].strip()}"
        )


def test_units_resolve_their_root_to_the_canonical_tree() -> None:
    """A unit must not name a Camelot checkout other than the canonical one.

    Scoped to Camelot checkouts on purpose. `/opt/luxora-nexus-lab` is a different project
    with its own WorkingDirectory, and an earlier revision of this test flagged it — the
    assertion was too broad, not the unit. Sibling deployments under /opt are expected; two
    spellings of the SAME deployment are the defect.
    """
    keys = ("WorkingDirectory=", "CAMELOT_OS_HOME=", "ReadWritePaths=", "Documentation=file://")
    offenders: list[str] = []
    for unit in sorted(p for p in UNIT_DIR.glob("*") if p.is_file()):
        for lineno, code in _directive_lines(unit):
            stripped = code.strip()
            if not stripped.startswith(keys):
                continue
            for token in re.findall(r"/opt/[A-Za-z0-9._-]+", stripped):
                if token.lower().startswith("/opt/camelot") and not token.startswith(CANONICAL_TREE):
                    offenders.append(f"{unit.name}:{lineno}: {stripped}")
    assert not offenders, (
        "units resolve against a Camelot checkout other than the canonical one:\n  "
        + "\n  ".join(offenders)
    )


def test_the_three_formerly_stale_units_are_canonical() -> None:
    """The units that actually pointed at the retired tree are pinned explicitly.

    The generic test above would pass if someone deleted these units' root settings
    entirely; naming them keeps the intent legible when this file is read alone.
    """
    for name in ("camelot-vps-mesh.service", "camelot-heimdall-bifrost.service",
                 "hermes-bifrost-sentinel.service", "hermes-notebook-compactor.service",
                 "camelot-evaluation.service"):
        text = (UNIT_DIR / name).read_text(encoding="utf-8-sig")
        assert f"WorkingDirectory={CANONICAL_TREE}" in text, f"{name} is not canonical"


def test_bootstrap_defaults_to_the_canonical_tree() -> None:
    text = (REPO_ROOT / "scripts/vps_hub_bootstrap.sh").read_text(encoding="utf-8-sig")
    assert f'CUBE_DIR="${{CUBE_DIR:-{CANONICAL_TREE}}}"' in text, (
        "the bootstrap must default CUBE_DIR to the canonical checkout; every unit it "
        "installs is read from there, so a stale default overwrites the live set"
    )


def test_bootstrap_installs_timers_as_well_as_services() -> None:
    """The timers it asserts are active must be installable by it.

    The original glob was `*.service` only, so a fresh hub could never satisfy the
    contract this same file checks at the end.
    """
    text = (REPO_ROOT / "scripts/vps_hub_bootstrap.sh").read_text(encoding="utf-8-sig")
    assert '"$CUBE_DIR"/infra/systemd/*.timer' in text, (
        "timers are asserted active but never installed"
    )


def test_bootstrap_gates_the_unit_install_on_a_valid_payload() -> None:
    """The `cp` over live units must be gated on a payload that is present AND current.

    Structural, not textual: an install that happens before (or outside) that gate replaces
    a working monitor — or a working gateway — with whatever the source tree contains.
    """
    path = REPO_ROOT / "scripts/vps_hub_bootstrap.sh"
    lines = [c.strip() for _, c in _directive_lines(path)]

    def index(predicate, what: str) -> int:
        hit = next((i for i, c in enumerate(lines) if predicate(c)), None)
        assert hit is not None, f"{what} is gone from the bootstrap"
        return hit

    verifier = index(lambda c: c.startswith("verify_payload()"), "the payload verifier")
    checked = index(
        lambda c: c.startswith("if ") and "verify_payload" in c, "the payload check call"
    )
    install = index(
        lambda c: 'cp "${units[@]}" /etc/systemd/system/' in c, "the unit install"
    )
    assert verifier < checked < install, "units are installed before the payload is verified"
    assert any(
        c.startswith("if (( PAYLOAD_OK ))") for c in lines[checked:install]
    ), "the install is not gated on a valid payload"


def test_payload_validity_covers_presence_AND_staleness() -> None:
    """A checkout can carry every required file and still be behind.

    The hub's own tree did exactly that: its camelot-bifrost.service shipped
    `ExecStart=/usr/local/bin/camelot-bifrost` — a binary that was never built, i.e. the
    service cannot start — plus a reference to the retired tree. A presence-only preflight
    passes that payload and installs it over a working gateway, which is a clobber no
    file-existence check can see.
    """
    text = (REPO_ROOT / "scripts/vps_hub_bootstrap.sh").read_text(encoding="utf-8-sig")
    assert "payload_missing+=(" in text, "missing-unit detection is gone"
    assert "payload_stale+=(" in text, "stale-payload detection is gone"
    assert "payload is STALE" in text, "the stale payload is no longer reported"
    assert "refusing to install" in text, "the refusal is gone"

    # Both reasons must return non-zero, or the gate lets the bad payload through.
    lines = [c.strip() for _, c in _directive_lines(REPO_ROOT / "scripts/vps_hub_bootstrap.sh")]
    start = next(i for i, c in enumerate(lines) if c.startswith("verify_payload()"))
    end = next(i for i in range(start + 1, len(lines)) if lines[i] == "}")
    body = lines[start:end]
    # Substring, not equality: the returns are written inline as `if ...; then return 1; fi`.
    assert sum(1 for c in body if "return 1" in c) >= 2, (
        "both the missing and stale cases must fail the verifier"
    )
    assert body[-1] == "return 0", "the verifier must succeed only by falling through"


def test_bootstrap_asserts_the_alert_channel_and_route_contract() -> None:
    text = (REPO_ROOT / "scripts/vps_hub_bootstrap.sh").read_text(encoding="utf-8-sig")
    for needle in (
        "camelot-selfcheck-alert.service",
        "OnFailure",
        "CAMELOT_ALERT_RESEND_KEY",
    ):
        assert needle in text, f"bootstrap no longer checks the alert wiring ({needle})"
    for route in ("/mesh/status", "/bifrost/knights", "/hermes/telemetry", "/heimdall/governance"):
        assert route in text, f"bootstrap no longer checks the route contract ({route})"


def test_retire_script_cannot_target_the_canonical_checkout() -> None:
    text = (REPO_ROOT / "scripts/ops/retire-uppercase-tree.sh").read_text(encoding="utf-8-sig")
    assert f'CANONICAL="${{CANONICAL:-{CANONICAL_TREE}}}"' in text
    assert f'RETIRED="${{RETIRED:-{RETIRED_TREE}}}"' in text
    # The refusal is the safety property: identical paths would make this a no-op that
    # reports success while deleting the tree everything else runs from.
    assert "RETIRED and CANONICAL are the same path" in text, (
        "the retire script must refuse an ambiguous target"
    )


def test_retire_script_verifies_the_archive_before_removing_the_tree() -> None:
    """An unreadable archive is not a backup, so verification must precede deletion."""
    path = REPO_ROOT / "scripts/ops/retire-uppercase-tree.sh"
    lines = [c.strip() for _, c in _directive_lines(path)]

    def index(needle: str) -> int:
        hit = next((i for i, c in enumerate(lines) if needle in c), None)
        assert hit is not None, f"retire script lost its {needle!r} step"
        return hit

    create = index("tar czf")
    verify = index("tar tzf")
    remove = index('rm -rf "$RETIRED"')
    assert create < verify < remove, (
        "the tree is removed without proving the archive readable"
    )
