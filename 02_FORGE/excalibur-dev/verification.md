# EXCALIBUR — Verification Gates
| Gate | Command | Pass condition |
|---|---|---|
| G0 substrate | `make preflight` | exit 0 ([GO]) |
| G1 build | `cargo build --workspace` | 0 errors |
| G2 unit | `cargo test --workspace` + `pytest -q` | all pass |
| G3 trellis | bench harness | alloc/free within 512MB, no OOM |
| G4 omega | breach->restore test | chroot restored, state intact |
| G5 conductor (R) | eval harness + `/usr/bin/time -v` | routes correct; peak RSS < 1.2GB |
| G6 ouroboros (R) | N-turn memory probe | KV bytes flat across turns |
| G7 e2e | `excalibur route "<intent>"` | dispatches through conductor->ouroboros->trellis |
