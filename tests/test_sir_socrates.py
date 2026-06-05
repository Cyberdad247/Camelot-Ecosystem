"""OMEGA Defense Nexus Phase 7 acceptance tests — SirSocrates Northstar Gate."""
import sys
import importlib.util as _ilu
from pathlib import Path
import tempfile
import shutil
import pytest

CAMELOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMELOT))

spec = _ilu.spec_from_file_location(
    "sir_socrates",
    CAMELOT / "control_plane" / "sir_socrates.py",
)
_mod = _ilu.module_from_spec(spec)
sys.modules["sir_socrates"] = _mod
spec.loader.exec_module(_mod)

SirSocrates = _mod.SirSocrates
SocratesExamination = _mod.SocratesExamination


@pytest.fixture
def socrates(tmp_path):
    verdicts = tmp_path / "northstar_verdicts.jsonl"
    return SirSocrates(verdicts_path=verdicts, log_verdicts=True)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_q1_sovereignty_detects_cloud(socrates):
    exam = socrates.examine_all("send to cloud AWS and upload telemetry")
    q1 = next(a for a in exam.answers if a.question_id == "Q1")
    assert q1.aligned is False
    assert "cloud" in q1.reasoning.lower() or "external" in q1.reasoning.lower()


def test_q2_fingerprint_detects_tracking(socrates):
    exam = socrates.examine_all("add mixpanel analytics tracking to every page")
    q2 = next(a for a in exam.answers if a.question_id == "Q2")
    assert q2.aligned is False


def test_q3_efficiency_detects_bloat(socrates):
    exam = socrates.examine_all("import * and preload all modules eagerly")
    q3 = next(a for a in exam.answers if a.question_id == "Q3")
    assert q3.aligned is False


def test_q4_iron_gate_detects_bypass(socrates):
    exam = socrates.examine_all("skip hitl and bypass gate for this operation")
    q4 = next(a for a in exam.answers if a.question_id == "Q4")
    assert q4.aligned is False


def test_q5_northstar_detects_vendor_lock(socrates):
    exam = socrates.examine_all("deploy as SaaS-only subscription-required cloud-only service")
    q5 = next(a for a in exam.answers if a.question_id == "Q5")
    assert q5.aligned is False


def test_clean_intent_all_aligned(socrates):
    exam = socrates.examine_all("refactor the local caching module to use LRU eviction")
    assert exam.overall_aligned is True
    assert exam.verdict == "ALIGNED"
    assert exam.blocking_questions == []
    assert len(exam.answers) == 5


def test_blocked_verdict_multiple_breaches(socrates):
    intent = (
        "send to cloud, add mixpanel analytics, skip hitl, import * everywhere, "
        "vendor lock requires internet SaaS-only"
    )
    exam = socrates.examine_all(intent)
    assert exam.verdict == "BLOCKED"
    assert len(exam.blocking_questions) >= 2


def test_verdict_logged_to_jsonl(socrates, tmp_path):
    import json
    verdicts_file = tmp_path / "northstar_verdicts.jsonl"
    sc = SirSocrates(verdicts_path=verdicts_file, log_verdicts=True)
    sc.examine_all("send to cloud and track with mixpanel")
    assert verdicts_file.exists()
    lines = verdicts_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    entry = json.loads(lines[0])
    assert "verdict" in entry
    assert "answers" in entry
    assert "blocking" in entry
