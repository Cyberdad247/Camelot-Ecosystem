"""OMEGA Defense Nexus Phase 3 acceptance tests — DependencyEngine (offline/mocked)."""
import importlib.util as _ilu
import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

CAMELOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMELOT))

spec = _ilu.spec_from_file_location(
    "dependency_engine",
    CAMELOT / "control_plane" / "infra" / "dependency_engine.py",
)
_dep_mod = _ilu.module_from_spec(spec)
sys.modules["dependency_engine"] = _dep_mod
spec.loader.exec_module(_dep_mod)

DependencyEngine = _dep_mod.DependencyEngine
DepAuditResult = _dep_mod.DepAuditResult
DepEntry = _dep_mod.DepEntry
UpdateProposal = _dep_mod.UpdateProposal


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def repo_dir():
    d = Path(tempfile.mkdtemp(prefix="camelot_dep_test_"))
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def pyproject_repo(repo_dir):
    (repo_dir / "pyproject.toml").write_text(
        '[project]\nname = "camelot"\ndependencies = [\n'
        '    "fastapi>=0.95.0",\n'
        '    "httpx>=0.25.0",\n'
        '    "pydantic>=2.0",\n'
        "]\n",
        encoding="utf-8",
    )
    return repo_dir


@pytest.fixture
def requirements_repo(repo_dir):
    (repo_dir / "requirements.txt").write_text(
        "requests>=2.28.0\nflask==3.0.0\n# comment line\n",
        encoding="utf-8",
    )
    return repo_dir


@pytest.fixture
def cargo_repo(repo_dir):
    (repo_dir / "Cargo.toml").write_text(
        '[package]\nname = "camelot"\n\n[dependencies]\nserde = "1.0"\ntokio = "1.28"\n',
        encoding="utf-8",
    )
    return repo_dir


@pytest.fixture
def package_json_repo(repo_dir):
    (repo_dir / "package.json").write_text(
        json.dumps({"dependencies": {"react": "^18.0.0", "next": "14.0.0"}}),
        encoding="utf-8",
    )
    return repo_dir


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_audit_pyproject(pyproject_repo):
    eng = DependencyEngine(repo_root=pyproject_repo, hermes_enabled=False)
    result = eng.audit()
    assert isinstance(result, DepAuditResult)
    assert result.total_count >= 3
    assert "python" in result.ecosystems_found
    names = [e.name for e in result.entries]
    assert "fastapi" in names
    assert "httpx" in names


def test_audit_requirements_txt(requirements_repo):
    eng = DependencyEngine(repo_root=requirements_repo, hermes_enabled=False)
    result = eng.audit()
    assert result.total_count >= 2
    names = [e.name for e in result.entries]
    assert "requests" in names
    assert "flask" in names


def test_audit_cargo_toml(cargo_repo):
    eng = DependencyEngine(repo_root=cargo_repo, hermes_enabled=False)
    result = eng.audit()
    assert "rust" in result.ecosystems_found
    names = [e.name for e in result.by_ecosystem("rust")]
    assert "serde" in names
    assert "tokio" in names


def test_audit_package_json(package_json_repo):
    eng = DependencyEngine(repo_root=package_json_repo, hermes_enabled=False)
    result = eng.audit()
    assert "node" in result.ecosystems_found
    names = [e.name for e in result.by_ecosystem("node")]
    assert "react" in names
    assert "next" in names


def test_audit_empty_repo(repo_dir):
    eng = DependencyEngine(repo_root=repo_dir, hermes_enabled=False)
    result = eng.audit()
    assert result.total_count == 0
    assert result.ecosystems_found == []


def test_propose_update_dry_run(pyproject_repo):
    eng = DependencyEngine(repo_root=pyproject_repo, hermes_enabled=False)
    proposal = eng.propose_update("fastapi", "0.110.0", dry_run=True)
    assert isinstance(proposal, UpdateProposal)
    assert proposal.package == "fastapi"
    assert proposal.proposed_version == "0.110.0"
    assert proposal.approved is False
    assert "dry_run" in proposal.notes


def test_check_updates_mocked(pyproject_repo, monkeypatch):
    """check_updates with _pip_latest mocked — no network call."""
    eng = DependencyEngine(repo_root=pyproject_repo, hermes_enabled=False, galahad_stealth=False)

    def _fake_pip_latest(pkg: str):
        return "99.0.0"   # simulate every package having a new version

    monkeypatch.setattr(eng, "_pip_latest", _fake_pip_latest)
    proposals = eng.check_updates(ecosystem="python")
    assert len(proposals) > 0
    for p in proposals:
        assert p.proposed_version == "99.0.0"
        assert isinstance(p, UpdateProposal)


def test_hermes_fires_on_check_updates(pyproject_repo, monkeypatch):
    """Hermes dependency.updates channel receives proposals when updates found."""
    eng = DependencyEngine(repo_root=pyproject_repo, hermes_enabled=True, galahad_stealth=False)
    monkeypatch.setattr(eng, "_pip_latest", lambda pkg: "99.0.0")

    emit_calls = []
    monkeypatch.setattr(eng, "_emit_hermes_updates", lambda proposals: emit_calls.append(proposals))

    proposals = eng.check_updates(ecosystem="python")
    assert len(emit_calls) == 1
    assert len(emit_calls[0]) == len(proposals)
