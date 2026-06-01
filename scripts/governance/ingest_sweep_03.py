import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent
import importlib.util

repo_root = Path(__file__).resolve().parent.parent.parent
_MEM_PATH = repo_root / "01_KERNEL" / "memory" / "mempalace_l2.py"
_MEM_SPEC = importlib.util.spec_from_file_location("mempalace_l2", _MEM_PATH)
_MEM_MOD = importlib.util.module_from_spec(_MEM_SPEC)
_MEM_SPEC.loader.exec_module(_MEM_MOD)
MemPalaceL2 = _MEM_MOD.MemPalaceL2

def ingest_sweep_3():
    l2 = MemPalaceL2()
    
    ukgs = [
        {
            "id": "ukg_09_trellis",
            "content": "DISCOVERED_SCHEMA_09: THE TRELLIS RECURSIVE COMPRESSOR. A learnable, fixed-size memory pool for KV-cache. Two-pass recurrent compressor (latent pool + Forget Gate). Reduces 128K context footprint by 99%, enabling Infinite Context on 8GB limits.",
            "tags": ["kv-cache", "compression", "v1000", "memory"]
        },
        {
            "id": "ukg_10_jmoe",
            "content": "DISCOVERED_SCHEMA_10: HYBRID J-MOE (ATTENTION-SSM FUSION). Fuses Transformer layers with Mamba-2 selective scan layers and sparse MoE. 3x throughput gain. Attention for high-precision recall, Mamba for long-range sequence stability.",
            "tags": ["ssm", "mamba-2", "moe", "v1000", "inference"]
        },
        {
            "id": "ukg_11_chunkkv",
            "content": "DISCOVERED_SCHEMA_11: SEMANTIC-CHUNK PRUNING (ChunkKV). Linguistic-Aware KV Pruning replacing Top-K token pruning. Identifies complete linguistic structures. Increases precision by 8.7% over H2O/SnapKV.",
            "tags": ["kv-cache", "pruning", "v1000", "semantics"]
        },
        {
            "id": "ukg_12_opensre_mcp",
            "content": "DISCOVERED_SCHEMA_12: ADAPTIVE SRE PLAYBOOK REASONING (MCP-INTEGRATED). Agentic Multi-Step Remediation using Model Context Protocol (MCP) to query production clusters directly. Manager-Worker pattern. Sub-10 min MTTR.",
            "tags": ["sre", "mcp", "healing", "v1000", "operations"]
        }
    ]
    
    for ukg in ukgs:
        l2.store(
            wing="camelot",
            room="architecture",
            content=ukg["content"],
            metadata={"id": ukg["id"], "source": "sweep_03_distillation", "tags": ",".join(ukg["tags"])},
            tenant_id="sir_helio"
        )
    
    print(f"Successfully ingested {len(ukgs)} UKGs into MemPalace L2.")

if __name__ == "__main__":
    ingest_sweep_3()
