"""
knight-session — Interactive Camelot-OS Knight Router via CLIProxyAPI + OmniRoute
==================================================================================
Global command: routes terminal prompts to the correct Camelot-OS knight using
the Soul Equation (MFOE) + OmniRoute config (omniroute.json), then streams via
CLIProxyAPI (:8080).  CLAUDE.md constitution is injected as system prompt every
session so knights respond as Camelot-OS agents, not vanilla LLMs.

Routing pipeline (per prompt):
  1. Privacy override  — keyword match → force SIR_GHOST (air-gapped)
  2. Forced knight     — /knight override bypasses routing
  3. Soul Equation     — CLIIntercept scores intent → knight
  4. Tier classify     — T0 (local) / T1 (simple) / T2 (standard) / T3 (complex)
  5. Fallback chain    — on error: cliproxy → gemini → codex → open_coder

Usage:
    knight-session                      # interactive auto-routing
    knight-session --knight sir_helio   # start forced to one knight
    knight-session --list               # print model map and exit
    knight-session --route              # print OmniRoute config and exit
    knight-session --no-context         # skip CLAUDE.md injection (raw LLM)
    knight-session --system FILE        # override system prompt from file
    knight-session --verbose            # show context token counts on boot

Commands inside the session:
    /knight <id>   Force a specific knight
    /auto          Return to Soul-Equation auto-routing
    /models        Show knight→model table
    /route         Show OmniRoute tier + engine config
    /status        Probe and show switchboard health
    /history       Show conversation history (system prompt excluded)
    /clear         Clear conversation history (system prompt preserved)
    /help          Show commands
    /exit          Quit  (also Ctrl+C)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUTF8", "1")
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── path setup ────────────────────────────────────────────────────────────────
_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO))

import httpx
from control_plane.cli_intercept import CLIIntercept
from control_plane.soul_router import CLIPROXY_URL
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

try:
    from bin.camelot_context import KNIGHT_PERSONAS as _ctx_KNIGHT_PERSONAS
    from bin.camelot_context import build_system_prompt as _ctx_build_system_prompt
    _CONTEXT_MODULE = True
except ImportError:
    try:
        import importlib.util
        import sys as _sys
        _spec = importlib.util.spec_from_file_location(
            "camelot_context", Path(__file__).resolve().parent / "camelot_context.py"
        )
        if _spec and _spec.loader:
            _cm = importlib.util.module_from_spec(_spec)
            _sys.modules["camelot_context"] = _cm
            _spec.loader.exec_module(_cm)
            _ctx_build_system_prompt = _cm.build_system_prompt
            _ctx_KNIGHT_PERSONAS = _cm.KNIGHT_PERSONAS
            _CONTEXT_MODULE = True
        else:
            _CONTEXT_MODULE = False
    except Exception:
        _CONTEXT_MODULE = False

# ── Load OmniRoute config ─────────────────────────────────────────────────────
_OMNIROUTE_PATH = _REPO / "03_VAULT" / "training" / "configs" / "config" / "omniroute.json"

def _load_omniroute() -> dict:
    try:
        return json.loads(_OMNIROUTE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

OMNIROUTE = _load_omniroute()
_upstream    = OMNIROUTE.get("upstream", {})
_cliproxy    = _upstream.get("cliproxy", {})
_constraints = OMNIROUTE.get("constraints", {})
_routing     = OMNIROUTE.get("routing_matrix", {})
_privacy     = _routing.get("privacy_override", {})
_tiers       = _routing.get("tiers", {})
_fallback    = _routing.get("fallback_chain", ["cliproxy", "gemini", "codex", "open_coder"])
_engines     = OMNIROUTE.get("engines", {})

# ── Constants ─────────────────────────────────────────────────────────────────
CLIPROXY_KEY   = os.environ.get("CLIPROXY_KEY", _cliproxy.get("api_key", "proxy-admin-key"))
OLLAMA_URL     = "http://127.0.0.1:11434/v1"
STREAM_TIMEOUT = _constraints.get("request_timeout_ms", 120000) / 1000

PRIVACY_KEYWORDS: frozenset[str] = frozenset(
    _privacy.get("trigger_keywords", ["secret", "local", "private", "credential", "key", "password"])
)
PRIVACY_KNIGHT = _privacy.get("forced_knight", "SIR_GHOST").lower().replace("-", "_")

_TIER_MAP = {
    "T0": "tier0_local_kinetic",
    "T1": "tier1_low_stakes",
    "T2": "tier2_standard",
    "T3": "tier3_complex",
}

# LATTICE_SIGNAL — Google-priority routing (2026-05-14)
# Source of truth: omniroute.json knight_model_map (loaded below)
# Harness-locked: sir_forge (qwen3:1.7b/Ollama), sir_ghost (qwen3:8b/Ollama)
def _build_knight_model_map() -> dict[str, tuple[str, str]]:
    kmm = OMNIROUTE.get("knight_model_map", {})
    if kmm:
        return {k: (v["primary"], v["provider"]) for k, v in kmm.items()}
    # Static fallback if omniroute.json unavailable
    return {
        "sir_boris":      ("gemini-3-pro-preview",     "google"),
        "sir_helio":      ("gemini-3.1-pro-preview",   "google"),
        "sir_alex":       ("gemini-3-pro-preview",     "google"),
        "sir_sentinel":   ("gemini-3-pro-preview",     "google"),
        "sir_codex":      ("gpt-5.4",                  "openai"),
        "sir_link":       ("gemini-3-flash-preview",   "google"),
        "sir_debug":      ("gemini-3-flash-preview",   "google"),
        "lady_apis":      ("gemini-3.1-pro-preview",   "google"),
        "sir_mnemo":      ("gemini-3.1-pro-preview",   "google"),
        "lady_mnemosyne": ("gemini-3.1-pro-preview",   "google"),
        "sir_liberte":    ("gemini-2.5-flash",         "google"),
        "sir_valerian":   ("gemini-3-pro-preview",     "google"),
        "sir_forge":      ("qwen3:1.7b",               "ollama"),
        "sir_ghost":      ("qwen3:8b",                 "ollama"),
    }

KNIGHT_MODEL_MAP: dict[str, tuple[str, str]] = _build_knight_model_map()

def _build_knight_fallback_map() -> dict[str, tuple[str, str]]:
    kmm = OMNIROUTE.get("knight_model_map", {})
    if kmm:
        return {k: (v.get("fallback", v["primary"]), v.get("fallback_provider", v["provider"]))
                for k, v in kmm.items()}
    return {}

KNIGHT_FALLBACK_MAP: dict[str, tuple[str, str]] = _build_knight_fallback_map()

_KNIGHT_WEIGHTS: dict[str, float] = {
    e["knight_binding"].lower().replace("-", "_"): e.get("weight", 0.0)
    for e in _engines.values()
    if "knight_binding" in e
}

KNIGHT_STYLE: dict[str, str] = {
    "sir_boris":    "bold yellow",
    "sir_alex":     "bold cyan",
    "sir_sentinel": "bold red",
    "sir_mnemo":    "bold magenta",
    "sir_codex":    "bold green",
    "sir_helio":    "bold bright_yellow",
    "sir_link":     "bold blue",
    "sir_liberte":  "white",
    "sir_forge":    "bold orange1",
    "sir_ghost":    "dim white",
}

# ── Context injection — ELEPHAS mode (LADY_MNEMOSYNE) ─────────────────────────

_CARTRIDGE_ROOT = _REPO / "03_VAULT" / "training" / "configs" / "cartridges"

# Ordered: first match wins
_CARTRIDGE_DETECT: list[tuple[str, str]] = [
    ("package.json",     "nextjs.yaml"),
    ("Cargo.toml",       "rust-kinetic.yaml"),
    ("pyproject.toml",   "python-api.yaml"),
    ("setup.py",         "python-api.yaml"),
    ("requirements.txt", "python-api.yaml"),
    ("go.mod",           "python-api.yaml"),
    ("*.sol",            "security.yaml"),
]
_DEFAULT_CARTRIDGE = "reasoning.yaml"

_KNIGHT_PERSONAS: dict[str, str] = {
    "sir_boris":    "SIR_BORIS v3.0 (The Anvil) — Lead Architect. 5-Phase Crucible conductor. 13-Agent Critique. Risk-weighted orchestration. W=0.85.",
    "sir_alex":     "SIR_ALEX — Cognitive Orchestrator. GoT/DoT/ToT reasoning. Critical path decomposition. W=0.88.",
    "sir_sentinel": "SIR_SENTINEL — Security Warden. AgentArmor PDG. Iron Gate HITL. Vulnerability scanning. W=0.85.",
    "sir_mnemo":    "LADY_MNEMOSYNE — Archivist. Living Notebook guardian. Deep-Sync Hydration. ELEPHAS mode. W=0.92.",
    "sir_codex":    "SIR_CODEX — High-velocity code generation. Rapid prototyping. Boilerplate synthesis. W=0.75.",
    "sir_helio":    "SIR_HELIO — 1M+ context mapping. Cloud Burst. Cross-platform specialist. W=0.90.",
    "sir_link":     "SIR_LINK — LLM Switchboard ATC. Bridge coordination. Handoff protocols. W=0.78.",
    "sir_liberte":  "SIR_LIBERTE — OSS-first. Anti-vendor lock-in. Sovereignty guardian. W=0.80.",
    "sir_forge":    "SIR_FORGE — Kinetic Edge. Rust/Go compiled binaries only. AST-aware patching. W=0.70.",
    "sir_ghost":    "SIR_GHOST — Zero-Trust Air-Gapped. Privacy absolute. No cloud calls. W=1.00.",
}

_CONSTITUTION_PRIORITY_SECTIONS = [
    "## IDENTITY",
    "## TITANIUM LAWS",
    "## KNIGHT DISPATCH",
    "## RUNIC COMMANDS",
    "## THE CONSCIOUS TRIUMVIRATE",
    "## ANYA SOUL MATRIX",
]


def _load_constitution() -> tuple[str, int]:
    """Load CLAUDE.md. QFT-compress if > 1500 estimated tokens. Returns (text, tok_est)."""
    candidates = [
        _REPO / "CLAUDE.md",
        Path.home() / "CLAUDE.md",
        _REPO / "03_VAULT" / "training" / "configs" / "CLAUDE.md",
    ]
    raw = ""
    for p in candidates:
        if p.exists():
            try:
                raw = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            break
    if not raw:
        return "", 0

    tok_est = len(raw) // 4
    if tok_est <= 1500:
        return raw, tok_est

    # QFT compress: keep priority sections in full; trim others to 5 lines
    lines = raw.splitlines()
    extracted: list[str] = []
    current_block: list[str] = []
    keep = False

    for line in lines:
        if line.startswith("## "):
            if current_block:
                extracted.extend(current_block if keep else current_block[:5])
            current_block = [line]
            keep = any(line.startswith(s) for s in _CONSTITUTION_PRIORITY_SECTIONS)
        else:
            current_block.append(line)

    if current_block:
        extracted.extend(current_block if keep else current_block[:5])

    compressed = "\n".join(extracted)
    return compressed, len(compressed) // 4


def _detect_and_load_cartridge(cwd: Path) -> tuple[str, str]:
    """Detect project domain from cwd, return (cartridge_name, cartridge_text)."""
    cartridge_name = _DEFAULT_CARTRIDGE
    for sentinel, name in _CARTRIDGE_DETECT:
        if "*" in sentinel:
            if list(cwd.glob(sentinel)):
                cartridge_name = name
                break
        elif (cwd / sentinel).exists():
            cartridge_name = name
            break

    cart_path = _CARTRIDGE_ROOT / cartridge_name
    if not cart_path.exists():
        return cartridge_name, ""

    try:
        text = cart_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return cartridge_name, ""

    # Strip YAML frontmatter
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:].strip()

    # Limit to 80 lines ≈ 300 tokens
    lines = text.splitlines()
    if len(lines) > 80:
        text = "\n".join(lines[:80]) + "\n...[cartridge truncated — token budget]"
    return cartridge_name, text


def _build_system_prompt(
    knight_id: Optional[str] = None,
    system_file: Optional[str] = None,
    verbose: bool = False,
) -> tuple[str, str, int]:
    """Build injected system prompt. Returns (prompt_text, cartridge_name, total_tokens)."""
    if system_file:
        p = Path(system_file)
        text = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
        return text, "custom", len(text) // 4

    # Delegate to camelot_context (4-layer: constitution + cartridge + persona + UKG anchor)
    if _CONTEXT_MODULE:
        try:
            return _ctx_build_system_prompt(
                knight_id=knight_id,
                cwd=Path.cwd(),
                verbose=verbose,
                repo=_REPO,
            )
        except Exception:
            pass  # fall through to inline

    # Inline fallback (3-layer: constitution + cartridge + persona, no UKG anchor)
    cwd = Path.cwd()
    parts: list[str] = []
    total_tok = 0

    constitution, tok1 = _load_constitution()
    if constitution:
        parts.append(f"# CAMELOT-OS CONSTITUTION\n{constitution}")
        total_tok += tok1

    cartridge_name, cartridge_text = _detect_and_load_cartridge(cwd)
    tok2 = len(cartridge_text) // 4
    if cartridge_text:
        parts.append(f"# ACTIVE CARTRIDGE: {cartridge_name}\n{cartridge_text}")
        total_tok += tok2

    if knight_id and knight_id in _KNIGHT_PERSONAS:
        persona_block = f"# ACTIVE KNIGHT: {knight_id.upper()}\n{_KNIGHT_PERSONAS[knight_id]}"
        parts.append(persona_block)
        total_tok += len(persona_block) // 4

    if verbose:
        print(
            f"[context] constitution≈{tok1}t  cartridge={tok2}t ({cartridge_name})  total≈{total_tok}t",
            file=sys.stderr,
        )

    return "\n\n---\n\n".join(parts), cartridge_name, total_tok


# ── OmniRoute helpers ─────────────────────────────────────────────────────────

def _privacy_check(prompt: str) -> Optional[str]:
    words = set(prompt.lower().split())
    if words & PRIVACY_KEYWORDS:
        return PRIVACY_KNIGHT
    return None


def _classify_tier(knight_id: str, soul_score: float) -> str:
    # LATTICE_SIGNAL: Google-priority tiers (G0/G1/G2/G3/X1/L0)
    if knight_id in ("sir_forge", "sir_ghost"):
        return "L0"  # harness-locked local
    if knight_id == "sir_codex":
        return "X1"  # Codex velocity channel
    if knight_id in ("sir_link", "sir_debug", "sir_liberte"):
        return "G1"  # Google flash bridge
    if knight_id in ("sir_helio", "lady_apis", "sir_mnemo", "lady_mnemosyne"):
        return "G2"  # Google pro context/research
    if soul_score >= 0.7 or knight_id in ("sir_boris", "sir_alex", "sir_sentinel", "sir_valerian"):
        return "G3"  # Google frontier apex
    return "G2"     # default to Google pro


def _resolve(knight_id: str, fallback_model: str = "", use_fallback: bool = False) -> tuple[str, str, str]:
    map_to_use = KNIGHT_FALLBACK_MAP if use_fallback else KNIGHT_MODEL_MAP
    entry = map_to_use.get(knight_id) or KNIGHT_MODEL_MAP.get(knight_id)
    if entry:
        model, provider = entry
        if provider == "ollama":
            return model, OLLAMA_URL, "ollama"
        return model, CLIPROXY_URL, CLIPROXY_KEY
    return fallback_model or "gemini-3-pro-preview", CLIPROXY_URL, CLIPROXY_KEY


# ── Streaming ─────────────────────────────────────────────────────────────────

def _stream(
    model: str,
    base_url: str,
    api_key: str,
    messages: list[dict],
    console: Console,
    knight_id: str,
    fallback_knights: Optional[list[str]] = None,
) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "stream": True, "temperature": 0.7}
    full: list[str] = []
    try:
        with httpx.Client(timeout=STREAM_TIMEOUT) as client:
            with client.stream("POST", url, json=payload, headers=headers) as resp:
                if resp.status_code != 200:
                    body = resp.read().decode("utf-8", errors="replace")
                    console.print(f"\n[red]CLIProxy {resp.status_code}: {body[:200]}[/red]")
                    if fallback_knights:
                        next_k = fallback_knights[0]
                        console.print(f"[yellow]  OmniRoute fallback → {next_k}[/yellow]")
                        fb_model, fb_url, fb_key = _resolve(next_k)
                        return _stream(fb_model, fb_url, fb_key, messages, console, next_k, fallback_knights[1:])
                    return ""
                console.print()
                for raw in resp.iter_lines():
                    if not raw or not raw.startswith("data: "):
                        continue
                    chunk_str = raw[6:].strip()
                    if chunk_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(chunk_str)
                        delta = (
                            chunk.get("choices", [{}])[0]
                            .get("delta", {})
                            .get("content", "")
                        )
                        if delta:
                            full.append(delta)
                            console.print(delta, end="", markup=False, highlight=False)
                    except json.JSONDecodeError:
                        pass
                console.print()
    except httpx.ConnectError:
        console.print(f"[red]Cannot connect to {base_url} — is CLIProxy running on :8080?[/red]")
        if fallback_knights:
            next_k = fallback_knights[0]
            console.print(f"[yellow]  OmniRoute fallback → {next_k}[/yellow]")
            fb_model, fb_url, fb_key = _resolve(next_k)
            return _stream(fb_model, fb_url, fb_key, messages, console, next_k, fallback_knights[1:])
    except Exception as exc:
        console.print(f"[red]Stream error: {exc}[/red]")
    return "".join(full)


# ── Display helpers ───────────────────────────────────────────────────────────

def _models_table(console: Console) -> None:
    t = Table(title="Knight → LLM Binding  [LATTICE_SIGNAL — Google Priority]",
              show_lines=True, border_style="dim")
    t.add_column("Knight ID", style="bold", min_width=14)
    t.add_column("Primary Model")
    t.add_column("Provider")
    t.add_column("Tier")
    t.add_column("Fallback")
    t.add_column("W")
    for kid, (model, provider) in KNIGHT_MODEL_MAP.items():
        style    = KNIGHT_STYLE.get(kid, "white")
        weight   = _KNIGHT_WEIGHTS.get(kid, 0.0)
        w_str    = f"{weight:.2f}" if weight else "—"
        fb_entry = KNIGHT_FALLBACK_MAP.get(kid)
        fb_str   = fb_entry[0] if fb_entry else "—"
        tier     = _classify_tier(kid, weight)
        locked   = " [dim]🔒[/dim]" if provider == "ollama" else ""
        t.add_row(f"[{style}]{kid}[/{style}]{locked}", model, provider, tier, fb_str, w_str)
    console.print(t)
    console.print("  [dim]🔒 = harness-locked (local Ollama, never rerouted)[/dim]")


def _route_table(console: Console) -> None:
    t = Table(title="OmniRoute Tier Matrix", show_lines=True, border_style="cyan")
    t.add_column("Tier", style="bold", min_width=6)
    t.add_column("Description")
    t.add_column("Models")
    t.add_column("Local?")
    tier_labels = {"tier0_local_kinetic": "T0", "tier1_low_stakes": "T1",
                   "tier2_standard": "T2", "tier3_complex": "T3"}
    for tier_key, label in tier_labels.items():
        td     = _tiers.get(tier_key, {})
        models = ", ".join(td.get("models", []))
        local  = "✓" if td.get("local_eligible") or label == "T0" else "—"
        t.add_row(label, td.get("description", "—"), models or "—", local)
    console.print(t)
    console.print(
        f"\n[bold red]Privacy Override[/bold red]  "
        f"keywords={list(PRIVACY_KEYWORDS)[:6]}…  "
        f"→ force [bold]{PRIVACY_KNIGHT}[/bold] (air-gapped)"
    )
    console.print(
        f"[bold yellow]Fallback Chain[/bold yellow]  {' → '.join(_fallback)}"
    )
    t2 = Table(title="Engine Weights (omniroute.json)", show_lines=False, border_style="dim")
    t2.add_column("Engine")
    t2.add_column("Knight")
    t2.add_column("Weight")
    t2.add_column("Tier")
    t2.add_column("Function")
    for eng_name, eng in _engines.items():
        t2.add_row(
            eng_name,
            eng.get("knight_binding", "—"),
            str(eng.get("weight", "—")),
            eng.get("tier", "—"),
            eng.get("function", "—")[:40],
        )
    console.print(t2)


def _status(console: Console) -> None:
    import asyncio

    from control_plane.switchboard import get_manifest, probe_all
    asyncio.run(probe_all())
    manifest   = get_manifest()
    terminals  = manifest.get("terminals", {})
    t = Table(title="Switchboard Health", show_lines=False, border_style="dim")
    t.add_column("Knight", style="bold", min_width=14)
    t.add_column("Cost Tier")
    t.add_column("Status")
    t.add_column("Port")
    t.add_column("Notes")
    for tid, term in sorted(terminals.items()):
        s       = term["status"]
        s_style = "green" if s in ("live", "assumed_live") else "red"
        t.add_row(
            tid, term["cost_tier"],
            f"[{s_style}]{s}[/{s_style}]",
            str(term["probe_port"]) if term["probe_port"] else "—",
            term.get("notes", "")[:45],
        )
    console.print(t)


HELP_TEXT = """\
[bold]Session Commands[/bold]
  /knight <id>   Force a specific knight (e.g. /knight sir_helio)
  /auto          Return to auto-routing via Soul Equation + OmniRoute
  /models        Show knight→model map
  /route         Show OmniRoute tier config and engine weights
  /status        Probe and show switchboard health
  /history       Show conversation history (system prompt excluded)
  /clear         Clear conversation history (system prompt preserved)
  /runes         List all runic commands and Omega runes
  /help          Show this help
  /exit          Quit  (or Ctrl+C)

[bold]Runic Commands[/bold] (prefix with //)
  //BOOT         Run awaken 6-phase boot sequence
  //FORGE <task> Kinetic build dispatch → SIR_FORGE
  //SWARM <task> Parallel colony dispatch → SIR_BORIS
  //PLAN <task>  ToT strategic planning → MERLIN_OMEGA
  //HEAL <path>  PIV self-healing → SIR_DEBUG
  //SCAN <path>  Squire Colony triage → CLARITY_CORE
  //FLEET <task> Graph orchestrator dispatch
  Omega_* runes  29 system-level operations

[bold]Valid knight IDs:[/bold] """ + "  ".join(KNIGHT_MODEL_MAP)


def _handle_runic(user_input: str, console: "Console") -> bool:
    """
    Detect //RUNE or Omega_RUNE prefix and execute.
    Returns True if handled (caller should `continue`), False otherwise.
    """
    stripped = user_input.strip()

    # //SCAN is a CLARITY_CORE alias — not in runic_router, handle locally
    if stripped.upper().startswith("//SCAN"):
        parts = stripped.split(maxsplit=1)
        path = parts[1].strip() if len(parts) > 1 else "."
        console.print(f"[dim]CLARITY_CORE: squire colony triage → {path}[/dim]")
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "squires.colony", "triage", path, "--auto-approve"],
            cwd=str(_REPO),
            capture_output=False,
        )
        return True

    # //BOOT — run awaken.py
    if stripped.upper().startswith("//BOOT"):
        console.print("[dim]Executing awaken 6-phase boot...[/dim]")
        import subprocess
        subprocess.run([sys.executable, str(_REPO / "bin" / "awaken.py")], cwd=str(_REPO))
        return True

    # Generic runic / Omega dispatch
    if stripped.startswith("//") or stripped.startswith("Omega_"):
        try:
            from control_plane.runic_router import detect_and_route
            result = detect_and_route(stripped)
            if result is None:
                return False
            from rich.panel import Panel
            from rich.table import Table
            t = Table(show_header=False, box=None, padding=(0, 1))
            t.add_row("[bold]Rune[/bold]", result.rune)
            t.add_row("[bold]Knight[/bold]", result.knight)
            t.add_row("[bold]Mode[/bold]", result.mode)
            t.add_row("[bold]Task ID[/bold]", result.task_id)
            t.add_row("[bold]Queued[/bold]", "[green]Yes[/green]" if result.queued else "[red]No[/red]")
            for k, v in result.metadata.items():
                t.add_row(f"[dim]{k}[/dim]", str(v)[:80])
            console.print(Panel(t, title=f"[bold yellow]{result.rune}[/bold yellow] dispatched", border_style="yellow"))
        except Exception as e:
            console.print(f"[red]Runic dispatch error: {e}[/red]")
        return True

    return False


# ── Main REPL ─────────────────────────────────────────────────────────────────

def _repl(
    forced_start: Optional[str],
    console: Console,
    no_context: bool = False,
    system_file: Optional[str] = None,
    verbose: bool = False,
) -> None:
    # ── Keyring auto-load (inject stored API keys into env) ─────────────────────
    try:
        from bin.camelot_keys import load_keys_to_env
        load_keys_to_env()
    except Exception:
        pass

    intercept     = CLIIntercept()
    forced_knight: Optional[str] = forced_start

    # ── Build system prompt (ELEPHAS / LADY_MNEMOSYNE) ────────────────────────
    system_text    = ""
    cartridge_name = "disabled"
    total_tok      = 0

    if not no_context:
        system_text, cartridge_name, total_tok = _build_system_prompt(
            knight_id=forced_start,
            system_file=system_file,
            verbose=verbose,
        )

    # System message is always first in history; never cleared, never shown in /history
    messages: list[dict] = []
    if system_text:
        messages.append({"role": "system", "content": system_text})

    # ── Boot banner ───────────────────────────────────────────────────────────
    omni_version = OMNIROUTE.get("version", "?")
    if no_context:
        ctx_line = "[dim]Context: disabled (--no-context) — raw LLM mode[/dim]"
    elif system_text:
        ctx_line = (
            f"Context: [bold]{cartridge_name}[/bold]  ·  "
            f"Constitution: [bold green]injected ≈{total_tok}t[/bold green]"
        )
    else:
        ctx_line = "[yellow]Context: CLAUDE.md not found — running without constitution[/yellow]"

    console.print(Panel(
        "[bold yellow]CAMELOT-OS Knight Session[/bold yellow]\n"
        f"CLIProxyAPI  [bold]{CLIPROXY_URL}[/bold]  ·  "
        f"OmniRoute v{omni_version}  ·  "
        f"Privacy shield [bold red]{len(PRIVACY_KEYWORDS)} keywords[/bold red]\n"
        f"Fallback chain: [dim]{' → '.join(_fallback)}[/dim]\n"
        f"{ctx_line}\n"
        "Type [bold]/help[/bold] for commands · [bold]/route[/bold] for tier config · "
        "[bold]/exit[/bold] or Ctrl+C to quit",
        title="[bold]⚔  KNIGHT-SESSION  //  OMNIROUTE[/bold]",
        border_style="yellow",
    ))
    _models_table(console)
    console.print()

    while True:
        if forced_knight:
            label_model, _, _ = _resolve(forced_knight)
            style = KNIGHT_STYLE.get(forced_knight, "white")
            ctx_suffix = "[dim]|raw[/dim]" if no_context else ""
            prompt_label = (
                f"[bold {style}]{forced_knight}[/bold {style}]"
                f"[dim]|{label_model}|forced{ctx_suffix}[/dim] > "
            )
        else:
            raw_suffix = "[dim]|raw[/dim]" if no_context else ""
            prompt_label = f"[bold green]auto[/bold green][dim]|omni{raw_suffix}[/dim] > "

        try:
            user_input = console.input(prompt_label).strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Exiting knight-session.[/dim]")
            break

        if not user_input:
            continue

        # ── Commands ──────────────────────────────────────────────────────────
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd   = parts[0].lower()
            arg   = parts[1].strip() if len(parts) > 1 else ""

            if cmd in ("/exit", "/quit", "/q"):
                console.print("[dim]Exiting knight-session.[/dim]")
                break
            elif cmd == "/help":
                console.print(HELP_TEXT)
            elif cmd == "/models":
                _models_table(console)
            elif cmd == "/route":
                _route_table(console)
            elif cmd == "/status":
                _status(console)
            elif cmd == "/clear":
                # Preserve system prompt across clear
                messages.clear()
                if system_text:
                    messages.append({"role": "system", "content": system_text})
                console.print("[dim]History cleared. System context preserved.[/dim]")
            elif cmd == "/history":
                visible = [m for m in messages if m["role"] != "system"]
                if not visible:
                    console.print("[dim]No history.[/dim]")
                else:
                    for m in visible:
                        role_style = "bold green" if m["role"] == "user" else "bold yellow"
                        console.print(
                            f"[{role_style}]{m['role']}[/{role_style}]: {m['content'][:300]}"
                        )
            elif cmd == "/auto":
                forced_knight = None
                console.print("[dim]Auto-routing via Soul Equation + OmniRoute enabled.[/dim]")
            elif cmd == "/knight":
                if arg in KNIGHT_MODEL_MAP:
                    forced_knight = arg
                    m, url, _ = _resolve(arg)
                    style = KNIGHT_STYLE.get(arg, "white")
                    console.print(
                        f"[{style}]Forced → {arg}[/{style}]  "
                        f"model=[bold]{m}[/bold]  backend={url}"
                    )
                else:
                    console.print(
                        f"[red]Unknown knight '[bold]{arg}[/bold]'. "
                        f"Valid: {', '.join(KNIGHT_MODEL_MAP)}[/red]"
                    )
            elif cmd == "/context":
                # T-04 bonus: show current context status
                if no_context:
                    console.print("[dim]Context injection: disabled (--no-context)[/dim]")
                elif system_text:
                    console.print(
                        f"[green]Context: ACTIVE[/green]\n"
                        f"  Cartridge: [bold]{cartridge_name}[/bold]\n"
                        f"  Tokens: ≈{total_tok}\n"
                        f"  System prompt: {len(system_text)} chars"
                    )
                else:
                    console.print("[yellow]Context: CLAUDE.md not found[/yellow]")
            elif cmd == "/runes":
                try:
                    from control_plane.runic_router import list_runes
                    runes = list_runes()
                    console.print("[bold yellow]Runic Commands:[/bold yellow] " + "  ".join(runes["runic_commands"]))
                    console.print("[bold yellow]Omega Runes:[/bold yellow] " + "  ".join(runes["omega_runes"]))
                except Exception as e:
                    console.print(f"[red]Could not load rune table: {e}[/red]")
            else:
                console.print(f"[red]Unknown command: {cmd}. Type /help.[/red]")
            continue

        # ── Runic dispatch (// prefix) ────────────────────────────────────────
        if user_input.startswith("//") or (user_input.startswith("Omega_") and "_" in user_input[6:]):
            if _handle_runic(user_input, console):
                continue

        # ── Route and respond ─────────────────────────────────────────────────
        messages.append({"role": "user", "content": user_input})

        privacy_hit = _privacy_check(user_input)

        if forced_knight:
            knight_id = forced_knight
            model, base_url, api_key = _resolve(forced_knight)
            reason = f"FORCED /knight {forced_knight}"
            tier   = _classify_tier(knight_id, 0.0)
        elif privacy_hit:
            knight_id = privacy_hit
            model, base_url, api_key = _resolve(knight_id)
            reason = "PRIVACY OVERRIDE — keyword match → air-gapped"
            tier   = "T0"
            console.print(
                f"[bold red]  ⚠ PRIVACY SHIELD — routing to {knight_id.upper()} (local)[/bold red]"
            )
        else:
            result     = intercept.intercept(user_input)
            knight_id  = result.route.knight_id
            model, base_url, api_key = _resolve(knight_id, result.model)
            reason     = result.route.reason
            soul_score = getattr(result.route, "score", 0.5)
            tier       = _classify_tier(knight_id, soul_score)

        weight = _KNIGHT_WEIGHTS.get(knight_id, 0.0)
        w_str  = f"W={weight:.2f}" if weight else ""
        style  = KNIGHT_STYLE.get(knight_id, "white")

        console.print(
            f"[dim]  [{tier}] → [{style}]{knight_id.upper()}[/{style}] "
            f"[bold]{model}[/bold] "
            f"@ {base_url.split('/')[2]}  "
            f"{w_str}  [italic]{reason[:60]}[/italic][/dim]"
        )

        fallback_order  = ["sir_helio", "sir_codex", "sir_link", "sir_forge"]
        fallback_knights = [k for k in fallback_order if k != knight_id]

        assistant_text = _stream(
            model=model, base_url=base_url, api_key=api_key,
            messages=messages, console=console,
            knight_id=knight_id, fallback_knights=fallback_knights,
        )

        if assistant_text:
            messages.append({"role": "assistant", "content": assistant_text})


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Camelot-OS Knight Session — OmniRoute + CLIProxyAPI + Constitution"
    )
    parser.add_argument("--knight", "-k", metavar="KNIGHT_ID",
                        help="Start forced to a specific knight")
    parser.add_argument("--list", "-l", action="store_true",
                        help="Print knight→model map and exit")
    parser.add_argument("--route", "-r", action="store_true",
                        help="Print OmniRoute tier config and exit")
    parser.add_argument("--no-context", "-n", action="store_true",
                        help="Skip CLAUDE.md injection — raw LLM mode")
    parser.add_argument("--system", "-s", metavar="FILE",
                        help="Override system prompt from a file")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show context token counts and routing details")
    args = parser.parse_args()

    console = Console()

    if args.list:
        _models_table(console)
        return

    if args.route:
        _route_table(console)
        return

    forced: Optional[str] = None
    if args.knight:
        if args.knight not in KNIGHT_MODEL_MAP:
            console.print(
                f"[red]Unknown knight '{args.knight}'. "
                f"Valid: {', '.join(KNIGHT_MODEL_MAP)}[/red]"
            )
            sys.exit(1)
        forced = args.knight

    _repl(
        forced_start=forced,
        console=console,
        no_context=args.no_context,
        system_file=args.system,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
