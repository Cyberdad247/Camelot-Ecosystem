# EXCALIBUR v1000.0.0 — Topological Map :: PROFILE nitro-v15-cpu
> PRD 1 :: SIR HELIO :: CURRENT Acer Nitro V 15 substrate vs TARGET EXCALIBUR topology

```mermaid
flowchart TB
    subgraph CUR["CURRENT — Acer Nitro V 15 (pre-flight)"]
        direction TB
        C0["x86_64 CPU substrate · 8GB RAM"]
        C1["Linux / bash shell (WSL-aware)"]
        C2["NVMe SSD @ $HOME"]
        C3["python3 / rustc / cargo / bwrap ??? (unverified)"]
        C4["Flat process space — no KV governance, no isolation"]
        C0 --> C1 --> C2
        C1 --> C3
        C1 --> C4
    end
    subgraph TGT["TARGET — EXCALIBUR Topology (CPU-only)"]
        direction TB
        R["1.5B RL-Conductor<br/>(Runic routing / dispatch)"]
        O["Ouroboros Engine<br/>1.58-bit SSM · Zero KV-Cache"]
        T["Trellis<br/>512MB Fixed KV-Pool"]
        A["Aegis Shield<br/>eBPF(BTF) + Regex PII redaction"]
        Z["Omega-Root<br/>bubblewrap/unshare immutable chroot"]
        R -->|routes| O
        O -->|streams| T
        R -->|all I/O gated by| A
        A -.->|fault / breach| Z
        Z -.->|restore| R
    end
    C0 -.->|"audit: x86_64 / cores / 8GB ceiling"| R
    C3 -.->|"toolchain + sandbox gate"| A
    C2 -.->|"NVMe free-space gate (>=4GB)"| T
```

## Component → Pre-flight Gate Mapping (nitro-v15-cpu)
| EXCALIBUR Component | Physical Law | Audited By |
|---|---|---|
| 1.5B RL-Conductor | `uname -m == x86_64`, cores > 0 | Codex → Boris |
| Ouroboros (1.58-bit SSM, Zero KV) | MemAvailable ≥ 1712MB headroom | Codex → Boris |
| Trellis 512MB Fixed KV-Pool | avail RAM reserves 512MB | Boris |
| Aegis Shield (eBPF/Regex PII) | `/sys/kernel/btf/vmlinux` + sandbox primitive | Boris (eBPF=soft) |
| Omega-Root (immutable chroot) | NVMe free ≥ 4096MB + bwrap/proot/unshare | Boris |
