"""
Switchboard — LLM Flight Control Terminal
CAMELOT Apex OS v400 | Sovereign Terminal Registry

Every LLM engine is a Terminal (gate/runway). Sir Link owns the handshake.
The router NEVER dispatches blind — it queries the Switchboard first.

Lazy probing: health cache TTL=60s. No probe unless cache stale.
Manifest written to logs/switchboard_manifest.json for HUD/harness consumption.

Terminals: sir_boris(claude) | sir_helio(gemini) | sir_ghost(local) |
           sir_codex(openai) | sir_forge(open_coder) | sir_mnemo(integration_brain)
           sir_link(gemini/bridge) | sir_alex(claude/cognitive)
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

CAMELOT_HOME = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS")).resolve()
MANIFEST_PATH = CAMELOT_HOME / "logs" / "switchboard_manifest.json"
MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

HEALTH_TTL_S   = 60.0   # re-probe after 60s
PROBE_TIMEOUT  = 2.0    # max seconds per probe


# ── Terminal definitions ──────────────────────────────────────────────────────

@dataclass
class Terminal:
    id:          str
    engine:      str
    weight:      float
    cost_tier:   str       # "free" | "low" | "medium" | "high"
    capability:  list[str] = field(default_factory=list)
    probe_url:   str       = ""     # empty = local process check
    probe_port:  int       = 0      # 0 = no TCP probe
    status:      str       = "unknown"  # live|dark|degraded|unknown
    latency_ms:  float     = 0.0
    last_probe:  float     = 0.0
    error_count: int       = 0
    notes:       str       = ""


# Master terminal registry — the full switchboard
TERMINAL_REGISTRY: dict[str, Terminal] = {
    "sir_boris": Terminal(
        id="sir_boris", engine="claude_code", weight=0.85,
        cost_tier="medium", capability=["orchestration","architecture","critique","forge"],
        probe_port=8080, notes="Claude Code — CLIProxy gateway",
    ),
    "sir_helio": Terminal(
        id="sir_helio", engine="pydantic_ai", weight=0.95,
        cost_tier="low", capability=["context","research","burst","1m_token","pydantic_ai"],
        probe_port=0, notes="Sir Helio v400 — Pydantic AI Context Lord",
    ),
    "sir_alex": Terminal(
        id="sir_alex", engine="claude_code", weight=0.88,
        cost_tier="medium", capability=["cognitive","reasoning","critical","decision"],
        probe_port=8080, notes="Claude Code — cognitive cartridge orchestration",
    ),
    "sir_link": Terminal(
        id="sir_link", engine="antigravity.cli", weight=0.78,
        cost_tier="low", capability=["bridge","handoff","terminal","ui","switchboard"],
        probe_port=0, notes="Sir Link — handshake coordinator, switchboard ATC",
    ),
    "sir_ghost": Terminal(
        id="sir_ghost", engine="local_qwen", weight=1.00,
        cost_tier="free", capability=["privacy","air_gapped","zero_trust"],
        probe_port=11434, notes="Local Qwen 3.5 — air-gapped, zero trust",
    ),
    "sir_forge": Terminal(
        id="sir_forge", engine="open_coder", weight=0.70,
        cost_tier="free", capability=["code_gen","scaffold","technical","kinetic"],
        probe_port=11434, notes="Open Coder local — kinetic code gen",
    ),
    "sir_codex": Terminal(
        id="sir_codex", engine="openai_codex", weight=0.75,
        cost_tier="free", capability=["velocity","rapid_proto","openai"],
        probe_port=8080, notes="OpenAI Codex via CLIProxyAPI :8080 — free provider pool",
    ),
    "sir_liberte": Terminal(
        id="sir_liberte", engine="open_source", weight=0.80,
        cost_tier="free", capability=["sovereignty","oss","anti_lock"],
        probe_port=0, notes="Open Source — anti-vendor lock-in",
    ),
    "sir_mnemo": Terminal(
        id="sir_mnemo", engine="integration_brain", weight=0.92,
        cost_tier="low", capability=["memory","archive","recall","synthesize","route"],
        probe_port=0, notes="Integration Brain router — ST/LT memory (module probe)",
    ),
    "sir_sentinel": Terminal(
        id="sir_sentinel", engine="claude_code", weight=0.85,
        cost_tier="medium", capability=["security","audit","armor","pdg"],
        probe_port=3001, notes="Security warden — Agent-Armor PDG",
    ),
    "sir_gideon": Terminal(
        id="sir_gideon", engine="local_audit", weight=0.85,
        cost_tier="free", capability=["security","audit","scorpion","gideon","forensic"],
        probe_port=0, notes="Forensic auditor — GIDEON_RISK_MATRIX //SCORPION pass",
    ),
    "sir_octavian": Terminal(
        id="sir_octavian", engine="local_ops", weight=0.82,
        cost_tier="free", capability=["ops","metrics","monitoring","telemetry","status","alerts","factory"],
        probe_port=8400, notes="Ops & metrics sentinel — factory throughput, health dashboard (:8400)",
    ),
    "sir_sonus": Terminal(
        id="sir_sonus", engine="kitten_tts", weight=0.88,
        cost_tier="free", capability=["tts","audio","voice","speak","synthesize","kitten","streaming"],
        probe_port=8300, notes="Kitten TTS streaming node — chunked audio synthesis HTTP :8300",
    ),
    "sir_gravity": Terminal(
        id="sir_gravity", engine="antigravity", weight=0.88,
        cost_tier="free", capability=["code_gen","ide_native","gemini","google","antigravity","kinetic"],
        probe_port=8080, notes="Google Antigravity — Gemini models via CLIProxyAPI antigravity OAuth channel",
    ),
    "sir_kimi": Terminal(
        id="sir_kimi", engine="kimi_cli", weight=0.82,
        cost_tier="free", capability=["long_context","research","chinese","moonshot","kimi","k2"],
        probe_port=8080, notes="Moonshot Kimi K2.5 — 1M context via CLIProxyAPI kimi OAuth channel",
    ),
    "sir_heimdall": Terminal(
        id="sir_heimdall", engine="pydantic_ai", weight=0.99,
        cost_tier="low", capability=["security","mesh","bifrost","zero_trust","network","sentinel"],
        probe_port=0, notes="Sir Heimdall — Bifrost Guardian & Mesh Network Sentinel",
    ),
    "sir_hermes": Terminal(
        id="sir_hermes", engine="hermes_cli", weight=0.78,
        cost_tier="free", capability=[
            "agent","tool_use","nous","openrouter","kinetic","autonomous",
            "shopify_admin","shopify_storefront","graphql_orchestration","webhook_choreography",
        ],
        probe_port=0, notes="Nous Hermes Agent — autonomous tool-calling via subprocess (-q mode)",
    ),
    "sir_openclaw": Terminal(
        id="sir_openclaw", engine="openclaw", weight=0.90,
        cost_tier="free", capability=[
            "compliant_trend_research","source_attribution","robots_policy","rate_limit_respect",
        ],
        probe_port=0, notes="Claw Suite harvester: compliant public-source research only",
    ),
    "sir_rustclaw": Terminal(
        id="sir_rustclaw", engine="rustclaw", weight=0.86,
        cost_tier="free", capability=[
            "rust_image_pipeline","cmyk_contrast_check","halftone_underbase_plan","avif_transcode_contract",
        ],
        probe_port=0, notes="Claw Suite Rust image pipeline contract",
    ),
    "lady_nanobot": Terminal(
        id="lady_nanobot", engine="next_edge", weight=0.84,
        cost_tier="free", capability=[
            "edge_component_agents","webgl_mockup_contract","nfc_route_contract","telemetry_event_contract",
        ],
        probe_port=0, notes="Claw Suite edge component swarm contract",
    ),
    "sir_zeroclaw": Terminal(
        id="sir_zeroclaw", engine="local_qwen", weight=1.00,
        cost_tier="free", capability=[
            "zero_trust","ip_trademark_guard","affiliate_abuse_guard","checkout_risk_gate",
        ],
        probe_port=11434, notes="Claw Suite zero-trust sentry; HUMAN_GATE for fraud and fingerprint actions",
    ),
}


# ── Probing ───────────────────────────────────────────────────────────────────

async def _probe_tcp(port: int, host: str = "127.0.0.1") -> tuple[bool, float]:
    t0 = time.perf_counter()
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=PROBE_TIMEOUT
        )
        writer.close()
        await writer.wait_closed()
        return True, (time.perf_counter() - t0) * 1000
    except Exception:
        return False, (time.perf_counter() - t0) * 1000


async def _probe_terminal(t: Terminal) -> None:
    """Update terminal status in-place."""
    t.last_probe = time.time()
    if t.probe_port:
        ok, ms = await _probe_tcp(t.probe_port)
        t.status     = "live" if ok else "dark"
        t.latency_ms = ms
    elif t.engine == "integration_brain":
        # File probe — check if integration_brain.py exists in configs dir
        t0 = time.perf_counter()
        ib_path = CAMELOT_HOME / "03_VAULT" / "training" / "configs" / "integration_brain.py"
        if ib_path.exists():
            t.status     = "assumed_live"   # file present; NotebookLM bridge probed separately
            t.latency_ms = (time.perf_counter() - t0) * 1000
        else:
            t.status     = "dark"
            t.latency_ms = (time.perf_counter() - t0) * 1000
    elif t.engine == "local_audit":
        # Sir Gideon — live if sir_gideon.py present in knights package
        gideon_py = CAMELOT_HOME / "03_VAULT" / "training" / "configs" / "knights" / "sir_gideon.py"
        t.status     = "live" if gideon_py.exists() else "dark"
        t.latency_ms = 0.0
    elif t.engine in ("antigravity.cli", "openai_codex", "open_source", "antigravity", "kimi_cli", "openclaw", "rustclaw", "next_edge"):
        t.status     = "assumed_live"
        t.latency_ms = 0.0
    elif t.engine == "hermes_cli":
        hermes_cli = (
            CAMELOT_HOME / "02_FORGE" / "KINETIC_ARMORY" / "hermes-agent" / "cli.py"
        )
        t.status     = "live" if hermes_cli.exists() else "dark"
        t.latency_ms = 0.0
    else:
        t.status     = "unknown"
        t.latency_ms = 0.0


# ── Switchboard class ─────────────────────────────────────────────────────────

class Switchboard:
    """Flight Control Terminal for all LLM engines.

    Air Traffic Control (Sir Link) pattern:
      - All traffic declared before routing
      - No dispatch to dark/degraded without fallback
      - Manifest broadcast to HUD on every probe cycle
    """

    def __init__(self):
        self._reg: dict[str, Terminal] = {k: v for k, v in TERMINAL_REGISTRY.items()}

    # ── Probing ───────────────────────────────────────────────────────────────

    async def probe_all(self) -> None:
        await asyncio.gather(*[_probe_terminal(t) for t in self._reg.values()])
        self._write_manifest()

    async def probe_one(self, terminal_id: str) -> Terminal | None:
        t = self._reg.get(terminal_id)
        if t:
            await _probe_terminal(t)
            self._write_manifest()
        return t

    def _needs_probe(self, t: Terminal) -> bool:
        return (time.time() - t.last_probe) > HEALTH_TTL_S

    # ── Routing ───────────────────────────────────────────────────────────────

    async def best_for(self, capabilities: list[str], cost_ceiling: str = "high") -> Terminal | None:
        """Return best live terminal matching capabilities. Lazy-probes stale entries."""
        cost_order = ["free", "low", "medium", "high"]
        ceiling_idx = cost_order.index(cost_ceiling) if cost_ceiling in cost_order else 3

        candidates = [
            t for t in self._reg.values()
            if any(c in t.capability for c in capabilities)
            and cost_order.index(t.cost_tier) <= ceiling_idx
        ]

        # Probe stale candidates lazily
        stale = [t for t in candidates if self._needs_probe(t)]
        if stale:
            await asyncio.gather(*[_probe_terminal(t) for t in stale])
            self._write_manifest()

        live = [t for t in candidates if t.status in ("live", "assumed_live")]
        if not live:
            return None
        return max(live, key=lambda t: t.weight)

    def route_sync(self, knight_id: str) -> Terminal | None:
        """Synchronous cache-only lookup — zero probe cost."""
        t = self._reg.get(knight_id)
        if t and t.status in ("live", "assumed_live", "unknown"):
            return t
        # Find live fallback with highest weight
        live = [x for x in self._reg.values() if x.status in ("live", "assumed_live")]
        return max(live, key=lambda x: x.weight) if live else None

    # ── Manifest ──────────────────────────────────────────────────────────────

    def _write_manifest(self) -> None:
        data = {
            "updated": time.time(),
            "terminals": {k: asdict(v) for k, v in self._reg.items()},
        }
        try:
            MANIFEST_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def read_manifest(self) -> dict:
        try:
            return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def summary(self) -> dict[str, str]:
        return {k: v.status for k, v in self._reg.items()}


# ── Module-level singleton ────────────────────────────────────────────────────

_board = Switchboard()


async def probe_all() -> None:
    await _board.probe_all()

async def best_for(capabilities: list[str], cost_ceiling: str = "high") -> Terminal | None:
    return await _board.best_for(capabilities, cost_ceiling)

def route_sync(knight_id: str) -> Terminal | None:
    return _board.route_sync(knight_id)

def get_manifest() -> dict:
    return _board.read_manifest()

def summary() -> dict[str, str]:
    return _board.summary()

def get_board() -> Switchboard:
    return _board
