# Cognitive Council Portkey Plan

## Council Result

Camelot OS should treat Portkey as the routing and observability plane for AI calls, not as a replacement for the existing knight model.

## Source Inputs

- `ChristopherKahler/paul`: plan/apply/unify loop discipline.
- `xhd2015/skills`: small installable workflow command pattern.
- `Portkey-AI/portkey-python-sdk`: Python OpenAI-compatible client surface.
- `Portkey-AI/portkey-node-sdk`: Node OpenAI-compatible client surface.
- `Portkey-AI/terraform-provider-portkey`: governance, keys, workspaces, configs, guardrails, rate limits, usage limits.
- `Portkey-AI/gateway`: local or hosted gateway with retries, fallback, load balancing, caching, guardrails, logs, and MCP gateway support.

## Recommended Configuration

- Use hosted Portkey by default with `PORTKEY_BASE_URL=https://api.portkey.ai/v1`.
- Use local Gateway only for offline routing, dev observability, or private gateway testing with `PORTKEY_BASE_URL=http://localhost:8787/v1`.
- Keep `PORTKEY_API_KEY`, `PORTKEY_VIRTUAL_KEY`, and provider keys out of git.
- Standardize all knight calls on:
  - 3 retry attempts
  - retry status codes `408, 409, 429, 500, 502, 503, 504`
  - simple cache mode
  - 90 second timeout
  - metadata containing `system=camelot-os`

## Knight Mapping

- Merlin: planning and route selection.
- Hermes: memory relay and sync telemetry.
- Gideon: acceptance criteria and verification gates.
- Heimdall: guardrails, rate limits, policy checks.
- Sir Codex: implementation and repair loops.
- Squire Colony: discovery, graph expansion, and low-risk inventory.

## Implementation Artifacts

- `control_plane/critical_thinking.py`
- `control_plane/portkey_assimilation.py`
- `docs/skills/universal_critical_thinking.md`
- `.agents/skills/camelot-universal-critical-thinking/SKILL.md`
- `05_INFRASTRUCTURE/portkey/camelot_portkey_gateway.tf.example`

## Verification Gap

The live `//PLAN` router command could not run because the local Windows shell helper failed during this session. This file records the council plan output in durable form.

