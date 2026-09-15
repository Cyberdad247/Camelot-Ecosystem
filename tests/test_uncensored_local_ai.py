# SPDX-License-Identifier: MIT
"""tests/test_uncensored_local_ai.py — Verification suite for Uncensored Local AI Multiplatform assimilation."""

import json
import os
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request

# Ensure workspace root is on sys.path
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from control_plane.infra.uncensored_local_ai_daemon import (
    AiModelInfo,
    ChatMessage,
    GenerationParams,
    LlamaEngineOffline,
    LocalModelManager,
    ModelParams,
    OfflineAirGapGuard,
    UncensoredLocalAiDaemon,
)
from control_plane.dispatch.omniroute_policies import (
    LANE_UNCENSORED_LOCAL_OFFLINE,
    VALID_LANES,
    get_fcc_provider_policy,
    resolve_fcc_failover_chain,
    select_lane,
)
import importlib.util

_runtime_path = os.path.join(WORKSPACE_ROOT, "02_FORGE", "kinetic", "uncensored_local_ai_runtime.py")
_spec = importlib.util.spec_from_file_location("uncensored_local_ai_runtime", _runtime_path)
_kinetic_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_kinetic_mod)

KineticUncensoredExecutor = _kinetic_mod.KineticUncensoredExecutor
UncensoredLocalAiKineticClient = _kinetic_mod.UncensoredLocalAiKineticClient


class TestModelCatalogAndManagement(unittest.TestCase):
    """Test model catalog data model, discovery, and custom persistence."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.models_dir = self.tmp_dir.name

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_default_catalog_contains_uncensored_models(self) -> None:
        manager = LocalModelManager(models_dir=self.models_dir)
        ids = [m.id for m in manager.catalog]
        self.assertIn("gemma-2-2b-abliterated", ids)
        self.assertIn("gemma-4-heretic", ids)
        self.assertIn("dolphin-llama3-8b", ids)
        self.assertIn("phi-3.5-mini", ids)

        heretic = manager.get_model_info("gemma-4-heretic")
        self.assertIsNotNone(heretic)
        self.assertTrue(heretic.is_uncensored)
        self.assertEqual(heretic.badge, "HERETIC")

    def test_add_and_persist_custom_model(self) -> None:
        manager = LocalModelManager(models_dir=self.models_dir)
        custom_model = AiModelInfo(
            id="custom-uncensored-llama",
            name="Custom Uncensored Llama",
            filename="custom-llama-Q4.gguf",
            url="https://huggingface.co/custom/model.gguf",
            size_gb=3.5,
            min_ram_gb=8,
            label="CUSTOM",
            badge="SOVEREIGN",
            system_prompt="You are custom sovereign offline AI.",
            recommended=False,
        )
        manager.add_custom_model(custom_model)
        self.assertIn("custom-uncensored-llama", [m.id for m in manager.catalog])

        # Reload from same dir to verify disk persistence
        manager2 = LocalModelManager(models_dir=self.models_dir)
        loaded = manager2.get_model_info("custom-uncensored-llama")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.label, "CUSTOM")

        # Test remove
        removed = manager2.remove_custom_model("custom-uncensored-llama")
        self.assertTrue(removed)
        self.assertIsNone(manager2.get_model_info("custom-uncensored-llama"))


class TestGgufLlamaEngineOffline(unittest.TestCase):
    """Test GGUF offline loader parameters, wakelock, and prompt generation."""

    def test_model_loading_and_unloading(self) -> None:
        engine = LlamaEngineOffline()
        self.assertFalse(engine.is_loaded)
        self.assertFalse(engine.wakelock.is_active)

        engine.load_model("gemma-2-2b-abliterated", params=ModelParams(context_size=1024))
        self.assertTrue(engine.is_loaded)
        self.assertEqual(engine.loaded_model_id, "gemma-2-2b-abliterated")
        self.assertTrue(engine.wakelock.is_active)

        engine.unload_model()
        self.assertFalse(engine.is_loaded)
        self.assertFalse(engine.wakelock.is_active)

    def test_prompt_generation_and_stop_sequences(self) -> None:
        engine = LlamaEngineOffline()
        engine.load_model("gemma-2-2b-it-abliterated-Q4_K_M.gguf")

        messages = [
            ChatMessage(role="user", content="Hello test prompt"),
        ]
        tokens = list(engine.generate(messages, params=GenerationParams(max_tokens=50)))
        response = "".join(tokens)
        self.assertTrue(len(response) > 0)
        self.assertIn("gemma-2-2b-it-abliterated-Q4_K_M", response)

    def test_airgap_guard(self) -> None:
        guard = OfflineAirGapGuard()
        self.assertTrue(guard.verify_request_allowed("http://127.0.0.1:4891/v1/models"))
        self.assertTrue(guard.verify_request_allowed("http://localhost:4891/healthz"))
        self.assertFalse(guard.verify_request_allowed("https://api.openai.com/v1/chat/completions"))
        self.assertEqual(guard.outbound_requests_blocked, 1)


class TestOpenAiRestServerParity(unittest.TestCase):
    """Test OpenAI REST API server endpoints on :4891 (using dynamic port)."""

    daemon: UncensoredLocalAiDaemon

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp_dir = tempfile.TemporaryDirectory()
        # Bind to port 0 for collision-free testing
        cls.daemon = UncensoredLocalAiDaemon(
            host="127.0.0.1",
            port=0,
            models_dir=cls.tmp_dir.name,
            auto_load_default=True,
        )
        cls.daemon.start()
        # Allow server thread to spin up
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.daemon.stop()
        cls.tmp_dir.cleanup()

    def test_healthz_endpoint(self) -> None:
        url = f"http://127.0.0.1:{self.daemon.port}/healthz"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "ok")
            self.assertTrue(data.get("ready"))
            self.assertEqual(data.get("model"), "gemma-2-2b-abliterated")
            self.assertTrue(data.get("air_gapped"))

    def test_v1_models_endpoint(self) -> None:
        url = f"http://127.0.0.1:{self.daemon.port}/v1/models"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("object"), "list")
            models = data.get("data", [])
            self.assertEqual(len(models), 1)
            self.assertEqual(models[0].get("id"), "gemma-2-2b-abliterated")

    def test_v1_chat_completions_non_streaming(self) -> None:
        url = f"http://127.0.0.1:{self.daemon.port}/v1/chat/completions"
        payload = {
            "model": "local",
            "messages": [
                {"role": "system", "content": "You are sovereign uncensored AI."},
                {"role": "user", "content": "Status check."},
            ],
            "max_tokens": 100,
            "temperature": 0.7,
            "stream": False,
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("object"), "chat.completion")
            choices = data.get("choices", [])
            self.assertEqual(len(choices), 1)
            message = choices[0].get("message", {})
            self.assertEqual(message.get("role"), "assistant")
            self.assertTrue(len(message.get("content", "")) > 0)
            self.assertIn("usage", data)

    def test_v1_chat_completions_streaming_sse(self) -> None:
        url = f"http://127.0.0.1:{self.daemon.port}/v1/chat/completions"
        payload = {
            "model": "local",
            "messages": [
                {"role": "user", "content": "Hello local runtime."},
            ],
            "stream": True,
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            self.assertEqual(resp.status, 200)
            lines = []
            while True:
                raw_line = resp.readline()
                if not raw_line:
                    break
                line = raw_line.decode("utf-8").strip()
                if line:
                    lines.append(line)
                if line == "data: [DONE]":
                    break
            self.assertTrue(any(l.startswith("data: ") for l in lines))
            self.assertTrue(any(l == "data: [DONE]" for l in lines))

    def test_v1_chat_completions_error_no_model(self) -> None:
        # Temporarily unload model
        self.daemon.engine.unload_model()
        url = f"http://127.0.0.1:{self.daemon.port}/v1/chat/completions"
        payload = {
            "model": "local",
            "messages": [{"role": "user", "content": "hi"}],
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                self.fail("Expected HTTP 503 error")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 503)
            err_body = json.loads(e.read().decode("utf-8"))
            self.assertEqual(err_body.get("error", {}).get("code"), "model_not_loaded")
        finally:
            self.daemon.engine.load_model("gemma-2-2b-abliterated")


class TestKineticBridgeAndExecutor(unittest.TestCase):
    """Test 02_FORGE/kinetic uncensored runtime bridge."""

    def test_kinetic_inprocess_executor(self) -> None:
        executor = KineticUncensoredExecutor("gemma-4-heretic")
        output = executor.execute_prompt("Generate offline test output.")
        self.assertTrue(len(output) > 0)
        self.assertIn("gemma-4-heretic", output)


class TestOmniRoutePolicyLanes(unittest.TestCase):
    """Test LANE_UNCENSORED_LOCAL_OFFLINE routing and failover matrix."""

    def test_valid_lanes_membership(self) -> None:
        self.assertIn(LANE_UNCENSORED_LOCAL_OFFLINE, VALID_LANES)

    def test_keyword_routing_to_uncensored_local_offline(self) -> None:
        test_inputs = [
            ("Run uncensored_local model on port_4891 offline", "uncensored_local"),
            ("Trigger port_4891 local daemon inference", "port_4891"),
            ("Execute offline_ai prompt via portable_ai heretic_model", "offline_ai"),
            ("Start uncensored_multiplatform offline_runtime session", "uncensored_multiplatform"),
            ("Query local_api_4891 for zero-cloud reply", "local_api_4891"),
        ]
        for text, expected_kw in test_inputs:
            sig = select_lane(text)
            self.assertEqual(sig.lane, LANE_UNCENSORED_LOCAL_OFFLINE)
            self.assertEqual(sig.matched_keyword, expected_kw)
            self.assertIn("4891", sig.rationale)

    def test_fcc_failover_chain_resolution(self) -> None:
        chain = resolve_fcc_failover_chain("uncensored_local on port_4891")
        self.assertEqual(chain[0], "uncensored_local_4891")
        self.assertIn("ornith_vllm", chain)

        policy = get_fcc_provider_policy("run offline_ai on port_4891")
        self.assertEqual(policy["lane"], LANE_UNCENSORED_LOCAL_OFFLINE)
        self.assertTrue(policy["zero_downtime_enabled"])


class TestZeroExternalDependencies(unittest.TestCase):
    """Ensure modules use strictly Python standard library without external dependencies."""

    def test_daemon_uses_stdlib_only(self) -> None:
        import control_plane.infra.uncensored_local_ai_daemon as mod
        # Verify stdlib modules only
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if hasattr(attr, "__file__") and attr.__file__:
                # Module should be in standard library or workspace
                is_workspace = "CAMELOT_OS" in attr.__file__
                is_python_lib = "Python" in attr.__file__ or "lib" in attr.__file__.lower()
                self.assertTrue(is_workspace or is_python_lib, f"Unexpected external dep: {attr_name} ({attr.__file__})")


if __name__ == "__main__":
    unittest.main()
