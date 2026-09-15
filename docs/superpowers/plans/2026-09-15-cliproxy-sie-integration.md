# CLIProxyAPI SIE Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Add a guarded, opt-in CLIProxyAPI backend to Bifrost's Sovereign Inference Engine.

**Architecture:** `CLIProxyBackend` implements the existing `SIEBackend` protocol against the loopback OpenAI-compatible service. `cliproxy:<model>` is the only new selector convention; existing Ollama and air-gapped routing remain unchanged.

**Tech Stack:** Python standard-library HTTP, asyncio, pytest, CLIProxyAPI OpenAI-compatible API.

**Spec:** `docs/superpowers/specs/2026-09-15-cliproxy-sie-design.md`

## Global Constraints

- The configured endpoint is `http://127.0.0.1:8080/v1` and must reject non-loopback hosts.
- Credentials come only from `CLIPROXY_API_KEY`; no key value is written to a repository file.
- The new provider is non-air-gapped and is opt-in only through `cliproxy:<model>`.
- No new third-party dependency is added.

---

### Task 1: Add an OpenAI-compatible CLIProxy backend

**Files:**
- Modify: `control_plane/dispatch/sovereign_inference.py`
- Test: `tests/control_plane/test_sovereign_inference_cliproxy.py`

**Interfaces:**
- Consumes: `SIEBackend.stream(model, prompt, system, max_tokens)`.
- Produces: `CLIProxyBackend`, registered as `cliproxy`, and `cliproxy:<model>` model resolution.

- [ ] Write a failing test for model discovery, request shape, selector resolution, and air-gapped blocking.
- [ ] Run `python -m pytest tests/control_plane/test_sovereign_inference_cliproxy.py -q`; it must fail because `CLIProxyBackend` is absent.
- [ ] Implement the standard-library backend and register it in SIE.
- [ ] Re-run the focused test and `tests/test_bifrost_token_reduction.py`.

### Task 2: Register the high-reasoning proxy alias

**Files:**
- Modify: `03_VAULT/training/configs/sovereign_models.json`
- Modify: `01_KERNEL/EXCALIBUR/config/llm_routing.json`
- Test: `tests/control_plane/test_sovereign_inference_cliproxy.py`

**Interfaces:**
- Consumes: model registry entries with `backend`, `tag`, and `air_gapped` fields.
- Produces: `cliproxy:default` as an opt-in high-reasoning and swarm model profile.

- [ ] Write a failing registry assertion.
- [ ] Add the alias and selected route profiles.
- [ ] Run the focused and OmniRoute policy tests.
