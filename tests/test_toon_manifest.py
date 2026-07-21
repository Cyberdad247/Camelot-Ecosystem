from __future__ import annotations

import json

from control_plane.toon_manifest import (
    build_scarcity_core_manifest,
    compile_manifest_documents,
    encode_toon_document,
    parse_toon_config,
)


def test_scarcity_core_manifest_uses_folded_arrays():
    toon = encode_toon_document(build_scarcity_core_manifest(), title="camelot.toon")

    assert "skills: items[2]{constraints,entrypoint,id,name}:" in toon
    assert "agents: items[3]{environment,limit_ms,name,role}:" in toon
    assert "tasks: items[6]{deps,id,status}:" in toon
    assert '{"mem":' not in toon
    assert "{mem:67108864|max_threads:2},/bin/sve-compiler,skill:sve-compilation" in toon


def test_compile_manifest_documents_redacts_sensitive_values():
    toon = compile_manifest_documents(
        {
            "config.json": {
                "api_key": "actual-value",
                "nested": {"token": "secret-token"},
                "agents": [
                    {"name": "Sir Codex", "role": "builder"},
                    {"name": "Sir Sentinel", "role": "guard"},
                ],
            }
        }
    )

    assert "actual-value" not in toon
    assert "secret-token" not in toon
    assert "api_key: true" in toon
    assert "token: true" in toon
    assert "agents: items[2]{name,role}:" in toon


def test_parse_toon_config_skips_folded_array_headers():
    raw = """# header
MemoryManager:
  physical_limit_mb: 3072
agents: items[1]{name,role}:
  Sir Codex,builder
"""

    pairs = parse_toon_config(raw)

    assert [pair.key for pair in pairs] == ["MemoryManager", "physical_limit_mb"]
    assert pairs[1].value == "3072"


def test_compiled_manifest_is_smaller_than_pretty_json_for_tabular_payload():
    document = {"camelot": build_scarcity_core_manifest()}
    pretty_json = json.dumps(document, indent=2)
    toon = compile_manifest_documents(document)

    assert len(toon.encode("utf-8")) < len(pretty_json.encode("utf-8"))
