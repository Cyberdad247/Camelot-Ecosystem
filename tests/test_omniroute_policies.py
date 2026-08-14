# SPDX-License-Identifier: MIT

"""tests/test_omniroute_policies.py — lane-signal regression for spec items 1a + 1b.

The Iron Gate invariant (test_lane_signal_is_label_not_gate) is the single
most important test here: it forbids omniroute_policies from ever being
gate-shaped, in code, in attributes, or by exports.  Lane signals compose
DOWNSTREAM of soul_oversight.pre_execute — never pre-empt it.
"""
from __future__ import annotations

import pytest
from control_plane.omniroute_policies import (
    LANE_CLIPROXY_HEAVY_REASONING,
    LANE_DEFAULT,
    LANE_OMNI_ROUTE_CODEX,
    SCAFFOLD_KEYWORDS,
    VALID_LANES,
    LaneSignal,
    select_lane,
)

# ── Item 1a: scaffold → OmniRoute Codex lane ────────────────────────────────


def test_scaffold_intent_routes_to_omni_route_codex_lane():
    """Spec item 1a: rapid boilerplate scaffold → OmniRoute (:20128) → SIR_CODEX."""
    sig = select_lane("//CODEX scaffold a hello-world Rust project")
    assert sig.lane == LANE_OMNI_ROUTE_CODEX
    assert "OmniRoute" in sig.rationale
    assert ":20128" in sig.rationale
    assert "SIR_CODEX" in sig.rationale
    assert sig.matched_keyword == "scaffold"


def test_scaffold_intent_via_prototype_keyword_routes_to_omni_route_codex():
    """Same lane fires for any SCAFFOLD_KEYWORDS match (not only literal 'scaffold')."""
    sig = select_lane("Please iterate a prototype crud stub fast")
    assert sig.lane == LANE_OMNI_ROUTE_CODEX
    assert sig.matched_keyword in SCAFFOLD_KEYWORDS


# ── Item 1b: deep-context reasoning → CLIProxy Polyglot Matrix lane ─────────


def test_reasoning_intent_routes_to_cliproxy_heavy_reasoning_lane():
    """Spec item 1b: massive reasoning/deep-context → CLIProxyAPI (:8080)."""
    sig = select_lane("MERLIN deep-context reasoning over 1m-context window")
    assert sig.lane == LANE_CLIPROXY_HEAVY_REASONING
    assert "CLIProxyAPI" in sig.rationale
    assert ":8080" in sig.rationale
    assert "Polyglot" in sig.rationale
    assert sig.matched_keyword == "deep-context"


# ── Default fallthrough ─────────────────────────────────────────────────────


def test_neutral_intent_falls_to_default_lane():
    """Neutral runic commands (//STATUS, no keyword match, empty/blank input)
    route to the default lane and let factory_lane's normal dispatch take
    over — no preference is a valid preference."""
    assert select_lane("//STATUS").lane == LANE_DEFAULT
    assert select_lane("").lane == LANE_DEFAULT
    assert select_lane("   ").lane == LANE_DEFAULT
    assert select_lane("something unrelated").lane == LANE_DEFAULT
    assert select_lane("//STATUS").matched_keyword == ""
    sig = select_lane("//STATUS")
    assert isinstance(sig, LaneSignal)
    assert sig.lane == LANE_DEFAULT


# ── Iron Gate invariant: LaneSignal is a label, not a gate ──────────────────


def test_lane_signal_is_label_not_gate():
    """Critical invariant: a LaneSignal NEVER carries a go/approve/deny/decision
    shape.  The Iron Gate (soul_oversight.pre_execute) is the ONLY module
    that can deny a HUMAN_GATE-class move.  Lane signals compose DOWNSTREAM
    of the gate; they never pre-empt it."""
    sig = select_lane("//CODEX scaffold")
    assert isinstance(sig, LaneSignal)
    assert sig.lane in VALID_LANES
    # Forbidden gate-shaped attributes
    for forbidden_attr in ("go", "approve", "deny", "block", "verdict", "decision"):
        assert not hasattr(sig, forbidden_attr), (
            f"LaneSignal must not be gate-shaped; got forbidden attr {forbidden_attr!r}"
        )
    # The module itself must not export any gate-shaped symbol.
    import control_plane.omniroute_policies as mod
    for forbidden_export in ("GateDecision", "pre_execute", "approve", "deny", "block"):
        assert not hasattr(mod, forbidden_export), (
            f"omniroute_policies must not export gate-shaped {forbidden_export!r}"
        )


# ── Dual-match priority order ───────────────────────────────────────────────


def test_when_both_keyword_sets_match_scaffold_lane_wins():
    """If the input contains BOTH a scaffold keyword and a reasoning keyword,
    the scaffold lane wins (it appears first in the priority order defined in
    `select_lane`).  This preserves Cloud-Brain reasoning context for genuine
    deep-context work — not for trivially scaffolding a reasoning demo."""
    sig = select_lane("Please scaffold a reasoning demo with rapid prototype")
    assert sig.lane == LANE_OMNI_ROUTE_CODEX
    assert sig.matched_keyword == "scaffold"


# ── Purity / idempotence ────────────────────────────────────────────────────


def test_select_lane_is_idempotent():
    """`select_lane` is a pure function — same input → same output."""
    a = select_lane("//CODEX scaffold a hello-world Rust project")
    b = select_lane("//CODEX scaffold a hello-world Rust project")
    assert a == b
    assert a.lane == b.lane
    assert a.matched_keyword == b.matched_keyword


# ── Structural Iron Gate invariant: no upstream-dependency leak ──────────────


def test_lane_module_is_self_contained_no_upstream_dependencies():
    """Structural invariant: lane signals must be self-contained.  They must
    not import `soul_oversight` (the Iron Gate), `factory_lane` (the typed
    dispatch lane), or any other upstream control_plane module.  This guards
    against future edits that accidentally couple lane-signals back to the
    gate — which AGENTS.md Iron Gate forbids.

    The check inspects every callable export in `omniroute_policies` and
    asserts none of them originate from an upstream `control_plane.*`
    module.  Stdlib-only is enforced via the `__module__` tag.
    """
    import control_plane.omniroute_policies as mod

    # Upstream modules lane signals must NEVER couple to.
    upstream_modules = {
        "soul_oversight",
        "factory_lane",
        "anya_gate",
        "runic_router",
        "bifrost",
        "cloudbrain_sync",
        "kinetic_loop",
    }

    leak_paths = []
    for attr_name, attr_value in vars(mod).items():
        if attr_value is None:
            continue
        if callable(attr_value) and hasattr(attr_value, "__module__"):
            mod_tag = attr_value.__module__ or ""
            for forbidden in upstream_modules:
                if forbidden in mod_tag:
                    leak_paths.append((attr_name, mod_tag))
            if hasattr(attr_value, "__wrapped__"):
                inner = attr_value.__wrapped__
                if hasattr(inner, "__module__"):
                    inner_tag = inner.__module__ or ""
                    for forbidden in upstream_modules:
                        if forbidden in inner_tag:
                            leak_paths.append(
                                (f"{attr_name}.__wrapped__", inner_tag)
                            )

    assert not leak_paths, (
        "omniroute_policies must not import upstream control_plane modules; "
        f"leaks: {leak_paths}"
    )


def test_lane_module_source_ast_forbids_upstream_control_plane_imports():
    """Catch lazy function-body imports — top-level ``__module__`` inspection
    is insufficient.

    Walk the module's source AST; any ``Import`` / ``ImportFrom`` whose
    module path contains a forbidden upstream name is a leak.  This catches
    inlined lazy imports such as::

        def maybe_gate():
            from soul_oversight import pre_execute   # LAZY IMPORT
            return pre_execute(...)

    which the previous structural test does NOT catch because the lazy
    import happens at call time, not at module-load time.
    """
    import ast
    import inspect

    import control_plane.omniroute_policies as mod

    upstream_substrings = {
        "soul_oversight",
        "factory_lane",
        "anya_gate",
        "runic_router",
        "bifrost",
        "cloudbrain_sync",
        "kinetic_loop",
    }

    try:
        source = inspect.getsource(mod)
    except (OSError, TypeError) as exc:
        pytest.skip(f"can't read source for AST walk: {exc}")

    tree = ast.parse(source)
    leaks = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in upstream_substrings:
                    if forbidden in alias.name:
                        leaks.append((alias.name, f"line {node.lineno}"))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for forbidden in upstream_substrings:
                    if forbidden in node.module:
                        leaked_imports = ", ".join(
                            a.name for a in node.names
                        )
                        leaks.append(
                            (
                                f"from {node.module} import {leaked_imports}",
                                f"line {node.lineno}",
                            )
                        )

    assert not leaks, (
        "omniroute_policies source AST contains forbidden control_plane "
        f"imports: {leaks}"
    )
