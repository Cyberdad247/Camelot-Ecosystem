# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

"""01_KERNEL/reasoning/ornith_engine.py — Ornith-1.0 & 35B-MoE Assimilation Engine.

Assimilates DeepReinforce Ornith-1.0 and AEON-7 Ornith-1.0-35B-AEON-Ultimate-Uncensored:
1. 35B-MoE (qwen3_5_moe hybrid 30 GatedDeltaNet + 10 full-attention) architecture config.
2. Abliteration & Uncensored metadata (grimjim NPBA, winsorize 0.995, gaussian decay,
   Expert-Granular Abliteration across 256 fused + 1 shared expert, SSM conv1d repair L36/37).
3. vLLM / NVFP4 (W4A16) + DFlash (n=6 drafter) DGX Spark GB10 deployment parameters and guards.
4. Thinking model (<think>...</think>) & tool call parser with streaming support.
5. High-level OrnithEngine execution and routing interface for Camelot-OS.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import json
import re
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enums & Constants
# ---------------------------------------------------------------------------

class OrnithVariant(str, Enum):
    """Supported model variants in the Ornith family."""
    ORNITH_35B_MOE_UNCENSORED_NVFP4 = "AEON-7/Ornith-1.0-35B-AEON-Ultimate-Uncensored-NVFP4"
    ORNITH_35B_MOE_UNCENSORED_BF16 = "AEON-7/Ornith-1.0-35B-AEON-Ultimate-Uncensored-BF16"
    ORNITH_35B_MOE_BASE = "deepreinforce-ai/Ornith-1.0-35B"
    ORNITH_35B_MOE_FP8 = "deepreinforce-ai/Ornith-1.0-35B-FP8"
    ORNITH_9B_DENSE = "deepreinforce-ai/Ornith-1.0-9B"
    ORNITH_31B_DENSE = "deepreinforce-ai/Ornith-1.0-31B"
    ORNITH_397B_MOE = "deepreinforce-ai/Ornith-1.0-397B"


class PrecisionDtype(str, Enum):
    """Weight and activation quantization precision formats."""
    NVFP4_COMPRESSED = "nvfp4"
    BFLOAT16 = "bfloat16"
    FP8 = "fp8"
    BNB_4BIT = "bnb_4bit"


DEFAULT_DFLASH_DRAFTER = "AEON-7/AEON-DFlash-Qwen3.6-35B-A3B"
DEFAULT_VLLM_CONTAINER = "ghcr.io/aeon-7/aeon-vllm-ultimate:latest"
MAX_CONTEXT_WINDOW = 262144  # 256K


# ---------------------------------------------------------------------------
# 1. Architecture Configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class OrnithArchitectureConfig:
    """Detailed architectural layout of Ornith-1.0-35B MoE and sibling models."""
    model_id: str = OrnithVariant.ORNITH_35B_MOE_UNCENSORED_NVFP4.value
    arch_family: str = "qwen3_5_moe"
    lineage_init: str = "Qwen3.6-35B-A3B"
    total_layers: int = 40
    gated_deltanet_layers: int = 30  # SSM linear-attention recurrent layers
    full_attention_layers: int = 10  # Standard multi-head/GQA full-attention layers
    routed_experts: int = 256        # Fused routed experts
    shared_experts: int = 1          # Dedicated shared expert (A3B MoE)
    top_k_experts: int = 8           # Top-8 active experts per token
    hidden_size: int = 2048
    context_window: int = MAX_CONTEXT_WINDOW
    has_vision_tower: bool = True
    thinking_model: bool = True
    license: str = "MIT"

    def validate_invariants(self) -> bool:
        """Ensure architectural invariants match the proven qwen3_5_moe hybrid spec."""
        if self.gated_deltanet_layers + self.full_attention_layers != self.total_layers:
            raise ValueError(
                f"Layer breakdown ({self.gated_deltanet_layers} SSM + {self.full_attention_layers} Full) "
                f"must sum to total_layers ({self.total_layers})"
            )
        if self.routed_experts != 256 or self.top_k_experts != 8:
            raise ValueError("35B MoE architecture must specify 256 routed experts with top-8 dispatch")
        if self.context_window > MAX_CONTEXT_WINDOW:
            raise ValueError(f"Context window cannot exceed maximum {MAX_CONTEXT_WINDOW}")
        return True


# ---------------------------------------------------------------------------
# 2. Abliteration & Uncensoring Metadata
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AbliterationMetadata:
    """Abliteration recipe, tensor isolation, and empirical validation metrics."""
    base_model: str = OrnithVariant.ORNITH_35B_MOE_BASE.value
    driver: str = "abliterix v1.9 (grimjim NPBA)"
    algorithm: str = "projected_abliteration"  # Norm-Preserving Biprojection Abliteration
    decay_kernel: str = "gaussian"
    winsorize_quantile: float = 0.995
    ssm_repair_layers: Tuple[int, ...] = (36, 37)  # conv1d outlier sigma > 1.5x median rescaled
    expert_granular_ablation: bool = True
    total_experts_steered: int = 256
    shared_expert_steered: bool = True
    router_bias_suppression_max: float = 15.0
    disabled_steering_components: Tuple[str, ...] = (
        "attn.q_proj",
        "attn.k_proj",
        "attn.v_proj",
        "linear_attn.ssm_internal",
        "vision_tower",
    )
    steered_components: Tuple[str, ...] = (
        "attn.o_proj",
        "attn.out_proj",
        "mlp.down_proj",
        "fused_experts.down_proj",
        "shared_expert.down_proj",
    )
    # Validation scores
    refusals_rate_harmful: float = 0.0      # 0/80 refusals (0.0% vs ~94% base)
    agentic_pass_rate_pass1: float = 0.833  # 15/18 probe (identical to base 0.833)
    first_token_kl_divergence: float = 0.0014
    terminal_bench_2_1_score: float = 64.2
    swe_bench_verified_score: float = 75.6
    user_arbitration_clause_active: bool = True

    def get_summary(self) -> Dict[str, Any]:
        """Return structured summary of abliteration status."""
        return {
            "driver": self.driver,
            "algorithm": self.algorithm,
            "refusals": f"{self.refusals_rate_harmful * 100:.1f}% (0/80)",
            "pass_at_1": self.agentic_pass_rate_pass1,
            "kl_divergence": self.first_token_kl_divergence,
            "ssm_conv1d_repair": list(self.ssm_repair_layers),
            "uncensored": True,
            "safety_posture": "Downstream Sovereign HITL Enforcement",
        }


# ---------------------------------------------------------------------------
# 3. vLLM / NVFP4 + DFlash Deployment Parameters
# ---------------------------------------------------------------------------

@dataclass
class OrnithServingConfig:
    """vLLM deployment parameters tailored for DGX Spark GB10 / Blackwell and Cloud."""
    model_path: str = OrnithVariant.ORNITH_35B_MOE_UNCENSORED_NVFP4.value
    served_model_name: str = "ornith-ultimate"
    served_aliases: List[str] = field(default_factory=lambda: ["ornith", "aeon-ultimate", "aeon-fast", "aeon-deep"])
    container_image: str = DEFAULT_VLLM_CONTAINER
    dflash_drafter_path: Optional[str] = DEFAULT_DFLASH_DRAFTER
    num_speculative_tokens: int = 6
    dtype: str = "bfloat16"
    quantization: Optional[str] = "compressed-tensors"  # for NVFP4 MLP-only W4A16
    gpu_memory_utilization: float = 0.60  # 0.60 on DGX Spark unified memory with DFlash
    max_num_seqs: int = 16                # HARD CAP on Spark unified memory to prevent OOM panic
    max_model_len: int = MAX_CONTEXT_WINDOW
    max_num_batched_tokens: int = 16384
    mamba_cache_dtype: str = "float32"    # Required precision for GatedDeltaNet SSM state
    attention_backend: str = "flash_attn" # Mandatory for non-causal vision + DFlash verify
    kv_cache_dtype: str = "bfloat16"      # Forced BF16 due to vision tower
    reasoning_parser: str = "qwen3"
    tool_call_parser: str = "qwen3_coder"
    enable_auto_tool_choice: bool = True
    enable_chunked_prefill: bool = True
    enable_prefix_caching: bool = True
    trust_remote_code: bool = True
    port: int = 8000
    host: str = "0.0.0.0"
    limit_mm_per_prompt: Dict[str, int] = field(default_factory=lambda: {"image": 4, "video": 2})
    mm_encoder_tp_mode: str = "data"
    # Sampling parameters recommended for Ornith reasoning
    recommended_temperature: float = 0.6
    recommended_top_p: float = 0.95
    recommended_top_k: int = 20

    def get_spark_env_vars(self) -> Dict[str, str]:
        """Return environment variables required for GB10 sm_121a Blackwell kernels."""
        return {
            "TORCH_CUDA_ARCH_LIST": "12.1a",
            "CUTE_DSL_ARCH": "sm_121a",
            "ENABLE_NVFP4_SM100": "0",
            "VLLM_USE_FLASHINFER_SAMPLER": "1",
            "VLLM_NVFP4_GEMM_BACKEND": "flashinfer-cutlass",
            "NVIDIA_FORWARD_COMPAT": "1",
            "VLLM_ENABLE_CUDA_COMPATIBILITY": "0",
        }

    def build_vllm_cli_args(self) -> List[str]:
        """Generate vLLM serve command arguments."""
        aliases = [self.served_model_name] + [a for a in self.served_aliases if a != self.served_model_name]
        args = [
            "serve",
            self.model_path,
            "--served-model-name",
            *aliases,
            "--dtype",
            self.dtype,
            "--max-model-len",
            str(self.max_model_len),
            "--max-num-seqs",
            str(self.max_num_seqs),
            "--max-num-batched-tokens",
            str(self.max_num_batched_tokens),
            "--gpu-memory-utilization",
            f"{self.gpu_memory_utilization:.2f}",
            "--mamba-cache-dtype",
            self.mamba_cache_dtype,
            "--attention-backend",
            self.attention_backend,
            "--reasoning-parser",
            self.reasoning_parser,
            "--tool-call-parser",
            self.tool_call_parser,
            "--limit-mm-per-prompt",
            json.dumps(self.limit_mm_per_prompt),
            "--mm-encoder-tp-mode",
            self.mm_encoder_tp_mode,
            "--host",
            self.host,
            "--port",
            str(self.port),
        ]

        if self.quantization:
            args.extend(["--quantization", self.quantization])

        if self.dflash_drafter_path:
            spec_cfg = json.dumps({
                "method": "dflash",
                "model": self.dflash_drafter_path,
                "num_speculative_tokens": self.num_speculative_tokens,
            })
            args.extend(["--speculative-config", spec_cfg])

        if self.enable_auto_tool_choice:
            args.append("--enable-auto-tool-choice")
        if self.enable_chunked_prefill:
            args.append("--enable-chunked-prefill")
        if self.enable_prefix_caching:
            args.append("--enable-prefix-caching")
        if self.trust_remote_code:
            args.append("--trust-remote-code")

        return args

    def build_docker_run_command(self, model_host_dir: str = "/models/ornith-nvfp4", drafter_host_dir: Optional[str] = "/models/ornith-dflash-drafter") -> str:
        """Generate complete DGX Spark docker run command."""
        env_flags = " ".join(f"-e {k}={v}" for k, v in self.get_spark_env_vars().items())
        mount_flags = f"-v {model_host_dir}:/model:ro"
        if drafter_host_dir and self.dflash_drafter_path:
            mount_flags += f" -v {drafter_host_dir}:/drafter:ro"

        # Update paths for inside container
        args_copy = list(self.build_vllm_cli_args())
        args_copy[1] = "/model"  # model path
        if self.dflash_drafter_path and "--speculative-config" in args_copy:
            idx = args_copy.index("--speculative-config")
            args_copy[idx + 1] = json.dumps({
                "method": "dflash",
                "model": "/drafter",
                "num_speculative_tokens": self.num_speculative_tokens,
            })

        cli_str = " ".join(args_copy)
        return (
            f"docker run -d --name ornith-service --gpus all --ipc=host --net=host \\\n"
            f"  {env_flags} \\\n"
            f"  {mount_flags} \\\n"
            f"  --entrypoint vllm {self.container_image} \\\n"
            f"  {cli_str}"
        )


# ---------------------------------------------------------------------------
# 4. Reasoning Thinking Model (<think>...</think>) & Tool Call Parser
# ---------------------------------------------------------------------------

@dataclass
class ToolCallExtraction:
    """Represents a tool call parsed from model output."""
    name: str
    arguments: Dict[str, Any]
    raw_snippet: str


@dataclass
class ParsedReasoningResponse:
    """Separates <think>...</think> chain-of-thought, tool calls, and final response."""
    thinking: str = ""
    answer: str = ""
    tool_calls: List[ToolCallExtraction] = field(default_factory=list)
    has_thinking: bool = False
    has_tool_calls: bool = False
    is_streaming_incomplete: bool = False
    raw_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "thinking": self.thinking,
            "answer": self.answer,
            "tool_calls": [asdict(tc) for tc in self.tool_calls],
            "has_thinking": self.has_thinking,
            "has_tool_calls": self.has_tool_calls,
            "is_streaming_incomplete": self.is_streaming_incomplete,
            "raw_text": self.raw_text,
        }


class OrnithThinkingParser:
    """Parser for Ornith CoT thinking tags (<think>...</think>) and tool invocations."""

    THINK_REGEX = re.compile(r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE)
    UNCLOSED_THINK_REGEX = re.compile(r"<think>(.*)", re.DOTALL | re.IGNORECASE)
    TOOL_CALL_REGEX = re.compile(r"<tool_call>(.*?)</tool_call>", re.DOTALL | re.IGNORECASE)

    @classmethod
    def parse(cls, text: str) -> ParsedReasoningResponse:
        """Parse complete or chunked response from Ornith model."""
        if not text:
            return ParsedReasoningResponse(raw_text="")

        raw = text
        thinking_parts: List[str] = []
        tool_calls: List[ToolCallExtraction] = []
        is_incomplete = False

        # 1. Extract closed <think>...</think>
        think_matches = list(cls.THINK_REGEX.finditer(raw))
        cleaned_text = raw
        if think_matches:
            for match in think_matches:
                thinking_parts.append(match.group(1).strip())
            cleaned_text = cls.THINK_REGEX.sub("", cleaned_text)
        else:
            # Check for unclosed <think> (streaming or interrupted)
            unclosed = cls.UNCLOSED_THINK_REGEX.search(raw)
            if unclosed:
                thinking_parts.append(unclosed.group(1).strip())
                cleaned_text = cls.UNCLOSED_THINK_REGEX.sub("", cleaned_text)
                is_incomplete = True

        # 2. Extract <tool_call>...</tool_call>
        tool_matches = list(cls.TOOL_CALL_REGEX.finditer(cleaned_text))
        if tool_matches:
            for match in tool_matches:
                snippet = match.group(1).strip()
                parsed_call = cls._parse_single_tool_call(snippet)
                if parsed_call:
                    tool_calls.append(parsed_call)
            cleaned_text = cls.TOOL_CALL_REGEX.sub("", cleaned_text)

        thinking_content = "\n\n".join(thinking_parts).strip()
        final_answer = cleaned_text.strip()

        return ParsedReasoningResponse(
            thinking=thinking_content,
            answer=final_answer,
            tool_calls=tool_calls,
            has_thinking=bool(thinking_content),
            has_tool_calls=bool(tool_calls),
            is_streaming_incomplete=is_incomplete,
            raw_text=raw,
        )

    @classmethod
    def _parse_single_tool_call(cls, snippet: str) -> Optional[ToolCallExtraction]:
        """Attempt to parse JSON tool call snippet."""
        try:
            data = json.loads(snippet)
            if isinstance(data, dict):
                name = data.get("name") or data.get("function", {}).get("name", "unknown_tool")
                args = data.get("arguments") or data.get("parameters") or data.get("function", {}).get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {"raw_args": args}
                return ToolCallExtraction(name=str(name), arguments=args, raw_snippet=snippet)
        except Exception:
            pass

        # Regex fallback for {"name": "...", "arguments": {...}}
        name_match = re.search(r'["\']name["\']\s*:\s*["\']([^"\']+)["\']', snippet)
        name = name_match.group(1) if name_match else "generic_tool"
        return ToolCallExtraction(name=name, arguments={"raw": snippet}, raw_snippet=snippet)


# ---------------------------------------------------------------------------
# 5. High-Level Engine & Orchestration
# ---------------------------------------------------------------------------

class OrnithEngine:
    """Primary Ornith-1.0 & 35B-MoE Assimilation Engine for Camelot-OS."""

    def __init__(
        self,
        arch_config: Optional[OrnithArchitectureConfig] = None,
        abliteration_meta: Optional[AbliterationMetadata] = None,
        serving_config: Optional[OrnithServingConfig] = None,
    ) -> None:
        self.arch = arch_config or OrnithArchitectureConfig()
        self.abliteration = abliteration_meta or AbliterationMetadata()
        self.serving = serving_config or OrnithServingConfig()
        self.parser = OrnithThinkingParser()
        self.arch.validate_invariants()

    def get_model_profile(self) -> Dict[str, Any]:
        """Return comprehensive system identity and capabilities."""
        return {
            "model_id": self.arch.model_id,
            "architecture": {
                "family": self.arch.arch_family,
                "lineage": self.arch.lineage_init,
                "total_layers": self.arch.total_layers,
                "gated_deltanet_layers": self.arch.gated_deltanet_layers,
                "full_attention_layers": self.arch.full_attention_layers,
                "routed_experts": self.arch.routed_experts,
                "shared_experts": self.arch.shared_experts,
                "top_k": self.arch.top_k_experts,
                "context_window": self.arch.context_window,
                "vision": self.arch.has_vision_tower,
            },
            "abliteration": self.abliteration.get_summary(),
            "serving": {
                "container": self.serving.container_image,
                "dflash_drafter": self.serving.dflash_drafter_path,
                "gpu_mem_spark": self.serving.gpu_memory_utilization,
                "max_seqs_spark_cap": self.serving.max_num_seqs,
                "recommended_sampling": {
                    "temperature": self.serving.recommended_temperature,
                    "top_p": self.serving.recommended_top_p,
                    "top_k": self.serving.recommended_top_k,
                },
            },
        }

    def build_openai_payload(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Build standard OpenAI-compatible JSON payload configured with Ornith optimal defaults."""
        payload: Dict[str, Any] = {
            "model": self.serving.served_model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature if temperature is not None else self.serving.recommended_temperature,
            "top_p": top_p if top_p is not None else self.serving.recommended_top_p,
            "top_k": top_k if top_k is not None else self.serving.recommended_top_k,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        return payload

    def parse_completion(self, raw_content: str) -> ParsedReasoningResponse:
        """Parse raw model output into thinking and answer sections."""
        return self.parser.parse(raw_content)

    def generate_deploy_script(self, target_dir: str = "/models/ornith-nvfp4") -> str:
        """Generate standalone shell script to serve Ornith on DGX Spark."""
        return self.serving.build_docker_run_command(model_host_dir=target_dir)
