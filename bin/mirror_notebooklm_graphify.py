from __future__ import annotations

import argparse
import json
from pathlib import Path

from control_plane.infra.notebooklm_graphify_bridge import mirror_notebooklm_to_graphify
from control_plane.infra.notebooklm_graphify_manifest import write_manifest


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mirror NotebookLM storage state into a Graphify corpus.")
    parser.add_argument(
        "--storage-state",
        type=Path,
        default=Path.home() / ".notebooklm" / "storage_state.json",
        help="Path to NotebookLM storage_state.json",
    )
    parser.add_argument(
        "--corpus-root",
        type=Path,
        default=Path("03_VAULT/runtime_state/notebooklm_graphify"),
        help="Where to materialize the mirrored corpus",
    )
    parser.add_argument(
        "--run-graphify",
        action="store_true",
        help="Execute graphify extract after writing the corpus",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    result = mirror_notebooklm_to_graphify(
        storage_state_path=args.storage_state,
        corpus_root=args.corpus_root,
        dry_run=not args.run_graphify,
    )
    manifest_path = write_manifest(
        args.corpus_root / "camelot-manifest.json",
        args.storage_state,
        notebook_count=0,
        source_count=0,
    )
    result["camelot_manifest"] = str(manifest_path)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
