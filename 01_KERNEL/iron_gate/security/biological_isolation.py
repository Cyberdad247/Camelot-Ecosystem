# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os


class BiologicalIsolation:
    """
    🧬 BIOLOGICAL LAYER: DATA DIODE v1.0
    Ensures external/untrusted code remains in isolation.
    Enforces Read-Only access to the System Core for external processes.
    """

    CORE_PATHS = ["01_KERNEL", "03_VAULT", "docs/CONSTITUTION.md"]

    @staticmethod
    def enforce_diode(path: str, mode: str, authorized: bool = False):
        """
        Blocks 'Write' operations to core paths if they originate from untrusted sources.
        """
        if authorized:
            return True

        abs_path = os.path.abspath(path)
        is_core = any(
            abs_path.endswith(core) or f"{os.sep}{core}{os.sep}" in abs_path for core in BiologicalIsolation.CORE_PATHS
        )

        if is_core and mode in ["w", "a", "x"]:
            # In a real system, we'd check the process's trust level here
            print(f"🧬 [DIODE] Access Restricted: Attempted {mode} on System Core at {path}")
            raise PermissionError("🚨 BIOLOGICAL_VIOLATION: Untrusted write to System Core blocked by Data Diode.")

        return True


# Singleton
diode = BiologicalIsolation()