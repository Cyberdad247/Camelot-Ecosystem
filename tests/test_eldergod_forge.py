import sys
from pathlib import Path

# Add 01_KERNEL to sys.path so its modules can be imported
_ROOT = Path("01_KERNEL").resolve()
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agora.cloud_orchestrator_shim.modal_services import (  # noqa: E402
    ElderGodForgeRequest,
    ResearchComputeTier,
    eldergod_forge,
    eldergod_forge_health_endpoint,
)


def test_eldergod_forge_health_endpoint():
    """Test the elderGod forge health endpoint returns healthy status."""
    health = eldergod_forge_health_endpoint.local()
    assert health["service"] == "eldergod_forge"
    assert health["status"] == "healthy"
    assert "hybrid" in health["compute_tiers"]
    assert health["production_ready"]["omega_directive_aligned"] is True


def test_eldergod_forge_endpoint():
    """Test the elderGod forge function with a standard payload."""
    request = ElderGodForgeRequest(
        objective="Discover true meaning of 42",
        compute_tier=ResearchComputeTier.APEX,
        multiverse_enabled=True,
        omega_directive="absolute_singularity",
    )

    response = eldergod_forge.local(request.model_dump())
    assert response["service"] == "eldergod_forge"
    assert response["objective"] == "Discover true meaning of 42"
    assert response["compute_tier"] == ResearchComputeTier.APEX.value
    assert response["omega_directive"] == "absolute_singularity"
    assert "omega_singularity_matrix" in response["forged_artifacts"]
    assert response["dimensional_nodes"]["L8_MULTIVERSE"] == "Active"
    assert response["dimensional_nodes"]["L9_OVERSOUL"] == "Ascended"
    assert response["production_ready"]["quantum_state_lock"] is True


def test_eldergod_forge_multiverse_disabled():
    """Test the elderGod forge function with multiverse disabled."""
    request = ElderGodForgeRequest(
        objective="Discover true meaning of 42",
        compute_tier=ResearchComputeTier.APEX,
        multiverse_enabled=False,
        omega_directive="absolute_singularity",
    )

    response = eldergod_forge.local(request.model_dump())
    assert response["service"] == "eldergod_forge"
    assert response["dimensional_nodes"]["L8_MULTIVERSE"] == "Active"
    assert response["dimensional_nodes"]["L9_OVERSOUL"] == "Dormant"
