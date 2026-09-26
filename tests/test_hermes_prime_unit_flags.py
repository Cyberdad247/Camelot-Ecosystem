# SPDX-License-Identifier: MIT
"""Guard the Hermes Prime hub unit against the two defects that made it inert.

Background — the unit shipped to the hub as:

    Type=simple
    ExecStart=/usr/bin/python3 .../hermes_prime_phial.py --loop 60
    Restart=always
    RestartSec=10s

That unit could never have worked, in two independent ways, and neither was
caught by any test because nothing ever read the unit:

  1. `--loop` is not a flag the engine accepts. Running the exact ExecStart
     reproduced it: `error: unrecognized arguments: --loop 60`, exit=2. Paired
     with `Restart=always`/`RestartSec=10s`, enabling the unit would have
     crash-looped every 10 seconds forever.
  2. The engine resolves its root from `Path(__file__).resolve().parents[3]` and
     never reads `CAMELOT_OS_HOME`, so the unit's `Environment=CAMELOT_OS_HOME=`
     promised an override that did not exist, while the real state directory was
     root-owned — a second, later failure (`PermissionError`, exit=1).

The accepted-flag set is read from the engine's own `--help` output rather than
restated here. A test asserting against a hardcoded flag list only proves the
file agrees with itself.
"""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
UNIT_DIR = REPO_ROOT / "infra" / "systemd"
SERVICE = UNIT_DIR / "camelot-hermes-prime.service"
TIMER = UNIT_DIR / "camelot-hermes-prime.timer"
ENGINE = REPO_ROOT / "01_KERNEL" / "titan" / "phials" / "hermes_prime_phial.py"

# The canonical deployment tree. The hub also carries a stale uppercase clone
# (/opt/Camelot-Ecosystem) that the live consumer does NOT read; producing state
# there split the producer from the consumer and left GET /api/hermes empty.
CANONICAL_TREE = "/opt/camelot-ecosystem"
STALE_TREE = "/opt/Camelot-Ecosystem"


def _engine_accepted_flags() -> set[str]:
    """Every flag the engine actually accepts, straight from its runtime --help."""
    # encoding must be explicit: `text=True` alone uses the platform default (cp1252 on
    # Windows) while the engine emits UTF-8, so non-ASCII output would decode to mojibake.
    proc = subprocess.run(
        [sys.executable, str(ENGINE), "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    assert proc.returncode == 0, f"engine --help failed: {proc.stderr}"
    return set(re.findall(r"--[a-z][a-z-]*", proc.stdout))


def _unit_text(path: Path = SERVICE) -> str:
    assert path.exists(), f"missing {path}"
    return path.read_text(encoding="utf-8")


def _directives(text: str, key: str) -> list[str]:
    """Values of `key=` directives, ignoring comments."""
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or "=" not in stripped:
            continue
        name, _, value = stripped.partition("=")
        if name.strip() == key:
            out.append(value.strip())
    return out


def _exec_flags(text: str) -> list[str]:
    """Flags present in ExecStart, as parsed (no shell is involved)."""
    exec_starts = _directives(text, "ExecStart")
    assert exec_starts, "unit has no ExecStart"
    tokens = shlex.split(exec_starts[-1])
    return [t for t in tokens if t.startswith("--")]


def _expanded_vars(text: str) -> set[str]:
    tokens = " ".join(_directives(text, "ExecStart"))
    return set(re.findall(r"\$\{([A-Z_][A-Z0-9_]*)\}", tokens))


def _body(text: str) -> str:
    """Unit text with comment lines removed.

    Directives are what the unit does; comments are what it explains. A checker
    that greps the whole file confuses the two, which is how a variable that is
    deliberately absent while being explained gets reported as present.
    """
    return "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("#")
    )


def _check_flags_are_real(text: str, accepted: set[str]) -> list[str]:
    """Shared by the real unit and the negative control."""
    return sorted(f for f in _exec_flags(text) if f.split("=")[0] not in accepted)


# --------------------------------------------------------------------------- #
# the core invariant
# --------------------------------------------------------------------------- #


def test_execstart_uses_only_flags_the_engine_accepts() -> None:
    accepted = _engine_accepted_flags()
    assert "--cycle" in accepted, "engine lost --cycle; the unit depends on it"
    assert "--loop" not in accepted, (
        "engine now accepts --loop; revisit the timer design in the unit header"
    )
    bogus = _check_flags_are_real(_unit_text(), accepted)
    assert not bogus, f"ExecStart uses flags the engine does not accept: {bogus}"


def test_negative_control_catches_the_original_broken_invocation() -> None:
    """Prove the checker fires, rather than trusting an empty result."""
    accepted = _engine_accepted_flags()
    broken = _unit_text().replace(
        "--cycle ${HERMES_PRIME_SEED}", "--loop 60"
    )
    assert "--loop" not in accepted
    assert _check_flags_are_real(broken, accepted) == ["--loop"]


def test_the_retired_invocation_is_documented_not_just_deleted() -> None:
    """The reason belongs in the file: someone will otherwise 'fix' it back."""
    text = _unit_text()
    assert "--loop 60" in text, "unit no longer records the retired invocation"
    assert "unrecognized arguments" in text or "exit=2" in text


# --------------------------------------------------------------------------- #
# crash-loop trap
# --------------------------------------------------------------------------- #


def test_unit_is_oneshot_and_cannot_crash_loop() -> None:
    text = _unit_text()
    assert _directives(text, "Type") == ["oneshot"], (
        "unit must be Type=oneshot; a resident Type=simple unit re-introduces "
        "the Restart=always crash-loop"
    )
    assert not _directives(text, "Restart"), (
        "Restart= is forbidden here: with an exit=2 ExecStart it means an "
        "infinite 10-second crash-loop"
    )


# --------------------------------------------------------------------------- #
# env expansion
# --------------------------------------------------------------------------- #


def test_every_variable_in_execstart_is_declared() -> None:
    """An undeclared ${VAR} expands to empty and silently changes the argv."""
    text = _unit_text()
    declared = set()
    for value in _directives(text, "Environment"):
        if "=" in value:
            declared.add(value.partition("=")[0])
    undeclared = _expanded_vars(text) - declared
    assert not undeclared, f"ExecStart references undeclared vars: {sorted(undeclared)}"
    assert declared, "unit declares no Environment= at all"


def test_decorative_camelot_os_home_is_gone() -> None:
    """The engine never reads CAMELOT_OS_HOME; keeping it implied an override."""
    assert "CAMELOT_OS_HOME" not in _body(_unit_text()), (
        "CAMELOT_OS_HOME is inert (the engine uses Path(__file__).parents[3]); "
        "setting it only advertises an override that does not exist"
    )
    # ...but the explanation of why it is gone must survive.
    assert "CAMELOT_OS_HOME" in _unit_text(), (
        "the comment explaining the removal was lost with the directive"
    )


# --------------------------------------------------------------------------- #
# tree correctness — the producer/consumer split
# --------------------------------------------------------------------------- #


def test_unit_targets_the_canonical_tree_the_consumer_reads() -> None:
    text = _unit_text()
    assert CANONICAL_TREE in text
    # The stale clone must survive only inside the explanatory comment header.
    assert STALE_TREE not in _body(text), (
        "unit points at the stale uppercase clone; the live mesh bridge reads "
        f"{CANONICAL_TREE}, so state written there is never served"
    )


def test_state_directory_is_documented_as_requiring_a_dir_only_chown() -> None:
    text = _unit_text()
    assert "03_VAULT/runtime_state" in text
    assert "chown" in text
    assert "-R" in text, "the comment must warn against a recursive chown"


# --------------------------------------------------------------------------- #
# the timer owns the cadence
# --------------------------------------------------------------------------- #


def test_cadence_lives_in_the_timer_not_the_service() -> None:
    assert TIMER.exists(), "missing the timer that supplies the 60s cadence"
    timer = TIMER.read_text(encoding="utf-8")
    assert _directives(timer, "OnUnitActiveSec") == ["60s"]
    assert _directives(timer, "Unit") == ["camelot-hermes-prime.service"]
    assert _directives(timer, "WantedBy") == ["timers.target"]
    # The service must not try to own activation.
    assert not _directives(_unit_text(), "WantedBy")
