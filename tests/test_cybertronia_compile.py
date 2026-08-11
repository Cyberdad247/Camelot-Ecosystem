"""tests/test_cybertronia_compile.py

Phase 2 compiler regression battery — pins the contract with cybertronia-graph-ui-spec.md
(Draft 0.3). The 25-vector field-name lockbox test catches a §1-vs-compiler reorder
BETWEEN this file and CAMELOT_OS/docs/cybertronia-graph-ui-spec.md.

Tests are isolated to tmp_path so a real Phase 1 telemetry blast never leaks into
the artifact sink (PHASE2_ROOT). CAMELOT_HOME is monkeypatched per test.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterator

import pytest

# Make `control_plane` importable.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from control_plane.infra import cybertronia_compile as cc  # noqa: E402

# ── Vector25 spec §1 lockbox (drift pin) ───────────────────────────────────
#
# These 25 strings verbatim from CAMELOT_OS/docs/cybertronia-graph-ui-spec.md
# §1. Any reorder/rename fires both this test AND the lockbox test in the
# PWA-side drift mirror — so the entire cross-worktree contract stays
# byte-aligned.
_SPEC_VECTOR25_IN_DECLARED_ORDER: tuple[str, ...] = (
    "layer", "type", "path depth", "size", "file count",
    "recency", "churn", "cpu cost", "memory cost", "storage cost",
    "runtime state", "health", "exposure", "in_degree", "out_degree",
    "centrality", "betweenness", "pagerank", "community", "criticality",
    "sensitivity", "mutability", "provenance", "sync state", "resource pressure",
)


@pytest.fixture
def isolated_compile_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[Path]:
    """Redirect PHASE1_ROOT + PHASE2_ROOT to a tmp path; restore on teardown."""
    phase1 = tmp_path / "phase1"
    phase2 = tmp_path / "phase2"
    phase1.mkdir(parents=True, exist_ok=True)
    phase2.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cc, "PHASE1_ROOT", phase1)
    monkeypatch.setattr(cc, "PHASE2_ROOT", phase2)
    # Mirror into module-level constants that compile_from_phase1_path uses.
    monkeypatch.setattr(cc, "PHASE1_TELEMETRY",   phase1 / "node_telemetry.json")
    monkeypatch.setattr(cc, "PHASE1_CURSOR",      phase1 / "cursor.json")
    monkeypatch.setattr(cc, "PHASE1_SCAN_META",   phase1 / "scan.meta.json")
    monkeypatch.setattr(cc, "LATTICE_VECTORS",    phase2 / "lattice_vectors.json")
    monkeypatch.setattr(cc, "GRAPH_DELTA_FILE",   phase2 / "graph_delta.json")
    monkeypatch.setattr(cc, "REDACTED_ENTIREMAP", phase2 / "entiremap.md")
    monkeypatch.setattr(cc, "COMPILE_CURSOR",     phase2 / "compile_cursor.json")
    yield tmp_path


# ── 1. Spec §1 lockbox: VECTOR25_FIELD_NAMES verbatim against the spec ────

class TestLockbox:
    def test_vector25_field_names_count_pinned(self) -> None:
        assert len(cc.VECTOR25_FIELD_NAMES) == cc.EXPECTED_VECTOR_LEN == 25

    def test_vector25_field_names_match_spec_byte_for_byte(self) -> None:
        assert cc.VECTOR25_FIELD_NAMES == _SPEC_VECTOR25_IN_DECLARED_ORDER

    def test_vector25_field_names_unique(self) -> None:
        assert len(set(cc.VECTOR25_FIELD_NAMES)) == cc.EXPECTED_VECTOR_LEN

    def test_vector25_field_names_preserve_declared_order_not_alphabetical(self) -> None:
        sorted_ = sorted(cc.VECTOR25_FIELD_NAMES)
        assert sorted_ != list(cc.VECTOR25_FIELD_NAMES)
        # AND that "layer" is first (semantic anchor) — guards against a
        # sort-then-re-export mistake that preserves count + uniqueness.
        assert cc.VECTOR25_FIELD_NAMES[0] == "layer"
        assert cc.VECTOR25_FIELD_NAMES[-1] == "resource pressure"

    def test_schema_versions_pinned_per_draft_03(self) -> None:
        assert cc.SCHEMA_VERSION_SNAPSHOT == "cybertronia.snapshot/v1"
        assert cc.SCHEMA_VERSION_DELTA    == "cybertronia.delta/v1"


# ── 2. Vector25 derivation is deterministic + uses neutral 0/1.0 defaults ─

class TestCompileVector:
    NODE_FILE = {
        "path":  "02_FORGE/apps/pwa-cockpit/src/app/cockpit/cartridges/cybertronia-graph/index.tsx",
        "size":  42_000,
        "mtime": 1_700_000_000.0,
        "kind":  "file",
    }
    RUNTIME = {
        "mem_total_mib": 16384.0,
        "mem_avail_mib": 8192.0,
    }
    NOW = "2026-07-14T00:00:00+00:00"

    def test_returns_exactly_25_floats(self) -> None:
        v = cc.compile_vector(
            self.NODE_FILE, self.RUNTIME, now_iso=self.NOW
        )
        assert len(v) == 25
        assert all(isinstance(x, float) for x in v)

    def test_no_nan_sent_in_compile_vector(self) -> None:
        """NaN would trip the InstancedMesh STRIDE_SENTINEL (spec §4.2)."""
        import math
        v = cc.compile_vector(
            self.NODE_FILE, self.RUNTIME, now_iso=self.NOW
        )
        for i, x in enumerate(v):
            assert not math.isnan(x), f"v[{i}] is NaN — would trip STRIDE_SENTINEL"
            assert not math.isinf(x), f"v[{i}] is Inf — overflow"

    def test_deterministic_under_repeated_calls(self) -> None:
        v1 = cc.compile_vector(self.NODE_FILE, self.RUNTIME, now_iso=self.NOW)
        v2 = cc.compile_vector(self.NODE_FILE, self.RUNTIME, now_iso=self.NOW)
        assert v1 == v2

    def test_layer_index_matches_v0(self) -> None:
        v = cc.compile_vector(self.NODE_FILE, self.RUNTIME, now_iso=self.NOW)
        # path starts with "02_FORGE/" → layer index 2
        assert cc.LAYERS.index("02_FORGE") == 2
        assert v[cc.VECTOR25_FIELD_NAMES.index("layer")] == 2.0

    def test_kind_index_one_hot_for_file(self) -> None:
        v = cc.compile_vector(self.NODE_FILE, self.RUNTIME, now_iso=self.NOW)
        assert v[cc.VECTOR25_FIELD_NAMES.index("type")] == 0.0

    def test_dir_kind_gets_dormant_runtime_state(self) -> None:
        node = dict(self.NODE_FILE, kind="dir")
        v = cc.compile_vector(node, self.RUNTIME, now_iso=self.NOW)
        runtime_state_idx = cc.VECTOR25_FIELD_NAMES.index("runtime state")
        # v[10]=0=active, 1=dormant. Dir → dormant (no actionable script).
        assert v[runtime_state_idx] == 1.0

    def test_health_is_compile_time_neutral(self) -> None:
        v = cc.compile_vector(self.NODE_FILE, self.RUNTIME, now_iso=self.NOW)
        # 1.0 = healthy at compile time
        assert v[cc.VECTOR25_FIELD_NAMES.index("health")] == 1.0

    def test_resource_pressure_matches_runtime_available(self) -> None:
        node = dict(self.NODE_FILE)
        runtime = dict(self.RUNTIME, mem_total_mib=16384.0, mem_avail_mib=8192.0)
        v = cc.compile_vector(node, runtime, now_iso=self.NOW)
        # (16384 - 8192) / 16384 = 0.5
        assert abs(v[cc.VECTOR25_FIELD_NAMES.index("resource pressure")] - 0.5) < 1e-6

    def test_storage_cost_clamped_to_1_for_huge_file(self) -> None:
        node = dict(self.NODE_FILE, size=10**18)  # exabyte
        v = cc.compile_vector(node, self.RUNTIME, now_iso=self.NOW)
        assert v[cc.VECTOR25_FIELD_NAMES.index("storage cost")] == 1.0

    def test_sensitivity_high_for_dotenv(self) -> None:
        node = dict(self.NODE_FILE, path="bin/.env.production")
        v = cc.compile_vector(node, self.RUNTIME, now_iso=self.NOW)
        # basename starts with .env → sensitivity 2 (high) → 2.0
        assert v[cc.VECTOR25_FIELD_NAMES.index("sensitivity")] == 2.0

    def test_sensitivity_high_for_pem(self) -> None:
        node = dict(self.NODE_FILE, path="02_FORGE/some/secret.pem")
        v = cc.compile_vector(node, self.RUNTIME, now_iso=self.NOW)
        assert v[cc.VECTOR25_FIELD_NAMES.index("sensitivity")] == 2.0

    def test_sensitivity_low_for_normal_source(self) -> None:
        v = cc.compile_vector(self.NODE_FILE, self.RUNTIME, now_iso=self.NOW)
        assert v[cc.VECTOR25_FIELD_NAMES.index("sensitivity")] == 0.0


# ── 3. derive_node_id is spec-glossary compliant (16 hex chars) ───────────

class TestDeriveNodeId:
    def test_node_id_returns_16_hex_chars(self) -> None:
        nid = cc.derive_node_id("bin/awaken.py")
        assert len(nid) == 16
        int(nid, 16)  # raises if non-hex

    def test_node_id_deterministic(self) -> None:
        assert cc.derive_node_id("bin/awaken.py") == cc.derive_node_id("bin/awaken.py")

    def test_node_id_differs_for_different_paths(self) -> None:
        a = cc.derive_node_id("bin/awaken.py")
        b = cc.derive_node_id("bin/bootstrap.py")
        assert a != b


# ── 4. derive_layer pin to LAYERS ──────────────────────────────────────────

class TestDeriveLayer:
    def test_bin_prefix(self) -> None:
        assert cc.derive_layer("bin/awaken.py") == "bin"

    def test_control_plane_prefix(self) -> None:
        assert cc.derive_layer("control_plane/run.py") == "control_plane"

    def test_02_forge_prefix(self) -> None:
        assert cc.derive_layer("02_FORGE/apps/x.py") == "02_FORGE"

    def test_03_vault_prefix(self) -> None:
        assert cc.derive_layer("03_VAULT/runtime_state/x.json") == "03_VAULT"

    def test_runtime_default_catch_all(self) -> None:
        assert cc.derive_layer("foo/bar/baz.py") == "runtime"

    def test_windows_paths_normalized(self) -> None:
        assert cc.derive_layer("02_FORGE\\apps\\x.py") == "02_FORGE"


# ── 5. Sensitivity derivation ──────────────────────────────────────────────

class TestDeriveSensitivity:
    def test_dotenv_is_high(self) -> None:
        assert cc.derive_sensitivity(".env") == 2
        assert cc.derive_sensitivity(".env.production") == 2

    def test_pem_suffix_is_high(self) -> None:
        assert cc.derive_sensitivity("secret.pem") == 2
        assert cc.derive_sensitivity("cert.pfx") == 2

    def test_credentials_prefix_is_high(self) -> None:
        assert cc.derive_sensitivity("credentials.json") == 2

    def test_dotfile_is_med(self) -> None:
        assert cc.derive_sensitivity(".bashrc") == 1

    def test_gitignore_dotfiles_stay_low(self) -> None:
        assert cc.derive_sensitivity(".gitignore") == 0
        assert cc.derive_sensitivity(".gitkeep")   == 0

    def test_normal_source_low(self) -> None:
        assert cc.derive_sensitivity("awaken.py") == 0

    def test_case_insensitive(self) -> None:
        assert cc.derive_sensitivity("SECRET.PEM") == 2
        assert cc.derive_sensitivity(".ENV")        == 2


# ── 6. Redaction — entiremap never leaks sensitive basenames ──────────────

class TestRedaction:
    def test_dotenv_redacted(self) -> None:
        assert cc.redact_basename(".env") == "[REDACTED]"
        assert cc.redact_basename(".env.production") == "[REDACTED]"

    def test_pem_redacted(self) -> None:
        assert cc.redact_basename("secret.pem") == "[REDACTED]"

    def test_normal_basename_preserved(self) -> None:
        assert cc.redact_basename("awaken.py") == "awaken.py"


# ── 7. build_lattice_vectors — schema_version + 25-name fixture ───────────

class TestBuildLatticeVectors:
    NODES = [
        {"path": "bin/awaken.py",     "size": 1000, "mtime": 1_700_000_000.0, "kind": "file"},
        {"path": "control_plane/x",   "size": 2000, "mtime": 1_700_000_000.0, "kind": "file"},
        {"path": "02_FORGE/y/z.py",   "size": 3000, "mtime": 1_700_000_000.0, "kind": "file"},
        {"path": "03_VAULT/s.json",   "size": 4000, "mtime": 1_700_000_000.0, "kind": "file"},
        {"path": "bin/.env.local",    "size":  100, "mtime": 1_700_000_000.0, "kind": "file"},
    ]
    RUNTIME = {"mem_total_mib": 16384.0, "mem_avail_mib": 16384.0, "volumes": []}

    def test_schema_version_pinned(self) -> None:
        payload = cc.build_lattice_vectors(
            scan_id="abc123",
            nodes=self.NODES,
            runtime=self.RUNTIME,
            now_iso="2026-07-14T00:00:00+00:00",
        )
        assert payload["schema_version"] == cc.SCHEMA_VERSION_SNAPSHOT

    def test_vector_field_names_in_payload_match_spec(self) -> None:
        payload = cc.build_lattice_vectors(
            scan_id="abc123",
            nodes=self.NODES,
            runtime=self.RUNTIME,
            now_iso="2026-07-14T00:00:00+00:00",
        )
        assert tuple(payload["vector_field_names"]) == _SPEC_VECTOR25_IN_DECLARED_ORDER

    def test_every_node_produces_a_25_vector(self) -> None:
        payload = cc.build_lattice_vectors(
            scan_id="abc123",
            nodes=self.NODES,
            runtime=self.RUNTIME,
            now_iso="2026-07-14T00:00:00+00:00",
        )
        assert payload["vector_count"] == len(self.NODES)
        assert len(payload["vectors"]) == len(self.NODES)
        for nid, vec in payload["vectors"].items():
            assert len(vec) == 25

    def test_sensitive_node_keeps_high_sensitivity(self) -> None:
        payload = cc.build_lattice_vectors(
            scan_id="abc123",
            nodes=self.NODES,
            runtime=self.RUNTIME,
            now_iso="2026-07-14T00:00:00+00:00",
        )
        sens_idx = cc.VECTOR25_FIELD_NAMES.index("sensitivity")
        env_nid = cc.derive_node_id("bin/.env.local")
        assert payload["vectors"][env_nid][sens_idx] == 2.0


# ── 8. build_graph_delta — HLT determinism + base_digest anchor ───────────

class TestBuildGraphDelta:
    def test_schema_version_pinned(self) -> None:
        delta = cc.build_graph_delta(
            scan_id="abc123",
            base_digest="sha256:00",
            node_paths=["a", "b", "c"],
            received_at_ms=2_000_000,
        )
        assert delta["schema_version"] == cc.SCHEMA_VERSION_DELTA

    def test_every_path_becomes_an_upsert(self) -> None:
        delta = cc.build_graph_delta(
            scan_id="abc123",
            base_digest="sha256:00",
            node_paths=["a", "b", "c"],
            received_at_ms=2_000_000,
        )
        assert [op["kind"] for op in delta["operations"]] == ["upsert", "upsert", "upsert"]

    def test_hlt_logical_counter_is_occurrence_idx(self) -> None:
        delta = cc.build_graph_delta(
            scan_id="abc123",
            base_digest="sha256:00",
            node_paths=["a", "b", "c"],
            received_at_ms=2_000_000,
        )
        log_counters = [op["occurred_hlt"][1] for op in delta["operations"]]
        assert log_counters == [0, 1, 2]

    def test_hlt_physical_is_received_at_ms(self) -> None:
        delta = cc.build_graph_delta(
            scan_id="abc123",
            base_digest="sha256:00",
            node_paths=["a", "b"],
            received_at_ms=9_999_999_888,
        )
        assert all(op["occurred_hlt"][0] == 9_999_999_888 for op in delta["operations"])

    def test_base_digest_passed_through(self) -> None:
        delta = cc.build_graph_delta(
            scan_id="abc123",
            base_digest="sha256:deadbeef",
            node_paths=["a"],
            received_at_ms=1,
        )
        assert delta["base_digest"] == "sha256:deadbeef"


# ── 9. compile_cursor (read by sync-status handler) ───────────────────────

class TestCompileCursor:
    def test_has_four_spec_fields(self) -> None:
        cur = cc.build_compile_cursor(
            last_digest="sha256:abc",
            last_seen_at_ms=1_700_000_000_000,
        )
        # spec §8 row 4 mandates the four-field shape
        for key in ("last_digest", "last_seen_at_ms", "lag_batches", "divergence_pending"):
            assert key in cur

    def test_default_lag_batches_zero(self) -> None:
        cur = cc.build_compile_cursor("sha256:x", 0)
        assert cur["lag_batches"] == 0
        assert cur["divergence_pending"] is False

    def test_contract_ref_points_to_spec(self) -> None:
        cur = cc.build_compile_cursor("sha256:x", 0)
        assert "cybertronia-graph-ui-spec.md" in cur["contract_ref"]["spec"]
        assert "row 4" in cur["contract_ref"]["section"]

    def test_verify_hint_explains_base_digest_exclusion(self) -> None:
        cur = cc.build_compile_cursor("sha256:x", 0)
        # New field — saves a future SSE implementer from "false divergence"
        # bugs by spelling out the recomputation rule explicitly.
        assert "verify_hint" in cur["contract_ref"]
        assert "WITHOUT its 'base_digest'" in cur["contract_ref"]["verify_hint"]


# ── 10. compile_from_telemetry end-to-end ──────────────────────────────────

class TestCompileFromTelemetry:
    TELEMETRY = {
        "scan_id":      "fedcba9876543210",
        "schema":       "cybertronia.telemetry/v1",
        "completed_at": "2026-07-14T00:00:00+00:00",
        "runtime": {
            "mem_total_mib": 16384.0,
            "mem_avail_mib": 16384.0,
            "volumes": [],
        },
        "nodes": [
            {"path": "bin/awaken.py",     "size": 1000, "mtime": 1_700_000_000.0, "kind": "file"},
            {"path": "bin/.env.local",    "size":  100, "mtime": 1_700_000_000.0, "kind": "file"},
            {"path": "control_plane/x",   "size": 2000, "mtime": 1_700_000_000.0, "kind": "file"},
        ],
    }

    def test_full_pipeline_produces_all_artifacts(self) -> None:
        artifacts = cc.compile_from_telemetry(
            self.TELEMETRY,
            now_iso="2026-07-14T00:00:00+00:00",
            received_at_ms=1_700_000_000_000,
        )
        for k in ("lattice", "delta", "entiremap", "cursor"):
            assert k in artifacts
            assert artifacts[k] is not None

    def test_pipeline_cursors_reflects_lattice_digest(self) -> None:
        artifacts = cc.compile_from_telemetry(
            self.TELEMETRY,
            now_iso="2026-07-14T00:00:00+00:00",
            received_at_ms=1_700_000_000_000,
        )
        # last_digest of compile_cursor MUST equal base_digest of lattice
        # so the consumer's atomic-swap can verify continuity (spec §4.3 step 2)
        assert artifacts["cursor"]["last_digest"] == artifacts["lattice"]["base_digest"]

    def test_delta_base_digest_is_lattice_digest(self) -> None:
        artifacts = cc.compile_from_telemetry(
            self.TELEMETRY,
            now_iso="2026-07-14T00:00:00+00:00",
            received_at_ms=1_700_000_000_000,
        )
        assert artifacts["delta"]["base_digest"] == artifacts["lattice"]["base_digest"]

    def test_pipeline_refuses_empty_scan_id(self) -> None:
        bad = dict(self.TELEMETRY, scan_id="   ")
        with pytest.raises(ValueError):
            cc.compile_from_telemetry(
                bad,
                now_iso="2026-07-14T00:00:00+00:00",
                received_at_ms=0,
            )

    def test_pipeline_handles_empty_nodes(self) -> None:
        bare = dict(self.TELEMETRY, nodes=[])
        artifacts = cc.compile_from_telemetry(
            bare,
            now_iso="2026-07-14T00:00:00+00:00",
            received_at_ms=1_700_000_000_000,
        )
        assert artifacts["lattice"]["vector_count"] == 0
        assert artifacts["delta"]["operations"] == []
        assert artifacts["cursor"]["last_digest"].startswith("sha256:")


# ── 11. publish_artifacts writes all four files atomically ─────────────────

class TestPublishArtifacts:
    TELEMETRY = {
        "scan_id":      "abcdef0123456789",
        "schema":       "cybertronia.telemetry/v1",
        "runtime":      {"mem_total_mib": 1024.0, "mem_avail_mib": 1024.0, "volumes": []},
        "nodes":        [
            {"path": "bin/awaken.py", "size": 1000, "mtime": 1_700_000_000.0, "kind": "file"},
        ],
    }

    def test_publish_writes_all_four_files(
        self, isolated_compile_root: Path,
    ) -> None:
        artifacts = cc.compile_from_telemetry(
            self.TELEMETRY,
            now_iso="2026-07-14T00:00:00+00:00",
            received_at_ms=1_700_000_000_000,
        )
        paths = cc.publish_artifacts(artifacts)
        for k, p in paths.items():
            assert Path(p).exists(), f"failed to write {k} → {p}"
        # round-trip parse of compile_cursor
        cur = json.loads(paths["compile_cursor"].read_text(encoding="utf-8"))
        assert cur["last_digest"].startswith("sha256:")

    def test_entiremap_marks_sensitive(
        self, isolated_compile_root: Path,
    ) -> None:
        artifacts = cc.compile_from_telemetry(
            dict(self.TELEMETRY, nodes=[
                {"path": "bin/.env.production", "size": 100, "mtime": 1_700_000_000.0, "kind": "file"},
                {"path": "bin/awaken.py",       "size": 1000,"mtime": 1_700_000_000.0, "kind": "file"},
            ]),
            now_iso="2026-07-14T00:00:00+00:00",
            received_at_ms=1_700_000_000_000,
        )
        paths = cc.publish_artifacts(artifacts)
        text = paths["entiremap"].read_text(encoding="utf-8")
        # .env.production gets [REDACTED] (basename mask)
        assert "[REDACTED]" in text
        # awaken.py is NOT redacted
        assert "bin/awaken.py" in text
        # absolute paths are NEVER produced (Phase 1 already root-relative)
        assert "C:\\" not in text
        assert ":/" not in text

    def test_atomic_write_cleans_up_its_own_tmp_on_exception(
        self, isolated_compile_root: Path,
    ) -> None:
        """atomic_write_json exception branch must unlink its own .tmp file.

        Patches ``os.replace`` to crash mid-write; ``mkstemp`` is spied to
        capture every <file>.<rand>.tmp the helper creates so we can assert
        none survive. This deliberately does NOT itself emit a leftover file
        (the earlier version of this test was buggy — it claimed to verify
        cleanup but actually self-published the leftover it asserted on).
        """
        import unittest.mock as mock
        captured_tmp: list[Path] = []
        real_mkstemp = cc.tempfile.mkstemp
        def _spy_mkstemp(*args, **kwargs):
            fd, name = real_mkstemp(*args, **kwargs)
            captured_tmp.append(Path(name))
            return fd, name
        def _crash_on_replace(src, dst):
            raise OSError("simulated crash during os.replace")
        with mock.patch.object(cc.tempfile, "mkstemp", _spy_mkstemp), \
             mock.patch.object(cc.os, "replace", _crash_on_replace):
            with pytest.raises(OSError, match="simulated crash during os.replace"):
                cc.atomic_write_json(cc.LATTICE_VECTORS, {"x": 1, "y": 2})
        assert captured_tmp, "atomic_write_json never called mkstemp; test rigged"
        survivors = [p for p in captured_tmp if p.exists()]
        assert survivors == [], (
            f"atomic_write_json left orphan .tmp file(s) on exception: {survivors}"
        )


# ── 12. compile_from_phase1_path: missing telemetry raises ─────────────────

class TestCompileFromPhase1Path:
    def test_missing_telemetry_raises(self, isolated_compile_root: Path) -> None:
        with pytest.raises(FileNotFoundError):
            cc.compile_from_phase1_path(cc.PHASE1_TELEMETRY, publish=False)

    def test_invalid_json_raises(self, isolated_compile_root: Path) -> None:
        cc.PHASE1_TELEMETRY.write_text("{ not valid json", encoding="utf-8")
        with pytest.raises(ValueError):
            cc.compile_from_phase1_path(cc.PHASE1_TELEMETRY, publish=False)

    def test_publishes_to_ph2_when_publish_true(
        self, isolated_compile_root: Path,
    ) -> None:
        cc.PHASE1_TELEMETRY.write_text(json.dumps({
            "scan_id": "0123456789abcdef",
            "runtime": {"mem_total_mib": 1024.0, "mem_avail_mib": 1024.0, "volumes": []},
            "nodes":   [
                {"path": "bin/awaken.py", "size": 1000, "mtime": 1_700_000_000.0, "kind": "file"},
            ],
        }), encoding="utf-8")
        artifacts = cc.compile_from_phase1_path(cc.PHASE1_TELEMETRY, publish=True)
        assert "_published_paths" in artifacts
        assert (isolated_compile_root / "phase2" / "lattice_vectors.json").exists()


# ── 13. read_compile_cursor returns None when cursor absent ────────────────

def test_read_compile_cursor_returns_none_when_absent(
    isolated_compile_root: Path,
) -> None:
    assert cc.read_compile_cursor() is None


def test_read_compile_cursor_round_trips(isolated_compile_root: Path) -> None:
    cc.publish_artifacts(cc.compile_from_telemetry(
        {"scan_id": "round_trip_x", "runtime": {}, "nodes": []},
        now_iso="2026-07-14T00:00:00+00:00",
        received_at_ms=1,
    ))
    cur = cc.read_compile_cursor()
    assert cur is not None
    assert "last_digest" in cur
    assert cur["last_digest"].startswith("sha256:")
