# Node_C_Omni_Router — tsnet mesh (P4-T01)

A zero-port Empire mesh node built on [Tailscale `tsnet`](https://tailscale.com/kb/1244/tsnet).
Each node joins the tailnet and serves `/health` reachable **only over the mesh**.

## Build & run

```bash
go mod tidy                                  # fetch tailscale.com (needs network)
TS_AUTHKEY=tskey-... go run . -hostname node-c-a
```

## Two-node mesh test (P4-T01 acceptance)

`TestTwoNodeMesh` brings up two ephemeral nodes on the same tailnet and verifies
node B can reach node A's `/health` over the mesh:

```bash
TS_AUTHKEY=tskey-...reusable-ephemeral... go test -v -run TestTwoNodeMesh
```

Without `TS_AUTHKEY` the test **skips** (no tailnet identity to verify against),
so `go test` stays green in environments without a tailnet. Use a **reusable,
ephemeral** auth key from the Tailscale admin console.

The driver `scripts/wsl_verify.sh` runs this automatically under WSL2 when `go`
is installed and `TS_AUTHKEY` is exported.

## Next (P4-T02 integration)

The mesh transport is the carrier for the post-quantum channel: wrap the tsnet
listener/dialer with the `camelot-pqcrypto` ML-KEM-768 handshake
(`kinetic_edge/pqcrypto`) so peer sessions are PQ-secured end to end.
