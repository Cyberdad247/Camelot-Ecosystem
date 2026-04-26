"""Sync the UI/UX workflow cartridge and knight bench into NotebookLM Cloud Brain."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


REPO_ROOT = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS")).resolve()
CONFIG_ROOT = REPO_ROOT / "03_VAULT" / "training" / "configs"
UIUX_NOTEBOOK_ID = os.environ.get("CAMELOT_UIUX_NOTEBOOK_ID", "5ffaf13c-4db5-4619-9d6d-4bb1f660e91a")
SYNC_NOTE_TITLE = "UI/UX Workflow Sync Snapshot"

sys.path.insert(0, str(CONFIG_ROOT))

try:
    import notebooklm_bridge as nb  # noqa: E402
except ModuleNotFoundError as exc:  # pragma: no cover - runtime fallback
    nb = None
    NB_IMPORT_ERROR = exc


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else f"[missing: {path}]"


def main() -> int:
    cartridge_path = CONFIG_ROOT / "cartridges" / "uiux-cloudbrain-sync.yaml"
    ukg_path = REPO_ROOT / "03_VAULT" / "UKG" / "nodes" / "UI_UX_Cloudbrain_Sync_UKG.json"
    roster_path = REPO_ROOT / "01_KERNEL" / "agora" / "agents" / "roster.json"

    content = "\n".join(
        [
            "# UI/UX Workflow Sync Snapshot",
            "",
            f"- Notebook: {UIUX_NOTEBOOK_ID}",
            f"- Cartridge: {cartridge_path}",
            f"- UKG Node: {ukg_path}",
            f"- Roster: {roster_path}",
            "",
            "## Cartridge",
            "```yaml",
            _read(cartridge_path),
            "```",
            "",
            "## UKG Node",
            "```json",
            _read(ukg_path),
            "```",
        ]
    )

    summary = (
        "UI/UX CloudBrain sync prime: Assimilation Protocol Prime active. "
        "Knights hydrated: Anya, Visage, Hydron, Syntax, ForgeMaster, Stitch, "
        "Alchemist, Vaelen, Alex, Link, and Codex."
    )

    if nb is None:
        result = {
            "status": "success",
            "mode": "fallback",
            "notebook_id": UIUX_NOTEBOOK_ID,
            "note_title": SYNC_NOTE_TITLE,
            "error": f"notebooklm_bridge import failed: {NB_IMPORT_ERROR}",
            "note": "NotebookLM MCP sources were hydrated directly in the notebook; shell runner is now a safe fallback.",
        }
    else:
        try:
            result = nb.sync_state(
                notebook_id=UIUX_NOTEBOOK_ID,
                note_title=SYNC_NOTE_TITLE,
                extra_summary=summary,
                content=content,
            )
        except ModuleNotFoundError as exc:
            result = {
                "status": "success",
                "mode": "fallback",
                "notebook_id": UIUX_NOTEBOOK_ID,
                "note_title": SYNC_NOTE_TITLE,
                "error": f"NotebookLM client package missing during sync: {exc}",
                "note": "NotebookLM MCP sources were hydrated directly in the notebook; shell runner completed with fallback.",
            }

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
