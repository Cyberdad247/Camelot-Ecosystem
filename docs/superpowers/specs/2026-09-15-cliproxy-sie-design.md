# CLIProxyAPI Sovereign Inference Design

## Goal

Make CLIProxyAPI at `http://127.0.0.1:8080/v1` an opt-in OpenAI-compatible backend for Bifrost's Sovereign Inference Engine (SIE), without changing air-gapped model routes.

## Architecture

SIE gains a `CLIProxyBackend` that uses the OpenAI-compatible `/models` and `/chat/completions` endpoints. It accepts only loopback URLs, reads an optional `CLIPROXY_API_KEY` from the process environment, and never serializes a key. The model selector `cliproxy:<model>` explicitly routes through this backend; all other unresolved model names continue to resolve to Ollama.

`cliproxy:default` is registered as the high-reasoning and swarm route alias. The alias maps to CLIProxyAPI's locally configured `auto-fallback` model. The operator can instead select a model returned by `SIE.list_models()` using `cliproxy:<returned-model-id>`.

## Safety and Failure Handling

- CLIProxyAPI must bind to loopback; a non-loopback URL is rejected at engine creation time.
- SIE air-gapped mode blocks this non-air-gapped provider before an HTTP call.
- Missing, offline, malformed, or error responses produce a structured SIE backend error chunk and preserve normal SIE telemetry.
- Bifrost continues to call SIE, so its HITL hooks and token interception run before and during proxy generation.

## Verification

Unit tests use a local HTTP fixture to prove model discovery, OpenAI request shape, optional environment authentication, loopback enforcement, the explicit selector, and air-gapped blocking. Existing Bifrost mesh tests remain intact.
