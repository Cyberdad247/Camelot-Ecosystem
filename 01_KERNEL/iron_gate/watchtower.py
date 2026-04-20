# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Watchtower - System Metrics & Health Monitoring
Assimilated from CC_v32_Kingdom

Provides observability for:
- System resource usage
- Kingdom/Agent status
- Performance metrics
"""

import os
import platform
import sys
from datetime import datetime
from typing import Any, Dict

import psutil

# --- PATH ENFORCEMENT ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from security.enforcer import enforcer


class Watchtower:
    """System monitoring and metrics collection with Governor capabilities."""

    @staticmethod
    def governor_check():
        """
        Active Policy Enforcement (The Soft Governor).
        Checks current usage against policy.yaml limits.
        """
        try:
            # 1. Fetch Policy Limits
            policy = enforcer._policy if enforcer._policy else {}
            limits = policy.get("resource_limits", {})

            max_cpu = int(str(limits.get("max_cpu_usage", "90%")).replace("%", ""))
            max_ram = int(limits.get("max_ram_mb", 4096))

            # 2. Fetch Current Usage
            process = psutil.Process()
            current_cpu = process.cpu_percent(interval=None)  # Non-blocking
            current_ram = process.memory_info().rss / 1024 / 1024

            # 3. Enforce
            if current_ram > max_ram:
                enforcer._broadcast(
                    "RES_VIOLATION", "Memory", "CRITICAL", f"Using {int(current_ram)}MB (Limit: {max_ram}MB)"
                )
                # KINETIC ENFORCEMENT (Uncomment to enable Auto-Kill)
                # if current_ram > (max_ram * 1.5): # 50% buffer before kill
                #     enforcer._broadcast("RES_KILL", "Memory", "TERMINATED", "Process exceeded hard limit.")
                #     process.terminate()

            if current_cpu > max_cpu:
                enforcer._broadcast("RES_WARN", "CPU", "WARNING", f"Load {current_cpu}% (Limit: {max_cpu}%)")

            return {"cpu_usage": current_cpu, "ram_usage": current_ram, "cpu_limit": max_cpu, "ram_limit": max_ram}

        except Exception as e:
            print(f"⚠️ [GOVERNOR] Check failed: {e}")
            return {}

    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """
        Get system resource metrics.
        Returns: Dictionary with CPU, memory, disk usage
        """
        # Run Governor check on every heartbeat
        Watchtower.governor_check()

        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": (
                    psutil.disk_usage("/").percent
                    if platform.system() != "Windows"
                    else psutil.disk_usage("C:\\").percent
                ),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    @staticmethod
    def get_kingdom_status() -> Dict[str, Any]:
        """
        Get Chimera OS kingdom status.

        Returns:
            Dictionary with system info and version
        """
        return {
            "system": "Chimera OS",
            "version": "32.8.1",
            "kernel": "Merlin Enhanced",
            "mode": "PRODUCTION",
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def get_process_info() -> Dict[str, Any]:
        """
        Get current process information.

        Returns:
            Dictionary with process metrics
        """
        try:
            process = psutil.Process()
            return {
                "pid": process.pid,
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "threads": process.num_threads(),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}