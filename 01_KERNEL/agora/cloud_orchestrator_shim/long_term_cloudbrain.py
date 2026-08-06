# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Canonical long-term cloudbrain bootstrap for Camelot-OS.

This module turns the existing Open Notebook stack into a reusable service
surface that can run locally or behind Modal, while Appwrite remains the
durable long-term memory layer.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import types
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
KERNEL_ROOT = REPO_ROOT / "01_KERNEL"
AGORA_ROOT = KERNEL_ROOT / "agora"
SQUIRES_ROOT = AGORA_ROOT / "Squires"
NOTEBOOK_ROOT = SQUIRES_ROOT / "Notebook_Brain"
OPEN_NOTEBOOK_ROOT = SQUIRES_ROOT / "open_notebook"
APPWRITE_BRIDGE_PATH = KERNEL_ROOT / "titan" / "memory" / "appwrite_sync.py"
MEMORY_PACKAGE_ROOT = KERNEL_ROOT / "titan" / "memory"


@dataclass(frozen=True)
class OpenNotebookRuntimeConfig:
    """Runtime settings for the long-term Open Notebook cloudbrain."""

    api_base_url: str = "http://127.0.0.1:5055"
    surreal_url: str = "ws://localhost:8000/rpc"
    surreal_user: str = "root"
    surreal_pass: str = "root"
    surreal_namespace: str = "camelot"
    surreal_database: str = "notebook"


@dataclass(frozen=True)
class AppwriteRuntimeConfig:
    """Required Appwrite environment for durable cloud memory."""

    endpoint: str | None
    project_id: str | None
    api_key: str | None
    database_id: str
    collection_id: str

    @property
    def configured(self) -> bool:
        return bool(self.endpoint and self.project_id and self.api_key)


def _load_module(module_name: str, module_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module spec for {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _ensure_sys_path(*paths: Path) -> None:
    for path in paths:
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)


def configure_open_notebook_environment(
    runtime: OpenNotebookRuntimeConfig | None = None,
) -> OpenNotebookRuntimeConfig:
    """Prepare import paths and env vars for the existing Open Notebook stack."""

    runtime = runtime or OpenNotebookRuntimeConfig()

    _ensure_sys_path(REPO_ROOT, KERNEL_ROOT, AGORA_ROOT, SQUIRES_ROOT, NOTEBOOK_ROOT)

    os.environ.setdefault("API_BASE_URL", runtime.api_base_url)
    os.environ.setdefault("SURREAL_URL", runtime.surreal_url)
    os.environ.setdefault("SURREAL_USER", runtime.surreal_user)
    os.environ.setdefault("SURREAL_PASS", runtime.surreal_pass)
    os.environ.setdefault("SURREAL_NAMESPACE", runtime.surreal_namespace)
    os.environ.setdefault("SURREAL_DATABASE", runtime.surreal_database)

    api_module = types.ModuleType("api")
    api_module.__path__ = [str(NOTEBOOK_ROOT)]
    sys.modules["api"] = api_module

    return runtime


def get_appwrite_runtime_config() -> AppwriteRuntimeConfig:
    """Return current Appwrite cloud-memory configuration."""

    return AppwriteRuntimeConfig(
        endpoint=os.getenv("APPWRITE_ENDPOINT"),
        project_id=os.getenv("APPWRITE_PROJECT_ID"),
        api_key=os.getenv("APPWRITE_API_KEY"),
        database_id=os.getenv("APPWRITE_DB_ID", "sovereign_db"),
        collection_id=os.getenv("APPWRITE_COLLECTION_ID", "memory_spine"),
    )


@lru_cache(maxsize=1)
def create_open_notebook_app() -> Any:
    """Load the existing Open Notebook FastAPI app as the canonical cloudbrain."""

    configure_open_notebook_environment()
    notebook_main = _load_module("camelot_notebook_brain_main", NOTEBOOK_ROOT / "main.py")
    return notebook_main.app


def build_appwrite_memory_bridge() -> Any:
    """Load the existing Appwrite bridge without depending on package import layout."""
    package_name = "camelot_titan_memory"
    if package_name not in sys.modules:
        package = types.ModuleType(package_name)
        package.__path__ = [str(MEMORY_PACKAGE_ROOT)]
        sys.modules[package_name] = package

    _load_module(f"{package_name}.base_memory", MEMORY_PACKAGE_ROOT / "base_memory.py")
    bridge_module = _load_module(f"{package_name}.appwrite_sync", APPWRITE_BRIDGE_PATH)
    return bridge_module.AppwriteMemoryBridge()


def pull_long_term_memory(agent_id: str) -> list[dict[str, Any]]:
    """Fetch long-term memory records for a specific agent from Appwrite."""
    try:
        bridge = build_appwrite_memory_bridge()
        nodes = bridge.pull_long_term(agent_id)
        dumped: list[dict[str, Any]] = []
        for node in nodes:
            if hasattr(node, "model_dump"):
                dumped.append(node.model_dump(mode="json"))
            else:
                dumped.append(dict(node))
        return dumped
    except Exception:
        # Production-readiness requirement: research should still run without
        # taking the whole service down if long-term memory is unavailable.
        return []


def cloudbrain_status() -> dict[str, Any]:
    """Summarize the long-term cloudbrain topology and readiness."""

    notebook_runtime = configure_open_notebook_environment()
    appwrite = get_appwrite_runtime_config()
    return {
        "service": "long_term_cloudbrain",
        "repo_root": str(REPO_ROOT),
        "open_notebook_root": str(OPEN_NOTEBOOK_ROOT),
        "notebook_api_root": str(NOTEBOOK_ROOT),
        "runtime": asdict(notebook_runtime),
        "appwrite": {
            "configured": appwrite.configured,
            "database_id": appwrite.database_id,
            "collection_id": appwrite.collection_id,
            "endpoint_present": bool(appwrite.endpoint),
            "project_present": bool(appwrite.project_id),
            "api_key_present": bool(appwrite.api_key),
        },
    }
