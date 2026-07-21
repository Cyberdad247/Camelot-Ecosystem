"""Tests for Graphify — NL triplet extraction + MemCastle ingestion."""
import importlib.util
import sys
from pathlib import Path

import pytest

_CP = Path(__file__).resolve().parent.parent / "control_plane"


def _load(name, subdir="infra"):
    spec = importlib.util.spec_from_file_location(name, _CP / subdir / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


memcastle = _load("memcastle")
graphify = _load("graphify")


def _rels(triplets):
    return {(t.head.lower(), t.relation, t.tail.lower()) for t in triplets}


def test_copula_triplet():
    t = graphify.extract_triplets("go_router is a Go SSE daemon")
    assert ("go_router", "is_a", "go sse daemon") in _rels(t)


def test_relation_verb_triplet():
    t = graphify.extract_triplets("The supervisor restarts the daemons.")
    rels = _rels(t)
    assert ("supervisor", "restart", "daemons") in rels


def test_depends_on():
    t = graphify.extract_triplets("MemCastle depends on sqlite-vec")
    assert ("memcastle", "depends_on", "sqlite-vec") in _rels(t)


def test_multi_sentence():
    text = "Graphify uses MemCastle. NotebookLM is a cloud brain."
    rels = _rels(graphify.extract_triplets(text))
    assert ("graphify", "use", "memcastle") in rels
    assert ("notebooklm", "is_a", "cloud brain") in rels


def test_no_false_triplet_without_verb():
    assert graphify.extract_triplets("cybertronia tailnet node") == []


def test_ingest_and_query_pipeline(tmp_path):
    mc = memcastle.MemCastle(db_path=tmp_path / "gf.db", dim=128)
    gf = graphify.Graphify(memcastle=mc)
    triplets = gf.ingest(
        "go_router wires runes to the rust rtk engine. The tunnel exposes cybertronia.",
        source="phase3",
    )
    assert len(triplets) >= 1
    # stored triplets are searchable
    hits = gf.query("rust engine", k=3)
    assert any("rtk" in h["text"].lower() or "rust" in h["text"].lower() for h in hits)
    assert mc.count() == len(triplets)
    gf.close()


def test_pluggable_extractor(tmp_path):
    mc = memcastle.MemCastle(db_path=tmp_path / "p.db", dim=64)
    fake = lambda text: [graphify.Triplet("x", "rel", "y")]
    gf = graphify.Graphify(memcastle=mc, extractor=fake)
    ts = gf.ingest("anything at all")
    assert ts == [graphify.Triplet("x", "rel", "y")]
    assert mc.count() == 1
    gf.close()
