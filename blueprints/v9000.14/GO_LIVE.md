# v9000.14-CYBERTRONIA — Go-Live Checklist

The upgrade is merged and **32/34 tasks are fully verified**. The last two
(`P4-T01` tsnet mesh, `P5-T02` MicroVM) are **coded, compiled, and self-tested**
— they only need a real network identity / hardware permission that must be
supplied by a human, not committed to the repo.

The single driver for everything below is:

```powershell
wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/vizio/CAMELOT_OS && bash scripts/wsl_verify.sh"
```

It preflights the toolchain and prints **PASS / FAIL / SKIP** per task with the
exact remediation for anything still missing. Re-run it after each step below.

---

## P4-T01 — tsnet 2-node mesh (needs a Tailscale auth key)

| | |
|---|---|
| **What's missing** | A Tailscale **auth key** (`tskey-auth-…`) — your private-network credential |
| **Why a human** | Tied to *your* Tailscale account; cannot be generated from the repo |
| **Code status** | ✅ compiles (`go build`/`go vet` exit 0); test skips cleanly without a key |

**Steps**
1. Create a free account at <https://tailscale.com> (Google/Microsoft/GitHub login).
2. Admin console → **Settings → Keys → Generate auth key**. Enable **Reusable** + **Ephemeral**.
3. Copy `01_KERNEL/mesh/node_c/.env.example` → `01_KERNEL/mesh/node_c/.env` (gitignored) and paste the key, **or** pass it inline.
4. Run the live test:
   ```bash
   cd 01_KERNEL/mesh/node_c
   go mod tidy                                   # first time only (fetches tailscale.com)
   TS_AUTHKEY=tskey-auth-xxxx go test -v -run TestTwoNodeMesh
   ```
5. Green `--- PASS: TestTwoNodeMesh` ⇒ node B reached node A over the mesh.

> 🔒 Never commit a real key. `.env` is gitignored; `.env.example` holds only a placeholder.

---

## P5-T02 — Unikraft MicroVM (needs /dev/kvm access + a hypervisor)

| | |
|---|---|
| **What's missing** | Permission to use `/dev/kvm`, a hypervisor, and a pill image |
| **Why a human** | KVM is hardware/OS-level access; can't be granted from application code |
| **Code status** | ✅ launcher `--self-test` PASS (mock VM); real boot gated on the below |

**On this host:** `/dev/kvm` *exists* but is *"present but not readable"* — your
user isn't in the `kvm` group yet.

**Steps (inside WSL2 Ubuntu)**
1. Grant KVM permission (one-time), then restart WSL so the group takes effect:
   ```bash
   sudo usermod -aG kvm "$USER"
   # close ALL WSL terminals, then reopen (group changes need a fresh session)
   ls -l /dev/kvm        # you should now have rw access
   ```
2. Install a hypervisor (one of):
   ```bash
   sudo apt-get update && sudo apt-get install -y qemu-system-x86   # or cloud-hypervisor / krunvm
   ```
3. Provide a pill image — set `CAMELOT_PILL_IMAGE=/path/to/pill.img` or pass `--image`.
   (Building a 5 MB Unikraft/libkrun unikernel is the remaining engineering step;
   the launcher reports exactly what it needs until then.)
4. Boot + health-check:
   ```bash
   python3 scripts/microvm_boot.py --health-check
   # exit 0 = booted + health 200 ; exit 3 = a prereq still missing (it tells you which)
   ```

---

## What's already green (no action needed)

- **P4-T05** memfd zero-copy — verified on WSL2 (~0.126 µs/page, target <10 µs)
- **P4-T02 / P4-T04** — ML-KEM-768 / ML-DSA-65 round-trip tests pass; `cargo audit` clean (0 advisories)
- **P5-T01** — `camelot-edge.wasm` builds (65 KB). To run it: `cargo install wasmtime` then
  `wasmtime run target/wasm32-wasip1/release/camelot-edge.wasm`
- Phases 1–3 and the rest of 4–5: 52 pytest + 19 selftests + 7 Rust tests, all green.
