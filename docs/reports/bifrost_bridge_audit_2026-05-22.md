# Bifrost Bridge Audit (Rust + Tailscale + Go Sidecar)

Date: 2026-05-22  
Scope: Python gate (`bin/bifrost.py`), Rust gateway (`01_KERNEL/senses/morgana_bridge`), boot probe contract (`control_plane/boot_sequence.py`), and new Go sidecar (`01_KERNEL/senses/bifrost_go_sidecar`).

## Policy Matrix

| Surface | Loopback | Tailnet | Token Sources | Trusted Owners Source | Whois Timeout |
|---|---|---|---|---|---|
| Python `bifrost.py` | Owner-only; optional loopback token requirement | Requires tailnet + token + trusted owner | direct presented token | `BIFROST_TRUSTED_TAILNET_OWNERS` (CSV) | `BIFROST_TAILSCALE_WHOIS_TIMEOUT_S` |
| Rust `morgana_bridge` | Requires token by default; optional owner-only loopback bypass via env | Requires tailnet + token + trusted owner | `Authorization`, `x-camelot-token`, `x-bifrost-token`, WS `?token=` | `BIFROST_TRUSTED_TAILNET_OWNERS` (CSV) | `BIFROST_TAILSCALE_WHOIS_TIMEOUT_MS` |
| Go Sidecar | Proxies upstream auth; can inject configured gateway token | Delegated to Rust gateway | `Authorization`, `x-camelot-token`, `x-bifrost-token` normalized to canonical headers | Delegated to Rust gateway | Delegated to Rust gateway |

## Findings

### Critical

- `Resolved`: Rust loopback protected-route bypass when token was configured.  
  Fix: Rust auth now requires token on loopback by default and returns `401` on missing/invalid token.

### High

- `Resolved`: Hardcoded trusted tailnet owner list diverged across implementations.  
  Fix: Rust + Python now use env-configurable `BIFROST_TRUSTED_TAILNET_OWNERS` with safe defaults.

- `Resolved`: Tailscale whois path had timeout asymmetry and no explicit Rust timeout.  
  Fix: Rust now applies `BIFROST_TAILSCALE_WHOIS_TIMEOUT_MS`; Python uses `BIFROST_TAILSCALE_WHOIS_TIMEOUT_S`.

### Medium

- `Resolved`: Header contract mismatch (`x-bifrost-token` accepted in Python edge paths but not Rust gateway).  
  Fix: Rust now accepts `x-bifrost-token` alongside canonical auth headers.

- `Resolved`: No dedicated Go bridge for stable language boundary to Rust gateway.  
  Fix: Added Go sidecar with `/health`, `/v1/bifrost/status`, and `/v1/agent/dispatch` proxy contracts.

## Implementation Backlog (Completed in this pass)

1. Harden Rust auth policy and response codes for protected endpoints.
2. Add env-driven trusted-owner and whois-timeout controls in Rust and Python.
3. Normalize accepted auth header names across runtime boundaries.
4. Add test coverage for Rust auth behavior and Python gate policy toggles.
5. Add Go sidecar scaffold with trace-id propagation and token normalization.

## New/Updated Environment Controls

- `BIFROST_TRUSTED_TAILNET_OWNERS`
- `BIFROST_TAILSCALE_WHOIS_TIMEOUT_S` (Python)
- `BIFROST_TAILSCALE_WHOIS_TIMEOUT_MS` (Rust)
- `BIFROST_REQUIRE_TOKEN_ON_LOOPBACK` (Python)
- `BIFROST_ALLOW_LOOPBACK_OWNER_WITHOUT_TOKEN` (Rust, default disabled)
- `BIFROST_SIDECAR_BIND_ADDR` / `BIFROST_SIDECAR_UPSTREAM_URL` / `BIFROST_SIDECAR_TIMEOUT_MS` (Go sidecar)
