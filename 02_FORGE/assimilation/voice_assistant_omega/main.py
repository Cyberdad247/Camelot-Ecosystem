from __future__ import annotations

import asyncio
import os
import re
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Awaitable, Callable, Iterable

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field


class Provider(StrEnum):
    STUB = "stub"
    LOCAL = "local"
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    LLAMA_CPP = "llama_cpp"
    LUCIDA_RPC = "lucida_rpc"


class IntentLane(StrEnum):
    CONTROLLED = "controlled"
    MODEL = "model"
    SERVICE_GRAPH = "service_graph"


class QuantizationMode(StrEnum):
    NONE = "none"
    INT8 = "int8"
    TERNARY_1_58B = "ternary_1_58b"


class IntentRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4096)
    session_id: str = Field(default="default", min_length=1, max_length=128)
    context: dict[str, Any] = Field(default_factory=dict)


class IntentResponse(BaseModel):
    session_id: str
    lane: IntentLane
    intent: str
    response_text: str
    tool_calls: list[str] = Field(default_factory=list)
    elapsed_ms: int


class AudioEnvelope(BaseModel):
    session_id: str = "default"
    mime_type: str = "audio/pcm"
    sample_rate: int = 16000
    payload_b64: str | None = None
    text: str | None = None


@dataclass(frozen=True)
class RuntimeConfig:
    ws_token: str
    model_provider: Provider
    stt_provider: Provider
    tts_provider: Provider
    memory_limit_mb: int
    quantization_mode: QuantizationMode
    openai_key_present: bool
    openrouter_key_present: bool

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        return cls(
            ws_token=os.getenv("OMEGA_WS_TOKEN", "change-me"),
            model_provider=Provider(os.getenv("OMEGA_MODEL_PROVIDER", "local")),
            stt_provider=Provider(os.getenv("OMEGA_STT_PROVIDER", "stub")),
            tts_provider=Provider(os.getenv("OMEGA_TTS_PROVIDER", "stub")),
            memory_limit_mb=int(os.getenv("OMEGA_MEMORY_LIMIT_MB", "768")),
            quantization_mode=QuantizationMode(
                os.getenv("OMEGA_QUANTIZATION_MODE", "ternary_1_58b")
            ),
            openai_key_present=bool(os.getenv("OPENAI_API_KEY")),
            openrouter_key_present=bool(os.getenv("OPENROUTER_API_KEY")),
        )


@dataclass(frozen=True)
class QuantizationHook:
    mode: QuantizationMode
    max_ram_mb: int

    def model_flags(self) -> dict[str, Any]:
        if self.mode == QuantizationMode.TERNARY_1_58B:
            return {
                "weight_dtype": "ternary",
                "effective_bits": 1.58,
                "activation_dtype": "int8",
                "target_ram_mb": self.max_ram_mb,
            }
        if self.mode == QuantizationMode.INT8:
            return {"weight_dtype": "int8", "target_ram_mb": self.max_ram_mb}
        return {"weight_dtype": "fp16", "target_ram_mb": self.max_ram_mb}


SkillHandler = Callable[[IntentRequest], Awaitable[str]]


@dataclass(frozen=True)
class Skill:
    name: str
    patterns: tuple[re.Pattern[str], ...]
    priority: int
    handler: SkillHandler

    def matches(self, text: str) -> bool:
        return any(pattern.search(text) for pattern in self.patterns)


@dataclass
class SkillRegistry:
    skills: list[Skill] = field(default_factory=list)

    def register(self, skill: Skill) -> None:
        self.skills.append(skill)
        self.skills.sort(key=lambda item: item.priority, reverse=True)

    async def dispatch(self, request: IntentRequest) -> IntentResponse | None:
        started = time.perf_counter()
        normalized = request.text.strip().lower()
        for skill in self.skills:
            if skill.matches(normalized):
                response = await skill.handler(request)
                return IntentResponse(
                    session_id=request.session_id,
                    lane=IntentLane.CONTROLLED,
                    intent=skill.name,
                    response_text=response,
                    tool_calls=[skill.name],
                    elapsed_ms=int((time.perf_counter() - started) * 1000),
                )
        return None


@dataclass(frozen=True)
class ServiceNode:
    name: str
    input_type: str
    endpoint: str
    children: tuple[str, ...] = ()


@dataclass
class ServiceGraph:
    nodes: dict[str, ServiceNode] = field(default_factory=dict)

    def add(self, node: ServiceNode) -> None:
        self.nodes[node.name] = node

    async def run(self, start_nodes: Iterable[str], request: IntentRequest) -> str:
        async def run_node(name: str) -> str:
            node = self.nodes[name]
            child_results = await asyncio.gather(
                *(run_node(child) for child in node.children),
                return_exceptions=False,
            )
            joined = " | ".join(child_results)
            return f"{node.name}({node.input_type}) processed {request.text!r}{': ' + joined if joined else ''}"

        results = await asyncio.gather(*(run_node(name) for name in start_nodes))
        return "\n".join(results)


class WakeGate:
    def __init__(self, wake_terms: tuple[str, ...] = ("omega", "lakisha", "camelot")) -> None:
        self.wake_terms = wake_terms

    async def detect(self, text: str) -> bool:
        lowered = text.lower()
        return any(term in lowered for term in self.wake_terms)


class STTProvider:
    def __init__(self, provider: Provider) -> None:
        self.provider = provider

    async def transcribe(self, envelope: AudioEnvelope) -> str:
        if envelope.text:
            return envelope.text
        if self.provider == Provider.STUB:
            return "omega status"
        raise RuntimeError(f"STT provider {self.provider} is configured but not implemented")


class TTSProvider:
    def __init__(self, provider: Provider) -> None:
        self.provider = provider

    async def synthesize(self, text: str) -> dict[str, str]:
        if self.provider == Provider.STUB:
            return {"mime_type": "text/plain", "text": text}
        return {"mime_type": "application/json", "text": text}


class ModelBridge:
    def __init__(self, config: RuntimeConfig) -> None:
        self.config = config
        self.quantization = QuantizationHook(
            mode=config.quantization_mode,
            max_ram_mb=config.memory_limit_mb,
        )

    async def complete(self, request: IntentRequest) -> str:
        flags = self.quantization.model_flags()
        return (
            f"Model lane ready via {self.config.model_provider}. "
            f"Quantization={flags}. Request={request.text}"
        )


class IntentRouter:
    def __init__(
        self,
        registry: SkillRegistry,
        graph: ServiceGraph,
        model_bridge: ModelBridge,
    ) -> None:
        self.registry = registry
        self.graph = graph
        self.model_bridge = model_bridge

    async def route(self, request: IntentRequest) -> IntentResponse:
        started = time.perf_counter()
        controlled = await self.registry.dispatch(request)
        if controlled:
            return controlled

        text = request.text.lower()
        if any(term in text for term in ("image", "vision", "calendar", "question")):
            response = await self.graph.run(("asr",), request)
            return IntentResponse(
                session_id=request.session_id,
                lane=IntentLane.SERVICE_GRAPH,
                intent="lucida_service_graph",
                response_text=response,
                tool_calls=["asr", "qa"],
                elapsed_ms=int((time.perf_counter() - started) * 1000),
            )

        response = await self.model_bridge.complete(request)
        return IntentResponse(
            session_id=request.session_id,
            lane=IntentLane.MODEL,
            intent="model_completion",
            response_text=response,
            elapsed_ms=int((time.perf_counter() - started) * 1000),
        )


async def reminder_handler(request: IntentRequest) -> str:
    target = request.text.split("remind", 1)[-1].strip() or "the requested person"
    return f"Reminder captured: {target}"


async def order_handler(request: IntentRequest) -> str:
    item = request.text.split("order", 1)[-1].strip() or "requested item"
    return f"Order intent captured: {item}"


async def status_handler(request: IntentRequest) -> str:
    return f"Session {request.session_id} operational. Voice Assistant Omega online."


async def note_handler(request: IntentRequest) -> str:
    note = request.text.split("note", 1)[-1].strip() or request.text
    return f"Note staged: {note}"


def build_registry() -> SkillRegistry:
    registry = SkillRegistry()
    registry.register(
        Skill(
            name="reminder",
            patterns=(re.compile(r"\bremind\b"), re.compile(r"\bfollow up\b")),
            priority=100,
            handler=reminder_handler,
        )
    )
    registry.register(
        Skill(
            name="order",
            patterns=(re.compile(r"\border\b"), re.compile(r"\bpurchase\b")),
            priority=90,
            handler=order_handler,
        )
    )
    registry.register(
        Skill(
            name="status",
            patterns=(re.compile(r"\bstatus\b"), re.compile(r"\bhealth\b")),
            priority=80,
            handler=status_handler,
        )
    )
    registry.register(
        Skill(
            name="note",
            patterns=(re.compile(r"\bnote\b"), re.compile(r"\bwrite down\b")),
            priority=70,
            handler=note_handler,
        )
    )
    return registry


def build_graph() -> ServiceGraph:
    graph = ServiceGraph()
    graph.add(ServiceNode("qa", "text", "lucida://qa"))
    graph.add(ServiceNode("calendar", "text", "lucida://calendar"))
    graph.add(ServiceNode("asr", "audio", "lucida://asr", children=("qa",)))
    return graph


config = RuntimeConfig.from_env()
wake_gate = WakeGate()
stt = STTProvider(config.stt_provider)
tts = TTSProvider(config.tts_provider)
router = IntentRouter(build_registry(), build_graph(), ModelBridge(config))
app = FastAPI(title="Voice Assistant Omega", version="1.0.0")


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "model_provider": config.model_provider,
        "stt_provider": config.stt_provider,
        "tts_provider": config.tts_provider,
        "quantization": QuantizationHook(
            config.quantization_mode,
            config.memory_limit_mb,
        ).model_flags(),
        "credentials": {
            "openai_key_present": config.openai_key_present,
            "openrouter_key_present": config.openrouter_key_present,
        },
    }


@app.post("/v1/intent", response_model=IntentResponse)
async def intent(request: IntentRequest) -> IntentResponse:
    return await router.route(request)


@app.websocket("/v1/audio/ws")
async def audio_ws(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token", "")
    if token != config.ws_token:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_json()
            envelope = AudioEnvelope.model_validate(payload)
            text = await stt.transcribe(envelope)
            if not await wake_gate.detect(text):
                await websocket.send_json({"type": "WAKE_MISS", "text": text})
                continue
            response = await router.route(
                IntentRequest(
                    text=text,
                    session_id=envelope.session_id,
                    context={"transport": "websocket"},
                )
            )
            speech = await tts.synthesize(response.response_text)
            await websocket.send_json(
                {
                    "type": "ASSISTANT_RESPONSE",
                    "intent": response.model_dump(),
                    "speech": speech,
                }
            )
    except WebSocketDisconnect:
        return
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

