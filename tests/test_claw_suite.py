from control_plane.core.knight_agent import load_roster
from control_plane.dispatch.switchboard import TERMINAL_REGISTRY

from control_plane.runes import runic_router

CLAW_KNIGHTS = {
    "sir_openclaw",
    "sir_rustclaw",
    "sir_hermes",
    "lady_nanobot",
    "sir_zeroclaw",
}


def test_claw_suite_manifest_is_guarded_and_shopify_lanes_are_split():
    from control_plane.dispatch.claw_suite import build_claw_suite_manifest, is_forbidden_openclaw_intent

    manifest = build_claw_suite_manifest()

    assert set(manifest["knights"]) == CLAW_KNIGHTS
    assert manifest["ukg_state"]["state"] == "FORGED_GUARDED"
    assert manifest["safety"]["evasion_allowed"] is False
    assert is_forbidden_openclaw_intent("bypass Cloudflare and Datadome") is True
    assert is_forbidden_openclaw_intent("collect trends from approved public RSS feeds") is False

    shopify = manifest["shopify_lanes"]
    assert shopify["admin"]["purpose"] == "product_and_media_publication"
    assert "write_products" in shopify["admin"]["required_scopes"]
    assert shopify["storefront"]["purpose"] == "cart_and_checkout"
    assert "cartCreate" in shopify["storefront"]["graphql_entrypoints"]
    assert shopify["secret_policy"] == "presence_flags_only_no_values"


def test_claw_knights_are_registered_in_roster_and_switchboard():
    roster = load_roster()

    for knight_id in CLAW_KNIGHTS:
        assert knight_id in roster
        assert knight_id in TERMINAL_REGISTRY

    assert roster["sir_zeroclaw"].requires_air_gap is True
    assert "shopify_admin" in TERMINAL_REGISTRY["sir_hermes"].capability
    assert "compliant_trend_research" in TERMINAL_REGISTRY["sir_openclaw"].capability
    assert "edge_component_agents" in TERMINAL_REGISTRY["lady_nanobot"].capability


def test_claw_rune_routes_manifest_without_unsafe_execution(tmp_path, monkeypatch):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")

    result = runic_router.detect_and_route("//CLAW shopify headless forger")

    assert result is not None
    assert result.rune == "//CLAW"
    assert result.knight == "sir_boris"
    assert result.mode == "ORACLE"
    assert result.queued is True
    assert result.metadata["action"] == "claw_suite_manifest"
    assert result.metadata["execution"]["auto_execute"] is False
    assert "anti_bot_evasion" in result.metadata["safety"]["blocked_capabilities"]
