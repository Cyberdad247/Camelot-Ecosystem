# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Unit and Integration Tests for Camelot Sovereign Pipeline CLI (Phase 10).
==========================================================================
Verifies CLI command parsing, zero-trust gate enforcement, 6-stage lifecycle execution,
and structured output streaming.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest

from control_plane.cli.parser import _build_parser
from control_plane.cli.pipeline_cmd import (
    handle_pipeline,
    handle_pipeline_run,
    handle_pipeline_status,
    handle_pipeline_verify,
)
from control_plane.pipeline.sovereign_pipeline import PipelineStatus


@pytest.fixture
def cli_parser():
    return _build_parser()


def test_cli_parser_pipeline_status_args(cli_parser):
    """Verifies that 'pipeline status' parses correctly."""
    args = cli_parser.parse_args(["pipeline", "status", "--json"])
    assert args.command == "pipeline"
    assert args.pipeline_command == "status"
    assert args.json is True


def test_cli_parser_pipeline_verify_args(cli_parser):
    """Verifies that 'pipeline verify' parses correctly."""
    args = cli_parser.parse_args(["pipeline", "verify", "--json"])
    assert args.command == "pipeline"
    assert args.pipeline_command == "verify"
    assert args.json is True


def test_cli_parser_pipeline_run_args(cli_parser):
    """Verifies that 'pipeline run' parses with all options."""
    args = cli_parser.parse_args([
        "pipeline", "run",
        "--tenant", "tenant_custom",
        "--client-key", "key_123",
        "--intent", "run regression suite",
        "--effect-class", "workspace.test",
        "--risk-tier", "T1",
        "--bypass-approvals",
        "--auto-ratify",
        "--json",
    ])
    assert args.command == "pipeline"
    assert args.pipeline_command == "run"
    assert args.tenant == "tenant_custom"
    assert args.client_key == "key_123"
    assert args.intent == "run regression suite"
    assert args.effect_class == "workspace.test"
    assert args.risk_tier == "T1"
    assert args.bypass_approvals is True
    assert args.auto_ratify is True
    assert args.json is True


def test_pipeline_status_text_output():
    """Verifies that 'pipeline status' outputs cleanly in human-readable mode."""
    args = argparse.Namespace(pipeline_command="status", json=False)
    captured = io.StringIO()
    with patch("sys.stdout", captured):
        exit_code = handle_pipeline_status(args, json_mode=False)

    assert exit_code == 0
    text = captured.getvalue()
    assert "Sovereign Pipeline Control Status" in text
    assert "Zero-Docker Footprint" in text
    assert "Hardware Scarcity Role" in text


def test_pipeline_status_json_output():
    """Verifies that 'pipeline status --json' produces valid schema-compliant JSON."""
    args = argparse.Namespace(pipeline_command="status", json=True)
    captured = io.StringIO()
    with patch("sys.stdout", captured):
        exit_code = handle_pipeline_status(args, json_mode=True)

    assert exit_code == 0
    data = json.loads(captured.getvalue())
    assert data["status"] in ("HEALTHY", "DEGRADED")
    assert "zero_docker_compliant" in data["governance"]
    assert "authority_vector" in data["governance"]
    assert "hardware_scarcity" in data
    assert data["hardware_scarcity"]["hard_cap_mb"] > 0


def test_pipeline_verify_self_test_passes():
    """Verifies that 'pipeline verify' executes the 6-stage lifecycle self-test and passes."""
    args = argparse.Namespace(pipeline_command="verify", json=True)
    captured = io.StringIO()
    with patch("sys.stdout", captured):
        exit_code = handle_pipeline_verify(args, json_mode=True)

    assert exit_code == 0
    data = json.loads(captured.getvalue())
    assert data["status"] == "PASS"
    assert data["stages"]["stage_1_ingress_idempotency"] is True
    assert data["stages"]["stage_2_security_gate"] is True
    assert data["stages"]["stage_3_bounded_execution"] is True
    assert data["stages"]["stage_4_sir_gideon_audit"] is True
    assert data["stages"]["stage_5_arthur_merkle_commit"] is True
    assert data["stages"]["stage_6_telemetry_dispatch"] is True


def test_pipeline_run_default_success():
    """Verifies that 'pipeline run' with default test intent completes all 6 stages."""
    import uuid
    k = uuid.uuid4().hex[:8]
    args = argparse.Namespace(
        pipeline_command="run",
        manifest=None,
        tenant="tenant_default",
        client_key=f"test_client_key_{k}",
        intent="Run automated test suite",
        effect_class="workspace.test",
        risk_tier="T1",
        bypass_approvals=False,
        auto_ratify=False,
        json=True,
    )
    captured = io.StringIO()
    with patch("sys.stdout", captured):
        exit_code = handle_pipeline_run(args, json_mode=True)

    assert exit_code == 0
    data = json.loads(captured.getvalue())
    assert data["status"] == "SUCCESS"
    assert data["current_stage"] == "TELEMETRY_DISPATCH"
    assert data["gideon_verdict"] == "pass"
    assert data["receipt_id"] is not None
    assert data["receipt_ref"].startswith("receipt://vfs/chain/rec_")


def test_pipeline_run_blocked_mutation_without_approval():
    """Verifies that a material write without operator approval is blocked at Stage 2."""
    import uuid
    k = uuid.uuid4().hex[:8]
    args = argparse.Namespace(
        pipeline_command="run",
        manifest=None,
        tenant="tenant_default",
        client_key=f"test_client_key_blocked_{k}",
        intent="write patch to kernel code",
        effect_class="workspace.patch",
        risk_tier="T2",
        bypass_approvals=False,
        auto_ratify=False,
        json=True,
    )
    captured = io.StringIO()
    with patch("sys.stdout", captured):
        exit_code = handle_pipeline_run(args, json_mode=True)

    assert exit_code == 1
    data = json.loads(captured.getvalue())
    assert data["status"] == "BLOCKED"
    assert data["current_stage"] == "SECURITY_GATE"
    assert data["security_decision"]["decision"] == "require_approval"
    assert "APPROVAL REQUIRED" in data["error_message"]


def test_pipeline_run_approved_mutation_success():
    """Verifies that a material mutation with operator approval passes all gates."""
    import uuid
    k = uuid.uuid4().hex[:8]
    args = argparse.Namespace(
        pipeline_command="run",
        manifest=None,
        tenant="tenant_default",
        client_key=f"test_client_key_approved_{k}",
        intent="write patch to kernel code",
        effect_class="workspace.patch",
        risk_tier="T2",
        bypass_approvals=True,
        auto_ratify=False,
        json=True,
    )
    captured = io.StringIO()
    with patch("sys.stdout", captured):
        exit_code = handle_pipeline_run(args, json_mode=True)

    assert exit_code == 0
    data = json.loads(captured.getvalue())
    assert data["status"] == "SUCCESS"
    assert data["current_stage"] == "TELEMETRY_DISPATCH"
    assert data["receipt_id"] is not None


def test_pipeline_run_high_risk_auto_ratified():
    """Verifies that high-risk tier T3 tasks receive an Arthur Resolution when auto-ratified."""
    import uuid
    k = uuid.uuid4().hex[:8]
    args = argparse.Namespace(
        pipeline_command="run",
        manifest=None,
        tenant="tenant_default",
        client_key=f"test_client_key_t3_{k}",
        intent="promote worktree merge",
        effect_class="promote.worktree.merge",
        risk_tier="T3",
        bypass_approvals=True,
        auto_ratify=True,
        json=True,
    )
    captured = io.StringIO()
    with patch("sys.stdout", captured):
        exit_code = handle_pipeline_run(args, json_mode=True)

    assert exit_code == 0
    data = json.loads(captured.getvalue())
    assert data["status"] == "SUCCESS"
    assert data["arthur_resolution_id"] is not None


def test_master_pipeline_dispatch_routing():
    """Verifies that handle_pipeline routes correctly to subcommands."""
    args_status = argparse.Namespace(pipeline_command="status", json=True)
    assert handle_pipeline(args_status, None, None, ["status", "--json"]) == 0

    args_verify = argparse.Namespace(pipeline_command="verify", json=True)
    assert handle_pipeline(args_verify, None, None, ["verify", "--json"]) == 0

    args_invalid = argparse.Namespace(pipeline_command="unknown_subcommand", json=True)
    assert handle_pipeline(args_invalid, None, None, ["unknown_subcommand"]) == 1
