"""Typed routing for Camelot cloudbrain and research services."""

from __future__ import annotations

import importlib.util
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field

from cloud_orchestrator.long_term_cloudbrain import cloudbrain_status, pull_long_term_memory


# --- NotebookLM bridge loader (Ω₃) -----------------------------------------
# The bridge lives under 03_VAULT/training/configs/ which is not on sys.path.
# Load it by file-spec on first use, then cache the module handle.

_NOTEBOOKLM_BRIDGE = None


def _load_notebooklm_bridge():
    global _NOTEBOOKLM_BRIDGE
    if _NOTEBOOKLM_BRIDGE is not None:
        return _NOTEBOOKLM_BRIDGE
    home = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS"))
    bridge_path = home / "03_VAULT" / "training" / "configs" / "notebooklm_bridge.py"
    if not bridge_path.is_file():
        raise FileNotFoundError(f"notebooklm_bridge.py not found at {bridge_path}")
    spec = importlib.util.spec_from_file_location("notebooklm_bridge", bridge_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["notebooklm_bridge"] = module
    spec.loader.exec_module(module)
    _NOTEBOOKLM_BRIDGE = module
    return module


# Heavy cloud deps (modal, supabase, long-term cloudbrain) are imported lazily
# inside handler methods so lightweight consumers — e.g. the Ω₃ NotebookLM slice —
# don't pay the import cost or fail on a missing optional dependency.
def _modal_services():
    from cloud_orchestrator import modal_services
    return modal_services


def _long_term_cloudbrain():
    from cloud_orchestrator import long_term_cloudbrain
    return long_term_cloudbrain


class CloudServiceName(str, Enum):
    CLOUDBRAIN_STATUS = "cloudbrain_status"
    CLOUDBRAIN_MEMORY = "cloudbrain_memory"
    RESEARCH_AGENCY = "research_agency"
    RESEARCH_AGENCY_HEALTH = "research_agency_health"
    NORTHSTAR = "northstar"
    NORTHSTAR_HEALTH = "northstar_health"
    DEVELOPMENT_BLUEPRINT = "development_blueprint"
    DEVELOPMENT_BLUEPRINT_HEALTH = "development_blueprint_health"
    PRECISE_MODE = "precise_mode"
    PRECISE_MODE_HEALTH = "precise_mode_health"
    NOTEBOOKLM_HEALTH = "notebooklm_health"
    NOTEBOOKLM_SYNTHESIZE = "notebooklm_synthesize"
    NOTEBOOKLM_SYNC = "notebooklm_sync"
    NOTEBOOKLM_RESEARCH_START = "notebooklm_research_start"
    NOTEBOOKLM_RESEARCH_POLL = "notebooklm_research_poll"
    NOTEBOOKLM_STUDIO_LIST = "notebooklm_studio_list"
    NOTEBOOKLM_STUDIO_GENERATE = "notebooklm_studio_generate"
    NOTEBOOKLM_SOURCES_LIST = "notebooklm_sources_list"
    NOTEBOOKLM_SOURCES_ADD = "notebooklm_sources_add"
    NOTEBOOKLM_SOURCES_DELETE = "notebooklm_sources_delete"


class CloudServiceRequest(BaseModel):
    service: CloudServiceName
    payload: dict[str, Any] = Field(default_factory=dict)


class CloudServiceResult(BaseModel):
    service: CloudServiceName
    success: bool
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    source: str = "local"


class CloudServiceRouter:
    """Routes typed requests to local or remote cloud services."""

    def __init__(self):
        self.cloudbrain_url = os.getenv("CAMELOT_CLOUDBRAIN_URL", "").rstrip("/")
        self.research_url = os.getenv("CAMELOT_RESEARCH_AGENCY_URL", "").rstrip("/")
        self.research_health_url = os.getenv("CAMELOT_RESEARCH_AGENCY_HEALTH_URL", "").rstrip("/")
        self.northstar_url = os.getenv("CAMELOT_NORTHSTAR_URL", "").rstrip("/")
        self.northstar_health_url = os.getenv("CAMELOT_NORTHSTAR_HEALTH_URL", "").rstrip("/")
        self.blueprint_url = os.getenv("CAMELOT_BLUEPRINT_URL", "").rstrip("/")
        self.blueprint_health_url = os.getenv("CAMELOT_BLUEPRINT_HEALTH_URL", "").rstrip("/")
        self.precise_mode_url = os.getenv("CAMELOT_PRECISE_MODE_URL", "").rstrip("/")
        self.precise_mode_health_url = os.getenv("CAMELOT_PRECISE_MODE_HEALTH_URL", "").rstrip("/")

    async def invoke(self, request: CloudServiceRequest) -> CloudServiceResult:
        if request.service is CloudServiceName.CLOUDBRAIN_STATUS:
            return await self._cloudbrain_status()
        if request.service is CloudServiceName.CLOUDBRAIN_MEMORY:
            return await self._cloudbrain_memory(request.payload)
        if request.service is CloudServiceName.RESEARCH_AGENCY:
            return await self._research_agency(request.payload)
        if request.service is CloudServiceName.RESEARCH_AGENCY_HEALTH:
            return await self._research_agency_health()
        if request.service is CloudServiceName.NORTHSTAR:
            return await self._northstar(request.payload)
        if request.service is CloudServiceName.NORTHSTAR_HEALTH:
            return await self._northstar_health()
        if request.service is CloudServiceName.DEVELOPMENT_BLUEPRINT:
            return await self._development_blueprint(request.payload)
        if request.service is CloudServiceName.DEVELOPMENT_BLUEPRINT_HEALTH:
            return await self._development_blueprint_health()
        if request.service is CloudServiceName.PRECISE_MODE:
            return await self._precise_mode(request.payload)
        if request.service is CloudServiceName.PRECISE_MODE_HEALTH:
            return await self._precise_mode_health()
        if request.service is CloudServiceName.NOTEBOOKLM_HEALTH:
            return await self._notebooklm_health()
        if request.service is CloudServiceName.NOTEBOOKLM_SYNTHESIZE:
            return await self._notebooklm_synthesize(request.payload)
        if request.service is CloudServiceName.NOTEBOOKLM_SYNC:
            return await self._notebooklm_sync(request.payload)
        if request.service is CloudServiceName.NOTEBOOKLM_RESEARCH_START:
            return await self._notebooklm_research_start(request.payload)
        if request.service is CloudServiceName.NOTEBOOKLM_RESEARCH_POLL:
            return await self._notebooklm_research_poll(request.payload)
        if request.service is CloudServiceName.NOTEBOOKLM_STUDIO_LIST:
            return await self._notebooklm_studio_list(request.payload)
        if request.service is CloudServiceName.NOTEBOOKLM_STUDIO_GENERATE:
            return await self._notebooklm_studio_generate(request.payload)
        if request.service is CloudServiceName.NOTEBOOKLM_SOURCES_LIST:
            return await self._notebooklm_sources_list(request.payload)
        if request.service is CloudServiceName.NOTEBOOKLM_SOURCES_ADD:
            return await self._notebooklm_sources_add(request.payload)
        if request.service is CloudServiceName.NOTEBOOKLM_SOURCES_DELETE:
            return await self._notebooklm_sources_delete(request.payload)
        return CloudServiceResult(
            service=request.service,
            success=False,
            error=f"Unsupported cloud service: {request.service}",
        )

    async def _cloudbrain_status(self) -> CloudServiceResult:
        if self.cloudbrain_url:
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.get(f"{self.cloudbrain_url}/cloudbrain_health")
                    response.raise_for_status()
                    return CloudServiceResult(
                        service=CloudServiceName.CLOUDBRAIN_STATUS,
                        success=True,
                        result=response.json(),
                        source="remote",
                    )
            except Exception as exc:
                return CloudServiceResult(
                    service=CloudServiceName.CLOUDBRAIN_STATUS,
                    success=False,
                    error=str(exc),
                    source="remote",
                )

        return CloudServiceResult(
            service=CloudServiceName.CLOUDBRAIN_STATUS,
            success=True,
            result=_long_term_cloudbrain().cloudbrain_status(),
            source="local",
        )

    async def _cloudbrain_memory(self, payload: dict[str, Any]) -> CloudServiceResult:
        agent_id = str(payload.get("agent_id", "merlin"))
        try:
            memories = _long_term_cloudbrain().pull_long_term_memory(agent_id)
            return CloudServiceResult(
                service=CloudServiceName.CLOUDBRAIN_MEMORY,
                success=True,
                result={
                    "agent_id": agent_id,
                    "memory_count": len(memories),
                    "memories": memories,
                },
                source="local",
            )
        except Exception as exc:
            return CloudServiceResult(
                service=CloudServiceName.CLOUDBRAIN_MEMORY,
                success=False,
                error=str(exc),
                source="local",
            )

    async def _research_agency(self, payload: dict[str, Any]) -> CloudServiceResult:
        if self.research_url:
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(self.research_url, json=payload)
                    response.raise_for_status()
                    return CloudServiceResult(
                        service=CloudServiceName.RESEARCH_AGENCY,
                        success=True,
                        result=response.json(),
                        source="remote",
                    )
            except Exception as exc:
                return CloudServiceResult(
                    service=CloudServiceName.RESEARCH_AGENCY,
                    success=False,
                    error=str(exc),
                    source="remote",
                )

        try:
            result = _modal_services().run_research_agency(payload)
            return CloudServiceResult(
                service=CloudServiceName.RESEARCH_AGENCY,
                success=True,
                result=result,
                source="local",
            )
        except Exception as exc:
            return CloudServiceResult(
                service=CloudServiceName.RESEARCH_AGENCY,
                success=False,
                error=str(exc),
                source="local",
            )

    async def _research_agency_health(self) -> CloudServiceResult:
        if self.research_health_url:
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.get(self.research_health_url)
                    response.raise_for_status()
                    return CloudServiceResult(
                        service=CloudServiceName.RESEARCH_AGENCY_HEALTH,
                        success=True,
                        result=response.json(),
                        source="remote",
                    )
            except Exception as exc:
                return CloudServiceResult(
                    service=CloudServiceName.RESEARCH_AGENCY_HEALTH,
                    success=False,
                    error=str(exc),
                    source="remote",
                )

        return CloudServiceResult(
            service=CloudServiceName.RESEARCH_AGENCY_HEALTH,
            success=True,
            result=_modal_services().research_agency_health(),
            source="local",
        )

    async def _northstar(self, payload: dict[str, Any]) -> CloudServiceResult:
        if self.northstar_url:
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(self.northstar_url, json=payload)
                    response.raise_for_status()
                    return CloudServiceResult(
                        service=CloudServiceName.NORTHSTAR,
                        success=True,
                        result=response.json(),
                        source="remote",
                    )
            except Exception as exc:
                return CloudServiceResult(
                    service=CloudServiceName.NORTHSTAR,
                    success=False,
                    error=str(exc),
                    source="remote",
                )

        try:
            result = _modal_services().run_northstar(payload)
            return CloudServiceResult(
                service=CloudServiceName.NORTHSTAR,
                success=True,
                result=result,
                source="local",
            )
        except Exception as exc:
            return CloudServiceResult(
                service=CloudServiceName.NORTHSTAR,
                success=False,
                error=str(exc),
                source="local",
            )

    async def _northstar_health(self) -> CloudServiceResult:
        if self.northstar_health_url:
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.get(self.northstar_health_url)
                    response.raise_for_status()
                    return CloudServiceResult(
                        service=CloudServiceName.NORTHSTAR_HEALTH,
                        success=True,
                        result=response.json(),
                        source="remote",
                    )
            except Exception as exc:
                return CloudServiceResult(
                    service=CloudServiceName.NORTHSTAR_HEALTH,
                    success=False,
                    error=str(exc),
                    source="remote",
                )

        return CloudServiceResult(
            service=CloudServiceName.NORTHSTAR_HEALTH,
            success=True,
            result=_modal_services().northstar_health(),
            source="local",
        )

    async def _development_blueprint(self, payload: dict[str, Any]) -> CloudServiceResult:
        if self.blueprint_url:
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(self.blueprint_url, json=payload)
                    response.raise_for_status()
                    return CloudServiceResult(
                        service=CloudServiceName.DEVELOPMENT_BLUEPRINT,
                        success=True,
                        result=response.json(),
                        source="remote",
                    )
            except Exception as exc:
                return CloudServiceResult(
                    service=CloudServiceName.DEVELOPMENT_BLUEPRINT,
                    success=False,
                    error=str(exc),
                    source="remote",
                )

        try:
            result = _modal_services().run_development_blueprint(payload)
            return CloudServiceResult(
                service=CloudServiceName.DEVELOPMENT_BLUEPRINT,
                success=True,
                result=result,
                source="local",
            )
        except Exception as exc:
            return CloudServiceResult(
                service=CloudServiceName.DEVELOPMENT_BLUEPRINT,
                success=False,
                error=str(exc),
                source="local",
            )

    async def _development_blueprint_health(self) -> CloudServiceResult:
        if self.blueprint_health_url:
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.get(self.blueprint_health_url)
                    response.raise_for_status()
                    return CloudServiceResult(
                        service=CloudServiceName.DEVELOPMENT_BLUEPRINT_HEALTH,
                        success=True,
                        result=response.json(),
                        source="remote",
                    )
            except Exception as exc:
                return CloudServiceResult(
                    service=CloudServiceName.DEVELOPMENT_BLUEPRINT_HEALTH,
                    success=False,
                    error=str(exc),
                    source="remote",
                )

        return CloudServiceResult(
            service=CloudServiceName.DEVELOPMENT_BLUEPRINT_HEALTH,
            success=True,
            result=_modal_services().development_blueprint_health(),
            source="local",
        )

    async def _precise_mode(self, payload: dict[str, Any]) -> CloudServiceResult:
        if self.precise_mode_url:
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(self.precise_mode_url, json=payload)
                    response.raise_for_status()
                    return CloudServiceResult(
                        service=CloudServiceName.PRECISE_MODE,
                        success=True,
                        result=response.json(),
                        source="remote",
                    )
            except Exception as exc:
                return CloudServiceResult(
                    service=CloudServiceName.PRECISE_MODE,
                    success=False,
                    error=str(exc),
                    source="remote",
                )

        try:
            result = _modal_services().run_precise_mode(payload)
            return CloudServiceResult(
                service=CloudServiceName.PRECISE_MODE,
                success=True,
                result=result,
                source="local",
            )
        except Exception as exc:
            return CloudServiceResult(
                service=CloudServiceName.PRECISE_MODE,
                success=False,
                error=str(exc),
                source="local",
            )

    async def _precise_mode_health(self) -> CloudServiceResult:
        if self.precise_mode_health_url:
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.get(self.precise_mode_health_url)
                    response.raise_for_status()
                    return CloudServiceResult(
                        service=CloudServiceName.PRECISE_MODE_HEALTH,
                        success=True,
                        result=response.json(),
                        source="remote",
                    )
            except Exception as exc:
                return CloudServiceResult(
                    service=CloudServiceName.PRECISE_MODE_HEALTH,
                    success=False,
                    error=str(exc),
                    source="remote",
                )

        return CloudServiceResult(
            service=CloudServiceName.PRECISE_MODE_HEALTH,
            success=True,
            result=_modal_services().precise_mode_health(),
            source="local",
        )

    # --- NotebookLM Cloud Brain (Ω₃) ---------------------------------------

    async def _notebooklm_health(self) -> CloudServiceResult:
        try:
            bridge = _load_notebooklm_bridge()
            ok, msg, latency_ms = await bridge.async_health_probe()
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_HEALTH,
                success=ok,
                result={"message": msg, "latency_ms": round(latency_ms)},
                error=None if ok else msg,
                source="local",
            )
        except Exception as exc:
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_HEALTH,
                success=False,
                error=f"{type(exc).__name__}: {exc}",
                source="local",
            )

    async def _notebooklm_synthesize(self, payload: dict[str, Any]) -> CloudServiceResult:
        query = str(payload.get("query") or payload.get("question") or "").strip()
        if not query:
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_SYNTHESIZE,
                success=False,
                error="missing 'query' in payload",
                source="local",
            )
        notebook_id = payload.get("notebook_id")
        use_cache = bool(payload.get("use_cache", True))
        try:
            bridge = _load_notebooklm_bridge()
            kwargs: dict[str, Any] = {"use_cache": use_cache}
            if notebook_id:
                kwargs["notebook_id"] = str(notebook_id)
            text = await bridge.async_synthesize(query, **kwargs)
            ok = text is not None and not str(text).startswith("[Cloud Brain synthesis failed")
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_SYNTHESIZE,
                success=ok,
                result={
                    "query": query,
                    "notebook_id": notebook_id or bridge.CANONICAL_NOTEBOOK_ID,
                    "text": text,
                    "cache": bridge.cache_stats(),
                },
                error=None if ok else str(text),
                source="local",
            )
        except Exception as exc:
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_SYNTHESIZE,
                success=False,
                error=f"{type(exc).__name__}: {exc}",
                source="local",
            )

    async def _notebooklm_sync(self, payload: dict[str, Any]) -> CloudServiceResult:
        try:
            bridge = _load_notebooklm_bridge()
            kwargs: dict[str, Any] = {}
            if payload.get("notebook_id"):
                kwargs["notebook_id"] = str(payload["notebook_id"])
            if payload.get("note_title"):
                kwargs["note_title"] = str(payload["note_title"])
            if payload.get("extra_summary"):
                kwargs["extra_summary"] = str(payload["extra_summary"])
            if payload.get("content"):
                kwargs["content"] = str(payload["content"])
            result = await bridge.async_sync_state(**kwargs)
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_SYNC,
                success="error" not in result,
                result=result if "error" not in result else {},
                error=result.get("error") if "error" in result else None,
                source="local",
            )
        except Exception as exc:
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_SYNC,
                success=False,
                error=f"{type(exc).__name__}: {exc}",
                source="local",
            )

    # --- Ω₃.2 LADY_APIS research ---------------------------------------

    async def _notebooklm_research_start(self, payload: dict[str, Any]) -> CloudServiceResult:
        query = str(payload.get("query") or payload.get("objective") or "").strip()
        if not query:
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_RESEARCH_START,
                success=False, error="missing 'query' in payload", source="local",
            )
        try:
            bridge = _load_notebooklm_bridge()
            result = await bridge.async_research_start(
                query,
                notebook_id=str(payload.get("notebook_id") or bridge.CANONICAL_NOTEBOOK_ID),
                source=str(payload.get("source", "web")),
                mode=str(payload.get("mode", "fast")),
            )
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_RESEARCH_START,
                success=True, result=result, source="local",
            )
        except Exception as exc:
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_RESEARCH_START,
                success=False, error=f"{type(exc).__name__}: {exc}", source="local",
            )

    async def _notebooklm_research_poll(self, payload: dict[str, Any]) -> CloudServiceResult:
        try:
            bridge = _load_notebooklm_bridge()
            result = await bridge.async_research_poll(
                notebook_id=str(payload.get("notebook_id") or bridge.CANONICAL_NOTEBOOK_ID),
            )
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_RESEARCH_POLL,
                success=True, result=result, source="local",
            )
        except Exception as exc:
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_RESEARCH_POLL,
                success=False, error=f"{type(exc).__name__}: {exc}", source="local",
            )

    # --- Ω₃.3 SIR_SONUS studio ----------------------------------------

    async def _notebooklm_studio_list(self, payload: dict[str, Any]) -> CloudServiceResult:
        try:
            bridge = _load_notebooklm_bridge()
            result = await bridge.async_studio_list(
                artifact_type=str(payload.get("artifact_type", "audio")),
                notebook_id=str(payload.get("notebook_id") or bridge.CANONICAL_NOTEBOOK_ID),
            )
            ok = "error" not in result
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_STUDIO_LIST,
                success=ok,
                result=result if ok else {},
                error=result.get("error") if not ok else None,
                source="local",
            )
        except Exception as exc:
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_STUDIO_LIST,
                success=False, error=f"{type(exc).__name__}: {exc}", source="local",
            )

    async def _notebooklm_studio_generate(self, payload: dict[str, Any]) -> CloudServiceResult:
        artifact_type = str(payload.get("artifact_type") or "").strip()
        if not artifact_type:
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_STUDIO_GENERATE,
                success=False, error="missing 'artifact_type' in payload", source="local",
            )
        try:
            bridge = _load_notebooklm_bridge()
            source_ids = payload.get("source_ids")
            result = await bridge.async_studio_generate(
                artifact_type,
                notebook_id=str(payload.get("notebook_id") or bridge.CANONICAL_NOTEBOOK_ID),
                instructions=payload.get("instructions"),
                source_ids=list(source_ids) if source_ids else None,
            )
            ok = "error" not in result
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_STUDIO_GENERATE,
                success=ok,
                result=result if ok else {},
                error=result.get("error") if not ok else None,
                source="local",
            )
        except Exception as exc:
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_STUDIO_GENERATE,
                success=False, error=f"{type(exc).__name__}: {exc}", source="local",
            )

    # --- Ω₃.4 MASON sources -------------------------------------------

    async def _notebooklm_sources_list(self, payload: dict[str, Any]) -> CloudServiceResult:
        try:
            bridge = _load_notebooklm_bridge()
            result = await bridge.async_sources_list(
                notebook_id=str(payload.get("notebook_id") or bridge.CANONICAL_NOTEBOOK_ID),
            )
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_SOURCES_LIST,
                success=True, result=result, source="local",
            )
        except Exception as exc:
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_SOURCES_LIST,
                success=False, error=f"{type(exc).__name__}: {exc}", source="local",
            )

    async def _notebooklm_sources_add(self, payload: dict[str, Any]) -> CloudServiceResult:
        try:
            bridge = _load_notebooklm_bridge()
            result = await bridge.async_sources_add(
                url=payload.get("url"),
                text=payload.get("text"),
                title=payload.get("title"),
                notebook_id=str(payload.get("notebook_id") or bridge.CANONICAL_NOTEBOOK_ID),
                wait=bool(payload.get("wait", False)),
            )
            ok = "error" not in result
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_SOURCES_ADD,
                success=ok,
                result=result if ok else {},
                error=result.get("error") if not ok else None,
                source="local",
            )
        except Exception as exc:
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_SOURCES_ADD,
                success=False, error=f"{type(exc).__name__}: {exc}", source="local",
            )

    async def _notebooklm_sources_delete(self, payload: dict[str, Any]) -> CloudServiceResult:
        source_id = str(payload.get("source_id") or "").strip()
        if not source_id:
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_SOURCES_DELETE,
                success=False, error="missing 'source_id' in payload", source="local",
            )
        try:
            bridge = _load_notebooklm_bridge()
            result = await bridge.async_sources_delete(
                source_id,
                notebook_id=str(payload.get("notebook_id") or bridge.CANONICAL_NOTEBOOK_ID),
            )
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_SOURCES_DELETE,
                success=True, result=result, source="local",
            )
        except Exception as exc:
            return CloudServiceResult(
                service=CloudServiceName.NOTEBOOKLM_SOURCES_DELETE,
                success=False, error=f"{type(exc).__name__}: {exc}", source="local",
            )
