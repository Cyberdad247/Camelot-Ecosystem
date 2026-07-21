from __future__ import annotations

from pathlib import Path

from control_plane.ascension_mode import build_ascension_report, write_ascension_report


def test_build_ascension_report_scores_runtime_artifacts(tmp_path: Path) -> None:
    runtime = tmp_path / "03_VAULT" / "runtime_state"
    runtime.mkdir(parents=True)
    (runtime / "CloudBrain_Link.md").write_text("# link\n", encoding="utf-8")
    (runtime / "squire_index_latest.json").write_text("{}", encoding="utf-8")
    (tmp_path / "sample.py").write_text("print('ok')\n", encoding="utf-8")

    report = build_ascension_report(tmp_path, scan_path=tmp_path)

    assert report["schema"].endswith("/v1")
    assert report["cloudbrain"]["artifact_present"] >= 2
    assert "state" in report["score"]
    assert report["lady_m"]["triage"]["risk_score"] >= 0


def test_write_ascension_report_persists_json(tmp_path: Path) -> None:
    (tmp_path / "03_VAULT" / "runtime_state").mkdir(parents=True)
    result = write_ascension_report(tmp_path, scan_path=tmp_path)

    output = Path(result["output_path"])
    assert output.exists()
    assert output.name == "ascension_mode_latest.json"
