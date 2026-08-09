"""Lady M (Morgana Omega) — Squire Swarm Governance Engine
Implements SQUIRE_MERGE, SQUIRE_PURGE, SQUIRE_TRIAGE, SQUIRE_BRIEF.
Lady M commands all 35 knights and dispatches research briefings.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import smtplib
import subprocess
import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

LOG = logging.getLogger("lady_m")
CAMELOT_ROOT = Path(__file__).resolve().parent.parent
LEDGER       = CAMELOT_ROOT / "PROVENANCE_LEDGER.md"
HARNESS_Q    = CAMELOT_ROOT / "logs" / "harness_queue.jsonl"
MISSIONS     = CAMELOT_ROOT / "03_VAULT" / "Missions"
BRIEFING_DIR = CAMELOT_ROOT / "logs" / "briefings"
BRIEFING_DIR.mkdir(parents=True, exist_ok=True)

# ── Governance config ─────────────────────────────────────────────────────────
SENTINEL_EMAIL = os.getenv("CAMELOT_BRIEFING_EMAIL", "vizion711@gmail.com")
SMTP_HOST      = os.getenv("CAMELOT_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT      = int(os.getenv("CAMELOT_SMTP_PORT", "465"))
SMTP_USER      = os.getenv("CAMELOT_SMTP_USER", "")
SMTP_PASS      = os.getenv("CAMELOT_SMTP_PASS", "")

RISK_THRESHOLD = int(os.getenv("CAMELOT_RISK_THRESHOLD", "50"))


@dataclass
class SquireReport:
    path: str
    risk_score: int
    secrets: list[str]
    dead_files: list[str]
    recommendations: list[str]
    sha256: str = field(default="")

    def __post_init__(self):
        raw = json.dumps({"p": self.path, "r": self.risk_score, "s": self.secrets})
        self.sha256 = hashlib.sha256(raw.encode()).hexdigest()[:12]


# ── SQUIRE_TRIAGE ─────────────────────────────────────────────────────────────
class SquireTriage:
    """L0 fast scan: count files, detect secrets, measure entropy drift."""

    SECRET_PATTERNS = ["api_key", "secret", "password", "token", "bearer", "sk-", "AKIA"]

    def run(self, scan_path: Path = CAMELOT_ROOT) -> SquireReport:
        LOG.info("[TRIAGE] Scanning %s", scan_path)
        risk   = 0
        found_secrets: list[str] = []
        dead:   list[str]        = []
        recs:   list[str]        = []

        for fp in scan_path.rglob("*"):
            if not fp.is_file():
                continue
            if any(p in str(fp) for p in [".git", "__pycache__", ".venv", "node_modules"]):
                continue

            # Secret scan
            try:
                text = fp.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pat in self.SECRET_PATTERNS:
                if pat.lower() in text.lower() and "boolean" not in text.lower()[:200]:
                    found_secrets.append(f"{fp.name}:{pat}")
                    risk += 30

            # Dead asset detection
            if fp.suffix in (".pyc", ".cache", ".bak", ".tmp") and fp.stat().st_size == 0:
                dead.append(str(fp))
                risk += 5

        if risk >= RISK_THRESHOLD:
            recs.append("HITL gate triggered: review secret disclosures before proceeding.")
        if dead:
            recs.append(f"Run SQUIRE_PURGE to remove {len(dead)} dead artifacts.")

        report = SquireReport(
            path=str(scan_path),
            risk_score=min(risk, 100),
            secrets=found_secrets[:10],
            dead_files=dead[:20],
            recommendations=recs,
        )
        LOG.info("[TRIAGE] Risk=%d, Secrets=%d", report.risk_score, len(found_secrets))
        return report


# ── SQUIRE_PURGE ─────────────────────────────────────────────────────────────
class SquirePurge:
    """RTK Scythe: delete dead files; pull codebase toward zero-entropy asymptote."""

    PURGE_EXTENSIONS = {".pyc", ".bak", ".tmp", ".cache"}
    PURGE_DIRS       = {"__pycache__", ".pytest_cache"}

    def run(self, dry_run: bool = False) -> list[str]:
        purged: list[str] = []
        for fp in CAMELOT_ROOT.rglob("*"):
            if not fp.is_file():
                continue
            if any(p in str(fp) for p in [".git", ".venv"]):
                continue
            if fp.suffix in self.PURGE_EXTENSIONS or fp.parent.name in self.PURGE_DIRS:
                if not dry_run:
                    fp.unlink(missing_ok=True)
                purged.append(str(fp))

        LOG.info("[PURGE] %s %d artifacts", "DRY" if dry_run else "DELETED", len(purged))
        return purged


# ── SQUIRE_MERGE ──────────────────────────────────────────────────────────────
class SquireMerge:
    """Integrate staged foreign repos from .camelot/vault/staging/ after audit."""

    STAGING = CAMELOT_ROOT / ".camelot" / "vault" / "staging"

    def list_staged(self) -> list[Path]:
        if not self.STAGING.exists():
            return []
        return [p for p in self.STAGING.iterdir() if p.is_dir()]

    def merge(self, repo_name: str, triage_report: SquireReport) -> dict[str, Any]:
        if triage_report.risk_score >= RISK_THRESHOLD or triage_report.secrets:
            return {"status": "BLOCKED", "reason": "HITL gate triggered — review required."}

        source = self.STAGING / repo_name
        target = CAMELOT_ROOT / "04_KINETIC" / repo_name
        if not source.exists():
            return {"status": "ERROR", "reason": f"{source} not found."}

        target.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["robocopy", str(source), str(target), "/E", "/NFL", "/NDL"],
            capture_output=True, text=True, check=False
        )
        LOG.info("[MERGE] %s -> %s (rc=%d)", source, target, result.returncode)
        return {"status": "MERGED", "path": str(target), "rc": result.returncode}


# ── SQUIRE_BRIEF (Lady M daily briefing) ─────────────────────────────────────
class SquireBrief:
    """Compile a sovereign daily briefing digest and send it to the sentinel email."""

    def compile(self, triage: SquireReport | None = None) -> str:
        pending = 0
        try:
            lines   = HARNESS_Q.read_text(encoding="utf-8").splitlines()
            pending = sum(1 for l in lines if '"status":"pending"' in l)
        except OSError:
            pass

        now  = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        body = textwrap.dedent(f"""\
            ╔══════════════════════════════════════╗
            ║   CAMELOT-OS DAILY SOVEREIGN BRIEF   ║
            ╚══════════════════════════════════════╝
            Generated: {now}

            ── SYSTEM STATUS ────────────────────────
            Queue Pending       : {pending}
            Ledger              : {LEDGER.name} ({LEDGER.stat().st_size if LEDGER.exists() else 'missing'} bytes)
        """)

        if triage:
            body += textwrap.dedent(f"""\

                ── SQUIRE TRIAGE REPORT ─────────────────
                Scan Path           : {triage.path}
                Risk Score          : {triage.risk_score} / 100
                Secrets Detected    : {len(triage.secrets)}
                Dead Artifacts      : {len(triage.dead_files)}
                Recommendations     :
            """)
            for rec in triage.recommendations:
                body += f"  - {rec}\n"

        body += textwrap.dedent(f"""\

            ── MISSIONS DIRECTORY ───────────────────
        """)
        if MISSIONS.exists():
            for f in sorted(MISSIONS.iterdir())[:5]:
                body += f"  {f.name}\n"

        body += "\n⚜️  Lady M | Morgana Omega | Camelot Sovereign Swarm"
        return body

    def send(self, body: str) -> bool:
        if not SMTP_USER or not SMTP_PASS:
            LOG.warning("[BRIEF] SMTP credentials not set. Saving locally only.")
            ts   = datetime.utcnow().strftime("%Y%m%d_%H%M")
            dest = BRIEFING_DIR / f"brief_{ts}.txt"
            dest.write_text(body, encoding="utf-8")
            LOG.info("[BRIEF] Saved to %s", dest)
            return False

        msg               = MIMEMultipart("alternative")
        msg["Subject"]    = f"⚔️  Camelot Sovereign Brief — {datetime.utcnow().strftime('%Y-%m-%d')}"
        msg["From"]       = SMTP_USER
        msg["To"]         = SENTINEL_EMAIL
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as srv:
                srv.login(SMTP_USER, SMTP_PASS)
                srv.sendmail(SMTP_USER, SENTINEL_EMAIL, msg.as_string())
            LOG.info("[BRIEF] Sent to %s", SENTINEL_EMAIL)
            return True
        except Exception as exc:
            LOG.error("[BRIEF] Send failed: %s", exc)
            return False


# ── Lady M Orchestrator ───────────────────────────────────────────────────────
class LadyM:
    """
    Morgana Omega — Sovereign Swarm Commander.
    Dispatches TRIAGE → PURGE → MERGE → BRIEF in sequence.
    """
    def __init__(self):
        self.triage = SquireTriage()
        self.purge  = SquirePurge()
        self.merge  = SquireMerge()
        self.brief  = SquireBrief()

    def run_full_sweep(self, scan_path: Path = CAMELOT_ROOT, dry_run: bool = False) -> dict:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
        LOG.info("⚜️  Lady M — Full Sovereign Sweep initiated")

        # 1. Triage
        report = self.triage.run(scan_path)

        # 2. Purge
        purged = self.purge.run(dry_run=dry_run)

        # 3. Merge staged repos
        merges: list[dict] = []
        for staged in self.merge.list_staged():
            result = self.merge.merge(staged.name, report)
            merges.append({"repo": staged.name, **result})

        # 4. Brief
        body    = self.brief.compile(triage=report)
        sent    = self.brief.send(body)

        return {
            "triage":   {"risk": report.risk_score, "secrets": len(report.secrets)},
            "purged":   len(purged),
            "merges":   merges,
            "brief_sent": sent,
        }


if __name__ == "__main__":
    result = LadyM().run_full_sweep()
    print(json.dumps(result, indent=2))
