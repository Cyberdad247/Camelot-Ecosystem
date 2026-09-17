# SPDX-License-Identifier: MIT

"""The Hermes launcher stub must not shell into a container.

Rule 7 forbids a container runtime in the hot path. The hub runs Hermes as the
native ``hermes-agent.service`` unit, so the stub that fronts it must invoke the
binary directly.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from control_plane.dispatch.omarchy_agent_matrix import generate_omarchy_mise_stub

REPO_ROOT = Path(__file__).resolve().parents[1]
SYSTEMD_DIR = REPO_ROOT / "infra" / "systemd"
HERMES_UNIT = SYSTEMD_DIR / "hermes-agent.service"

_CONTAINER_DIRECTIVE = re.compile(
    r"^\s*(Exec[A-Za-z]*|Command)=.*\b(docker|podman|containerd)\b",
    re.IGNORECASE | re.MULTILINE,
)


def _executable_lines(path: Path) -> list[str]:
    """Unit-file lines that can actually do something (comments cannot)."""
    return [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("#")
    ]


def test_hermes_stub_has_no_container_reference() -> None:
    stub = generate_omarchy_mise_stub("hermes")
    for forbidden in ("docker", "podman", "containerd"):
        assert forbidden not in stub.lower()


def test_hermes_stub_targets_the_native_binary() -> None:
    stub = generate_omarchy_mise_stub("hermes")
    assert "/usr/local/bin/hermes" in stub


def test_hermes_stub_remains_a_valid_script() -> None:
    stub = generate_omarchy_mise_stub("hermes")
    assert stub.startswith("#!/bin/bash")
    assert "set -euo pipefail" in stub


def test_hermes_stub_quotes_arguments_for_the_remote_shell() -> None:
    """ssh joins argv into one remote command string, so bare "$@" would split
    on spaces. printf '%q ' is what keeps arguments intact."""
    stub = generate_omarchy_mise_stub("hermes")
    assert "printf '%q '" in stub


def test_other_agent_stubs_are_unaffected() -> None:
    codex_stub = generate_omarchy_mise_stub("codex")
    assert "sir_codex" in codex_stub.lower()


@pytest.mark.parametrize("agent", ["codex", "claude", "helios", "agy"])
def test_no_agent_stub_references_a_container(agent: str) -> None:
    """The de-Dockerization must not be Hermes-only; no stub may reintroduce it."""
    stub = generate_omarchy_mise_stub(agent)
    for forbidden in ("docker", "podman", "containerd"):
        assert forbidden not in stub.lower()


# --- The unit that replaces the container deployment -------------------------


def test_hermes_unit_has_no_container_directive() -> None:
    """Only executable directives matter.

    A comment cannot run anything, and an earlier over-broad guard here matched
    the literal string "docker" inside a comment and blocked a legitimate
    migration. This asserts the narrow property the migration script enforces.
    """
    unit = HERMES_UNIT.read_text(encoding="utf-8")
    assert not _CONTAINER_DIRECTIVE.search(unit)
    assert "ExecStart=/usr/local/bin/hermes" in "\n".join(_executable_lines(HERMES_UNIT))


def test_the_migration_guards_own_regex_is_not_vacuous() -> None:
    """Negative control: a unit that genuinely shells into a container must be
    caught. Without this, the guard above could pass by matching nothing at all."""
    offending = "[Service]\n# docker in a comment is fine\nExecStart=/usr/bin/docker run hermes\n"
    assert _CONTAINER_DIRECTIVE.search(offending)


def test_unit_slice_binding_resolves_to_a_tracked_slice_file() -> None:
    """The unit binds Slice=camelot-workers.slice. systemd cannot place a unit in
    a slice that does not exist, so the slice must ship alongside it."""
    unit = HERMES_UNIT.read_text(encoding="utf-8")
    match = re.search(r"^Slice=(\S+)", unit, re.MULTILINE)
    assert match, "hermes-agent.service declares no Slice="
    assert (SYSTEMD_DIR / match.group(1)).is_file(), (
        f"Slice={match.group(1)} has no unit file in {SYSTEMD_DIR}"
    )


def test_memory_high_sits_below_memory_max() -> None:
    """The scarcity-cap invariant: PSI reclaim must engage before the hard cap
    OOM-kills the worker."""

    def _megs(value: str) -> int:
        return int(value.rstrip("GM")) * (1024 if value.endswith("G") else 1)

    unit = HERMES_UNIT.read_text(encoding="utf-8")
    high = re.search(r"^MemoryHigh=(\S+)", unit, re.MULTILINE)
    maximum = re.search(r"^MemoryMax=(\S+)", unit, re.MULTILINE)
    assert high and maximum
    assert _megs(high.group(1)) < _megs(maximum.group(1))
