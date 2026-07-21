from __future__ import annotations

import hashlib
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

# Note: entiremap.md was consolidated into docs/architecture/ in July 2026
# as part of the root-level documentation cleanup.
CANONICAL_DOCS = [
    REPO_ROOT / "docs" / "architecture" / "entiremap.md",
    REPO_ROOT / "docs" / "architecture" / "SOURCE_OF_TRUTH_MAP.md",
    REPO_ROOT / "docs" / "OS_MANIFEST.md",
    REPO_ROOT / "docs" / "SEPTEM_REGNA" / "L7_ETHEREAL" / "OS_MANIFEST.md",
]

ENTIREMAP_MIRROR = REPO_ROOT / "docs" / "SEPTEM_REGNA" / "L7_ETHEREAL" / "entiremap.md"

EXPECTED_PATHS = [
    "bin/awaken.py",
    "control_plane/boot_sequence.py",
    "control_plane/runic_router.py",
    "control_plane/cloud_services.py",
    "03_VAULT/training/configs/notebooklm_bridge.py",
    ".camelot-config.yaml",
    "02_FORGE/PORTAL_CORE/Anya_Dashboard",
    "02_FORGE/apps/omni-eye-dashboard",
    "01_KERNEL/senses/morgana_bridge",
    "kinetic_edge",
    "logs/defense_grid/ledger_sync_status.json",
]

BANNED_CURRENT_ANCHORS = [
    "root `OS_MANIFEST.md`",
    "root `VERSION`",
    "root `config.json`",
    "repo-root `cloud_orchestrator/`",
    "`kinetic_edge/mcp_server/`",
    "`02_FORGE/web/`",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _extract_absolute_link_targets(text: str) -> list[Path]:
    matches = re.findall(r"\]\((C:/Users/vizio/CAMELOT_OS/[^)#]+)", text)
    cleaned: list[Path] = []
    for match in matches:
        base = re.sub(r":\d+(?::\d+)?$", "", match)
        cleaned.append(Path(base))
    return cleaned


def validate_architecture_docs() -> list[str]:
    errors: list[str] = []

    for doc in CANONICAL_DOCS + [ENTIREMAP_MIRROR]:
        if not doc.exists():
            errors.append(f"missing doc: {doc.relative_to(REPO_ROOT)}")

    if errors:
        return errors

    canonical_map = REPO_ROOT / "docs" / "architecture" / "entiremap.md"
    if canonical_map.exists() and ENTIREMAP_MIRROR.exists():
        if _sha256(canonical_map) != _sha256(ENTIREMAP_MIRROR):
            errors.append("entiremap mirror is not synced with docs/architecture/entiremap.md")

    for rel_path in EXPECTED_PATHS:
        if not (REPO_ROOT / rel_path).exists():
            errors.append(f"expected live path missing: {rel_path}")

    source_map_text = (REPO_ROOT / "docs" / "architecture" / "SOURCE_OF_TRUTH_MAP.md").read_text(
        encoding="utf-8"
    )
    entiremap_text = (REPO_ROOT / "docs" / "architecture" / "entiremap.md").read_text(encoding="utf-8")

    source_map_lower = source_map_text.lower()
    entiremap_lower = entiremap_text.lower()

    for anchor in BANNED_CURRENT_ANCHORS:
        anchor_lower = anchor.lower()
        if anchor_lower not in source_map_lower:
            errors.append(f"source of truth map missing stale-anchor note: {anchor}")
        if anchor_lower not in entiremap_lower:
            errors.append(f"entiremap missing stale-anchor note: {anchor}")

    for doc in CANONICAL_DOCS:
        text = doc.read_text(encoding="utf-8")
        for target in _extract_absolute_link_targets(text):
            if not target.exists():
                errors.append(
                    f"broken absolute link in {doc.relative_to(REPO_ROOT)} -> {target}"
                )

    return errors


def main() -> int:
    errors = validate_architecture_docs()
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1

    print("architecture docs verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
