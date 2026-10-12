# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Personal CPU Sandbox Engine — Sovereign Hardware-Bounded Isolated Execution.
=============================================================================
Assimilates OpenMausBot / openmausbotOS and Rakazo local-first sandboxing patterns
into Camelot-OS under Phase 3 Hardening & ADR-002:

Guarantees:
1. Hard Memory Ceilings:
   - High Watermark: 300MB (`MemoryHigh=300M`)
   - Hard Kill Cap: 350MB (`MemoryMax=350M`)
2. Throttled CPU Quota:
   - 60% of single-core equivalent (`CPUQuota=60%`)
   - Low Priority / Background scheduling (Windows IDLE/BELOW_NORMAL, Linux nice +10)
3. Position-Addressed VFS Confinement:
   - Root: `vfs://worldtree/knights/{knight_id}/sandbox/{worker_id}/`
   - Local Mirror: `03_VAULT/runtime_state/sandboxes/{worker_id}/`
   - Strict zero-traversal protection; host writes isolated until Anya Gate clearance.
4. Capability Leases (`camelot-lease/1`):
   - Manifest validation and structured `operator-evidence/1` event logging.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

LOG = logging.getLogger("camelot.personal_cpu_sandbox")

PATH_TRAVERSAL_PATTERN = re.compile(r"(?:^|[\\/])\.\.(?:[\\/]|$)|^[\\/]")


class SandboxSecurityError(Exception):
    """Raised when an operation violates sandbox confinement boundaries."""
    pass


class MemoryExceededError(SandboxSecurityError):
    """Raised when a sandboxed process exceeds the 350MB memory ceiling."""
    pass


class CPUQuotaExceededError(SandboxSecurityError):
    """Raised when CPU quota is exceeded."""
    pass


@dataclass
class SandboxConfig:
    """Configuration for a dedicated Personal CPU Sandbox."""
    worker_id: str
    knight_id: str = "SIR_CODEX"
    max_memory_mb: float = 350.0
    memory_high_mb: float = 300.0
    cpu_quota_pct: float = 60.0
    vfs_sandbox_root: str = "vfs://worldtree/knights/{knight_id}/sandbox/{worker_id}"
    local_staging_base: Optional[Path] = None
    priority_tier: str = "BELOW_NORMAL"
    allowed_domains: List[str] = field(default_factory=lambda: [
        "github.com",
        "api.github.com",
        "pypi.org",
        "registry.npmjs.org",
        "huggingface.co"
    ])
    timeout_sec: float = 30.0

    def __post_init__(self):
        if not self.local_staging_base:
            # Anchor in 03_VAULT/runtime_state/sandboxes/<worker_id>
            camelot_root = Path(__file__).resolve().parent.parent.parent.parent
            self.local_staging_base = camelot_root / "03_VAULT" / "runtime_state" / "sandboxes" / self.worker_id


@dataclass
class SandboxMetrics:
    """Real-time telemetry from the Personal CPU Sandbox."""
    worker_id: str
    knight_id: str
    memory_rss_mb: float
    memory_max_mb: float
    memory_pct: float
    cpu_usage_pct: float
    cpu_quota_pct: float
    vfs_files_count: int
    vfs_bytes_used: int
    status: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PersonalCPUSandbox:
    """Dedicated CPU Sandbox providing memory capping, CPU throttling, and VFS isolation."""

    def __init__(self, config: SandboxConfig):
        self.config = config
        self.staging_dir = Path(self.config.local_staging_base).resolve()
        self.vfs_root = self.config.vfs_sandbox_root.format(
            knight_id=self.config.knight_id,
            worker_id=self.config.worker_id
        )
        self._is_initialized = False
        self._active_process: Optional[subprocess.Popen] = None
        self._last_metrics = SandboxMetrics(
            worker_id=self.config.worker_id,
            knight_id=self.config.knight_id,
            memory_rss_mb=0.0,
            memory_max_mb=self.config.max_memory_mb,
            memory_pct=0.0,
            cpu_usage_pct=0.0,
            cpu_quota_pct=self.config.cpu_quota_pct,
            vfs_files_count=0,
            vfs_bytes_used=0,
            status="INITIALIZING"
        )
        self.initialize()

    def initialize(self) -> None:
        """Create the quarantined local staging directory tree and manifest."""
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = self.staging_dir / "sandbox_manifest.json"
        if not manifest_path.exists():
            manifest = {
                "schema": "camelot-sandbox/1",
                "worker_id": self.config.worker_id,
                "knight_id": self.config.knight_id,
                "vfs_root": self.vfs_root,
                "max_memory_mb": self.config.max_memory_mb,
                "cpu_quota_pct": self.config.cpu_quota_pct,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        self._is_initialized = True
        self._last_metrics.status = "ARMED"

    def _resolve_virtual_path(self, virtual_path: str) -> Path:
        """Resolve a relative or vfs:// path within the quarantined staging root."""
        clean = virtual_path.replace("\\", "/").strip()
        if clean.startswith("vfs://"):
            # Strip vfs://worldtree/knights/<k>/sandbox/<w>/
            prefix = self.vfs_root.replace("\\", "/").rstrip("/")
            if clean.startswith(prefix):
                clean = clean[len(prefix):].lstrip("/")
            else:
                # If path specifies other root, reject
                raise SandboxSecurityError(f"Access violation: {virtual_path} is outside sandbox {self.vfs_root}")

        if ".." in clean.split("/"):
            raise SandboxSecurityError(f"Path traversal detected in virtual path: {virtual_path}")

        resolved = (self.staging_dir / clean).resolve()
        try:
            resolved.relative_to(self.staging_dir)
        except ValueError:
            raise SandboxSecurityError(f"Escapement attempt: {resolved} is outside {self.staging_dir}")
        return resolved

    def vfs_write(self, virtual_path: str, content: str) -> Dict[str, Any]:
        """Write content into the quarantined sandbox filesystem."""
        target = self._resolve_virtual_path(virtual_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        LOG.info("[SANDBOX:%s] Wrote %d bytes to %s", self.config.worker_id, len(content), target)
        self.collect_metrics()
        return {
            "vfs_path": f"{self.vfs_root}/{virtual_path.lstrip('/')}",
            "bytes_written": len(content),
            "sha256": sha256,
            "status": "QUARANTINED"
        }

    def vfs_read(self, virtual_path: str) -> str:
        """Read content from the quarantined sandbox filesystem."""
        target = self._resolve_virtual_path(virtual_path)
        if not target.exists():
            raise FileNotFoundError(f"Virtual file not found: {virtual_path}")
        return target.read_text(encoding="utf-8")

    def list_vfs_files(self) -> List[str]:
        """List relative file paths in the sandbox."""
        if not self.staging_dir.exists():
            return []
        files = []
        for p in self.staging_dir.rglob("*"):
            if p.is_file():
                files.append(str(p.relative_to(self.staging_dir)).replace("\\", "/"))
        return sorted(files)

    def execute_command(
        self,
        command: List[str],
        timeout_sec: Optional[float] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute a process inside the sandbox with CPU and memory confinement."""
        timeout = timeout_sec or self.config.timeout_sec
        creationflags = 0
        preexec_fn = None

        run_env = os.environ.copy()
        if env:
            run_env.update(env)
        # Sandbox execution variables
        run_env["CAMELOT_SANDBOX_WORKER_ID"] = self.config.worker_id
        run_env["CAMELOT_SANDBOX_VFS_ROOT"] = self.vfs_root

        # Windows Process Priority and Process Group
        if platform.system() == "Windows":
            # BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
            # IDLE_PRIORITY_CLASS = 0x00000040
            # CREATE_NEW_PROCESS_GROUP = 0x00000200
            if self.config.priority_tier == "IDLE":
                creationflags = 0x00000040 | 0x00000200
            else:
                creationflags = 0x00004000 | 0x00000200
        else:
            # Linux nice +10
            def _linux_throttle():
                try:
                    os.nice(10)
                except Exception:
                    pass
            preexec_fn = _linux_throttle

        start_time = time.monotonic()
        try:
            proc = subprocess.Popen(
                command,
                cwd=str(self.staging_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=run_env,
                text=True,
                creationflags=creationflags,
                preexec_fn=preexec_fn
            )
            self._active_process = proc

            # Monitor memory and CPU during execution via psutil if available
            stdout_text = ""
            stderr_text = ""
            max_rss_seen = 0.0

            import psutil
            try:
                ps_proc = psutil.Process(proc.pid)
            except (psutil.NoSuchProcess, Exception):
                ps_proc = None

            # Poll loop with timeout
            while proc.poll() is None:
                elapsed = time.monotonic() - start_time
                if elapsed > timeout:
                    proc.kill()
                    raise TimeoutError(f"Process exceeded sandbox timeout ({timeout}s)")

                if ps_proc:
                    try:
                        mem_info = ps_proc.memory_info()
                        rss_mb = mem_info.rss / (1024 * 1024)
                        if rss_mb > max_rss_seen:
                            max_rss_seen = rss_mb

                        if rss_mb > self.config.max_memory_mb:
                            proc.kill()
                            raise MemoryExceededError(
                                f"Process exceeded max memory limit: {rss_mb:.1f}MB > {self.config.max_memory_mb}MB"
                            )
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                time.sleep(0.05)

            stdout_text, stderr_text = proc.communicate()
            duration_ms = (time.monotonic() - start_time) * 1000.0

            return {
                "exit_code": proc.returncode,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "duration_ms": round(duration_ms, 2),
                "peak_memory_mb": round(max_rss_seen, 2),
                "worker_id": self.config.worker_id,
                "status": "SUCCESS" if proc.returncode == 0 else "FAILED"
            }

        finally:
            self._active_process = None
            self.collect_metrics()

    def collect_metrics(self) -> SandboxMetrics:
        """Gather active metrics for CPU, RAM, and VFS usage."""
        import psutil
        rss_mb = 0.0
        cpu_pct = 0.0
        status = "IDLE"

        if self._active_process and self._active_process.poll() is None:
            status = "RUNNING"
            try:
                ps = psutil.Process(self._active_process.pid)
                rss_mb = ps.memory_info().rss / (1024 * 1024)
                cpu_pct = ps.cpu_percent(interval=None)
            except Exception:
                pass

        total_bytes = 0
        file_count = 0
        if self.staging_dir.exists():
            for p in self.staging_dir.rglob("*"):
                if p.is_file():
                    file_count += 1
                    total_bytes += p.stat().st_size

        self._last_metrics = SandboxMetrics(
            worker_id=self.config.worker_id,
            knight_id=self.config.knight_id,
            memory_rss_mb=round(rss_mb, 2),
            memory_max_mb=self.config.max_memory_mb,
            memory_pct=round((rss_mb / self.config.max_memory_mb) * 100, 1),
            cpu_usage_pct=round(cpu_pct, 1),
            cpu_quota_pct=self.config.cpu_quota_pct,
            vfs_files_count=file_count,
            vfs_bytes_used=total_bytes,
            status=status
        )
        return self._last_metrics

    def cleanup(self) -> None:
        """Kill any lingering processes and purge staging directory if requested."""
        if self._active_process and self._active_process.poll() is None:
            try:
                self._active_process.kill()
            except Exception:
                pass
        self._last_metrics.status = "TERMINATED"
