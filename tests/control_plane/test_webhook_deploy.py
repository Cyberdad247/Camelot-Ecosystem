# SPDX-License-Identifier: MIT
"""Contract tests for the deployment executor's gating logic.

No network, no git, no npm: the gating tests cover the decisions the
executor makes BEFORE any command runs. The command path is covered with
monkeypatched subprocess calls that assert ordering and arguments.
"""

from __future__ import annotations

import subprocess

import pytest

from control_plane.infra import webhook_deploy

SHA = "a" * 40
OTHER_SHA = "b" * 40


def _payload(ref: str = "refs/heads/main", sha: str = SHA) -> dict:
    return {"ref": ref, "after": sha}


def test_non_deploy_branch_is_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CAMELOT_DEPLOY_ENABLED", raising=False)
    result = webhook_deploy.execute_deploy(_payload(ref="refs/heads/feature-x"))
    assert result.status == "IGNORED"
    assert result.steps == []
    assert "not the deploy branch" in result.error


def test_short_sha_is_skipped(monkeypatch: pytest.MonkeyPatch) -> None:
    result = webhook_deploy.execute_deploy(_payload(sha="abc123"))
    assert result.status == "SKIPPED"
    assert result.steps == []


def test_non_hex_sha_is_skipped() -> None:
    result = webhook_deploy.execute_deploy(_payload(sha="not-a-sha"))
    assert result.status == "SKIPPED"


def test_happy_path_order_and_rsync_target(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    repo_dir = tmp_path / "repo"
    (repo_dir / ".git").mkdir(parents=True)
    out_dir = tmp_path / "dist"
    out_dir.mkdir()

    monkeypatch.setenv("CAMELOT_DEPLOY_REPO_DIR", str(repo_dir))
    monkeypatch.setenv("CAMELOT_DEPLOY_OUTPUT_DIR", str(out_dir))
    monkeypatch.setenv("CAMELOT_DEPLOY_TARGET_DIR", str(tmp_path / "www"))

    recorded: list = []

    def fake_run(cmd, cwd, steps, label):
        recorded.append((label, list(cmd)))
        if cmd[:3] == ["git", "-C", str(repo_dir)] and cmd[3] == "rev-parse":
            return subprocess.CompletedProcess(cmd, 0, stdout=SHA + "\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(webhook_deploy, "_run", fake_run)

    def fake_subprocess_run(*args, **kwargs):
        cmd = args[0]
        if "rev-parse" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout=SHA + "\n", stderr="")
        if "status" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
        raise AssertionError(f"unexpected direct subprocess call: {cmd}")

    monkeypatch.setattr(webhook_deploy.subprocess, "run", fake_subprocess_run)
    monkeypatch.setattr(webhook_deploy.os.path, "isdir", lambda p: not str(p).endswith("node_modules"))

    result = webhook_deploy.execute_deploy(_payload())
    assert result.status == "DEPLOYED", result.error
    labels = [label for label, _ in recorded]
    assert labels[0] == "fetch origin/main"
    assert labels[1] == f"reset --hard {SHA[:7]}"
    assert labels[-1].startswith("rsync -> ")
    assert not any("clone" in label for label in labels), "existing checkout must not re-clone"


def test_sha_mismatch_skips_before_reset(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    repo_dir = tmp_path / "repo"
    (repo_dir / ".git").mkdir(parents=True)
    monkeypatch.setenv("CAMELOT_DEPLOY_REPO_DIR", str(repo_dir))

    monkeypatch.setattr(
        webhook_deploy.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(a[0], 0, stdout=OTHER_SHA + "\n", stderr=""),
    )
    ran: list = []
    monkeypatch.setattr(
        webhook_deploy, "_run", lambda cmd, cwd, steps, label: ran.append(label) or subprocess.CompletedProcess(cmd, 0, "", "")
    )

    result = webhook_deploy.execute_deploy(_payload())
    assert result.status == "SKIPPED"
    assert ran == ["fetch origin/main"], "reset must not run when the SHA is unseen"
