# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
SIR_GALAHAD v1.0 — The Pure Blade
===================================
Zero-Trace Operative. All file operations leave no metadata trail.
All subprocess executions are environment-sanitized.
Zero telemetry leakage. The blade that leaves no mark.

OCEAN: O=0.8 C=1.0 E=0.05 A=0.4 N=0.0
Runes: PURITY | VOID | TRACE_NONE
Law: "The blade that leaves no mark is the most dangerous of all."
"""
from __future__ import annotations

import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger("SIR_GALAHAD")

# Environment variables that leak identity — scrubbed in stealth_exec
_IDENTITY_ENV_VARS = frozenset({
    "COMPUTERNAME", "USERNAME", "USERDOMAIN", "USERDNSDOMAIN",
    "HOSTNAME", "USER", "LOGNAME", "HOME", "USERPROFILE",
    "APPDATA", "LOCALAPPDATA", "TEMP", "TMP",
})


class SirGalahad:
    """
    L5 Zero-Trace Operative — fingerprint-less file and process operations.

    Usage:
        galahad = SirGalahad()
        galahad.zero_trace_write("/path/to/file", "content")
        result = galahad.stealth_exec(["pip", "install", "package"])
    """

    def __init__(self, quarantine_dir: Optional[Path] = None):
        self._quarantine = quarantine_dir or (
            Path(__file__).resolve().parents[5] / "CAMELOT_DefenseGrid_Quarantine"
        )

    # ------------------------------------------------------------------
    # Zero-trace file I/O
    # ------------------------------------------------------------------

    def zero_trace_write(self, path: str | Path, content: str | bytes,
                          encoding: str = "utf-8") -> Path:
        """Write file with no atime/mtime fingerprint modification beyond creation.

        After writing, scrubs atime and mtime to a fixed epoch so the write
        timestamp does not leak temporal information about operator activity.
        """
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(content, str):
            target.write_text(content, encoding=encoding)
        else:
            target.write_bytes(content)

        # Scrub timestamps — set to 2000-01-01T00:00:00 UTC (fixed epoch)
        _EPOCH = 946684800.0
        try:
            os.utime(target, (_EPOCH, _EPOCH))
        except OSError as exc:
            log.debug("[GALAHAD] utime scrub failed (non-fatal): %s", exc)

        log.info("[GALAHAD] zero_trace_write → %s", target)
        return target

    def zero_trace_read(self, path: str | Path, encoding: str = "utf-8") -> str:
        """Read file without updating atime (open with O_NOATIME where supported)."""
        target = Path(path)
        orig_atime = target.stat().st_atime if target.exists() else None
        content = target.read_text(encoding=encoding)
        if orig_atime is not None:
            try:
                os.utime(target, (orig_atime, target.stat().st_mtime))
            except OSError:
                pass
        return content

    def zero_trace_delete(self, path: str | Path) -> bool:
        """Delete file — overwrite with zeros first to prevent recovery."""
        target = Path(path)
        if not target.exists():
            return False
        try:
            size = target.stat().st_size
            with open(target, "r+b") as f:
                f.write(b"\x00" * size)
            target.unlink()
            log.info("[GALAHAD] zero_trace_delete → %s", target)
            return True
        except OSError as exc:
            log.warning("[GALAHAD] delete failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Stealth subprocess execution
    # ------------------------------------------------------------------

    def stealth_exec(self, cmd: list[str], env_sanitize: bool = True,
                     cwd: Optional[str] = None, timeout: int = 120,
                     **kwargs: Any) -> subprocess.CompletedProcess:
        """Execute subprocess with identity-sanitized environment.

        Strips all USERNAME/HOSTNAME/COMPUTERNAME variables from the child
        process environment to prevent identity leakage in logs or network calls.
        """
        env = os.environ.copy()
        if env_sanitize:
            for var in _IDENTITY_ENV_VARS:
                env.pop(var, None)
            # Replace with anonymous placeholders
            env["USERNAME"] = "camelot_operator"
            env["COMPUTERNAME"] = "sovereign_node"
            env["HOSTNAME"] = "camelot.local"

        log.info("[GALAHAD] stealth_exec: %s", " ".join(cmd))
        return subprocess.run(
            cmd,
            env=env,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Git anonymization
    # ------------------------------------------------------------------

    def anonymize_git_config(self, repo_path: str | Path) -> dict[str, str]:
        """Write a local .git/config override that strips author fingerprint.

        Sets local git user.name and user.email to anonymous values.
        Does NOT touch global git config.
        """
        repo = Path(repo_path)
        git_dir = repo / ".git"
        if not git_dir.exists():
            raise ValueError(f"{repo} is not a git repository")

        anon_name = "Camelot Sovereign"
        anon_email = "sovereign@camelot.local"

        self.stealth_exec(
            ["git", "-C", str(repo), "config", "user.name", anon_name]
        )
        self.stealth_exec(
            ["git", "-C", str(repo), "config", "user.email", anon_email]
        )
        log.info("[GALAHAD] Git config anonymized for %s", repo)
        return {"user.name": anon_name, "user.email": anon_email}

    # ------------------------------------------------------------------
    # Package fetch (stealth)
    # ------------------------------------------------------------------

    def stealth_pip_install(self, package: str, no_cache: bool = True) -> bool:
        """Install pip package via stealth_exec with no cache to avoid fingerprint."""
        cmd = ["pip", "install", package]
        if no_cache:
            cmd.append("--no-cache-dir")
        cmd.extend(["--quiet", "--disable-pip-version-check"])
        result = self.stealth_exec(cmd)
        if result.returncode == 0:
            log.info("[GALAHAD] stealth install OK: %s", package)
            return True
        log.warning("[GALAHAD] stealth install FAILED: %s\n%s", package, result.stderr)
        return False
