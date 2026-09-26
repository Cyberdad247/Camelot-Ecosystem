from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import control_plane.dispatch.bifrost_integration as integration_module
from control_plane.dispatch.bifrost_integration import BifrostIntegration, OptimizationProfile


def test_optimization_ledger_describes_plans_instead_of_applied_changes():
    integration = BifrostIntegration()
    integration.optimization_profile = OptimizationProfile(
        enable_multithreading=True,
        thread_pool_size=2,
        enable_avx=True,
        enable_sse=True,
        enable_gpu_acceleration=True,
        gpu_type="test",
        gpu_memory_pool_mb=128,
        enable_redis=True,
        enable_qdrant=True,
        enable_pytorch=True,
        worker_processes=2,
        async_workers=4,
    )

    asyncio.run(integration._apply_optimizations("pill-fixture"))

    assert integration.optimization_ledger
    assert all("Enabled" not in entry for entry in integration.optimization_ledger)
    assert all("optimized" not in entry for entry in integration.optimization_ledger)
    assert any("planned" in entry for entry in integration.optimization_ledger)


def test_integration_writes_runtime_artifacts_only_under_the_governed_state_directory(monkeypatch, tmp_path):
    monkeypatch.setattr(integration_module, "BIFROST_RUNTIME_DIR", tmp_path)
    integration = BifrostIntegration()

    result = asyncio.run(integration._configure_bifrost(OptimizationProfile()))

    assert result is True
    assert (tmp_path / "config.json").is_file()


def test_noop_forge_steps_return_a_partial_result(monkeypatch):
    integration = BifrostIntegration()
    integration._forge_main_py = AsyncMock(return_value=True)
    integration._forge_bifrost_py = AsyncMock(return_value=True)
    integration._forge_knight_brain = AsyncMock(return_value=True)
    integration._forge_memory_pyramid = AsyncMock(return_value=True)
    integration._forge_distance_travel = AsyncMock(return_value=True)
    integration._forge_startup_scripts = AsyncMock(return_value=True)

    result = asyncio.run(integration._forge_camelot_os(OptimizationProfile()))

    assert result is False
    assert any("partial" in entry for entry in integration.optimization_ledger)


def test_integration_does_not_report_success_when_configuration_fails():
    integration = BifrostIntegration()
    integration.analyzer.analyze = AsyncMock(return_value=object())
    integration._generate_optimization_profile = AsyncMock(
        return_value=OptimizationProfile()
    )
    integration._apply_optimizations = AsyncMock(return_value=True)
    integration._configure_bifrost = AsyncMock(return_value=False)
    integration._forge_camelot_os = AsyncMock(return_value=True)
    integration._log_integration = AsyncMock(return_value=None)

    result = asyncio.run(integration.integrate("pill-fixture"))

    assert result is False
    assert integration.is_integrated is False
