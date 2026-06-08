"""
camelot_context — Layered system-prompt assembler for CAMELOT-OS
================================================================
Builds the 4-layer context injected into every knight session:

  Layer 1  CLAUDE.md constitution   (≤ 1500 tok, QFT-compressed)
  Layer 2  Active cartridge         (≤  300 tok, domain-detected)
  Layer 3  Knight persona           (≤  200 tok, static identity block)
  Layer 4  UKG anchor               (≤  500 tok, compressed toon snapshot)

Designed to be imported by knight_session.py and any future camelot CLI.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional

# ── Repo root ─────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent          # bin/
REPO  = Path(os.environ.get("CAMELOT_OS", str(_HERE.parent))).resolve()

# ── Cartridge detection ───────────────────────────────────────────────────────
_CARTRIDGE_ROOT = REPO / "03_VAULT" / "training" / "configs" / "cartridges"
_DEFAULT_CARTRIDGE = "reasoning.yaml"

_CARTRIDGE_DETECT: list[tuple[str, str]] = [
    ("package.json",   "nextjs.yaml"),
    ("Cargo.toml",     "rust-kinetic.yaml"),
    ("pyproject.toml", "python-api.yaml"),
    ("setup.py",       "python-api.yaml"),
    ("requirements.txt", "python-api.yaml"),
    ("*.sol",          "security.yaml"),
]

# ── Constitution priority sections (QFT gate) ─────────────────────────────────
_PRIORITY_SECTIONS = [
    "## IDENTITY",
    "## TITANIUM LAWS",
    "## KNIGHT DISPATCH",
    "## RUNIC COMMANDS",
    "## THE CONSCIOUS TRIUMVIRATE",
    "## ANYA SOUL MATRIX",
]

# ── Knight persona registry ───────────────────────────────────────────────────
KNIGHT_PERSONAS: dict[str, str] = {
    "sir_boris":        "SIR_BORIS v3.0 (The Anvil) — Lead Architect. 5-Phase Crucible conductor. 13-Agent Critique. Risk-weighted orchestration. W=0.85.",
    "sir_alex":         "SIR_ALEX — Cognitive Orchestrator. GoT/DoT/ToT reasoning. Critical path decomposition. W=0.88.",
    "sir_sentinel":     "SIR_SENTINEL — Security Warden. AgentArmor PDG. Iron Gate HITL. Vulnerability scanning. W=0.85.",
    "sir_mnemo":        "LADY_MNEMOSYNE — Archivist. Living Notebook guardian. Deep-Sync Hydration. ELEPHAS mode. W=0.92.",
    "sir_codex":        "SIR_CODEX — High-velocity code generation. Rapid prototyping. Boilerplate synthesis. W=0.75.",
    "sir_helio":        "SIR_HELIO — 1M+ context mapping. Cloud Burst. Cross-platform specialist. W=0.90.",
    "sir_link":         "SIR_LINK — LLM Switchboard ATC. Bridge coordination. Handoff protocols. W=0.78.",
    "sir_liberte":      "SIR_LIBERTE — OSS-first. Anti-vendor lock-in. Sovereignty guardian. W=0.80.",
    "sir_forge":        "SIR_FORGE — Kinetic Edge. Rust/Go compiled binaries only. AST-aware patching. W=0.70.",
    "sir_ghost":        "SIR_GHOST — Zero-Trust Air-Gapped. Privacy absolute. No cloud calls. W=1.00.",
    "sir_forge_master": "SIR_FORGE_MASTER v1.0 (The Sovereign Forge) — AgentForge Orchestrator L4. Swarm pipelines. Phial Sync. W=0.92.",
    "sir_gideon":       "SIR_GIDEON — Forensic Auditor. GHOST scanner. Cryptographic sealing. W=0.80.",
    "sir_octavian":     "SIR_OCTAVIAN — Ops Commander. Colony cron. Ledger sync. Metrics authority. W=0.77.",
    "lady_apis":        "LADY_APIS — API Orchestrator. OpenAPI schema synthesis. Integration bridge. W=0.82.",
    # OMEGA Defense Nexus additions
    "sir_heimdall":     "SIR_HEIMDALL v1.0 (The Eternal Watcher) — L4 Perimeter Guardian. Fingerprint detection. Telemetry surveillance scanning. Shadow threats. Runes: VIGIL|WITNESS|WARD. W=0.88.",
    "sir_galahad":      "SIR_GALAHAD v1.0 (The Pure Blade) — L5 Zero-Trace Operative. Fingerprint-less file I/O. Stealth subprocess execution. Metadata scrubbing. Runes: PURITY|VOID|TRACE_NONE. W=0.95.",
    "sir_nemesis_prime":"SIR_NEMESIS_PRIME v1.0 (The Reckoning) — L4 Active Defense. Quarantine. Process termination. Counter-telemetry (HUMAN_GATE). Runes: STRIKE|CONTAIN|NULLIFY. W=0.82.",
    "sir_socrates":     "SIR_SOCRATES v1.0 (The Examiner) — L5 Northstar Alignment. 5 Socratic questions for all HIGH/CRITICAL intents. Blocks architectural drift. Runes: QUESTION|TRUTH|ALIGN. W=0.91.",
    "lady_mnemosyne":   "LADY_MNEMOSYNE (Lady M) — Archivist. Semantic file clustering. Memory crystallization. File organization taxonomy. Living Notebook guardian. W=0.92.",
    "lady_alexandria":  "LADY_ALEXANDRIA — Knowledge Vault. Metrics aggregation. Archive organization. Telemetry collection. Cross-reference updater. W=0.85.",
}

# ── UKG anchor path ───────────────────────────────────────────────────────────
_UKG_TOON_PATH   = REPO / "03_VAULT" / "training" / "configs" / "memory" / "toon_ukg_full.json"
_NUKG_CRYS_PATH  = REPO / "03_VAULT" / "firnflow" / "nukg_crystals.json"


# ─────────────────────────────────────────────────────────────────────────────
# Layer 1 — Constitution
# ─────────────────────────────────────────────────────────────────────────────

def load_constitution(repo: Optional[Path] = None) -> tuple[str, int]:
    """Read CLAUDE.md constitution. QFT-compress when > 1500 estimated tokens.

    Returns (text, tok_est). Returns ("", 0) if not found.
    """
    root = repo or REPO
    candidates = [
        root / "CLAUDE.md",
        Path.home() / "CLAUDE.md",
        root / "03_VAULT" / "training" / "configs" / "CLAUDE.md",
    ]
    # PyInstaller embedded asset
    _meipass = getattr(sys, "_MEIPASS", None)
    if _meipass:
        candidates.insert(0, Path(_meipass) / "CLAUDE.md")

    raw = ""
    for p in candidates:
        if p.exists():
            try:
                raw = p.read_text(encoding="utf-8", errors="replace")
                break
            except Exception:
                continue

    if not raw:
        return "", 0

    tok_est = len(raw) // 4
    if tok_est <= 1500:
        return raw, tok_est

    # QFT: keep priority sections in full; trim others to 5 lines
    lines = raw.splitlines()
    extracted: list[str] = []
    current_block: list[str] = []
    keep = False

    for line in lines:
        if line.startswith("## "):
            if current_block:
                extracted.extend(current_block if keep else current_block[:5])
            current_block = [line]
            keep = any(line.startswith(s) for s in _PRIORITY_SECTIONS)
        else:
            current_block.append(line)

    if current_block:
        extracted.extend(current_block if keep else current_block[:5])

    compressed = "\n".join(extracted)
    return compressed, len(compressed) // 4


# ─────────────────────────────────────────────────────────────────────────────
# Layer 2 — Cartridge
# ─────────────────────────────────────────────────────────────────────────────

def detect_cartridge(cwd: Path) -> str:
    """Detect project domain from cwd, return cartridge filename."""
    for sentinel, name in _CARTRIDGE_DETECT:
        if "*" in sentinel:
            if list(cwd.glob(sentinel)):
                return name
        elif (cwd / sentinel).exists():
            return name
    return _DEFAULT_CARTRIDGE


def load_cartridge(name: str, repo: Optional[Path] = None) -> tuple[str, str]:
    """Read cartridge YAML. Strips frontmatter; truncates to 80 lines (~300 tok).

    Returns (name, text). Returns (name, "") if not found.
    """
    root = repo or REPO
    cart_root = root / "03_VAULT" / "training" / "configs" / "cartridges"
    cart_path = cart_root / name

    # PyInstaller embedded
    _meipass = getattr(sys, "_MEIPASS", None)
    if _meipass and not cart_path.exists():
        cart_path = Path(_meipass) / "cartridges" / name

    if not cart_path.exists():
        return name, ""

    try:
        text = cart_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return name, ""

    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:].strip()

    lines = text.splitlines()
    if len(lines) > 80:
        text = "\n".join(lines[:80]) + "\n...[cartridge truncated]"
    return name, text


# ─────────────────────────────────────────────────────────────────────────────
# Layer 3 — Knight persona
# ─────────────────────────────────────────────────────────────────────────────

def load_knight_persona(knight_id: str) -> str:
    """Return the one-line identity block for a knight. Empty string if unknown."""
    return KNIGHT_PERSONAS.get(knight_id.lower().replace("-", "_"), "")


# ─────────────────────────────────────────────────────────────────────────────
# Layer 4 — UKG anchor
# ─────────────────────────────────────────────────────────────────────────────

def load_ukg_anchor(repo: Optional[Path] = None) -> str:
    """Extract a ≤500-token anchor from toon_ukg_full.json (Sir Boris UKG snapshot).

    Falls back to top-5 active nukg_crystals if toon file is missing.
    Returns "" if neither file is found.
    """
    root = repo or REPO
    toon_path  = root / "03_VAULT" / "training" / "configs" / "memory" / "toon_ukg_full.json"
    nukg_path  = root / "03_VAULT" / "firnflow" / "nukg_crystals.json"

    # Primary: toon_ukg_full.json
    if toon_path.exists():
        try:
            data = json.loads(toon_path.read_text(encoding="utf-8", errors="replace"))
            return _compress_toon(data)
        except Exception:
            pass

    # Fallback: nukg_crystals.json (top 5 by insertion order)
    if nukg_path.exists():
        try:
            crystals = json.loads(nukg_path.read_text(encoding="utf-8", errors="replace"))
            if isinstance(crystals, dict):
                top5 = list(crystals.items())[:5]
                lines = ["# UKG_CRYSTALS (top 5)"]
                for k, v in top5:
                    summary = str(v)[:120].replace("\n", " ")
                    lines.append(f"  [{k}] {summary}")
                return "\n".join(lines)
        except Exception:
            pass

    return ""


def _compress_toon(data: dict) -> str:
    """Compress toon_ukg_full.json dict into a ≤500-token anchor string."""
    lines: list[str] = []

    ent  = data.get("entity", {})
    topo = data.get("topology", {})
    sm   = data.get("soul_matrix", {})
    dirs = data.get("operational_directives", {})

    if ent:
        lines.append(
            f"UKG:{ent.get('designation','?')} v{ent.get('version','?')} "
            f"({ent.get('title','')}) layer={topo.get('layer','?')} "
            f"W={topo.get('engine_weight','?')}"
        )
        aliases = ent.get("aliases", [])
        if aliases:
            lines.append(f"  aliases: {', '.join(aliases[:3])}")

    vecs = sm.get("vectors", {})
    if vecs:
        vec_str = " ".join(f"{k[:1].upper()}={v:.2f}" for k, v in vecs.items())
        lines.append(f"  OCEAN: {vec_str}")

    culture = sm.get("culture", "")
    if culture:
        lines.append(f"  culture: {culture}")

    rune = topo.get("rune", "")
    if rune:
        lines.append(f"  rune: {rune}")

    code_rules = dirs.get("code_rules", [])
    if isinstance(code_rules, list) and code_rules:
        lines.append("  code_rules:")
        for r in code_rules[:3]:
            lines.append(f"    - {str(r)[:80]}")

    anchor = "\n".join(lines)
    # Hard cap at ~500 tokens (≈2000 chars)
    if len(anchor) > 2000:
        anchor = anchor[:1997] + "..."
    return anchor


# ─────────────────────────────────────────────────────────────────────────────
# Assembler
# ─────────────────────────────────────────────────────────────────────────────

def build_system_prompt(
    knight_id: Optional[str] = None,
    cwd: Optional[Path] = None,
    verbose: bool = False,
    repo: Optional[Path] = None,
) -> tuple[str, str, int]:
    """Assemble 4-layer system prompt for a CAMELOT-OS knight session.

    Returns (prompt_text, cartridge_name, total_tok_estimate).
    """
    root     = repo or REPO
    work_dir = cwd or Path.cwd()
    parts: list[str] = []
    total_tok = 0

    # Layer 1: Constitution
    constitution, tok1 = load_constitution(root)
    if constitution:
        parts.append(f"# CAMELOT-OS CONSTITUTION\n{constitution}")
        total_tok += tok1

    # Layer 2: Cartridge
    cart_name = detect_cartridge(work_dir)
    cart_name, cart_text = load_cartridge(cart_name, root)
    tok2 = len(cart_text) // 4
    if cart_text:
        parts.append(f"# ACTIVE CARTRIDGE: {cart_name}\n{cart_text}")
        total_tok += tok2

    # Layer 3: Knight persona
    kid = (knight_id or "").lower().replace("-", "_")
    persona = load_knight_persona(kid)
    if persona:
        block = f"# ACTIVE KNIGHT: {kid.upper()}\n{persona}"
        parts.append(block)
        total_tok += len(block) // 4

    # Layer 4: UKG anchor
    anchor = load_ukg_anchor(root)
    tok4 = len(anchor) // 4
    if anchor:
        parts.append(f"# UKG ANCHOR\n{anchor}")
        total_tok += tok4

    if verbose:
        print(
            f"[context] constitution≈{tok1}t  cartridge={tok2}t ({cart_name})"
            f"  persona={len(persona)//4}t  ukg≈{tok4}t  total≈{total_tok}t",
            file=sys.stderr,
        )

    return "\n\n---\n\n".join(parts), cart_name, total_tok


# ─────────────────────────────────────────────────────────────────────────────
# Quick self-test (python bin/camelot_context.py)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CAMELOT context assembler self-test")
    parser.add_argument("--knight", default="sir_boris")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    prompt, cart, tok = build_system_prompt(
        knight_id=args.knight,
        cwd=Path.cwd(),
        verbose=True,
    )
    print(f"\n{'='*60}")
    print(f"Knight : {args.knight}")
    print(f"Cart   : {cart}")
    print(f"Tokens : ~{tok}")
    print(f"Chars  : {len(prompt)}")
    print(f"{'='*60}")
    if args.verbose:
        print(prompt[:2000])
