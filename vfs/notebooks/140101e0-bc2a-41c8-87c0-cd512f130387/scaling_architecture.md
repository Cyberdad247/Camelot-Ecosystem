# Titan Grade and Above Scaling Architecture
*Distributed Topology, High-Concurrency Mesh & Hardware Scarcity Governance*

```
                 ┌──────────────────────────────────────────────┐
                 │       KING ARTHUR (Operator Sovereign)       │
                 └──────────────────────┬───────────────────────┘
                                        │ (Arthur Ed25519)
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │           ANYA_OMEGA (Helm Gate)             │
                 └──────┬───────────────┬────────────────┬──────┘
                        │               │                │
            ┌───────────▼─────┐ ┌───────▼──────┐ ┌───────▼─────────────┐
            │   CYBERTRONIA   │ │   VPS HUB    │ │  EXCALIBUR S26 ULTRA │
            │  (Windows Main) │ │   (KVM563)   │ │  (Android Sentinel)  │
            │   100.118.224.52│ │162.35.107.134│ │  100.106.246.126    │
            └─────────────────┘ └──────────────┘ └─────────────────────┘
```

## 1. Distributed Multi-Tier Memory Storage
- **Tier-0 Local VFS:** Position-addressed files under `vfs/` providing zero-latency reads.
- **Tier-1 MemCastle & DuckDB-WASM:** Ephemeral in-memory vector cache with sqlite-vec for sub-millisecond local similarity lookup.
- **Tier-2 Graphiti Temporal Knowledge Graph:** Bi-temporal interval tracking (`valid_at`, `expired_at`) in partitioned databases (`03_VAULT/memory/graphiti/<knight_id>_graphiti.db`), slashing context prompt tokens by up to 90%.
- **Tier-3 WorldTree CloudBrain Mesh:** Distributed 294-notebook knowledge mesh anchored to Root UUID `a0a4bfb9-e847-4c38-be39-7aee398f0795`.

## 2. Cryptographic Receipts & Merkle Tenancy (RFC 8785)
- **TenantReceiptChain:** Immutable append-only cryptographic ledger where each receipt binds to `parent_hash = sha256(...)`, monotonic `height`, and operator Ed25519 signature.
- **Row-Level Security (RLS):** Strict multi-tenant isolation enforced in PostgreSQL (`ENABLE` and `FORCE ROW LEVEL SECURITY`) keyed to `current_setting('app.current_tenant_id')`.
- **Compound Idempotency Key:** `SHA-256(client_key || tenant_id || manifest_hash)` with sub-second FastMutex and WAL persistence.

## 3. Hardware Scarcity Protocol (8GB Ceiling)
- **VPS Hub KVM563:** Hard ceiling of 7.2GB memory usage monitored via Linux eBPF PSI (`/proc/pressure/memory`).
- **Hysteresis Throttling:** Automatic SIGSTOP / SIGCONT process deprioritization when memory pressure exceeds 80%.
- **Mobile Sentinel Slice:** Samsung Galaxy S26 Ultra allocated max 350MB active RAM for Kickbox-audio VAD, WebRTC, and telemetry.
- **Rule 7 Hotpath:** 0% Python and 0% Node in the high-concurrency dispatch path. 100% bare-metal systemd services, Rust crates (`camelot-crawler`, `camelot-harness-forge`), Go daemons, and Wasmtime modules.

## 4. Tailscale Mesh Inventory
- `cybertronia` (`100.118.224.52`): Windows Orchestrator
- `vashawns-s26-ultra` (`100.106.246.126`): Excalibur Command Center / Mobile Cockpit
- `fothers-camelot` (`100.121.48.50`): Windows Sovereign Secondary
- `lakesha` (`100.100.155.55`): Lakisha Voice OS Host
- `camelot-relay-modal` (`100.84.98.39`): Linux Cloud Relay
- `kba-services` (`100.71.218.75`): Linux Remote Services
- `motorola-moto-g-power-5g---2024` (`100.89.129.105`): Auxiliary Mobile Sentinel
