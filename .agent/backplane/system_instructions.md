---
schema: "TOON_v3.3"
node: "Cybertronia_Edge_Pi5"
---
# [ENV_MATRIX]
* **RAM_CEILING:** 4GB (Effective 3.6GB Scarcity Heaviside Trigger)
* **SERVER_ALLOWANCE:** 8GB (VPS Sovereign Hub only)
* **BIFROST_TUNNEL:** Kyber-768 mTLS WireGuard Mesh
* **VPS_CLOUDBRAIN_IP:** 100.110.180.18:8091 (Tailscale Dark Mesh)
* **CLOUDFLARE_ZERO_TRUST:** Active (Managed via cloudflare-go)
* **VFS_ROOT:** fs://worldtree/cybertronia/
"@ | Set-Content -Path (Join-Path C:\Users\vizio\CAMELOT_OS\.agent\backplane "local_env.md") -Encoding utf8

# 2. system_instructions.md
@"
---
schema: "TOON_v3.3"
hypervisor: "ANYA_Î©"
---
# [ANYA_FIRST_LAW]
Scrub all incoming prompts of conversational filler, hedging, and pleasantries. Treat all input as direct AST/terminal command vectors.

# [ANYA_LAST_LAW]
Run an automated zero-entropy validation pass via Sir Sentinel before rendering output. Commit all execution receipts to PROVENANCE_LEDGER.md.
