# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Tool Registry — the REAL cartridge executor
============================================
CartridgeSandbox delegates execution to a ``tool_executor`` callable. The default
one is an explicit ``[SIMULATION]``. This module provides the production replacement:
a registry that maps a cartridge ``tool_id`` to a real Python callable and returns
its actual result.

The registry does NOT decide *whether* a tool may run — that is the sandbox's job
(signature → deny-list → HITL → allow-list → budget). By the time the executor is
invoked, the call is already authorized; the registry just does the work.

    reg = ToolRegistry(with_builtins=True)

    @reg.tool("summarize")
    def _summarize(params): return {"summary": params["text"][:100]}

    sandbox = CartridgeSandbox(trust_manager=tm, tool_executor=reg.executor)

Built-in safe tools (opt-in via with_builtins): echo, utc_now, http_get.
An unregistered tool_id raises ToolNotFound — the sandbox turns that into a
structured error, it never crashes the host.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable, Dict

ToolFn = Callable[[Dict[str, Any]], Any]


class ToolNotFound(KeyError):
    pass


class ToolRegistry:
    def __init__(self, *, with_builtins: bool = False):
        self._tools: Dict[str, ToolFn] = {}
        if with_builtins:
            self.register("echo", _echo)
            self.register("utc_now", _utc_now)
            self.register("http_get", _http_get)

    # ── registration ───────────────────────────────────────────────────────────
    def register(self, tool_id: str, fn: ToolFn) -> None:
        self._tools[tool_id] = fn

    def tool(self, tool_id: str) -> Callable[[ToolFn], ToolFn]:
        """Decorator form: @reg.tool("name")."""
        def _wrap(fn: ToolFn) -> ToolFn:
            self.register(tool_id, fn)
            return fn
        return _wrap

    def has(self, tool_id: str) -> bool:
        return tool_id in self._tools

    @property
    def tool_ids(self) -> list[str]:
        return sorted(self._tools)

    # ── the executor the sandbox calls ─────────────────────────────────────────
    def executor(self, tool_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sandbox-compatible executor. Returns {"data", "token_cost", "simulated": False}.
        Raises ToolNotFound for an unregistered tool_id (the sandbox reports it as an
        error rather than crashing).
        """
        fn = self._tools.get(tool_id)
        if fn is None:
            raise ToolNotFound(
                f"tool '{tool_id}' is allowed by the cartridge but not implemented in the registry "
                f"(registered: {self.tool_ids})")
        t0 = time.time()
        data = fn(params or {})
        return {
            "data": data,
            "token_cost": _estimate_cost(params, data),
            "simulated": False,
            "exec_ms": round((time.time() - t0) * 1000, 2),
        }


# ── built-in real tools (safe by construction) ────────────────────────────────
def _echo(params: Dict[str, Any]) -> Any:
    return params.get("value", params)


def _utc_now(_params: Dict[str, Any]) -> str:
    return datetime.now(timezone.utc).isoformat()


def _http_get(params: Dict[str, Any]) -> Dict[str, Any]:
    """GET a URL. http/https only, 5s timeout, response body capped at 8KB."""
    url = str(params.get("url", ""))
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("http_get: only http(s) URLs are allowed")
    req = urllib.request.Request(url, headers={"User-Agent": "camelot-cartridge/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            body = resp.read(8192).decode("utf-8", "replace")
            return {"status": resp.status, "body": body, "url": url}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "error": e.reason, "url": url}


def _estimate_cost(params: Dict[str, Any], data: Any) -> int:
    """Rough token proxy from payload sizes — real budgeting, not a mock constant."""
    try:
        size = len(json.dumps(params, default=str)) + len(json.dumps(data, default=str))
    except (TypeError, ValueError):
        size = 512
    return max(1, size // 4)


if __name__ == "__main__":
    reg = ToolRegistry(with_builtins=True)
    print("registered:", reg.tool_ids)
    print("echo    ->", reg.executor("echo", {"value": "hi"}))
    print("utc_now ->", reg.executor("utc_now", {})["data"])
