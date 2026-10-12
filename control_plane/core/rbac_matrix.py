# -*- coding: utf-8 -*-
"""
RBAC Matrix — A2A Permission Enforcement
=========================================
Shatterpoint SP-01 remediation. Enforces access_matrix.json at Anya gate.

Usage (called from anya_gate._stage_validate):
    from .rbac_matrix import RBACMatrix
    rbac = RBACMatrix()
    ok, issues = rbac.check(knight_id, execution_mode, domain, complexity)
"""

from __future__ import annotations

__version__ = "9000.14"  # CYBERTRONIA — set by P1-T01


import json
import logging
from functools import lru_cache
from typing import Optional

from control_plane._paths import VAULT

logger = logging.getLogger(__name__)

_MATRIX_PATH = VAULT / "training" / "configs" / "config" / "access_matrix.json"


class RBACUnavailableError(RuntimeError):
    """The access matrix could not be loaded, so no grant can be evaluated.

    Raised instead of degrading to an empty matrix: an empty matrix denies every
    knight, which reads as a deliberate zero-trust decision but is really a
    missing or malformed file. Callers must distinguish "denied by policy" from
    "policy could not be read".
    """


@lru_cache(maxsize=1)
def _load_matrix() -> dict:
    """Load access_matrix.json, raising rather than returning a silent {}."""
    if not _MATRIX_PATH.exists():
        raise RBACUnavailableError(
            f"access matrix not found at {_MATRIX_PATH} — RBAC cannot authorize "
            f"any knight. Restore the file or set CAMELOT_HOME to the repo root."
        )
    try:
        with _MATRIX_PATH.open("r", encoding="utf-8") as f:
            matrix = json.load(f)
    except (OSError, json.JSONDecodeError) as err:
        raise RBACUnavailableError(
            f"access matrix at {_MATRIX_PATH} could not be parsed: {err}"
        ) from err

    if not isinstance(matrix, dict) or not matrix.get("knights"):
        raise RBACUnavailableError(
            f"access matrix at {_MATRIX_PATH} declares no knights — every intent "
            f"would be blocked. Refusing to start with an empty grant table."
        )
    return matrix


class RBACMatrix:
    """Lightweight RBAC enforcer — loaded once, cached.

    Raises :class:`RBACUnavailableError` if the matrix is missing, unparseable,
    or empty. ``anya_gate`` already treats an RBAC exception as BLOCKED, so the
    failure stays fail-closed while becoming diagnosable.
    """

    def __init__(self) -> None:
        self._matrix = _load_matrix()
        self._knights: dict = self._matrix.get("knights", {})
        self._deny_rules: list = self._matrix.get("deny_rules", [])
        logger.debug(
            "RBAC matrix loaded from %s (%d knights, %d deny rules)",
            _MATRIX_PATH, len(self._knights), len(self._deny_rules),
        )

    def _get_knight(self, knight_id: str) -> Optional[dict]:
        key = knight_id.lower().replace("-", "_").replace(" ", "_")
        return self._knights.get(key)

    def check(
        self,
        knight_id: str,
        execution_mode: str,
        domain: str,
        complexity: float = 0.5,
    ) -> tuple[bool, list[str]]:
        """
        Returns (allowed: bool, issues: list[str]).
        Called in _stage_validate before iron_gate decision.
        """
        issues: list[str] = []
        knight = self._get_knight(knight_id)

        if not knight:
            issues.append(f"RBAC: unknown knight '{knight_id}' — no access record, BLOCKED")
            return False, issues

        # Mode check
        allowed_modes = knight.get("allowed_modes", [])
        if execution_mode not in allowed_modes:
            issues.append(
                f"RBAC: {knight_id} mode={execution_mode} not in allowed={allowed_modes}"
            )

        # Domain check — "*" means all domains allowed
        allowed_domains = knight.get("allowed_domains", [])
        if "*" not in allowed_domains and domain not in allowed_domains:
            issues.append(
                f"RBAC: {knight_id} domain={domain} not in allowed={allowed_domains}"
            )

        # Deny rule evaluation
        _tier = knight.get("tier", "KNIGHT")
        _role = knight.get("role", "")
        cost_ceiling = knight.get("cost_ceiling", "low")
        _can_spawn = knight.get("can_spawn_swarm", False)

        for rule in self._deny_rules:
            rid = rule.get("id", "?")
            _action = rule.get("action", "BLOCKED")

            if rid == "DENY-04" and complexity < 0.5 and cost_ceiling == "high":
                issues.append(f"RBAC [{rid}]: cost ceiling violation — reroute to cheaper terminal")

        blocked = any(
            "BLOCKED" in i or "not in allowed" in i for i in issues
        )
        return not blocked, issues

    def is_omega(self, knight_id: str) -> bool:
        knight = self._get_knight(knight_id)
        return knight.get("tier", "") == "OMEGA" if knight else False

    def can_spawn_swarm(self, knight_id: str) -> bool:
        knight = self._get_knight(knight_id)
        return bool(knight.get("can_spawn_swarm", False)) if knight else False

    def max_net_lines(self, knight_id: str) -> int:
        knight = self._get_knight(knight_id)
        return int(knight.get("max_net_lines", 50)) if knight else 50

    def invalidate_cache(self) -> None:
        _load_matrix.cache_clear()
        self._matrix = _load_matrix()
        self._knights = self._matrix.get("knights", {})
        self._deny_rules = self._matrix.get("deny_rules", [])
