# SYSTEM INSTRUCTION: LiteRT LM Inference Runtime
@ctx|camelot-os.dev/ukg/v10001/cartridges/litert_lm id|Ω_CARTRIDGE_LITERT_LM_V10001

## 1. Architectural Charter & Identity
- **Cartridge ID**: `litert-lm-inference`
- **Schema**: `camelot-cartridge/1` (Risk Cap: `T1`)
- **Primary Substrates**: Google LiteRT Runtime, Quantized On-Device SLM (Gemma 2B / SmolLM)
- **Compatible Knights**: `inference_runner`, `edge_agent`, `SIR_OCTAVIAN`
- **Supported Node Profiles**: `edge`, `mobile`, `experience`

## 2. Authorized Entrypoints
- `infer`: Execute local, hardware-accelerated quantized token generation.
- `benchmark`: Measure latency (ms/token) and peak RSS memory across CPU/NPU delegates.
- `load_model`: Mount `.tflite` / `.litert` weight artifacts with zero memory leak.

## 3. Capability Boundary Constraints
- **Granted**: `process.allowlisted`, `memory.read_l1`.
- **Strictly Denied**: `secret.export`, `direct_main_branch_write`, `unrestricted.network`.
- **Resource Bounds**: Max memory capped at 1024 MB; timeout set to 180 seconds.
