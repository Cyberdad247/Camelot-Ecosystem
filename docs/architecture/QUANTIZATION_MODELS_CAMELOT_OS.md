# 🔮 CAMELOT-OS QUANTIZATION MODELS ARCHITECTURAL REPORT

**Target Environment:** Cybertronia Windows / Nitro V15  
**RAM Ceiling:** 8,192 MB (8GB)  
**VRAM Ceiling:** 4,096 MB (4GB)  
**Native Engine:** Ouroboros 1.58-Bit Ternary SSM (`01_KERNEL/reasoning/ouroboros_engine`) & OmniRouter (`:20128`)  

---

## 🏛️ ARCHITECTURAL FIT MATRIX

```
┌─────────────────────────────────────────────────────────────────────────────┐
║                         CAMELOT-OS SCARCITY TIER                            ║
├──────────────────────────────┬──────────────────────────────┬───────────────┤
║ 1.58-Bit Ternary (BitNet)    ║ GGUF Importance Matrix       ║ EXL2 / AWQ    ║
║ {-1, 0, +1} Integer Add/Sub  ║ (IQ2_XS / IQ3_XXS / Q4_K_M)  ║ (2.5 - 4.0bpw)║
║ VRAM: ~1.2GB - 2.1GB         ║ VRAM: ~1.1GB - 3.4GB         ║ VRAM: ~3.1GB  ║
└──────────────┬───────────────┴──────────────┬───────────────┴───────┬───────┘
               │                              │                       │
               ▼                              ▼                       ▼
   ⚡ Ouroboros 0.8ms SSM            🔮 OmniRouter (:20128)   🔌 CLIProxyAPI
```

---

## 📋 TOP QUANTIZATION MODELS FOR CAMELOT-OS

### 1. ⚡ 1.58-Bit Ternary Native Models (BitNet b1.58 & Ouroboros Engine)
*Replaces floating-point matrix multiplications with integer addition/subtraction. Ultra-low latency (0.8ms), 3x-10x smaller memory footprint.*

| Model ID | Native Architecture | VRAM Usage | Precision / Format | Camelot-OS Role |
|---|---|:---:|:---:|---|
| **`microsoft/bitnet-b1.58-2B-4T-gguf`** | BitNet b1.58 2B | **1.2 GB** | 1.58-bit Ternary | Rapid Code & Agent Execution (`bitnet.cpp`) |
| **`microsoft/bitnet-b1.58-3B`** | BitNet b1.58 3B | **1.8 GB** | 1.58-bit Ternary | Edge Reasoning & Task DAG Planning |
| **`Ouroboros-1.58bit-SSM-v1`** | Mamba-Firn SSM | **1.1 GB** | 1.58-bit Ternary | On-Device Selective Scan Recurrence (`/api/infer`) |

---

### 2. 🔮 GGUF Quantization Models (IQ2_XS, IQ3_XXS, Q4_K_M)
*Compatible with `llama.cpp`, `ollama`, and `OmniRouter (:20128)`. Fits comfortably inside 4GB VRAM with zero RAM spillover.*

| Model ID | Parameters | VRAM (Q4_K_M) | VRAM (IQ3_XXS) | Primary Use Case |
|---|---|:---:|:---:|---|
| **`Qwen/Qwen2.5-Coder-7B-Instruct-GGUF`** | 7.6 B | 4.1 GB | **3.2 GB** | Local AST Code Generation & Refactoring |
| **`unsloth/gemma-2-2b-it-GGUF`** | 2.6 B | **1.6 GB** | 1.2 GB | Rapid General Reasoning & Instruction |
| **`Qwen/Qwen2.5-1.5B-Instruct-GGUF`** | 1.5 B | **1.1 GB** | 0.9 GB | Sub-millisecond Local Agentic Loops |
| **`HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF`**| 1.7 B | **1.2 GB** | 1.0 GB | Lightweight Hive Swarm Subagent Execution |
| **`microsoft/Phi-3.5-mini-instruct-GGUF`** | 3.8 B | **2.4 GB** | 1.9 GB | High MMLU Benchmark Reasoning |

---

### 3. 🏎️ EXL2 & AWQ 4-Bit Models (High-Speed GPU Ingress)
*Optimized for NVIDIA GPUs with fast FlashAttention-2 kernels.*

| Model ID | Quantization | VRAM Usage | Speeds (tok/s) | Integration |
|---|---|:---:|:---:|---|
| **`turboderp/Qwen2.5-7B-Instruct-exl2`** | 3.0 bpw | **3.1 GB** | ~85 tok/s | ExLlamaV2 / OmniRouter |
| **`Qwen/Qwen2.5-Coder-7B-Instruct-AWQ`** | AWQ 4-bit | **4.0 GB** | ~70 tok/s | vLLM / CLIProxyAPI |

---

## ⚡ EXECUTION & DEPLOYMENT RUNES

```powershell
# 1. Inspect BitNet b1.58 2B GGUF via Sir HuggingFace
python -m control_plane.runic_router --rune Omega_HuggingFace --task "Inspect microsoft/bitnet-b1.58-2B-4T-gguf and Qwen/Qwen2.5-Coder-7B-Instruct-GGUF"

# 2. Sync dynamic quantization tissue into Open-Notebook
python vfs/open_notebook_bridge.py
```
