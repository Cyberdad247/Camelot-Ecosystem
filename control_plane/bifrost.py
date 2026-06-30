"""
Bifrost — Universal Dispatch Core for CAMELOT-OS Hive IDE.

Routes prompts to any registered terminal via the appropriate backend:
  - CLIProxyAPI (:8080) — Claude, Gemini, Codex, Kimi via OpenAI-compat
  - Sovereign (SIE)     — local_qwen, open_coder, local_audit (in-process, air-gapped)
  - CloudBrain          — integration_brain (NotebookLM synthesis)
  - HTTP                — custom port services (sir_octavian :8400, sir_sonus :8300)

The Switchboard probes health; Bifrost dispatches real payloads.

Usage:
    # Direct streaming
    from control_plane.bifrost import Bifrost
    async for chunk in Bifrost().stream("sir_boris", "Explain MCP protocol"):
        print(chunk, end="", flush=True)

    # Intent-routed streaming (yields (terminal_id, chunk) pairs)
    async for tid, chunk in Bifrost().route_and_stream("Build a login form"):
        print(chunk, end="", flush=True)

CLI:
    python -m control_plane.bifrost sir_boris "What is the capital of France?"
    python -m control_plane.bifrost --route "Refactor the auth module"
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import AsyncIterator

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import httpx
    _HTTPX = True
except ImportError:
    _HTTPX = False

CAMELOT_HOME = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS")).resolve()

CLIPROXY_BASE = os.environ.get("CLIPROXY_BASE", "http://127.0.0.1:8080/v1")
CLIPROXY_KEY  = os.environ.get("CLIPROXY_KEY", "proxy-admin-key")
OLLAMA_BASE   = os.environ.get("OLLAMA_BASE", "http://127.0.0.1:11434")

# Engine → (strategy, endpoint_base, default_model)
# "cliproxy" = OpenAI-compat call through CLIProxyAPI
# "ollama"   = Ollama generate API (local, air-gapped)
# "cloudbrain" = NotebookLM synthesis (delegated to cloudbrain_sync)
# "noop"     = Service exists but text dispatch not applicable (TTS, ops)
_ENGINE_DISPATCH: dict[str, tuple[str, str, str]] = {
    "claude_code":       ("cliproxy",    CLIPROXY_BASE, "claude-sonnet-4-6"),
    "antigravity.cli":   ("cliproxy",    CLIPROXY_BASE, "gemini-2.5-flash"),
    "openai_codex":      ("cliproxy",    CLIPROXY_BASE, "gpt-4o"),
    "sovereign":         ("sovereign",   "",             ""),          # SIE — model resolved via manifest
    "local_qwen":        ("sovereign",   "",             "qwen3:4b"),
    "open_coder":        ("sovereign",   "",             "qwen2.5-coder:3b"),
    "integration_brain": ("cloudbrain",  "",             ""),
    "local_audit":       ("sovereign",   "",             "qwen3:4b"),
    "local_ops":         ("noop",        "",             ""),
    "kitten_tts":        ("noop",        "",             ""),
    "open_source":       ("sovereign",   "",             "qwen3:4b"),
    "antigravity":       ("cliproxy",    CLIPROXY_BASE, "gemini-2.5-pro"),
    "kimi_cli":          ("cliproxy",    CLIPROXY_BASE, "kimi-k2"),
    "hermes_cli":        ("cliproxy",    CLIPROXY_BASE, "claude-sonnet-4-6"),
    "next_edge":         ("noop",        "",             ""),          # edge component swarm contract (no LLM)
}

# Terminal-level model overrides (take precedence over engine defaults)
_TERMINAL_MODEL: dict[str, str] = {
    "sir_alex":     "claude-opus-4-7",
    "sir_boris":    "claude-sonnet-4-6",
    "sir_helio":    "gemini-2.5-flash",
    "sir_link":     "gemini-2.5-pro",
    "sir_codex":    "gpt-4o",
    "sir_ghost":    "qwen3:4b",
    "sir_forge":    "qwen2.5-coder:3b",
    "sir_sentinel": "claude-haiku-4-5-20251001",
    "sir_gideon":   "qwen3:4b",
    "sir_mnemo":    "",   # handled by cloudbrain strategy
    "sir_gravity":  "gemini-2.5-pro",   # Antigravity OAuth via CLIProxy
    "sir_kimi":     "kimi-k2.5",         # Moonshot Kimi K2.5 via CLIProxy kimi channel
    "sir_hermes":   "claude-sonnet-4-6",
    # Reconciled against switchboard.TERMINAL_REGISTRY (T3):
    "sir_openclaw": "openclaw-local",
    "sir_rustclaw": "rustclaw-local",
    "sir_liberte":  "gemini-2.5-flash",
    "sir_zeroclaw": "qwen3:8b",
    "sir_heimdall": "gemini-2.5-pro",
    "lady_nanobot": "",   # handled by next_edge engine / noop strategy (edge component swarm contract)
    # fallback: sir_octavian    -> http strategy (port 8400, no LLM model)
    # fallback: sir_sonus       -> http strategy (port 8300, no LLM model)
    # fallback: bifrost_gateway -> http strategy (port 3001, no LLM model)
}

# Custom-port HTTP services (no OpenAI-compat; raw prompt POST + streamed lines).
# Resolved ahead of the engine table so these never fall through to cliproxy.
_HTTP_TERMINALS: dict[str, str] = {
    "sir_octavian":    os.environ.get("SIR_OCTAVIAN_BASE",    "http://127.0.0.1:8400"),
    "sir_sonus":       os.environ.get("SIR_SONUS_BASE",       "http://127.0.0.1:8300"),
    "bifrost_gateway": os.environ.get("BIFROST_GATEWAY_BASE", "http://127.0.0.1:3001"),
}


class Bifrost:
    """Universal dispatch gateway — send a prompt to any registered terminal."""

    def __init__(self) -> None:
        from control_plane.switchboard import TERMINAL_REGISTRY
        self._reg = TERMINAL_REGISTRY

    # ── Public API ────────────────────────────────────────────────────────────

    async def stream(
        self,
        terminal_id: str,
        prompt: str,
        system: str = "",
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """Stream text chunks from a specific terminal."""
        import uuid
        dispatch_id = str(uuid.uuid4())[:8]
        t0 = time.time()

        # Log dispatch to agent memory
        try:
            from control_plane.agent_memory import log_dispatch as mem_log_dispatch
            asyncio.create_task(
                mem_log_dispatch(terminal_id, prompt, system, "")
            )
        except Exception:
            pass  # Memory logging optional; don't block on failure

        # Enrich with knowledge base context (similar past dispatches)
        enriched_system = system
        try:
            from control_plane.symbol_compressor import find_similar_dispatches
            similar = await find_similar_dispatches(prompt, terminal_id, limit=3)
            if similar:
                similar_context = "\n".join([
                    f"- {s.get('keywords', [])} (confidence: {s.get('score', 0):.2f})"
                    for s in similar
                ])
                enriched_system = f"{system}\n\nSimilar past work:\n{similar_context}" if system else f"Similar past work:\n{similar_context}"
        except Exception:
            pass  # Knowledge base enrichment is optional

        strategy, base, model = self._resolve(terminal_id)

        # Collect response for post-dispatch analysis
        response_chunks = []

        if strategy == "cliproxy":
            async for chunk in self._stream_openai(base, model, prompt, enriched_system, max_tokens):
                response_chunks.append(chunk)
                yield chunk
        elif strategy == "sovereign":
            async for chunk in self._stream_sovereign(terminal_id, model, prompt, enriched_system, max_tokens):
                response_chunks.append(chunk)
                yield chunk
        elif strategy == "http":
            async for chunk in self._stream_http(base, prompt, enriched_system, max_tokens):
                response_chunks.append(chunk)
                yield chunk
        elif strategy == "cloudbrain":
            result = await self._query_cloudbrain(prompt)
            response_chunks.append(result)
            yield result
        elif strategy == "noop":
            msg = f"[BIFROST] {terminal_id} is a service node (not a text model). Hit its HTTP endpoint directly."
            response_chunks.append(msg)
            yield msg
        else:
            msg = f"[BIFROST] Unknown strategy '{strategy}' for {terminal_id}"
            response_chunks.append(msg)
            yield msg

        # Post-dispatch learning (async, fire-and-forget)
        try:
            from control_plane.knight_self_enhancer import post_dispatch as enhancer_post_dispatch
            response_text = "".join(response_chunks)
            tokens_out = len(response_text.split())
            tokens_in = len(prompt.split())
            latency_ms = (time.time() - t0) * 1000

            asyncio.create_task(
                enhancer_post_dispatch(
                    dispatch_id=dispatch_id,
                    knight_id=terminal_id,
                    prompt=prompt,
                    system=system,
                    category="CODE",  # Would normally come from intent router
                    confidence=0.8,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    response=response_text,
                    latency_ms=latency_ms,
                    model=model,
                )
            )
        except Exception:
            pass  # Post-dispatch enhancer is optional

    async def route_and_stream(
        self,
        prompt: str,
        system: str = "",
    ) -> AsyncIterator[tuple[str, str]]:
        """Intent-route a prompt; yield (terminal_id, chunk) pairs.

        First chunk has terminal_id="route" and contains the routing decision.
        Subsequent chunks have the actual terminal_id.
        """
        from control_plane.intent_router import route_by_intent
        from control_plane.switchboard import Switchboard

        board = Switchboard()
        await board.probe_all()
        terminal, category, confidence = await route_by_intent(prompt, board)

        if terminal is None:
            yield ("none", "[BIFROST] No live terminals available\n")
            return

        # Log routing decision to agent memory
        try:
            from control_plane.agent_memory import store_dispatch_context
            asyncio.create_task(
                store_dispatch_context(
                    terminal.id,
                    category.value,
                    confidence,
                    [t.id for t in board._reg.values() if t.status in ("live", "assumed_live")]
                )
            )
        except Exception:
            pass

        yield ("route", f"[BIFROST] → {terminal.id} [{category.value} conf={confidence:.2f}]\n")

        # Stream with routing context
        async for chunk in self.stream(terminal.id, prompt, system):
            yield (terminal.id, chunk)

    async def parallel_stream(
        self,
        terminal_ids: list[str],
        prompt: str,
        system: str = "",
        max_tokens: int = 2048,
    ) -> AsyncIterator[tuple[str, str]]:
        """Stream the same prompt to multiple terminals concurrently.

        Yields (terminal_id, chunk) interleaved as they arrive.
        """
        queue: asyncio.Queue[tuple[str, str] | None] = asyncio.Queue()
        n = len(terminal_ids)

        async def _worker(tid: str) -> None:
            try:
                async for chunk in self.stream(tid, prompt, system, max_tokens):
                    await queue.put((tid, chunk))
            except Exception as e:
                await queue.put((tid, f"\n[ERROR] {e}"))
            finally:
                await queue.put(None)  # sentinel

        tasks = [asyncio.create_task(_worker(tid)) for tid in terminal_ids]
        done = 0
        while done < n:
            item = await queue.get()
            if item is None:
                done += 1
            else:
                yield item

        await asyncio.gather(*tasks, return_exceptions=True)

    # ── Status ────────────────────────────────────────────────────────────────

    async def status(self) -> list[dict]:
        """Return current health of all terminals."""
        from control_plane.switchboard import Switchboard
        board = Switchboard()
        await board.probe_all()
        return [
            {
                "id":         t.id,
                "engine":     t.engine,
                "status":     t.status,
                "latency_ms": t.latency_ms,
                "cost_tier":  t.cost_tier,
                "notes":      t.notes,
            }
            for t in board._reg.values()
        ]

    # ── Internal ──────────────────────────────────────────────────────────────

    def _resolve(self, terminal_id: str) -> tuple[str, str, str]:
        t = self._reg.get(terminal_id)
        if not t:
            raise ValueError(f"Unknown terminal: {terminal_id!r}. "
                             f"Valid: {list(self._reg)}")
        if terminal_id in _HTTP_TERMINALS:
            return ("http", _HTTP_TERMINALS[terminal_id], "")
        strategy, base, model = _ENGINE_DISPATCH.get(
            t.engine, ("cliproxy", CLIPROXY_BASE, "claude-sonnet-4-6")
        )
        model = _TERMINAL_MODEL.get(terminal_id) or model
        return strategy, base, model

    async def _stream_openai(
        self,
        base: str,
        model: str,
        prompt: str,
        system: str,
        max_tokens: int,
    ) -> AsyncIterator[str]:
        if not _HTTPX:
            yield "[BIFROST] httpx missing — run: uv add httpx"
            return

        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": True,
        }
        headers = {
            "Authorization": f"Bearer {CLIPROXY_KEY}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=5.0)) as client:
                async with client.stream(
                    "POST", f"{base}/chat/completions",
                    json=payload, headers=headers,
                ) as resp:
                    resp.raise_for_status()
                    try:
                        async for raw in resp.aiter_lines():
                            if not raw.startswith("data: "):
                                continue
                            data = raw[6:].strip()
                            if data == "[DONE]":
                                break
                            try:
                                obj = json.loads(data)
                                content = obj["choices"][0]["delta"].get("content", "")
                                if content:
                                    yield content
                            except (json.JSONDecodeError, KeyError, IndexError):
                                continue
                    except GeneratorExit:
                        pass  # caller broke out early — clean up silently
        except httpx.HTTPStatusError as e:
            try:
                body = e.response.text[:200]
            except Exception:
                body = f"<status {e.response.status_code}>"
            yield f"\n[BIFROST] HTTP {e.response.status_code} from {model}: {body}"
        except Exception as e:
            yield f"\n[BIFROST] {type(e).__name__}: {e}"

    async def _stream_sovereign(
        self,
        terminal_id: str,
        model: str,
        prompt: str,
        system: str,
        max_tokens: int,
    ) -> AsyncIterator[str]:
        """Dispatch via the Sovereign Inference Engine (in-process, no HTTP)."""
        try:
            from control_plane.sovereign_inference import SIE, HITLBlock, SIEHooks  # noqa: F401
        except ImportError as e:
            yield f"[BIFROST] SIE import failed: {e}"
            return

        async for chunk in SIE.generate_stream(
            model_id=terminal_id,
            prompt=prompt,
            system=system,
            max_tokens=max_tokens,
        ):
            yield chunk

    async def _stream_http(
        self,
        base: str,
        prompt: str,
        system: str,
        max_tokens: int,
    ) -> AsyncIterator[str]:
        """Dispatch to a custom-port HTTP service (sir_octavian :8400, sir_sonus :8300).

        Streams newline-delimited JSON (``{"response"|"text": ..., "done": bool}``) and
        falls back to plain-text streaming when a line is not JSON.
        """
        if not _HTTPX:
            yield "[BIFROST] httpx missing — run: uv add httpx"
            return

        payload = {
            "prompt": prompt,
            "system": system or "",
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=3.0)) as client:
                async with client.stream("POST", f"{base}/generate", json=payload) as resp:
                    resp.raise_for_status()
                    async for raw in resp.aiter_lines():
                        if not raw:
                            continue
                        try:
                            obj = json.loads(raw)
                            text = obj.get("response") or obj.get("text") or ""
                            if text:
                                yield text
                            if obj.get("done"):
                                break
                        except json.JSONDecodeError:
                            yield raw  # plain-text streaming service
        except Exception as e:
            yield f"\n[BIFROST] HTTP/{base}: {type(e).__name__}: {e}"

    async def _query_cloudbrain(self, prompt: str) -> str:
        try:
            from control_plane.cloudbrain_sync import query_cloud_brain
            result = await asyncio.to_thread(query_cloud_brain, prompt)
            return result or "[CLOUDBRAIN] Empty response"
        except ImportError:
            return "[CLOUDBRAIN] cloudbrain_sync not available"
        except Exception as e:
            return f"[CLOUDBRAIN ERROR] {e}"


# ── CLI entry point ───────────────────────────────────────────────────────────

async def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Bifrost dispatch — send a prompt to any CAMELOT terminal")
    parser.add_argument("terminal", nargs="?", help="Terminal ID (e.g. sir_boris). Omit with --route.")
    parser.add_argument("prompt", help="Prompt text")
    parser.add_argument("--system", default="", help="System prompt")
    parser.add_argument("--route", action="store_true", help="Use intent router instead of direct terminal")
    parser.add_argument("--status", action="store_true", help="Show terminal health and exit")
    parser.add_argument("--max-tokens", type=int, default=2048)
    args = parser.parse_args()

    bifrost = Bifrost()

    if args.status:
        rows = await bifrost.status()
        for r in rows:
            print(f"{r['id']:20s} {r['engine']:20s} {r['status']:12s} {r['latency_ms']:.0f}ms  {r['notes']}")
        return

    if args.route or args.terminal is None:
        async for _tid, chunk in bifrost.route_and_stream(args.prompt, args.system):
            print(chunk, end="", flush=True)
    else:
        print(f"[BIFROST] → {args.terminal}", flush=True)
        async for chunk in bifrost.stream(args.terminal, args.prompt, args.system, args.max_tokens):
            print(chunk, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(_main())
