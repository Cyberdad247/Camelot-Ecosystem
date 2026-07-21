# Portkey Assimilation Protocol

Use this protocol when a Camelot knight calls an LLM provider, routes a tool-backed model request, or needs observable fallback behavior.

## Required Environment

- `PORTKEY_API_KEY`
- `PORTKEY_VIRTUAL_KEY`
- `PORTKEY_BASE_URL`
- `PORTKEY_PROVIDER`

## Runtime Defaults

- Hosted default: `https://api.portkey.ai/v1`
- Local gateway: `http://localhost:8787/v1`
- Retry attempts: `3`
- Retry status codes: `408, 409, 429, 500, 502, 503, 504`
- Cache mode: `simple`
- Timeout: `90000` milliseconds

## Runtime Helper

Use `control_plane.portkey_assimilation.load_portkey_runtime_config()`.

## Governance Layer

Use `05_INFRASTRUCTURE/portkey/camelot_portkey_gateway.tf.example` as the starting point for Terraform-managed Portkey workspaces, providers, configs, rate limits, and usage limits.

## Rule

No knight should embed provider API keys directly. Route keys through environment variables, Portkey virtual keys, or managed secret references.

