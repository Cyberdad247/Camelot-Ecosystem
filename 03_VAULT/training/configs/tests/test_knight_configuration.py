from __future__ import annotations

import json
from pathlib import Path

from control_plane.core.knight_configuration import write_knight_configuration


def test_write_knight_configuration_writes_runtime_artifact(tmp_path: Path):
    home = tmp_path / "CAMELOT_OS"
    cartridge_dir = home / "03_VAULT" / "training" / "configs" / "cartridges"
    cartridge_dir.mkdir(parents=True)
    (cartridge_dir / "security.yaml").write_text("name: security\n", encoding="utf-8")
    (home / "logs").mkdir(parents=True)
    (home / "logs" / "switchboard_manifest.json").write_text(
        json.dumps({"terminals": [{"id": "sir_helio"}]}),
        encoding="utf-8",
    )

    snapshot = write_knight_configuration(home)

    artifact = home / "03_VAULT" / "runtime_state" / "knight_configuration_latest.json"
    assert snapshot["status"] == "OK"
    assert snapshot["cartridges"]["active_count"] == 1
    assert snapshot["switchboard_roster"]["count"] == 1
    assert artifact.exists()
    assert json.loads(artifact.read_text(encoding="utf-8"))["artifact_path"] == str(artifact)
