# SPDX-License-Identifier: MIT
"""tests/test_xinference_adapter.py — Comprehensive tests for Xinference Multi-Engine Cluster Adapter.

Tests cover:
1. ModelSpec & WorkerResource data structures and serialization.
2. Multi-backend engine wrappers: XLlamaCppEngine, VLLMEngine, SGLangEngine, TransformersEngine.
3. Distributed worker node orchestration & resource tracking.
4. Cluster Supervisor: worker scheduling, multi-model lifecycle, round-robin replica routing, health guard.
5. OpenAI-compatible REST server (:9997 API endpoints, sync & SSE streaming, error handling).
6. XinferenceKineticClient forge client integration.
7. OmniRoute lane policy selection (LANE_XINFERENCE_MULTI_MODEL).
8. Zero external dependencies stdlib purity check.
"""

from __future__ import annotations

import ast
import inspect
import socket
import time


from control_plane.dispatch.omniroute_policies import (
    LANE_XINFERENCE_MULTI_MODEL,
    VALID_LANES,
    XINFERENCE_MULTI_MODEL_KEYWORDS,
    get_fcc_provider_policy,
    resolve_fcc_failover_chain,
    select_lane,
)
from control_plane.infra.xinference_engine_adapter import (
    EngineBackend,
    ModelSpec,
    ModelType,
    WorkerResource,
    WorkerStatus,
    XLlamaCppEngine,
    VLLMEngine,
    SGLangEngine,
    TransformersEngine,
    XinferenceClusterSupervisor,
    XinferenceRestDaemon,
    XinferenceWorkerNode,
    create_engine_wrapper,
)
import os
import importlib.util

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_runtime_path = os.path.join(WORKSPACE_ROOT, "02_FORGE", "kinetic", "xinference_kinetic_runtime.py")
_spec = importlib.util.spec_from_file_location("xinference_kinetic_runtime", _runtime_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
XinferenceKineticClient = _mod.XinferenceKineticClient


# ── 1. Data Models & Specs ──────────────────────────────────────────────────

def test_model_spec_serialization():
    spec = ModelSpec(
        model_uid="qwen-2.5-coder",
        model_name="qwen2.5-coder-7b",
        model_type=ModelType.LLM,
        engine=EngineBackend.XLLAMACPP,
        quantization="q4_k_m",
        context_length=8192,
        gpu_layers=33,
        replica_count=2,
    )
    d = spec.to_dict()
    assert d["model_uid"] == "qwen-2.5-coder"
    assert d["model_name"] == "qwen2.5-coder-7b"
    assert d["model_type"] == "LLM"
    assert d["engine"] == "xllamacpp"
    assert d["quantization"] == "q4_k_m"
    assert d["context_length"] == 8192
    assert d["gpu_layers"] == 33

    restored = ModelSpec.from_dict(d)
    assert restored.model_uid == spec.model_uid
    assert restored.model_name == spec.model_name
    assert restored.engine == spec.engine
    assert restored.context_length == spec.context_length


def test_worker_resource_and_descriptor():
    res = WorkerResource(
        cpu_count=8,
        total_memory_mb=32768,
        available_memory_mb=24576,
        gpu_count=2,
        gpu_vram_total_mb=49152,
        gpu_vram_available_mb=40960,
        device_ids=[0, 1],
        max_slots=16,
        used_slots=2,
    )
    d = res.to_dict()
    assert d["cpu_count"] == 8
    assert d["gpu_count"] == 2
    assert d["gpu_vram_total_mb"] == 49152

    node = XinferenceWorkerNode("worker-node-1", "127.0.0.1", 9998, res)
    desc = node.descriptor()
    assert desc.worker_uid == "worker-node-1"
    assert desc.status == WorkerStatus.ONLINE
    node.ping()
    assert node.last_heartbeat > 0


# ── 2. Multi-Backend Engine Wrappers ────────────────────────────────────────

def test_xllamacpp_engine_wrapper():
    spec = ModelSpec(
        model_uid="llama-3-8b",
        model_name="llama-3-8b-instruct",
        engine=EngineBackend.XLLAMACPP,
        quantization="q4_k_m",
    )
    engine = create_engine_wrapper(spec)
    assert isinstance(engine, XLlamaCppEngine)

    # Chat completion
    messages = [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a binary search function."},
    ]
    resp = engine.chat(messages, temperature=0.7)
    assert "choices" in resp
    assert len(resp["choices"]) > 0
    assert "content" in resp["choices"][0]["message"]
    assert "xllamacpp" in resp["choices"][0]["message"]["content"]
    assert resp["backend"] == "xllamacpp"

    # Streaming chat completion
    stream_chunks = list(engine.chat_stream(messages))
    assert len(stream_chunks) > 0
    assert any("delta" in c["choices"][0] for c in stream_chunks)

    # Text completion
    gen = engine.generate("Scaffold a python class")
    assert "text" in gen["choices"][0]
    assert gen["backend"] == "xllamacpp"

    # Text completion streaming
    gen_chunks = list(engine.generate_stream("Scaffold a python class"))
    assert len(gen_chunks) > 0

    # Embeddings & Reranking
    embeddings = engine.embed(["test vector 1", "test vector 2"])
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 16

    rerank_res = engine.rerank("python", ["python guide", "java guide", "python advanced"])
    assert len(rerank_res) == 3
    assert rerank_res[0]["relevance_score"] >= rerank_res[-1]["relevance_score"]


def test_vllm_engine_wrapper():
    spec = ModelSpec(
        model_uid="mistral-7b-vllm",
        model_name="mistral-7b",
        engine=EngineBackend.VLLM,
        tensor_parallel_size=2,
    )
    engine = create_engine_wrapper(spec)
    assert isinstance(engine, VLLMEngine)

    messages = [{"role": "user", "content": "High throughput request"}]
    resp = engine.chat(messages)
    assert "PagedAttention" in resp["choices"][0]["message"]["content"]
    assert "tp=2" in resp["choices"][0]["message"]["content"]
    assert resp["backend"] == "vLLM"

    chunks = list(engine.chat_stream(messages))
    assert len(chunks) > 0

    gen = engine.generate("Generate tokens fast")
    assert "vLLM" in gen["choices"][0]["text"]

    embeds = engine.embed(["query doc"])
    assert len(embeds[0]) == 32


def test_sglang_engine_wrapper():
    spec = ModelSpec(
        model_uid="deepseek-sglang",
        model_name="deepseek-coder",
        engine=EngineBackend.SGLANG,
    )
    engine = create_engine_wrapper(spec)
    assert isinstance(engine, SGLangEngine)

    messages = [{"role": "user", "content": "Execute structured query"}]
    resp = engine.chat(messages)
    assert "RadixAttention" in resp["choices"][0]["message"]["content"]
    assert resp["backend"] == "SGLang"

    chunks = list(engine.chat_stream(messages))
    assert len(chunks) > 0

    gen = engine.generate("JSON schema format")
    assert "SGLang" in gen["choices"][0]["text"]


def test_transformers_engine_wrapper():
    spec = ModelSpec(
        model_uid="hf-bert-model",
        model_name="bert-base-uncased",
        model_type=ModelType.EMBEDDING,
        engine=EngineBackend.TRANSFORMERS,
    )
    engine = create_engine_wrapper(spec)
    assert isinstance(engine, TransformersEngine)

    messages = [{"role": "user", "content": "Hello HF"}]
    resp = engine.chat(messages)
    assert "Transformers" in resp["choices"][0]["message"]["content"]
    assert resp["backend"] == "Transformers"

    embeds = engine.embed(["huggingface test text"])
    assert len(embeds) == 1
    assert len(embeds[0]) == 16

    reranks = engine.rerank("search query", ["relevant document", "other document"])
    assert len(reranks) == 2


# ── 3. Distributed Worker Orchestration & Supervisor ────────────────────────

def test_supervisor_worker_management_and_scheduling():
    supervisor = XinferenceClusterSupervisor(supervisor_uid="test-sup", heartbeat_timeout=2.0)
    try:
        # Check initial local default worker
        workers = supervisor.list_workers()
        assert len(workers) >= 1

        # Register additional custom worker node
        w2 = XinferenceWorkerNode(
            worker_uid="remote-worker-2",
            worker_ip="192.168.1.50",
            worker_port=9998,
            resource=WorkerResource(cpu_count=16, max_slots=32, available_memory_mb=65536),
        )
        supervisor.register_worker(w2)
        assert len(supervisor.list_workers()) >= 2

        # Launch model
        spec = ModelSpec(
            model_uid="cluster-model-1",
            model_name="cluster-model-1",
            engine=EngineBackend.XLLAMACPP,
        )
        uid = supervisor.launch_model(spec)
        assert uid == "cluster-model-1"

        models = supervisor.list_models()
        assert len(models) == 1
        assert models[0]["id"] == "cluster-model-1"
        assert models[0]["status"] == "RUNNING"

        desc = supervisor.describe_model("cluster-model-1")
        assert desc is not None
        assert desc["model_name"] == "cluster-model-1"

        # Resolve engine and round-robin
        eng = supervisor.get_engine_for_model("cluster-model-1")
        assert eng is not None
        assert isinstance(eng, XLlamaCppEngine)

        # Cluster status
        status = supervisor.get_cluster_status()
        assert status["status"] == "HEALTHY"
        assert status["total_models"] == 1
        assert status["total_workers"] >= 2

        # Terminate model
        term_ok = supervisor.terminate_model("cluster-model-1")
        assert term_ok is True
        assert len(supervisor.list_models()) == 0

        # Unregister worker
        unreg_ok = supervisor.unregister_worker("remote-worker-2")
        assert unreg_ok is True
    finally:
        supervisor.shutdown()


def test_supervisor_worker_health_check_timeout():
    supervisor = XinferenceClusterSupervisor(supervisor_uid="test-sup-health", heartbeat_timeout=0.01)
    try:
        stale_worker = XinferenceWorkerNode(
            worker_uid="stale-worker-node",
            worker_ip="10.0.0.99",
            worker_port=9998,
        )
        stale_worker.last_heartbeat = time.time() - 10.0  # Missed heartbeat
        supervisor.register_worker(stale_worker)

        supervisor.check_worker_health()
        assert stale_worker.status == WorkerStatus.OFFLINE
    finally:
        supervisor.shutdown()


# ── 4. OpenAI-Compatible REST Server (:9997) & Kinetic Client ───────────────

def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_rest_daemon_and_kinetic_client():
    free_port = _get_free_port()
    supervisor = XinferenceClusterSupervisor(supervisor_uid="test-rest-supervisor")
    daemon = XinferenceRestDaemon(host="127.0.0.1", port=free_port, supervisor=supervisor)
    bound_port = daemon.start(daemon=True)

    client = XinferenceKineticClient(
        base_url=f"http://127.0.0.1:{bound_port}/v1",
        timeout_seconds=10.0,
    )

    try:
        time.sleep(0.1)  # Allow socket to bind

        # 1. Health check
        health = client.check_health()
        assert health.get("status") == "ok"
        assert health.get("engine") == "xinference"

        # 2. Cluster info & workers
        cluster_info = client.get_cluster_status()
        assert cluster_info.get("status") in ("HEALTHY", "DEGRADED")
        workers = client.list_workers()
        assert len(workers) >= 1

        # 3. Launch model via API
        launch_res = client.launch_model(
            model_name="qwen-2.5-7b",
            model_type="LLM",
            engine="xllamacpp",
            quantization="q4_k_m",
            model_uid="qwen-rest-test",
        )
        assert launch_res.get("model_uid") == "qwen-rest-test"
        assert launch_res.get("status") == "RUNNING"

        # 4. List and describe models
        models = client.list_models()
        assert len(models) >= 1
        assert any(m["id"] == "qwen-rest-test" for m in models)

        desc = client.describe_model("qwen-rest-test")
        assert desc.get("id") == "qwen-rest-test"
        assert desc.get("model_engine") == "xllamacpp"

        # 5. Chat completion (sync)
        chat_resp = client.chat_complete(
            model="qwen-rest-test",
            messages=[{"role": "user", "content": "Explain quicksort"}],
        )
        assert "choices" in chat_resp
        assert len(chat_resp["choices"]) > 0
        content = chat_resp["choices"][0]["message"]["content"]
        assert "quicksort" in content or "xllamacpp" in content

        # 6. Streaming chat completion (SSE)
        stream_chunks = list(client.stream_chat_complete(
            model="qwen-rest-test",
            messages=[{"role": "user", "content": "Explain merge sort"}],
        ))
        assert len(stream_chunks) > 0
        full_streamed = "".join(stream_chunks)
        assert len(full_streamed) > 0

        # 7. Text completion
        text_resp = client.text_complete(
            model="qwen-rest-test",
            prompt="def fibonacci(n):",
        )
        assert "choices" in text_resp
        assert len(text_resp["choices"]) > 0

        # 8. Embeddings
        embed_resp = client.embed(
            texts=["camelot sovereign ai", "xinference distributed orchestration"],
            model="qwen-rest-test",
        )
        assert len(embed_resp) == 2
        assert len(embed_resp[0]) > 0

        # 9. Rerank
        rerank_resp = client.rerank(
            query="sovereign",
            documents=["camelot sovereign ai", "another document"],
            model="qwen-rest-test",
        )
        assert len(rerank_resp) == 2

        # 10. Terminate model
        term_res = client.terminate_model("qwen-rest-test")
        assert term_res.get("status") == "terminated"

    finally:
        daemon.stop()


# ── 5. OmniRoute Policy Integration ─────────────────────────────────────────

def test_omniroute_policy_xinference_lane_selection():
    # Direct keyword routing
    assert LANE_XINFERENCE_MULTI_MODEL in VALID_LANES

    test_queries = [
        "Deploy model on xinference multi_model_cluster",
        "Run distributed worker cluster on port_9997",
        "Execute local inference with xllamacpp engine",
        "Route high throughput task to vllm backend",
        "Execute structured decoding via sglang",
        "Deploy model_replica on xinference cluster",
    ]

    for q in test_queries:
        sig = select_lane(q)
        assert sig.lane == LANE_XINFERENCE_MULTI_MODEL
        assert "Xinference" in sig.rationale
        assert sig.matched_keyword in XINFERENCE_MULTI_MODEL_KEYWORDS

    # Failover chain and policy
    chain = resolve_fcc_failover_chain("xinference distributed inference")
    assert chain[0] == "xinference_cluster_9997"

    policy = get_fcc_provider_policy("deploy model on xinference cluster")
    assert policy["lane"] == LANE_XINFERENCE_MULTI_MODEL
    assert policy["primary_provider"] == "xinference_cluster_9997"
    assert policy["zero_downtime_enabled"] is True


# ── 6. Zero External Dependencies Purity Check ──────────────────────────────

def test_xinference_adapter_stdlib_only():
    """Verify that xinference adapter has zero dependencies outside Python stdlib."""
    import control_plane.infra.xinference_engine_adapter as adapter_mod
    runtime_mod = _mod

    stdlib_prefixes = {
        "__future__", "collections", "dataclasses", "enum", "hashlib",
        "http", "json", "math", "os", "platform", "re", "socket",
        "socketserver", "sys", "threading", "time", "typing",
        "urllib", "uuid", "control_plane", "02_FORGE",
    }

    for mod in (adapter_mod, runtime_mod):
        source = inspect.getsource(mod)
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_pkg = alias.name.split(".")[0]
                    assert root_pkg in stdlib_prefixes, f"Non-stdlib import detected: {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_pkg = node.module.split(".")[0]
                    assert root_pkg in stdlib_prefixes, f"Non-stdlib import from detected: {node.module}"
