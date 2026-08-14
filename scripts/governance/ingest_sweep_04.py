# SPDX-License-Identifier: MIT

import importlib.util
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent
_MEM_PATH = repo_root / "01_KERNEL" / "memory" / "mempalace_l2.py"
_MEM_SPEC = importlib.util.spec_from_file_location("mempalace_l2", _MEM_PATH)
_MEM_MOD = importlib.util.module_from_spec(_MEM_SPEC)
_MEM_SPEC.loader.exec_module(_MEM_MOD)
MemPalaceL2 = _MEM_MOD.MemPalaceL2

def ingest_sweep_4():
    l2 = MemPalaceL2()
    
    ukgs = [
        {
            "id": "ukg_r1_affinity",
            "content": "DISCOVERED_SCHEMA_R1: STATEFUL AFFINITY ROUTING. Use a router that understands prefill vs decode. Route follow-ups to the same worker that holds the KV cache using affinity keys (session_id, template_id) to maximize cache reuse.",
            "tags": ["routing", "cache-affinity", "vllM", "v1000"]
        },
        {
            "id": "ukg_r2_disaggregated",
            "content": "DISCOVERED_SCHEMA_R2: DISAGGREGATED SERVING & RDMA WARNING. Separate prefill and decode worker pools. Dynamo explicit warning: KV transfer without RDMA creates massive bottlenecks. Prefer affinity routing over disaggregation if fast KV transport is unavailable.",
            "tags": ["dynamo", "disaggregation", "rdma", "v1000"]
        },
        {
            "id": "ukg_r3_staging",
            "content": "DISCOVERED_SCHEMA_R3: GPU STAGING BUFFERS. Efficient KV transfer trick: gather head slices into contiguous buffer on prefill side, bulk RDMA transfer, then scatter into decode-side KV pages.",
            "tags": ["kv-transfer", "sglang", "optimization", "v1000"]
        },
        {
            "id": "ukg_r4_dualmap",
            "content": "DISCOVERED_SCHEMA_R4: DUALMAP-LITE SLO ESCAPE HATCH. Always affinity creates hotspots; always load-balance kills cache. Solution: Default to affinity key. Monitor TTFT. If TTFT breaches SLO, temporarily relax affinity and route to least-loaded worker.",
            "tags": ["dualmap", "routing", "slo", "v1000"]
        },
        {
            "id": "ukg_r5_feather",
            "content": "DISCOVERED_SCHEMA_R5: FEATHER HOMOGENEOUS MICROBATCHING. Batch formation should stop early for prefix-homogeneous microbatches. Partition requests by template_id/prefix-hash bucket and build batches preferentially within buckets to maximize internal cache hits.",
            "tags": ["feather", "batching", "scheduler", "v1000"]
        }
    ]
    
    for ukg in ukgs:
        l2.store(
            wing="camelot",
            room="architecture",
            content=ukg["content"],
            metadata={"id": ukg["id"], "source": "sweep_04_distillation", "tags": ",".join(ukg["tags"])},
            tenant_id="sir_helio"
        )
    
    print(f"Successfully ingested {len(ukgs)} UKGs into MemPalace L2.")

if __name__ == "__main__":
    ingest_sweep_4()
