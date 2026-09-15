# SPDX-License-Identifier: MIT

"""Tests for the OMNI_VOICE_DAG_VMAX crystal, evidence gate and persona dispatch.

The Omni-Voice D.A.G. manifest arrived as **pasted sovereign seed** text. These
tests pin the three invariants that keep it honest:

1. **Structural soundness** — the topology is acyclic, every edge points at a
   declared node, and the node memory budgets never breach the declared 384 MB
   hardware ceiling.

2. **Evidence gate** — a node may only be labelled ``confirmed`` when its
   ``resolved_paths`` actually exist on disk. A claim that names a path which
   does not exist must be downgraded at runtime rather than reported as
   deployed infrastructure.

3. **Deterministic routing** — ``τ=0`` collapses the Softmax distribution to a
   one-hot argmax (Sentinel-governed deterministic lane), and the ``ᛟ_`` runic
   bypass short-circuits before any inference work.

Importing ``control_plane.omni_voice_dag`` works because the ``control_plane``
package installs a meta-path finder that redirects legacy
``control_plane.<leaf>`` imports into the real ``control_plane.<subdir>``
location.
"""

from __future__ import annotations

import copy
import json
import math

import pytest

from control_plane import omni_voice_dag as ovd
from control_plane import runic_router as rr


@pytest.fixture()
def crystal() -> ovd.Crystal:
    return ovd.load_crystal()


@pytest.fixture()
def raw_crystal() -> dict:
    import json

    return json.loads(ovd.CRYSTAL_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 1) Crystal shape
# ---------------------------------------------------------------------------


def test_crystal_loads_with_declared_identity(crystal: ovd.Crystal) -> None:
    assert crystal.schema_version == "camelot.omni-voice-dag/1"
    assert crystal.fingerprint == "νKG_CRYSTAL_OMNI_VOICE_DAG_VMAX"
    assert crystal.system_identity == "OMNI_VOICE_ROUTER_vMAX"
    assert crystal.hardware_ceiling_mb == 384


def test_pasted_seed_is_marked_untrusted(crystal: ovd.Crystal) -> None:
    """The seed is input, never authority — the crystal must say so."""
    assert crystal.provenance["trust"] == "untrusted_external_input"
    assert crystal.provenance["hitl_required_for_process_launch"] is True


def test_five_stages_map_to_five_nodes(crystal: ovd.Crystal) -> None:
    assert len(crystal.nodes) == 5
    assert {n.stage for n in crystal.nodes} == {1, 2, 3, 4, 5}


# ---------------------------------------------------------------------------
# 2) Topology
# ---------------------------------------------------------------------------


def test_topological_order_is_acyclic_and_ordered(crystal: ovd.Crystal) -> None:
    order = crystal.node_order
    assert len(order) == len(crystal.nodes)
    assert order[0] == "node_01_ingress"
    assert order[-1] == "node_04_egress"
    # Every predecessor must appear before its dependant.
    position = {node_id: i for i, node_id in enumerate(order)}
    for node in crystal.nodes:
        for pred in node.predecessors:
            assert position[pred] < position[node.node_id]


def test_parallel_fanout_and_reduce_anchors(crystal: ovd.Crystal) -> None:
    assert crystal.fan_out_at == "node_02_routing"
    assert crystal.reduce_at == "node_04_egress"
    assert set(crystal.parallel_threads) == {
        "node_03_thread_a_viseme",
        "node_03_thread_b_synthesis",
    }
    # Both parallel threads must feed the reduce node.
    egress = next(n for n in crystal.nodes if n.node_id == crystal.reduce_at)
    assert set(crystal.parallel_threads) <= set(egress.predecessors)


def test_cycle_is_rejected(raw_crystal: dict) -> None:
    payload = copy.deepcopy(raw_crystal)
    # node_01 depends on the egress node -> closes a cycle.
    for node in payload["nodes"]:
        if node["node_id"] == "node_01_ingress":
            node["predecessors"] = ["node_04_egress"]
    with pytest.raises(ovd.CrystalError, match="cycle"):
        ovd.parse_crystal(payload)


def test_dangling_predecessor_is_rejected(raw_crystal: dict) -> None:
    payload = copy.deepcopy(raw_crystal)
    payload["nodes"][1]["predecessors"] = ["node_99_ghost"]
    with pytest.raises(ovd.CrystalError, match="unknown predecessor"):
        ovd.parse_crystal(payload)


def test_duplicate_node_id_is_rejected(raw_crystal: dict) -> None:
    payload = copy.deepcopy(raw_crystal)
    payload["nodes"][1]["node_id"] = payload["nodes"][0]["node_id"]
    with pytest.raises(ovd.CrystalError, match="duplicate node_id"):
        ovd.parse_crystal(payload)


def test_wrong_schema_version_is_rejected(raw_crystal: dict) -> None:
    payload = copy.deepcopy(raw_crystal)
    payload["schema_version"] = "camelot.omni-voice-dag/999"
    with pytest.raises(ovd.CrystalError, match="schema_version"):
        ovd.parse_crystal(payload)


# ---------------------------------------------------------------------------
# 3) Memory ceiling (the 384 MB VPS hub cap)
# ---------------------------------------------------------------------------


def test_node_budgets_fit_the_hardware_ceiling(crystal: ovd.Crystal) -> None:
    assert crystal.memory_total_mb() == 384
    assert crystal.memory_total_mb() <= crystal.hardware_ceiling_mb


def test_ceiling_breach_is_rejected(raw_crystal: dict) -> None:
    payload = copy.deepcopy(raw_crystal)
    for node in payload["nodes"]:
        if node["node_id"] == "node_03_thread_b_synthesis":
            node["memory_budget_mb"] = 512
    with pytest.raises(ovd.CrystalError, match="memory ceiling breached"):
        ovd.parse_crystal(payload)


def test_memory_invariants_are_declared(crystal: ovd.Crystal) -> None:
    joined = " ".join(crystal.memory_invariants).lower()
    assert "ceiling" in joined
    assert "ring buffer" in joined
    assert "audio clock" in joined


# ---------------------------------------------------------------------------
# 4) Evidence gate
# ---------------------------------------------------------------------------


def test_confirmed_node_without_artifacts_is_rejected(raw_crystal: dict) -> None:
    payload = copy.deepcopy(raw_crystal)
    for node in payload["nodes"]:
        if node["node_id"] == "node_02_routing":
            node["resolved_paths"] = []
    with pytest.raises(ovd.CrystalError, match="without a resolved_paths artifact"):
        ovd.parse_crystal(payload)


def test_invalid_evidence_class_is_rejected(raw_crystal: dict) -> None:
    payload = copy.deepcopy(raw_crystal)
    payload["nodes"][0]["evidence_class"] = "basically_done"
    with pytest.raises(ovd.CrystalError, match="invalid evidence_class"):
        ovd.parse_crystal(payload)


def test_live_gate_verifies_confirmed_nodes_on_disk(crystal: ovd.Crystal) -> None:
    report = ovd.resolve_evidence(crystal)
    assert "node_02_routing" in report["verified"]
    assert "node_03_thread_b_synthesis" in report["verified"]
    assert report["downgraded"] == []
    # Every declared path must be accounted for as either found or missing.
    for node_report in report["nodes"].values():
        assert set(node_report["found_paths"]) | set(node_report["missing_paths"]) == set(
            node_report["resolved_paths"]
        )
    # The unbuilt viseme node declares no artifacts at all — nothing to verify.
    viseme = report["nodes"]["node_03_thread_a_viseme"]
    assert viseme["resolved_paths"] == []
    assert viseme["precursor_found"] is False


def test_live_gate_downgrades_missing_artifacts(raw_crystal: dict) -> None:
    """A confirmed claim naming a non-existent path must be demoted, not trusted."""
    payload = copy.deepcopy(raw_crystal)
    for node in payload["nodes"]:
        if node["node_id"] == "node_02_routing":
            node["resolved_paths"] = ["control_plane/runes/does_not_exist.py"]
    crystal = ovd.parse_crystal(payload)
    report = ovd.resolve_evidence(crystal)
    assert "node_02_routing" in report["downgraded"]
    assert report["nodes"]["node_02_routing"]["effective_evidence_class"] == "planned"
    assert report["nodes"]["node_02_routing"]["missing_paths"]


def test_declared_but_unbuilt_services_stay_unconfirmed(crystal: ovd.Crystal) -> None:
    """The viseme extractor and the Go SIP bridge are still only declared."""
    unconfirmed = set(crystal.unconfirmed_nodes())
    assert "node_03_thread_a_viseme" in unconfirmed  # VisemeExtractor
    assert "node_04_egress" in unconfirmed  # camelot-sip-bridge (Go)

    summary = crystal.evidence_summary()
    assert summary["confirmed"] == 3
    assert summary["planned"] == 1
    assert summary["aspirational"] == 1


def test_ingress_is_confirmed_only_because_the_crate_exists(crystal: ovd.Crystal) -> None:
    """`node_01_ingress` earned `confirmed` by the DSP crate landing on disk.

    The claim is not self-certifying: the evidence gate re-checks every listed
    artifact, and this test asserts those artifacts are present and complete.
    """
    ingress = next(n for n in crystal.nodes if n.node_id == "node_01_ingress")
    assert ingress.evidence_class == "confirmed"
    assert ingress.declared_service == "camelot-audio-dsp"
    assert ingress.declared_runtime == "Rust/WASM"
    assert ingress.memory_budget_mb == 96
    assert "wasm/camelot-audio-dsp/Cargo.toml" in ingress.resolved_paths
    assert "wasm/camelot-audio-dsp/src/lib.rs" in ingress.resolved_paths

    report = ovd.resolve_evidence(crystal)
    assert "node_01_ingress" in report["verified"]
    assert report["nodes"]["node_01_ingress"]["missing_paths"] == []


def test_evidence_summary_always_covers_all_classes(crystal: ovd.Crystal) -> None:
    assert set(crystal.evidence_summary()) == set(ovd.EVIDENCE_CLASSES)


# ---------------------------------------------------------------------------
# 5) Softmax persona dispatch
# ---------------------------------------------------------------------------


def test_tau_zero_is_a_one_hot_argmax(crystal: ovd.Crystal) -> None:
    features = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    probs, logits, winner, confidence = ovd.softmax_dispatch(
        features, crystal.weights, crystal.deterministic_tau
    )
    assert confidence == 1.0
    assert probs[winner] == 1.0
    assert sum(1 for value in probs.values() if value == 1.0) == 1
    assert winner == max(logits, key=lambda k: (logits[k], k))


def test_tau_zero_is_deterministic_across_calls(crystal: ovd.Crystal) -> None:
    features = [1.0, 1.0, 0.0, 0.0, 0.0, 1.0]
    winners = {
        ovd.softmax_dispatch(features, crystal.weights, 0)[2] for _ in range(5)
    }
    assert len(winners) == 1


def test_tau_one_matches_the_reference_softmax(crystal: ovd.Crystal) -> None:
    features = [1.0, 1.0, 0.0, 0.0, 0.0, 1.0]
    tau = crystal.exploratory_tau
    probs, logits, winner, confidence = ovd.softmax_dispatch(features, crystal.weights, tau)

    # Independent reference implementation of P(K_i|v).
    reference = {
        knight: math.exp(ovd.dot(features, vec) / tau)
        for knight, vec in crystal.weights.items()
    }
    total = sum(reference.values())
    for knight, value in reference.items():
        assert probs[knight] == pytest.approx(value / total, abs=1e-12)

    assert sum(probs.values()) == pytest.approx(1.0, abs=1e-12)
    assert confidence == pytest.approx(max(probs.values()), abs=1e-12)
    assert winner == max(probs, key=lambda k: (probs[k], k))


def test_higher_tau_flattens_the_distribution(crystal: ovd.Crystal) -> None:
    features = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    _, _, _, confident = ovd.softmax_dispatch(features, crystal.weights, 0)
    _, _, _, exploratory = ovd.softmax_dispatch(features, crystal.weights, 1)
    assert confident == 1.0
    assert exploratory < confident


def test_dimension_mismatch_raises(crystal: ovd.Crystal) -> None:
    with pytest.raises(ValueError, match="dimension mismatch"):
        ovd.softmax_dispatch([1.0, 1.0], crystal.weights, 0)


def test_negative_tau_raises(crystal: ovd.Crystal) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        ovd.softmax_dispatch([1.0] * 6, crystal.weights, -1)


def test_tau_policy_is_enforced(crystal: ovd.Crystal) -> None:
    assert crystal.allowed_tau_values == (0, 1)
    assert ovd.resolve_tau(crystal, 0) == 0
    assert ovd.resolve_tau(crystal, 1) == 1
    assert ovd.resolve_tau(crystal) == crystal.deterministic_tau
    with pytest.raises(ovd.TauPolicyError):
        ovd.resolve_tau(crystal, 7)


def test_weights_match_declared_feature_dims(crystal: ovd.Crystal) -> None:
    assert len(crystal.feature_dims) == 6
    for knight, vector in crystal.weights.items():
        assert len(vector) == len(crystal.feature_dims), knight


# ---------------------------------------------------------------------------
# 6) Runic bypass
# ---------------------------------------------------------------------------


def test_bypass_token_must_open_the_utterance(crystal: ovd.Crystal) -> None:
    assert ovd.detect_rune("ᛟ_SILENCE", crystal) is not None
    assert ovd.detect_rune("   ᛟ_SILENCE   ", crystal) is not None
    assert ovd.detect_rune("please ᛟ_SILENCE", crystal) is None


def test_bypass_tolerates_asr_trailing_punctuation(crystal: ovd.Crystal) -> None:
    assert ovd.detect_rune("ᛟ_STATUS.", crystal) is not None
    assert ovd.detect_rune("ᛟ_STATUS!", crystal) is not None


def test_undeclared_bypass_token_is_ignored(crystal: ovd.Crystal) -> None:
    assert ovd.detect_rune("ᛟ_NOPE", crystal) is None
    assert ovd.detect_rune("", crystal) is None
    assert ovd.detect_rune("just talking", crystal) is None


def test_all_bypass_tokens_carry_the_declared_prefix(crystal: ovd.Crystal) -> None:
    assert crystal.bypass_prefix == "ᛟ_"
    for token, command in crystal.bypass_commands.items():
        assert token.startswith(crystal.bypass_prefix)
        assert command.knight
        assert command.delegates_rune.startswith("//")


def test_bypass_delegates_resolve_to_real_runes(crystal: ovd.Crystal) -> None:
    """The bypass must never point at a rune the router does not know."""
    for command in crystal.bypass_commands.values():
        assert command.delegates_rune in rr.RUNIC_COMMANDS
    assert set(ovd.BYPASS_DELEGATE_RUNES) <= set(rr.RUNIC_COMMANDS)


def test_silence_routes_to_the_interlock_knight(crystal: ovd.Crystal) -> None:
    silence = ovd.detect_rune("ᛟ_SILENCE", crystal)
    assert silence is not None
    assert silence.knight == "sir_sentinel"
    assert silence.delegates_rune == "//BIFROST_LOCK"


# ---------------------------------------------------------------------------
# 7) Routing decisions
# ---------------------------------------------------------------------------


def test_bypass_route_costs_zero_inference(crystal: ovd.Crystal) -> None:
    result = ovd.route_intent("ᛟ_SUMMON the voice knight", crystal=crystal)
    assert result["status"] == "ROUTED_BYPASS"
    assert result["path"] == "runic_bypass"
    assert result["llm_inference_cost"] == 0
    assert result["delegates_rune"] == "//VOICE_ROUTER"


def test_free_text_routes_through_softmax(crystal: ovd.Crystal) -> None:
    result = ovd.route_intent("forge a new audio pipeline now", crystal=crystal)
    assert result["status"] == "ROUTED_SOFTMAX"
    assert result["path"] == "softmax"
    assert result["tau"] == crystal.deterministic_tau
    assert result["knight"] in crystal.weights
    assert sum(result["probabilities"].values()) == pytest.approx(1.0, abs=1e-5)


def test_tau_policy_denial_is_reported_not_crashed(crystal: ovd.Crystal) -> None:
    result = ovd.route_intent("hello", tau=9, crystal=crystal)
    assert result["status"] == "TAU_POLICY_DENIED"
    assert "tau" in result["error"]


def test_feature_dim_mismatch_is_reported(crystal: ovd.Crystal) -> None:
    result = ovd.route_intent("hello", features=[1.0, 0.0], crystal=crystal)
    assert result["status"] == "FEATURE_DIM_MISMATCH"


def test_feature_inference_is_keyword_driven(crystal: ovd.Crystal) -> None:
    audio = ovd.infer_features("let me speak to you", crystal)
    privacy = ovd.infer_features("my api token is exposed", crystal)
    index = {dim: i for i, dim in enumerate(crystal.feature_dims)}
    assert audio[index["audio_focus"]] == 1.0
    assert privacy[index["privacy_sensitive"]] == 1.0
    assert len(audio) == len(crystal.feature_dims)


def test_privacy_utterance_selects_the_sentinel(crystal: ovd.Crystal) -> None:
    """A secrets-flavoured utterance must not land on the build or voice lanes."""
    result = ovd.route_intent("my password and private key leaked", crystal=crystal)
    assert result["knight"] == "sir_sentinel"


def test_missing_crystal_degrades_instead_of_crashing(tmp_path) -> None:
    missing = tmp_path / "nope.json"
    with pytest.raises(ovd.CrystalError):
        ovd.load_crystal(missing)


# ---------------------------------------------------------------------------
# 8) Runic router integration
# ---------------------------------------------------------------------------


def test_rune_is_registered_on_the_voice_lane() -> None:
    entry = rr.RUNIC_COMMANDS["//OMNI_VOICE_DAG"]
    assert entry["knight"] == "sir_sonus"
    assert entry["handler"] == "_handle_omni_voice_dag"
    assert entry["hydrate"] is False


def test_handler_validates_without_launching_anything() -> None:
    result = rr._handle_omni_voice_dag("", {})
    assert result["status"] == "CRYSTAL_VALIDATED"
    assert result["read_only"] is True
    assert result["process_launch"] == "HITL_REQUIRED"
    assert result["memory_mb"] == "384/384"
    assert result["topology"][0] == "node_01_ingress"
    assert "route" not in result


def test_handler_routes_an_utterance_when_given_one() -> None:
    result = rr._handle_omni_voice_dag("ᛟ_SILENCE", {})
    assert result["status"] == "ROUTED_BYPASS"
    assert result["route"]["knight"] == "sir_sentinel"


def test_handler_surfaces_evidence_classes() -> None:
    result = rr._handle_omni_voice_dag("", {})
    assert result["evidence_summary"]["confirmed"] == 3
    assert "node_03_thread_a_viseme" in result["unconfirmed_nodes"]
    assert "node_01_ingress" not in result["unconfirmed_nodes"]


def test_handler_reports_invalid_crystal(monkeypatch) -> None:
    def boom(*_args, **_kwargs):
        raise ovd.CrystalError("synthetic corruption")

    monkeypatch.setattr(ovd, "load_crystal", boom)
    result = rr._handle_omni_voice_dag("", {})
    assert result["status"] == "CRYSTAL_INVALID"
    assert "synthetic corruption" in result["error"]


# ---------------------------------------------------------------------------
# 9) Self-test
# ---------------------------------------------------------------------------


def test_module_self_test_passes(capsys) -> None:
    assert ovd.self_test() == 0
    captured = capsys.readouterr()
    assert "PASS" in captured.out


def test_module_self_test_reports_node_count(capsys) -> None:
    ovd.self_test()
    captured = capsys.readouterr()
    assert "5 nodes" in captured.out
    assert "384/384 MB" in captured.out


# ---------------------------------------------------------------------------
# 10) Cross-language parity fixture (apps/bifrost)
# ---------------------------------------------------------------------------


def test_parity_fixture_is_in_sync_with_this_generator() -> None:
    """The gateway's TypeScript port is pinned by a fixture generated from HERE.

    Change the crystal, the feature keywords or the softmax and the checked-in
    fixture goes stale — the gateway would then keep replaying yesterday's
    expectations while its own tests stayed green. This test closes that loop by
    regenerating the fixture and demanding exact equality.
    """
    fixture_path = ovd.CAMELOT_HOME / "apps" / "bifrost" / "src" / "omniVoice.crystal.json"
    assert fixture_path.exists(), f"parity fixture is missing: {fixture_path}"

    checked_in = json.loads(fixture_path.read_text(encoding="utf-8"))
    regenerated = ovd.build_parity_fixture()
    assert checked_in == regenerated, (
        "apps/bifrost/src/omniVoice.crystal.json is stale; regenerate it with "
        "`python -m control_plane.omni_voice_dag --write-vectors "
        "apps/bifrost/src/omniVoice.crystal.json`"
    )


def test_parity_fixture_covers_both_lanes() -> None:
    fixture = ovd.build_parity_fixture()
    statuses = {vector["status"] for vector in fixture["vectors"]}
    assert "ROUTED_BYPASS" in statuses
    assert "ROUTED_SOFTMAX" in statuses
    # A bypass vector must carry the delegated rune so the port can prove it
    # did not invent one; a softmax vector must carry the full distribution.
    for vector in fixture["vectors"]:
        if vector["status"] == "ROUTED_BYPASS":
            assert vector["delegates_rune"].startswith("//")
        elif vector["status"] == "ROUTED_SOFTMAX":
            assert len(vector["features"]) == len(fixture["feature_dims"])
            assert abs(sum(vector["probabilities"].values()) - 1.0) < 1e-9
