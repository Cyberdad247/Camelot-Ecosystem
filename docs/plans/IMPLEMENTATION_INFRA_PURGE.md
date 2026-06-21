# IMPLEMENTATION: Infrastructure Purge (Redis & Qdrant Decommissioning)
**Status:** DRAFT  
**Objective:** Decouple Camelot-OS Kernel from external infrastructure services to achieve absolute sovereignty and "Dark Mode" stability.

## 1. Architectural Changes
- **Memory Layer:** Replace `redis_store.py` and `qdrant_store.py` with a unified `local_sovereign_store.py` (SQLite-backed).
- **Context Hydration:** Migrate `HydrationManager` from Redis hashes to local file-based `tissue/` caching.
- **Boot Sequence:** Remove the `boot_hermes_omniroute_orchestrator` phase from the `awaken` lifecycle.

## 2. Phase 1: Qdrant Removal
- [ ] Delete `01_KERNEL/memory/qdrant_store.py`.
- [ ] Remove `qdrant_client` from `requirements.txt` and `pyproject.toml`.
- [ ] Clean up imports in:
    - `01_KERNEL/memory/agent_memory.py`
    - `01_KERNEL/merlin/merlin_omega.py`
    - `01_KERNEL/merlin/rag/chronos_haystack.py`

## 3. Phase 2: Redis Migration
- [ ] Refactor `01_KERNEL/memory/redis_store.py` -> `01_KERNEL/memory/local_store.py`.
- [ ] Implement SQLite backend for session memory and vector metadata.
- [ ] Update `HydrationManager` in `hydration_manager.py` to use `local_store.py`.
- [ ] Update `Memory_Squire` (FastAPI) to point at local SQLite instead of Redis.

## 4. Phase 3: Boot Streamlining
- [ ] Modify `control_plane/boot_sequence.py`:
    - Disable `boot_hermes_omniroute_orchestrator`.
    - Remove Redis health probes (`:6379`).
- [ ] Update `01_KERNEL/config/registry/chimera_unified_kernel.json` to remove Redis/Qdrant endpoints.
- [ ] Update `bin/awaken.py` to reflect simplified dependency tree.

## 5. Verification & Testing
- [ ] `pytest tests/test_hydration.py` (Must pass without Redis).
- [ ] `pytest tests/test_boot_omniroute.py` (Verify warning-free boot).
- [ ] Manual `//BOOT` check to confirm UI/HUD stability.

## 6. Rollback Strategy
- Keep backups of `redis_store.py` and `qdrant_store.py` in `99_ARCHIVE/infra_purge_backup/`.
- Maintain git checkpoints before each phase.
