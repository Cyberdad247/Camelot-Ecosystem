
from control_plane import hyper_evolve


def test_promote_mutation_approves_safe_rule(tmp_path, monkeypatch):
    config_root = tmp_path / "configs"
    monkeypatch.setattr(hyper_evolve, "CONFIG_ROOT", config_root)
    monkeypatch.setattr(hyper_evolve, "LEARNINGS_PATH", config_root / "learnings.md")
    monkeypatch.setattr(hyper_evolve, "SKILLS_REGISTRY_PATH", config_root / "skills.md")
    monkeypatch.setattr(hyper_evolve, "AGENTS_REGISTRY_PATH", config_root / "agents.md")
    monkeypatch.setattr(hyper_evolve, "REPO_ROOT", tmp_path)

    ledger_path = tmp_path / "PROVENANCE_LEDGER.md"
    ledger_path.write_text("# Ledger\n", encoding="utf-8")
    monkeypatch.setattr(hyper_evolve, "append_provenance_entry", lambda **kwargs: {"status": "UPDATED", **kwargs})

    result = hyper_evolve.promote_mutation(
        agent="sir_syntax",
        objective="stabilize swarm review loop",
        learning="Record repeat failures before proposing permanent operating rules.",
        proposal="Require every promoted swarm rule to include at least one verification artifact.",
        verification=["pytest 03_VAULT/training/configs/tests/test_hyper_evolve.py"],
        scope=["control_plane/hyper_evolve.py"],
        actor="test",
    )

    assert result["status"] == "APPROVED"
    assert "Approved Rule" in (config_root / "skills.md").read_text(encoding="utf-8")
    assert (config_root / "agents.md").exists()
    assert (config_root / "learnings.md").exists()


def test_review_mutation_rejects_verification_bypass():
    review = hyper_evolve.review_mutation(
        proposal="Disable verification for fast merges.",
        learning="skip verification when it slows the swarm down",
        verification=["manual inspection"],
    )

    assert review["approved"] is False
    assert any("verification" in item.lower() for item in review["failures"])
