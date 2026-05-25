"""Serve the built Anya Dashboard with SPA route fallback."""

from __future__ import annotations

import argparse
import functools
import json
import os
import sys
import time
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from control_plane import frontier_nodes  # noqa: E402

DEFAULT_DIST = REPO_ROOT / "02_FORGE" / "PORTAL_CORE" / "Anya_Dashboard" / "dist"
RUNTIME_STATE = REPO_ROOT / "03_VAULT" / "runtime_state"


def _read_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return fallback


def _read_text(path: Path, *, limit: int = 4000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    return text[-limit:]


def _file_state(path: Path) -> dict:
    try:
        stat = path.stat()
    except OSError:
        return {"exists": False, "path": str(path.relative_to(REPO_ROOT))}
    return {
        "exists": True,
        "path": str(path.relative_to(REPO_ROOT)),
        "bytes": stat.st_size,
        "updated": stat.st_mtime,
    }


def _living_notebook_url() -> str:
    config = _read_text(REPO_ROOT / ".camelot-config.yaml", limit=2000)
    for line in config.splitlines():
        if line.startswith("living_notebook_url:"):
            return line.split(":", 1)[1].strip()
    return ""


def build_camelot_os_dashboard_state() -> dict:
    manifest_path = RUNTIME_STATE / "camelot_cloudbrain_v701_manifest.json"
    knight_path = RUNTIME_STATE / "knight_configuration_latest.json"
    codex_path = RUNTIME_STATE / "codex_integration_latest.json"
    queue_path = RUNTIME_STATE / "cloudbrain_sync_queue.jsonl"
    ledger_path = REPO_ROOT / "PROVENANCE_LEDGER.md"
    verification_path = REPO_ROOT / "03_VAULT" / "Missions" / "verification_ledger.jsonl"

    manifest = _read_json(manifest_path, {})
    knight_config = _read_json(knight_path, {})
    codex = _read_json(codex_path, {})
    queue_lines = [line for line in _read_text(queue_path, limit=20000).splitlines() if line.strip()]

    architecture_layers = manifest.get("architecture_layers") or []
    schematic_edges = manifest.get("schematic_edges") or []
    surfaces = codex.get("surfaces") or {}
    cartridges = knight_config.get("cartridges") or {}
    roster = knight_config.get("excalibur_roster") or {}

    return {
        "status": "OK",
        "generated_utc": manifest.get("generated_utc") or codex.get("generated_utc"),
        "repo_root": str(REPO_ROOT),
        "version": manifest.get("version") or "local",
        "summary": {
            "architecture_layers": len(architecture_layers),
            "schematic_edges": len(schematic_edges),
            "active_cartridges": cartridges.get("active_count", 0),
            "knights": roster.get("count", 0),
            "codex_surfaces_online": sum(1 for value in surfaces.values() if value),
            "cloudbrain_queue_pending": len(queue_lines),
        },
        "orchestration": {
            "layers": architecture_layers,
            "edges": schematic_edges,
            "soul_router": manifest.get("soul_router") or {},
            "switchboard_terminals": manifest.get("switchboard_terminals") or [],
            "codex_surfaces": surfaces,
            "cartridges": cartridges,
            "roster": roster,
        },
        "memory_tiers": [
            {
                "id": "flash",
                "label": "Flash",
                "owner": "Anya / Bifrost",
                "status": "LIVE_UI",
                "purpose": "Current dashboard session, websocket events, and immediate command context.",
                "source": "browser runtime + Bifrost live event stream",
                "action": "Use for what is happening right now.",
            },
            {
                "id": "short",
                "label": "Short",
                "owner": "NotebookLM Cloud Brain",
                "status": "QUEUE_CLEAR" if not queue_lines else "QUEUE_PENDING",
                "purpose": "Canonical session synthesis, recent project state, and NotebookLM-backed recall.",
                "source": "control_plane/cloudbrain_sync.py",
                "notebook_url": _living_notebook_url(),
                "queue_pending": len(queue_lines),
                "action": "Use for active project memory and fast synthesis.",
            },
            {
                "id": "long",
                "label": "Long",
                "owner": "Sir Mnemo / Modal / Appwrite",
                "status": "CONFIGURED",
                "purpose": "Permanent archive, ledger-backed memory, Appwrite/Modal storage, and local LT fallback.",
                "source": "03_VAULT/training/configs/integration_brain.py",
                "local_db": _file_state(RUNTIME_STATE / "lt_memory.db"),
                "action": "Use for durable history, audit, and recall.",
            },
        ],
        "ledgers": {
            "root": _file_state(ledger_path),
            "verification": _file_state(verification_path),
            "cloudbrain_manifest": _file_state(manifest_path),
            "codex_integration": _file_state(codex_path),
            "knight_configuration": _file_state(knight_path),
            "latest_root_excerpt": _read_text(ledger_path, limit=1600),
        },
        "outputs": manifest.get("outputs") or {},
        "frontier": frontier_nodes.public_state(),
    }


# ── Cartridge dispatch via CLIProxy ──────────────────────────────────────────

_CLIPROXY_URL = "http://127.0.0.1:8080/v1/chat/completions"
_CLIPROXY_KEY = "proxy-admin-key"

_CARTRIDGE_SYSTEM_PROMPTS: dict[str, str] = {
    "COGNITIVE": (
        "You are SIR_ALEX, a master of reasoning chains and cognitive architecture. "
        "Apply Tree-of-Thought, Graph-of-Thought, or Chain-of-Thought as appropriate. "
        "Be precise, structured, and show your reasoning steps."
    ),
    "ENGINEER": (
        "You are SIR_FORGE, an expert software engineer. "
        "Write clean, production-quality code with error handling. "
        "Prefer Rust, Go, Python, or TypeScript. Always include brief inline explanations."
    ),
    "RESEARCH": (
        "You are LADY_APIS, a research intelligence sovereign. "
        "Synthesize information from multiple angles using the CHIMERA pipeline: "
        "semantic audit → topology shift → anchor compression. "
        "Provide sourced, structured findings with confidence levels."
    ),
    "CREATIVE": (
        "You are SIR_SONUS, a creative director and voice AI specialist. "
        "Generate compelling, original content with vivid language and strong narrative structure. "
        "Adapt tone to context: professional, casual, epic, or NYC street-smart."
    ),
    "MARKETING": (
        "You are SIR_VALERIAN, a growth and marketing strategist. "
        "Focus on ROI, conversion, and measurable outcomes. "
        "Produce actionable campaigns, copy, and strategies with clear KPIs."
    ),
    "LEGAL": (
        "You are SIR_SENTINEL, a legal intelligence agent with Agent-Armor v2.0. "
        "Analyze contracts, compliance, and risk with precision. "
        "Flag issues clearly, cite relevant frameworks (GDPR, SOC2, HIPAA, CCPA), "
        "and rate severity. Never give definitive legal advice — always recommend counsel."
    ),
    "BRAINSTORM": (
        "You are MERLIN_OMEGA, a divergent ideation master. "
        "Use SCAMPER, TRIZ, and cross-domain synthesis to generate creative ideas. "
        "Produce multiple distinct concepts, then converge on the strongest."
    ),
    "CRITICAL_THINKING": (
        "You are SIR_ALEX in critical analysis mode. "
        "Apply Socratic questioning, red-team adversarial thinking, and bias detection. "
        "Surface hidden assumptions, identify failure modes, and demand evidence. "
        "Be rigorous and intellectually honest."
    ),
}

_CARTRIDGE_MODELS: dict[str, str] = {
    "COGNITIVE":         "gemini-2.5-pro",
    "ENGINEER":          "gemini-2.5-pro",
    "RESEARCH":          "gemini-2.5-pro",
    "CREATIVE":          "gemini-2.5-pro",
    "MARKETING":         "gemini-2.5-pro",
    "LEGAL":             "gemini-2.5-pro",
    "BRAINSTORM":        "gemini-2.5-pro",
    "CRITICAL_THINKING": "gemini-2.5-pro",
}

_CARTRIDGE_KNIGHTS: dict[str, str] = {
    "COGNITIVE":         "sir_alex",
    "ENGINEER":          "sir_forge",
    "RESEARCH":          "lady_apis",
    "CREATIVE":          "sir_sonus",
    "MARKETING":         "sir_valerian",
    "LEGAL":             "sir_sentinel",
    "BRAINSTORM":        "merlin_omega",
    "CRITICAL_THINKING": "sir_alex",
}


def _build_user_message(intent: str, params: dict) -> str:
    parts = [intent]
    if params:
        filtered = {k: v for k, v in params.items() if v not in (None, "", False, [])}
        if filtered:
            parts.append("\n\nParameters: " + json.dumps(filtered, ensure_ascii=False))
    return "\n".join(parts)


def dispatch_cartridge(cartridge: str, intent: str, params: dict) -> dict:
    """Call CLIProxy with the cartridge's system prompt and return a response dict."""
    cartridge_id = cartridge.upper()
    system_prompt = _CARTRIDGE_SYSTEM_PROMPTS.get(
        cartridge_id, "You are a Camelot-OS knight. Answer the directive concisely."
    )
    model = _CARTRIDGE_MODELS.get(cartridge_id, "gemini-2.5-pro")
    knight = _CARTRIDGE_KNIGHTS.get(cartridge_id, "sir_alex")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": _build_user_message(intent, params)},
        ],
        "max_tokens": 1024,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    t0 = time.monotonic()
    try:
        req = urllib.request.Request(
            _CLIPROXY_URL,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {_CLIPROXY_KEY}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        latency_ms = round((time.monotonic() - t0) * 1000)
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        if not content:
            content = str(data)

        return {
            "response": content,
            "knight": knight,
            "model": model,
            "cartridge": cartridge_id,
            "source": "CLIPROXY",
            "latency_ms": latency_ms,
        }

    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        return {
            "error": f"CLIProxy {exc.code}: {detail}",
            "cartridge": cartridge_id,
            "source": "CLIPROXY",
        }
    except Exception as exc:
        return {
            "error": str(exc),
            "cartridge": cartridge_id,
            "source": "CLIPROXY",
        }


class SpaHandler(SimpleHTTPRequestHandler):
    """Static file handler that falls back to index.html for client routes."""

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _operator_authorized(self) -> bool:
        expected = os.getenv("CAMELOT_DASHBOARD_OPERATOR_TOKEN", "").strip()
        if not expected:
            return False
        supplied = self.headers.get("X-Camelot-Operator-Token", "").strip()
        return bool(supplied) and supplied == expected

    def _require_operator(self) -> bool:
        if self._operator_authorized():
            return True
        self._send_json(
            {"status": "ERROR", "error": "operator token required"},
            status=403,
        )
        return False

    def do_GET(self):  # noqa: N802 - stdlib override
        parsed = urlparse(self.path)
        if parsed.path == "/api/camelot-os/status":
            self._send_json(build_camelot_os_dashboard_state())
            return
        if parsed.path == "/api/camelot-os/frontier-nodes":
            self._send_json(frontier_nodes.public_state())
            return
        return super().do_GET()

    def do_OPTIONS(self):  # noqa: N802 - CORS preflight
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}
        return payload if isinstance(payload, dict) else {}

    def do_POST(self):  # noqa: N802 - stdlib override
        parsed = urlparse(self.path)
        payload = self._read_json_body()
        try:
            if parsed.path == "/api/cartridge/dispatch":
                cartridge = payload.get("cartridge", "COGNITIVE")
                intent = payload.get("intent", "")
                params = payload.get("params") or {}
                if not intent:
                    self._send_json({"error": "intent is required"}, status=400)
                    return
                result = dispatch_cartridge(cartridge, intent, params)
                self._send_json(result)
                return

            if parsed.path == "/api/camelot-os/frontier-nodes/register":
                if not self._require_operator():
                    return
                self._send_json(frontier_nodes.register_node(payload))
                return
            if parsed.path == "/api/camelot-os/support/activate":
                if not self._require_operator():
                    return
                self._send_json(frontier_nodes.activate_support_session(payload))
                return
            if parsed.path == "/api/camelot-os/support/revoke":
                if not self._require_operator():
                    return
                self._send_json(frontier_nodes.revoke_support_session(payload))
                return
            if parsed.path == "/api/camelot-os/support/validate":
                session_id = str(payload.get("session_id") or "")
                token = str(payload.get("token") or "")
                self._send_json(frontier_nodes.validate_support_session(session_id, token))
                return
        except ValueError as exc:
            self._send_json({"status": "ERROR", "error": str(exc)}, status=400)
            return
        self._send_json({"status": "ERROR", "error": "unknown endpoint"}, status=404)

    def send_head(self):  # noqa: N802 - stdlib override
        requested = Path(self.translate_path(self.path))
        if requested.exists() or "." in Path(self.path.split("?", 1)[0]).name:
            return super().send_head()
        self.path = "/index.html"
        return super().send_head()


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve Anya Dashboard dist with SPA fallback.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5173)
    parser.add_argument("--dist", type=Path, default=DEFAULT_DIST)
    args = parser.parse_args()

    dist = args.dist.resolve()
    if not (dist / "index.html").exists():
        raise SystemExit(f"Missing built dashboard at {dist}. Run npm run build in Anya_Dashboard first.")

    handler = functools.partial(SpaHandler, directory=str(dist))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Anya Dashboard serving {dist} at http://{args.host}:{args.port}/", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
