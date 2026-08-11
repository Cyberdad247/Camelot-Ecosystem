from __future__ import annotations

from control_plane.runes.critical_thinking import Evidence, universal_knight_protocol


def test_universal_knight_protocol_returns_qualified_frame() -> None:
    frame = universal_knight_protocol(
        "Evaluate the request",
        evidence=[Evidence(claim="Repo contains control_plane", source="local repo", confidence=0.9)],
        constraints=["Do not mutate production state without approval"],
    )

    assert frame.objective == "Evaluate the request"
    assert frame.facts
    assert frame.decisions
    assert frame.next_actions

