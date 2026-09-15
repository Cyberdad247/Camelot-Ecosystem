# SPDX-License-Identifier: MIT

"""Comprehensive Smoke and Health Aggregation Test Suite (Tracks B4, B5, B6, A7).

Tests:
1. CloudTimeoutPolicy: bounded retries, exponential backoff, circuit breaker.
2. DeploymentContract: env var validation, URL syntax, privacy compliance.
3. CloudServiceRouter: unified health aggregation and local fallback handling.
4. CLI Smoke Suite: status, research-health, northstar-health, blueprint-health,
   precise-health, eldergod-health, and unified health rollup.
"""

import argparse
import asyncio
import os
import time
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from control_plane.cli.handlers import _handle_cloudbrain, _handle_health
from control_plane.infra.cloud_policy import CloudTimeoutPolicy
from control_plane.infra.cloud_services import (
    CloudServiceName,
    CloudServiceRequest,
    CloudServiceResult,
    CloudServiceRouter,
)
from control_plane.infra.deployment_contract import (
    DeploymentContractReport,
    validate_deployment_contract,
)


# ===========================================================================
# 1. Track B6: CloudTimeoutPolicy & Circuit Breaker Tests
# ===========================================================================

def test_cloud_timeout_policy_defaults():
    policy = CloudTimeoutPolicy()
    assert policy.connect_timeout_s == 5.0
    assert policy.health_read_timeout_s == 10.0
    assert policy.action_read_timeout_s == 60.0
    assert policy.max_retries == 2
    assert policy.circuit_breaker_threshold == 3

    h_to = policy.get_httpx_timeout(is_health=True)
    assert h_to.connect == 5.0
    assert h_to.read == 10.0

    a_to = policy.get_httpx_timeout(is_health=False)
    assert a_to.connect == 5.0
    assert a_to.read == 60.0


def test_cloud_timeout_policy_retryable_classification():
    policy = CloudTimeoutPolicy()

    # Retryable
    assert policy.is_retryable_exception(httpx.ConnectError("Connection refused"))
    assert policy.is_retryable_exception(httpx.ConnectTimeout("Connect timed out"))
    assert policy.is_retryable_exception(httpx.ReadTimeout("Read timed out"))

    resp_503 = httpx.Response(status_code=503, request=httpx.Request("GET", "http://test"))
    assert policy.is_retryable_exception(httpx.HTTPStatusError("503", request=resp_503.request, response=resp_503))

    resp_502 = httpx.Response(status_code=502, request=httpx.Request("GET", "http://test"))
    assert policy.is_retryable_exception(httpx.HTTPStatusError("502", request=resp_502.request, response=resp_502))

    # Non-retryable
    resp_404 = httpx.Response(status_code=404, request=httpx.Request("GET", "http://test"))
    assert not policy.is_retryable_exception(httpx.HTTPStatusError("404", request=resp_404.request, response=resp_404))

    resp_403 = httpx.Response(status_code=403, request=httpx.Request("GET", "http://test"))
    assert not policy.is_retryable_exception(httpx.HTTPStatusError("403", request=resp_403.request, response=resp_403))

    assert not policy.is_retryable_exception(ValueError("Invalid argument"))


def test_cloud_timeout_policy_retry_success():
    policy = CloudTimeoutPolicy(max_retries=2, backoff_factor=0.01)
    call_count = 0

    async def _failing_then_succeeding():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise httpx.ConnectError("Transient connection drop")
        return httpx.Response(200, json={"status": "ok"}, request=httpx.Request("GET", "http://test"))

    res = asyncio.run(policy.execute_http(_failing_then_succeeding, service_key="test_svc", is_health=True))
    assert res.status_code == 200
    assert call_count == 2
    assert not policy.is_circuit_open("test_svc")


def test_cloud_timeout_policy_circuit_breaker_trip():
    policy = CloudTimeoutPolicy(max_retries=0, circuit_breaker_threshold=2, circuit_breaker_recovery_s=5.0)

    async def _always_failing():
        raise httpx.ConnectError("Down")

    # Call 1: failure 1
    with pytest.raises(httpx.ConnectError):
        asyncio.run(policy.execute_http(_always_failing, service_key="broken_svc", is_health=True))
    assert not policy.is_circuit_open("broken_svc")

    # Call 2: failure 2 -> trips circuit breaker
    with pytest.raises(httpx.ConnectError):
        asyncio.run(policy.execute_http(_always_failing, service_key="broken_svc", is_health=True))
    assert policy.is_circuit_open("broken_svc")

    # Call 3: should fast-fail without invoking function
    invoked = False

    async def _probe():
        nonlocal invoked
        invoked = True
        return httpx.Response(200, request=httpx.Request("GET", "http://test"))

    with pytest.raises(RuntimeError, match="Circuit breaker OPEN"):
        asyncio.run(policy.execute_http(_probe, service_key="broken_svc", is_health=True))
    assert not invoked

    # Diagnostic summary
    summary = policy.get_circuit_summary()
    assert "broken_svc" in summary
    assert summary["broken_svc"]["circuit_open"] is True
    assert summary["broken_svc"]["consecutive_failures"] == 2


# ===========================================================================
# 2. Track B4: Remote Deployment Contract Tests
# ===========================================================================

def test_deployment_contract_validation_defaults():
    report = validate_deployment_contract()
    assert isinstance(report, DeploymentContractReport)
    assert report.status in {"PASS", "WARN"}
    assert report.local_fallback_available is True
    assert len(report.endpoints) > 10
    assert report.invalid_urls == []


def test_deployment_contract_invalid_url_rejection(monkeypatch):
    monkeypatch.setenv("CAMELOT_RESEARCH_AGENCY_URL", "not-a-valid-url")
    report = validate_deployment_contract()
    assert report.status == "FAIL"
    assert "CAMELOT_RESEARCH_AGENCY_URL" in report.invalid_urls
    endpoint = report.endpoints["CAMELOT_RESEARCH_AGENCY_URL"]
    assert endpoint.is_valid_url is False
    assert "Malformed URL format" in (endpoint.error or "")


def test_deployment_contract_appwrite_cohesion(monkeypatch):
    monkeypatch.setenv("APPWRITE_ENDPOINT_PUBLIC", "https://appwrite.camelot.local/v1")
    monkeypatch.delenv("APPWRITE_PROJECT", raising=False)
    monkeypatch.delenv("APPWRITE_API_KEY", raising=False)

    report = validate_deployment_contract()
    assert "APPWRITE_PROJECT" in report.missing_required
    assert "APPWRITE_API_KEY" in report.missing_required


def test_deployment_contract_privacy_secrets_masked(monkeypatch):
    secret_key = "super-secret-key-12345"
    monkeypatch.setenv("APPWRITE_API_KEY", secret_key)
    report = validate_deployment_contract()
    endpoint = report.endpoints["APPWRITE_API_KEY"]
    assert secret_key not in endpoint.value_masked
    assert f"<CONFIGURED: {len(secret_key)} chars>" == endpoint.value_masked


# ===========================================================================
# 3. Track B5: Health Aggregation Tests
# ===========================================================================

def test_health_rollup_aggregation():
    router = CloudServiceRouter()
    result = asyncio.run(router.invoke(CloudServiceRequest(
        service=CloudServiceName.HEALTH_ROLLUP,
        payload={"probe_remote": False},
    )))

    assert isinstance(result, CloudServiceResult)
    assert result.service == CloudServiceName.HEALTH_ROLLUP
    assert result.success is True
    assert result.source == "rollup"

    data = result.result
    assert data["overall_status"] in {"HEALTHY", "DEGRADED"}
    assert data["score_pct"] > 0
    assert "subsystems" in data
    assert "cloudbrain" in data["subsystems"]
    assert "research" in data["subsystems"]
    assert "northstar" in data["subsystems"]
    assert "blueprint" in data["subsystems"]
    assert "precise_mode" in data["subsystems"]
    assert "eldergod" in data["subsystems"]
    assert "notebooklm" in data["subsystems"]
    assert "deployment_contract" in data


def test_health_rollup_core_failure_degradation():
    router = CloudServiceRouter()

    # Mock one core service failing
    async def _mock_failed_research():
        return CloudServiceResult(
            service=CloudServiceName.RESEARCH_AGENCY_HEALTH,
            success=False,
            error="Connection refused",
            source="remote",
        )

    router._research_agency_health = _mock_failed_research  # type: ignore

    result = asyncio.run(router._health_rollup())
    assert result.result["overall_status"] in {"DEGRADED", "UNAVAILABLE"}
    assert result.result["subsystems"]["research"]["healthy"] is False


# ===========================================================================
# 4. Track A7: CLI Health Smoke Test Suite
# ===========================================================================

def test_cli_health_command_json_mode(capsys):
    args = argparse.Namespace(
        command="health",
        json=True,
        probe_remote=False,
        verbose=False,
        profile="default",
    )
    code = _handle_health(args, None, None, ["health", "--json"])
    assert code == 0
    captured = capsys.readouterr()
    assert '"service": "health_rollup"' in captured.out
    assert '"overall_status":' in captured.out


def test_cli_health_command_terminal_mode(capsys):
    args = argparse.Namespace(
        command="health",
        json=False,
        probe_remote=False,
        verbose=True,
        profile="default",
    )
    code = _handle_health(args, None, None, ["health", "-v"])
    assert code == 0
    captured = capsys.readouterr()
    assert "CAMELOT-OS UNIFIED HEALTH ROLLUP" in captured.out
    assert "Subsystem" in captured.out
    assert "Deployment Contract:" in captured.out
    assert "Circuit Breaker Status:" in captured.out


def test_cli_cloudbrain_health_subcommand(capsys):
    args = argparse.Namespace(
        command="cloudbrain",
        cloudbrain_command="health",
        json=True,
        probe_remote=False,
        verbose=False,
        profile="default",
    )
    code = _handle_cloudbrain(args, None, None, ["cloudbrain", "health", "--json"])
    assert code == 0
    captured = capsys.readouterr()
    assert '"overall_status":' in captured.out


@pytest.mark.parametrize("subcmd,expected_service", [
    ("status", "cloudbrain_status"),
    ("research-health", "research_agency_health"),
    ("northstar-health", "northstar_health"),
    ("blueprint-health", "development_blueprint_health"),
    ("precise-health", "precise_mode_health"),
    ("eldergod-health", "eldergod_forge_health"),
])
def test_cli_cloudbrain_individual_health_probes_smoke(subcmd, expected_service, capsys):
    args = argparse.Namespace(
        command="cloudbrain",
        cloudbrain_command=subcmd,
        json=True,
        profile="default",
    )
    code = _handle_cloudbrain(args, None, None, ["cloudbrain", subcmd, "--json"])
    assert code == 0
    captured = capsys.readouterr()
    assert expected_service in captured.out or "status" in captured.out
