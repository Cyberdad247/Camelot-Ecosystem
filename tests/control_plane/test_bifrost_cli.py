from __future__ import annotations

import io
import json
from argparse import Namespace
from unittest.mock import patch

from control_plane.cli.bifrost_cmd import (
    build_route_preview,
    handle_bifrost,
    validate_routing_config,
)
from control_plane.cli.contracts_cmd import validate_contracts
from control_plane.cli.parser import _build_parser

DIALECT = "https://json-schema.org/draft/2020-12/schema"


def test_parser_recognizes_bifrost_route_status_and_validate():
    parser = _build_parser()

    route_args = parser.parse_args(["bifrost", "route", "use", "bifrost_gateway", "--json"])
    assert route_args.command == "bifrost"
    assert route_args.bifrost_command == "route"
    assert route_args.intent == ["use", "bifrost_gateway"]
    assert route_args.json is True

    status_args = parser.parse_args(["bifrost", "status", "--json"])
    assert status_args.bifrost_command == "status"
    assert status_args.probe is False

    validate_args = parser.parse_args(["bifrost", "validate", "--json"])
    assert validate_args.bifrost_command == "validate"
    assert validate_args.path is None
    assert validate_args.registry is None


def test_parser_recognizes_contracts_validate():
    args = _build_parser().parse_args(["contracts", "validate", "--json"])
    assert args.command == "contracts"
    assert args.contracts_command == "validate"
    assert args.path is None
    assert args.json is True


def test_route_preview_selects_bifrost_and_never_executes():
    result = build_route_preview("route this through bifrost_gateway")

    assert result["read_only"] is True
    assert result["lane"] == "maxim_bifrost_gateway"
    assert result["provider_chain"][0] == "maxim_bifrost_gateway"
    assert result["bifrost_first"] is True
    assert result["execution"] == "not_invoked"


def test_route_preview_redacts_secret_values():
    result = build_route_preview("send api_key=super-secret-value to bifrost")

    serialized = json.dumps(result)
    assert "super-secret-value" not in serialized
    assert "api_key=[REDACTED]" in result["intent_redacted"]


def test_route_preview_redacts_provider_prefixed_credentials():
    result = build_route_preview('OPENAI_API_KEY=super-secret-value BIFROST_MESH_TOKEN=another-secret')

    serialized = json.dumps(result)
    assert "super-secret-value" not in serialized
    assert "another-secret" not in serialized
    assert "OPENAI_API_KEY=[REDACTED]" in result["intent_redacted"]
    assert "BIFROST_MESH_TOKEN=[REDACTED]" in result["intent_redacted"]


def test_route_preview_reports_a_local_policy_violation():
    result = build_route_preview("run local model on vllm")

    assert result["read_only"] is True
    assert result["bifrost_first"] is False
    assert result["local_policy"]["status"] == "REVIEW"
    assert result["local_policy"]["reasons"]


def test_validate_routing_config_accepts_small_ollama_models(tmp_path):
    manifest = tmp_path / "models.json"
    manifest.write_text(
        json.dumps(
            {
                "models": {
                    "small": {"backend": "ollama", "tag": "qwen3:4b"},
                    "code": {"backend": "ollama", "tag": "qwen2.5-coder:3b"},
                }
            }
        ),
        encoding="utf-8",
    )

    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps(
            {
                "bifrost_bridge": {
                    "ws_endpoint": "ws://100.110.180.18:4433/ws",
                    "mTLS": True,
                    "fallback_proxy": "http://127.0.0.1:11434",
                },
                "knight_pill_allocations": [
                    {
                        "knight_id": "TEST_KNIGHT",
                        "bifrost_route": "/bifrost/knights/test_knight",
                        "assigned_tiny_llm": "ollama/qwen3:1.5b",
                        "worker_ram_mb": 256,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = validate_routing_config(manifest, registry_path=registry)

    assert result["read_only"] is True
    assert result["status"] == "PASS"
    assert result["local_policy"]["status"] == "PASS"
    assert result["bifrost_registry"]["status"] == "PASS"


def test_hub_scope_must_match_a_registry_route(tmp_path):
    manifest = tmp_path / "models.json"
    manifest.write_text(
        json.dumps(
            {
                "models": {
                    "hub": {
                        "backend": "vllm",
                        "tag": "large-70b",
                        "inference_scope": "bifrost_hub",
                        "bifrost_route": "/bifrost/models/rogue",
                        "bifrost_endpoint": "http://127.0.0.1:8000/v1",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps(
            {
                "bifrost_bridge": {
                    "ws_endpoint": "ws://100.110.180.18:4433/ws",
                    "mTLS": True,
                    "fallback_proxy": "http://127.0.0.1:11434",
                },
                "knight_pill_allocations": [
                    {
                        "knight_id": "HUB",
                        "inference_scope": "bifrost_hub",
                        "bifrost_route": "/bifrost/models/canonical",
                        "endpoint": "http://127.0.0.1:8000/v1",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = validate_routing_config(manifest, registry_path=registry)

    assert result["status"] == "FAIL"
    assert result["local_policy"]["violations"]


def test_validate_routing_config_reports_large_local_model(tmp_path):
    manifest = tmp_path / "models.json"
    manifest.write_text(
        json.dumps(
            {
                "models": {
                    "large": {"backend": "vllm", "tag": "mistral-small3.1-24b"},
                }
            }
        ),
        encoding="utf-8",
    )

    result = validate_routing_config(manifest, registry_path=tmp_path / "missing-registry.json")

    assert result["status"] == "FAIL"
    assert result["local_policy"]["status"] == "FAIL"
    assert result["local_policy"]["violations"][0]["model"] == "large"


def test_validate_routing_config_accepts_explicit_bifrost_hub_models(tmp_path):
    manifest = tmp_path / "models.json"
    manifest.write_text(
        json.dumps(
            {
                "models": {
                    "hub-engine": {
                        "backend": "vllm",
                        "tag": "large-70b",
                        "inference_scope": "bifrost_hub",
                        "bifrost_route": "/bifrost/models/hub-engine",
                        "bifrost_endpoint": "http://127.0.0.1:8000/v1",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps(
            {
                "bifrost_bridge": {
                    "ws_endpoint": "ws://100.110.180.18:4433/ws",
                    "mTLS": True,
                    "fallback_proxy": "http://127.0.0.1:11434",
                },
                "knight_pill_allocations": [
                    {
                        "knight_id": "HUB_ENGINE",
                        "inference_scope": "bifrost_hub",
                        "bifrost_route": "/bifrost/models/hub-engine",
                        "assigned_tiny_llm": "vllm/large-70b",
                        "endpoint": "http://127.0.0.1:8000/v1",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = validate_routing_config(manifest, registry_path=registry)

    assert result["status"] == "PASS"
    assert result["local_policy"]["status"] == "PASS"
    assert result["bifrost_registry"]["status"] == "PASS"


def test_validate_contracts_accepts_a_valid_catalog(tmp_path):
    schema_path = tmp_path / "thing.schema.json"
    schema_path.write_text(
        json.dumps(
            {
                "$schema": DIALECT,
                "$id": "https://camelot-os/schemas/thing.schema.json",
                "type": "object",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "index.json").write_text(
        json.dumps(
            {
                "$schema": DIALECT,
                "version": "1.0",
                "json_schema_dialect": DIALECT,
                "schemas": [
                    {
                        "file": schema_path.name,
                        "$id": "https://camelot-os/schemas/thing.schema.json",
                        "schema_version": "1.0",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = validate_contracts(tmp_path)

    assert result["read_only"] is True
    assert result["status"] == "PASS"
    assert result["schema_count"] == 1
    assert result["errors"] == []


def test_validate_contracts_reports_invalid_schema(tmp_path):
    schema_path = tmp_path / "bad.schema.json"
    schema_path.write_text(json.dumps({"$schema": DIALECT, "type": 42}), encoding="utf-8")

    result = validate_contracts(tmp_path)

    assert result["status"] == "FAIL"
    assert result["errors"]
    assert "bad.schema.json" in result["errors"][0]


def test_handler_emits_json_without_managers():
    args = Namespace(
        command="bifrost",
        bifrost_command="route",
        intent=["bifrost_gateway"],
        json=True,
    )

    captured = io.StringIO()
    with patch("sys.stdout", captured):
        exit_code = handle_bifrost(args, None, None, ["bifrost", "route", "bifrost_gateway"])

    assert exit_code == 0
    assert json.loads(captured.getvalue())["read_only"] is True
