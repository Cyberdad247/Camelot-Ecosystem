# SPDX-License-Identifier: MIT
"""Every mesh-bridge endpoint asserted through nginx must have a matching route.

WHY THIS TEST EXISTS

Four endpoints were post-conditions of the hub's contract while having no route through
nginx: two were answered by the `location /` catch-all (the Hermes dashboard's
`302 /login`) and one was swallowed by the Bifrost gateway's prefix match (`404`). The
checks were correct; the routes simply did not exist, so a check that looked like it
verified the client contract was really asserting someone else's login redirect.

The failure mode this guards against is the *next* one: adding an endpoint check to the
bootstrap, or a path to the client env, without adding the route — which yields a
permanently failing post-condition, or a check that passes for the wrong reason. So this
is a **cross-check between independent files** (the audit's endpoints, the client's
declared paths, the bridge's served paths, the snippet's locations) rather than an
assertion about any one of them. A test that only read the snippet could not notice a new
endpoint at all — which is exactly how this drifted to begin with.

The snippet is versioned because the hub's own server block is written by the Hermes
installer and exists nowhere in this repository; hand-editing it produces an asset a
re-install silently reverts.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SNIPPET = REPO_ROOT / "infra" / "nginx" / "camelot-mesh-bridge.conf"
INSTALLER = REPO_ROOT / "scripts" / "ops" / "install-mesh-bridge-routes.sh"
AUDIT = REPO_ROOT / "scripts" / "vps_hub_bootstrap.sh"
LAB_DEPLOY = REPO_ROOT / "scripts" / "deploy_luxora_nexus_lab.sh"
BRIDGE = REPO_ROOT / "control_plane" / "dispatch" / "vps_mobile_mesh_bridge.py"

BRIDGE_PORT = "8095"

# Paths the snippet must route: the client contract that the bridge itself serves.
EXPECTED_ROUTED = {
    "/mesh/status",
    "/bifrost/knights",
    "/hermes/telemetry",
    "/heimdall/governance",
}


def _code(text: str) -> str:
    """Drop `#` comments — a directive scanner that reads prose reports documentation.

    This has bitten five separate guards while building this layer, so it is centralised
    here rather than re-derived per assertion.
    """
    return "\n".join(re.sub(r"#.*$", "", line) for line in text.splitlines())


def _locations() -> dict[str, str]:
    """`{path: modifier}` for each location, e.g. `{"/mesh/status": "="}`."""
    found: dict[str, str] = {}
    for m in re.finditer(
        r"^\s*location\s+(?:(=)\s+)?(\S+)\s*\{", _code(SNIPPET.read_text(encoding="utf-8")), re.MULTILINE
    ):
        found[m.group(2)] = m.group(1) or "prefix"
    return found


def _audit_endpoints() -> set[str]:
    """Paths the hub audit verifies through nginx."""
    paths = set()
    for url in re.findall(r'check_endpoint\s+"[^"]*"\s+"([^"]+)"', AUDIT.read_text(encoding="utf-8")):
        if urlparse(url).netloc.endswith("localhost"):
            paths.add(urlparse(url).path)
    return paths


def _client_contract_paths() -> set[str]:
    """Paths the deployable client is built to call (NEXT_PUBLIC_* in the lab deploy)."""
    if not LAB_DEPLOY.exists():  # pragma: no cover - depends on untracked file presence
        pytest.skip("deploy_luxora_nexus_lab.sh is not present")
    return set(re.findall(r"NEXT_PUBLIC_\w+=(/\S+)", LAB_DEPLOY.read_text(encoding="utf-8")))


def _bridge_paths() -> set[str]:
    """Every path the mesh bridge actually serves."""
    src = BRIDGE.read_text(encoding="utf-8")
    found: set[str] = set()
    for m in re.finditer(r"self\.path in \[([^\]]+)\]", src):
        found.update(re.findall(r"'([^']+)'", m.group(1)))
    return found


def _matches(path: str, locations: dict[str, str]) -> bool:
    if path in locations:
        return True
    return any(mod == "prefix" and path.startswith(loc) for loc, mod in locations.items())


# --------------------------------------------------------------------------- #
# the snippet
# --------------------------------------------------------------------------- #


def test_the_snippet_exists_and_has_no_cr_bytes() -> None:
    """A CR here ships verbatim and nginx rejects it, taking the ingress down on reload."""
    assert SNIPPET.exists(), f"missing {SNIPPET}"
    raw = SNIPPET.read_bytes()
    assert raw.count(b"\r") == 0, "the snippet carries CR bytes; nginx will reject it"
    assert raw.count(b"\n") > 5, "the snippet is unexpectedly empty"


def test_every_audited_endpoint_has_a_route() -> None:
    """The cross-check. A new audited endpoint with no route is a permanent failure."""
    locations = _locations()
    assert locations, "no locations parsed from the snippet"
    missing = sorted(p for p in _audit_endpoints() if not _matches(p, locations))
    assert not missing, (
        f"the hub audit verifies {missing} through nginx but the snippet declares no route "
        f"for it/them (declared: {sorted(locations)})"
    )


def test_every_client_contract_path_the_bridge_serves_has_a_route() -> None:
    """The declared `NEXT_PUBLIC_*` contract must be reachable where the bridge serves it.

    Intersected with the bridge's own path list on purpose: the contract also carries
    `/ws` and `/v1`, which belong to the Bifrost gateway and the OpenAI-compatible
    endpoint on :8642. Those are routed by the hub's own server block, not by this
    snippet, so requiring them here would be asserting the wrong file.
    """
    served = _bridge_paths()
    assert served, "could not parse the bridge's served paths"
    needs_route = {p for p in _client_contract_paths() if p in served}
    assert needs_route == EXPECTED_ROUTED, (
        f"the contract/bridge intersection changed: {sorted(needs_route)}. If the contract "
        f"gained a bridge-served path, add its route and update EXPECTED_ROUTED."
    )
    missing = sorted(p for p in needs_route if not _matches(p, _locations()))
    assert not missing, f"client contract paths without an nginx route: {missing}"


def test_the_routes_use_exact_match_so_they_cannot_shadow_the_gateway() -> None:
    """`/bifrost/` belongs to the gateway on :3001, which strips the prefix.

    A prefix route for the bridge on that path would have to out-rank the gateway's,
    risking `/ws` and the traffic that shares it. Exact matches are consulted first, so
    they cannot shadow a prefix route.
    """
    locations = _locations()
    assert "/bifrost/knights" in locations
    assert locations["/bifrost/knights"] == "=", (
        "the knights route is a prefix match and can shadow the Bifrost gateway"
    )
    assert "/bifrost/" not in locations, (
        "the snippet claims the gateway's own path — the gateway and its WebSocket share it"
    )
    assert all(mod == "=" for mod in locations.values()), "every route here must be exact-match"


def test_the_routes_point_at_the_bridge_and_not_another_port() -> None:
    code = _code(SNIPPET.read_text(encoding="utf-8"))
    assert f"127.0.0.1:{BRIDGE_PORT}" in code, f"the snippet does not proxy to :{BRIDGE_PORT}"
    # :3001 is the Bifrost gateway and :9119 the Hermes dashboard; neither belongs here.
    for other in ("127.0.0.1:3001", "127.0.0.1:9119", "127.0.0.1:8642"):
        assert other not in code, f"the snippet proxies a mesh route to {other}"


def test_access_rules_are_inside_locations_and_never_at_server_level() -> None:
    """`allow`/`deny` are inherited by nested contexts.

    Written at the top level of this snippet they would be rules for the whole `server`
    block, gating the Hermes dashboard, the OpenAI-compatible gateway and everything else
    on :80 — not just these four routes. This was written that way once; the guard exists
    so it cannot be again.
    """
    code = _code(SNIPPET.read_text(encoding="utf-8"))
    first_location = code.find("location")
    assert first_location != -1, "no location parsed"
    head = code[:first_location]
    for rule in ("allow", "deny"):
        assert rule not in head, (
            f"`{rule}` appears before the first location, so it would apply to the whole "
            f"server block and break the dashboard: {head.strip()[:120]!r}"
        )
    # And every route must carry its own gate, so none is accidentally left wide open.
    assert code.count("deny  all;") == code.count("location = "), (
        "some locations are ungated — an ungated route publishes the mesh inventory"
    )


def test_the_closed_exposure_is_documented_and_reversible() -> None:
    """The response carries tailnet addresses; whoever opens it must be told so."""
    raw = SNIPPET.read_text(encoding="utf-8")
    assert "MESH_BRIDGE_TOKEN" in raw, "the auth coupling is not documented"
    assert "100.64.0.0/10" in raw, "the tailnet allowance is not documented"
    assert "crawler" in raw or "deliberately" in raw, (
        "the consequence of removing the gate is not stated"
    )


# --------------------------------------------------------------------------- #
# the installer
# --------------------------------------------------------------------------- #


def test_the_installer_backs_up_outside_the_include_globs() -> None:
    """A backup inside sites-enabled/ or conf.d/ is itself LOADED as a live config.

    Not hypothetical: the first run of this script copied a `listen 80 default_server`
    site into sites-enabled/, and `nginx -t` reported "a duplicate default server" — a
    reload would have taken the whole ingress down.
    """
    text = INSTALLER.read_text(encoding="utf-8")
    m = re.search(r"^BACKUP_DIR=(\S+)", text, re.MULTILINE)
    assert m, "the installer does not declare a backup directory"
    for forbidden in ("sites-enabled", "conf.d"):
        assert forbidden not in m.group(1), f"backups land in an include glob: {m.group(1)}"


def test_the_installer_validates_before_reloading_and_can_roll_back() -> None:
    text = INSTALLER.read_text(encoding="utf-8")
    assert "nginx -t" in text, "the installer reloads without validating"
    assert text.index("nginx -t") < text.index("systemctl reload nginx"), (
        "the installer reloads before validating"
    )
    assert "cp -a" in text and ".bak-" in text, "no restore path on validation failure"


def test_the_installer_refuses_a_backup_left_inside_an_include_glob() -> None:
    """The specific mistake run one made must be impossible to repeat silently."""
    text = INSTALLER.read_text(encoding="utf-8")
    assert "INCLUDE_GLOBS" in text and "bak-*" in text, (
        "the installer no longer checks for stray backups inside include globs"
    )


def test_the_installer_covers_every_contract_path() -> None:
    """Its preflight and post-conditions must cover all four, not the original two."""
    text = INSTALLER.read_text(encoding="utf-8")
    for path in sorted(EXPECTED_ROUTED):
        assert path in text, f"the installer does not check {path}"
    assert "CONTRACT_PATHS" in text, "the installer hardcodes paths in more than one place"


def test_the_installer_asserts_behaviour_preservation_for_untouched_paths() -> None:
    """Fixing a missing route must not move a route that already worked."""
    text = INSTALLER.read_text(encoding="utf-8")
    for path in ("/bifrost/", "/ws", "/"):
        assert path in text
    assert "express" in text.lower(), (
        "the installer does not verify that /bifrost/ is still the Express gateway"
    )
