# SKILL BIBLE — BitNet 1.58-bit Swarm Inference
# Knight: Lukas_Omega (inference engine) / Sir Boris (swarm coord) | Layer: L2_KINETIC | v400.1.0
# LOAD: BITNET — instilled on swarm inference, on-device model, token budget tasks

## WHAT IS BITNET 1.58
Model weights constrained to ternary {-1, 0, +1} (AbsMax quantization to 1.58 bits effective).
8× RAM reduction vs FP32. Enables 6-species Bio-Swarm within 8GB ceiling.
Source: Microsoft/BitNet (github), "The Era of 1-bit LLMs" (Ma et al., 2024).

## SPECIES → MODEL ASSIGNMENT
| Species | Model | Budget | RAM | Use Case |
|---|---|---|---|---|
| Formica (Ant) | BitNet-b1.58-1B | 150 tok | 512 MB | map-reduce file ops |
| Pongid (Gorilla) | BitNet-b1.58-3B | 300 tok | 1024 MB | heavy API calls |
| Castor (Beaver) | BitNet-b1.58-2B | 200 tok | 768 MB | infra/Docker builds |
| Arachne (Spider) | BitNet-b1.58-2B | 200 tok | 768 MB | browser/MCP scraping |
| Simian (Chaos) | BitNet-b1.58-1B | 150 tok | 512 MB | resilience injection |
| Strigiform (Owl) | BitNet-b1.58-1B | 100 tok | 256 MB | oversight (inline) |

**Max concurrent**: 8GB / 7800MB usable. Never exceed ceiling (Titanium Law #7).

## BINARY PATH
- Executable: `CAMELOT_OS/bin/bitnet.cpp`
- Models: `CAMELOT_OS/03_VAULT/models/bitnet/*.gguf`
- Config: `CAMELOT_OS/03_VAULT/training/configs/bitnet_swarm.py`

## CLI INVOCATION PATTERN
```bash
bin/bitnet.cpp \
  -m 03_VAULT/models/bitnet/bitnet-b1.58-2b-q1_5.gguf \
  -p "<system>\n<prompt>" \
  -n 200 -c 768 -t 6 \
  --no-display-prompt -f json
```

## RAM CEILING PROTOCOL
Before spawning any BitNet cell:
1. Call `BitNetSwarm._check_ram_ceiling(species, active_species)`
2. If total_MB > 7800 → defer task, log IRON_GATE warning
3. Strigiform always runs inline (256MB) — never defer owl oversight

## ANTI-PATTERNS
- Running all 6 species simultaneously → ~3840MB nominal but spikes crash 8GB system
- Using Pongid (3B, 1024MB) for simple file ops → use Formica (1B, 512MB)
- Python interpreter for inference when bitnet.cpp binary exists → Kinetic Law #1 violation
- Skipping RAM ceiling check before spawn → OOM crash, T7 violation
- Loading full FP32 model when BitNet GGUF available → 8× RAM waste

## INSTALL TRIGGER
If `bin/bitnet.cpp` missing: `BitNetSwarm.status()` prints install guide.
Lord Archivist GEP scan detects missing binary and logs to learnings.md.
Lady Apis assigned to source latest GGUF from HuggingFace Hub.
