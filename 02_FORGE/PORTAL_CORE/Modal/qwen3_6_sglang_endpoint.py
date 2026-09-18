# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Qwen3.6-35B SGLang inference endpoint (Modal, 1xB200).
# App: ep-qwen3-6-35b-a3b. Deploy: `.venv\Scripts\modal.exe deploy <this file>`
# (requires `modal setup`; endpoint bills GPU while containers are live).
"""Qwen/Qwen3.6-35B-A3B on 1xB200 with SGLang.

Serving metadata:
engine: sglang
base_model_repo_id: Qwen/Qwen3.6-35B-A3B
base_model_revision: 995ad96eacd98c81ed38be0c5b274b04031597b0
model_family: qwen36

Deployed with MODAL_IMAGE_BUILDER_VERSION=2025.06"""
import modal


MINUTES = 60
DEFAULT_PORT = 8000
HF_IMAGE_ENV = {
    "HF_XET_HIGH_PERFORMANCE": "1",
}

MODEL_PATH = "/flash-endpoint-model/huggingface/hub/models--Qwen--Qwen3.6-35B-A3B/snapshots/995ad96eacd98c81ed38be0c5b274b04031597b0"
SERVED_MODEL_NAME = "Qwen/Qwen3.6-35B-A3B"
ROUTING_REGION = "us-west"
REQUIRE_AUTHENTICATION = True
SPECULATIVE_DRAFT_MODEL_PATH = "/flash-endpoint-model/huggingface/hub/models--modal-labs--Qwen3.6-35B-A3B-DFlash/snapshots/45197228fd8152743a4566620c7aa4014d35f773"
SGLANG_IMAGE_TAG = "lmsysorg/sglang:v0.5.18-cu130"
AUTOINFERENCE_UTILS_VERSION = "0.2.2"

GPU_TYPE = "B200"
N_GPUS = 1
GPU = f"{GPU_TYPE}:{N_GPUS}"
CPU = 4
MEMORY_MB = 16384

SCALEDOWN_WINDOW = 5 * MINUTES
TARGET_INPUTS = 16
STARTUP_TIMEOUT = 60 * MINUTES

EXTRA_IMAGE_ENV = {
    "HF_XET_HIGH_PERFORMANCE": "1",
    "SGLANG_CUDA_COREDUMP_BEFORE_CRASH": "0",
    "SGLANG_ENABLE_OVERLAP_PLAN_STREAM": "1",
    "SGLANG_PYSPY_DUMP_BEFORE_CRASH": "0",
}

serving_image = (
    modal.Image.from_registry(SGLANG_IMAGE_TAG)
    .uv_pip_install(
        f"autoinference-utils=={AUTOINFERENCE_UTILS_VERSION}",
    )
    .env(HF_IMAGE_ENV | EXTRA_IMAGE_ENV)
)

EXTRA_SERVER_ARGS = {
    "--mamba-scheduler-strategy": "extra_buffer",
    "--mamba-ssm-dtype": "float32",
    "--mem-fraction-static": "0.85",
    "--reasoning-parser": "qwen3",
    "--speculative-algorithm": "DFLASH",
    "--speculative-dflash-block-size": "16",
    "--speculative-draft-attention-backend": "fa4",
    "--tool-call-parser": "qwen3_coder",
    "--trust-remote-code": "",
}

SERVER_ARGS = {
    "--served-model-name": SERVED_MODEL_NAME,
} | EXTRA_SERVER_ARGS


WARMUP_PAYLOAD = {
    "model": SERVED_MODEL_NAME,
    "messages": [{"role": "user", "content": "Reply with JSON facts about Tokyo."}],
    "max_tokens": 64,
    "temperature": 0,
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "city_facts",
            "schema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "population": {"type": "integer"},
                },
                "required": ["city", "population"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
}


app = modal.App(name="ep-qwen3-6-35b-a3b")


@app.server(
    image=serving_image,
    gpu=GPU,
    cpu=CPU,
    memory=MEMORY_MB,
    min_containers=0,
    scaledown_window=SCALEDOWN_WINDOW,
    port=DEFAULT_PORT,
    routing_region=ROUTING_REGION,
    unauthenticated=not REQUIRE_AUTHENTICATION,
    exit_grace_period=25,
    startup_timeout=STARTUP_TIMEOUT,
    target_concurrency=TARGET_INPUTS,
    volumes={"/flash-endpoint-model": modal.Volume.from_name("endpoint-ep-iWfH1j56R3oKwqJvw48tV5")},
)
class Server:
    @modal.enter()
    def startup(self):
        from autoinference_utils.endpoint import SGLangEndpoint, warmup_chat_completions

        self.endpoint = SGLangEndpoint(
            model_path=MODEL_PATH,
            worker_port=DEFAULT_PORT,
            tp=N_GPUS,
            speculative_model_path=SPECULATIVE_DRAFT_MODEL_PATH,
            extra_server_args=SERVER_ARGS,
            health_timeout=STARTUP_TIMEOUT,
            health_poll_interval=5.0,
        )
        self.endpoint.start()
        warmup_chat_completions(
            port=DEFAULT_PORT,
            payload=WARMUP_PAYLOAD,
            successful_requests=2,
            request_timeout=60.0,
        )
        print(f"{SERVED_MODEL_NAME} ({GPU}) sglang deployment is ready.")

    @modal.exit()
    def stop(self):
        if hasattr(self, "endpoint"):
            self.endpoint.stop()
