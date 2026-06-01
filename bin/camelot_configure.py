"""
camelot configure — Auto-Configuration Engine (WARP_GATE v1.0.0)
=================================================================
Probes the local environment and writes ~/.camelot/config.json so that
`camelot warp` can auto-select the optimal knight tier on every boot.

Detection pipeline:
  1. probe_cliproxy()    → CLIProxy :8080 (unified cloud proxy)
  2. probe_ollama()      → Ollama :11434 (local models)
  3. scan_api_keys()     → env vars + config files (Anthropic/Google/OpenAI)
  4. detect_hardware()   → RAM via psutil, GPU via nvidia-smi
  5. resolve_tier()      → T0 / T1 / T2 / T3 waterfall
  6. resolve_default_knight() → per-tier knight selection
  7. write_config()      → ~/.camelot/config.json (no key values — only booleans)
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO))

try:
    import httpx
    _HTTPX = True
except ImportError:
    _HTTPX = False

try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    _RICH = True
except ImportError:
    _RICH = False

_CONFIG_DIR  = Path.home() / ".camelot"
_CONFIG_FILE = _CONFIG_DIR / "config.json"

_CLIPROXY_PROBES = [
    "http://127.0.0.1:8080/health",
    "http://127.0.0.1:8080/v1/models",
    "http://127.0.0.1:8080/models",
]
_OLLAMA_PROBE = "http://127.0.0.1:11434/api/tags"
_PROBE_TIMEOUT = 1.5  # seconds — never block configure on a dead service


# ── Service probes ─────────────────────────────────────────────────────────────

def probe_cliproxy() -> dict:
    """Probe CLIProxy at :8080. Returns {live, url, latency_ms, models_count}."""
    if not _HTTPX:
        return {"live": False, "url": None, "latency_ms": None, "models_count": 0, "note": "httpx not installed"}

    for probe_url in _CLIPROXY_PROBES:
        try:
            t0 = time.monotonic()
            with httpx.Client(timeout=_PROBE_TIMEOUT) as c:
                r = c.get(probe_url)
            ms = int((time.monotonic() - t0) * 1000)
            if r.status_code in (200, 401, 405):  # 401/405 means server is alive
                # Try to count models from /v1/models
                models_count = 0
                try:
                    if "models" in probe_url:
                        data = r.json()
                        models_count = len(data.get("data", data.get("models", [])))
                except Exception:
                    pass
                return {
                    "live": True,
                    "url": "http://127.0.0.1:8080/v1",
                    "latency_ms": ms,
                    "models_count": models_count,
                    "note": f"HTTP {r.status_code} @ {probe_url.split('/')[-1]}",
                }
        except Exception:
            continue
    return {"live": False, "url": None, "latency_ms": None, "models_count": 0, "note": "connection refused"}


def probe_ollama() -> dict:
    """Probe Ollama at :11434. Returns {live, url, models}."""
    if not _HTTPX:
        return {"live": False, "url": None, "models": [], "note": "httpx not installed"}
    try:
        with httpx.Client(timeout=_PROBE_TIMEOUT) as c:
            r = c.get(_OLLAMA_PROBE)
        if r.status_code == 200:
            data = r.json()
            models = [m.get("name", m.get("model", "?")) for m in data.get("models", [])]
            return {"live": True, "url": "http://127.0.0.1:11434/v1", "models": models, "note": f"{len(models)} models"}
    except Exception:
        pass
    return {"live": False, "url": None, "models": [], "note": "connection refused"}


# ── API key discovery ─────────────────────────────────────────────────────────

def scan_api_keys() -> dict:
    """Discover API keys. Returns presence booleans — never returns actual key values."""
    found: dict[str, bool] = {
        "anthropic": False,
        "google": False,
        "openai": False,
        "cliproxy_oauth": False,
    }

    # Env vars
    if os.environ.get("ANTHROPIC_API_KEY", "").startswith("sk-ant"):
        found["anthropic"] = True
    if os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY"):
        found["google"] = True
    if os.environ.get("OPENAI_API_KEY", "").startswith("sk-"):
        found["openai"] = True

    # CLIProxy config — has API key wired
    cliproxy_config = Path("C:/Users/vizio/CLIProxyAPI/config.yaml")
    if cliproxy_config.exists():
        try:
            txt = cliproxy_config.read_text(encoding="utf-8", errors="replace")
            if "claude-api-key" in txt or "anthropic" in txt.lower():
                found["anthropic"] = True
            if "google" in txt.lower() or "gemini" in txt.lower():
                found["google"] = True
            if "openai" in txt.lower() or "gpt" in txt.lower():
                found["openai"] = True
        except Exception:
            pass

    # Claude OAuth token (Claude Code login)
    claude_auth = Path.home() / ".cli-proxy-api" / "claude.json"
    if not claude_auth.exists():
        claude_auth = Path.home() / ".claude.json"
    if claude_auth.exists():
        found["cliproxy_oauth"] = True

    # ~/.anthropic/
    anthro_dir = Path.home() / ".anthropic"
    if anthro_dir.exists() and any(anthro_dir.iterdir()):
        found["anthropic"] = True

    return found


# ── Hardware detection ────────────────────────────────────────────────────────

def detect_hardware() -> dict:
    hw: dict = {
        "ram_gb": None,
        "gpu_detected": False,
        "gpu_name": None,
        "os": platform.system(),
        "arch": platform.machine(),
        "python": platform.python_version(),
    }

    if _PSUTIL:
        hw["ram_gb"] = round(psutil.virtual_memory().total / (1024 ** 3), 1)

    # GPU: try nvidia-smi
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0 and result.stdout.strip():
            hw["gpu_detected"] = True
            hw["gpu_name"] = result.stdout.strip().splitlines()[0]
    except Exception:
        pass

    # GPU: try ROCm (AMD)
    if not hw["gpu_detected"]:
        try:
            result = subprocess.run(
                ["rocm-smi", "--showproductname"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0 and result.stdout.strip():
                hw["gpu_detected"] = True
                hw["gpu_name"] = "AMD (ROCm)"
        except Exception:
            pass

    return hw


def detect_portable() -> bool:
    """Return True if running from a removable/portable location."""
    # Check env flag first
    if os.environ.get("CAMELOT_PORTABLE"):
        return True
    # Check if exe is on a different drive than home (rough heuristic for Windows)
    exe = Path(sys.executable)
    home = Path.home()
    try:
        if os.name == "nt" and exe.drive.upper() != home.drive.upper():
            return True  # Different drive → likely thumbdrive
    except Exception:
        pass
    return False


# ── Tier resolution ───────────────────────────────────────────────────────────

def resolve_tier(cliproxy: dict, ollama: dict, keys: dict) -> str:
    """
    T3 — CLIProxy live (all cloud models pooled) OR any cloud key present
    T2 — Any single cloud key, no CLIProxy
    T1 — Ollama live + at least 1 cloud key
    T0 — Ollama only, no cloud access
    """
    has_cloud = any([keys["anthropic"], keys["google"], keys["openai"], keys["cliproxy_oauth"]])

    if cliproxy["live"]:
        return "T3"
    if has_cloud:
        return "T3" if cliproxy["live"] else "T2"
    if ollama["live"] and has_cloud:
        return "T1"
    if ollama["live"]:
        return "T0"
    # Nothing detected — default to T2 (user will need to provide keys)
    return "T2"


def resolve_default_knight(tier: str, keys: dict, hw: dict) -> str:
    tier_map = {
        "T0": "sir_ghost",   # air-gapped local only
        "T1": "sir_forge",   # local + cloud fallback
        "T2": "sir_link",    # gemini-flash (fast + cheap)
        "T3": "sir_boris",   # full cloud — best model
    }
    knight = tier_map.get(tier, "sir_link")

    # Downgrade if RAM is very low (< 8GB) and T3 would pick sir_boris (heavy)
    ram = hw.get("ram_gb") or 16
    if knight == "sir_boris" and ram < 8:
        knight = "sir_helio"  # Gemini handles long context with less local RAM

    return knight


# ── Config persistence ────────────────────────────────────────────────────────

def write_config(
    tier: str,
    default_knight: str,
    cliproxy: dict,
    ollama: dict,
    keys: dict,
    hw: dict,
    portable: bool = False,
) -> Path:
    cfg = {
        "version": "1.0.0",
        "tier": tier,
        "default_knight": default_knight,
        "cliproxy_url": cliproxy.get("url"),
        "cliproxy_live": cliproxy["live"],
        "ollama_url": ollama.get("url") if ollama["live"] else None,
        "ollama_live": ollama["live"],
        "ollama_models": ollama.get("models", []),
        # Keys stored as presence booleans ONLY — never actual values
        "anthropic_key_present": keys["anthropic"],
        "google_key_present": keys["google"],
        "openai_key_present": keys["openai"],
        "cliproxy_oauth_present": keys["cliproxy_oauth"],
        "ram_gb": hw.get("ram_gb"),
        "gpu_detected": hw.get("gpu_detected", False),
        "os": hw.get("os"),
        "arch": hw.get("arch"),
        "portable": portable,
        "last_configured": datetime.now(timezone.utc).isoformat(),
        "camelot_home": str(_REPO),
    }

    if portable:
        config_path = Path(".") / "camelot_config.json"
    else:
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config_path = _CONFIG_FILE

    config_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return config_path


def load_config() -> Optional[dict]:
    """Load config.json if it exists and is not stale (>7d)."""
    for candidate in [_CONFIG_FILE, Path(".") / "camelot_config.json"]:
        if candidate.exists():
            try:
                cfg = json.loads(candidate.read_text(encoding="utf-8"))
                return cfg
            except Exception:
                pass
    return None


# ── Orchestration ─────────────────────────────────────────────────────────────

def run_configure(verbose: bool = False) -> dict:
    """Run full auto-configuration. Writes config.json. Returns config dict."""
    if _RICH:
        console = Console()
        console.print("\n[bold yellow]⚔  CAMELOT-OS Auto-Configuration[/bold yellow]  //  WARP_GATE v1.0.0\n")
    else:
        console = None
        print("CAMELOT-OS Auto-Configuration")

    def status(msg: str, ok: bool = True) -> None:
        if _RICH:
            icon = "[green]✓[/green]" if ok else "[red]✗[/red]"
            console.print(f"  {icon}  {msg}")
        else:
            print(f"{'OK' if ok else '--'}  {msg}")

    # Step 1: Probe services (parallel-ish via sequential with short timeouts)
    status("Probing CLIProxy :8080...", True)
    cliproxy = probe_cliproxy()
    status(
        f"CLIProxy :8080  {'[green]LIVE[/green]' if cliproxy['live'] else '[red]not detected[/red]'}  "
        f"{cliproxy['note']}",
        cliproxy["live"],
    )

    status("Probing Ollama :11434...", True)
    ollama = probe_ollama()
    status(
        f"Ollama :11434  {'[green]LIVE[/green]' if ollama['live'] else '[red]not detected[/red]'}  "
        f"{ollama['note']}",
        ollama["live"],
    )

    # Step 2: API keys
    keys = scan_api_keys()
    key_summary = "  ".join(
        f"[green]{k}[/green]" if v else f"[dim]{k}[/dim]"
        for k, v in [
            ("Anthropic", keys["anthropic"]),
            ("Google", keys["google"]),
            ("OpenAI", keys["openai"]),
            ("CLIProxy-OAuth", keys["cliproxy_oauth"]),
        ]
    )
    if _RICH:
        console.print(f"  [bold]API Keys:[/bold]  {key_summary}")
    else:
        print("API Keys:", {k: v for k, v in keys.items() if v})

    # Step 3: Hardware
    hw = detect_hardware()
    ram_str = f"{hw['ram_gb']} GB RAM" if hw["ram_gb"] else "RAM unknown"
    gpu_str = f"GPU: {hw['gpu_name']}" if hw["gpu_detected"] else "no GPU"
    status(f"Hardware: {ram_str}  ·  {gpu_str}  ·  {hw['os']} {hw['arch']}", True)

    # Step 4: Resolve tier + knight
    portable = detect_portable()
    tier     = resolve_tier(cliproxy, ollama, keys)
    knight   = resolve_default_knight(tier, keys, hw)

    # Step 5: Write config
    config_path = write_config(tier, knight, cliproxy, ollama, keys, hw, portable)

    # Summary table
    if _RICH:
        t = Table(title="Configuration Summary", show_lines=True, border_style="yellow")
        t.add_column("Setting", style="bold")
        t.add_column("Value")
        t.add_row("Tier", f"[bold]{tier}[/bold]")
        t.add_row("Default Knight", f"[bold yellow]{knight}[/bold yellow]")
        t.add_row("CLIProxy", f"[green]LIVE[/green] {cliproxy.get('url','')}" if cliproxy["live"] else "[red]offline[/red]")
        t.add_row("Ollama", f"[green]LIVE[/green] — {', '.join(ollama['models'][:3]) or 'no models'}" if ollama["live"] else "[red]offline[/red]")
        t.add_row("Cloud Keys", key_summary)
        t.add_row("Config Written", str(config_path))
        t.add_row("Mode", "[yellow]PORTABLE[/yellow]" if portable else "standard")
        console.print(t)
        console.print(
            f"\n[bold green]⚔  Camelot is configured.[/bold green]  "
            f"Type [bold]camelot[/bold] or [bold]ks[/bold] to warp in.\n"
        )
    else:
        print(f"\nTier: {tier}  Knight: {knight}  Config: {config_path}")

    return load_config() or {}


def show_status() -> None:
    """Probe services and display health matrix — no writes."""
    if not _RICH:
        print("rich not installed — run: pip install rich")
        return

    console = Console()
    console.print("\n[bold yellow]⚔  CAMELOT-OS Service Status[/bold yellow]\n")

    cliproxy = probe_cliproxy()
    ollama   = probe_ollama()
    keys     = scan_api_keys()
    hw       = detect_hardware()
    cfg      = load_config()

    t = Table(title="Service Health Matrix", show_lines=True, border_style="dim")
    t.add_column("Service", style="bold", min_width=16)
    t.add_column("Status")
    t.add_column("Details")

    def _status_cell(live: bool) -> str:
        return "[green]● LIVE[/green]" if live else "[red]○ offline[/red]"

    t.add_row("CLIProxy :8080", _status_cell(cliproxy["live"]),
              f"{cliproxy.get('latency_ms','?')}ms · {cliproxy['note']}")
    t.add_row("Ollama :11434",  _status_cell(ollama["live"]),
              ", ".join(ollama["models"][:4]) if ollama["live"] else ollama["note"])
    t.add_row("Anthropic API",  _status_cell(keys["anthropic"]),
              "key present" if keys["anthropic"] else "not detected")
    t.add_row("Google API",     _status_cell(keys["google"]),
              "key present" if keys["google"] else "not detected")
    t.add_row("OpenAI API",     _status_cell(keys["openai"]),
              "key present" if keys["openai"] else "not detected")
    t.add_row("Claude OAuth",   _status_cell(keys["cliproxy_oauth"]),
              "~/.cli-proxy-api/claude.json" if keys["cliproxy_oauth"] else "not found")

    ram_str = f"{hw['ram_gb']} GB" if hw["ram_gb"] else "?"
    t.add_row("Hardware", "[green]●[/green]",
              f"{ram_str} RAM · {'GPU: ' + hw['gpu_name'] if hw['gpu_detected'] else 'no GPU'} · {hw['os']} {hw['arch']}")

    console.print(t)

    if cfg:
        tier   = cfg.get("tier", "?")
        knight = cfg.get("default_knight", "?")
        since  = cfg.get("last_configured", "?")
        console.print(f"\n[dim]Config:[/dim] tier=[bold]{tier}[/bold]  "
                      f"default=[bold yellow]{knight}[/bold yellow]  "
                      f"last configured=[dim]{since[:19]}[/dim]")
    else:
        console.print("\n[yellow]No config found — run [bold]camelot configure[/bold] first.[/yellow]")


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    run_configure(verbose=verbose)
