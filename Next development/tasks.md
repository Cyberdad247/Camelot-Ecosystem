# EXCALIBUR — Task DAG (phased)
STATUS legend: [ ] todo · [~] in-progress · [x] done · (R) research-gated

## P0 — Substrate (gate: GO)
- [x] P0.1 pre-flight audit (core/excalibur_audit.sh)
- [x] P0.2 adjudication GO/NO-GO (core/excalibur_adjudicate.sh)
- [ ] P0.3 CI: run `make preflight` in pipeline (allow NO-GO to fail soft on x86 runners)

## P1 — Skeleton (gate: build+test green)  [depends P0]
- [x] P1.1 cargo workspace + 5 crates compile
- [x] P1.2 orchestrator pkg + CLI import
- [x] P1.3 Aegis regex PII (WIRED) + tests
- [ ] P1.4 wire CLI `preflight` to core scripts end-to-end on target
- [ ] P1.5 Makefile/justfile targets verified on Nitro

## P2 — Trellis + Omega-Root (STUB -> done)  [depends P1]
- [ ] P2.1 Trellis: fixed 512MB arena allocator + OOM-safe alloc/free + bench
- [ ] P2.2 Omega-Root: wrap bwrap/unshare; immutable chroot; restore-from-breach test
- [ ] P2.3 Aegis eBPF layer behind BTF feature flag (fallback = regex)

## P3 — Conductor + Ouroboros (RESEARCH)  [depends P2]
- [ ] (R) P3.1 Conductor: intent router; boot RAM < 1.2GB; eval harness
- [ ] (R) P3.2 Ouroboros: 1.58-bit SSM step; prove zero KV-cache growth over N turns
- [ ] (R) P3.3 integrate Conductor->Ouroboros->Trellis dataflow per topology

## P4 — Integration (gate: verification.md all-pass)  [depends P3]
- [ ] P4.1 end-to-end `excalibur route` dispatches through full stack
- [ ] P4.2 soak: sprawl + KV-growth profiled under load
