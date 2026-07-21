from __future__ import annotations

import json
from pathlib import Path

from control_plane.notebooklm_graphify_bridge import (
    build_graphify_command,
    materialize_graphify_corpus,
    notebooklm_state_to_graph_context,
)


def test_notebooklm_state_to_graph_context_handles_nested_notebooks() -> None:
    payload = {
        "notebooks": [
            {
                "id": "nb-1",
                "title": "Notebook One",
                "description": "First notebook",
                "sources": [
                    {
                        "id": "src-1",
                        "title": "Source One",
                        "type": "url",
                        "url": "https://example.com",
                        "text": "Hello world",
                    }
                ],
            }
        ]
    }

    context = notebooklm_state_to_graph_context(payload)

    assert context["notebook_count"] == 1
    assert context["source_count"] == 1
    assert context["notebooks"][0]["title"] == "Notebook One"
    assert context["notebooks"][0]["sources"][0]["uri"] == "https://example.com"


def test_materialize_graphify_corpus_writes_manifest_and_markdown(tmp_path: Path) -> None:
    storage_state = tmp_path / "storage_state.json"
    storage_state.write_text(
        json.dumps(
            {
                "notebooks": [
                    {
                        "id": "nb-1",
                        "title": "Notebook One",
                        "sources": [
                            {
                                "id": "src-1",
                                "title": "Source One",
                                "type": "text",
                                "content": "Body text",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    corpus_root = materialize_graphify_corpus(storage_state_path=storage_state, corpus_root=tmp_path / "corpus")

    manifest = json.loads((corpus_root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["notebook_count"] == 1
    assert manifest["source_count"] == 1
    assert (corpus_root / "notebooks").exists()
    assert (corpus_root / "sources").exists()
    assert any(path.suffix == ".md" for path in (corpus_root / "notebooks").iterdir())


def test_build_graphify_command_defaults_to_safe_extraction() -> None:
    command = build_graphify_command(Path("corpus"))
    assert command[:3] == ["graphify", "extract", "corpus"]
    assert "--no-viz" in command
    assert "--force" in command
