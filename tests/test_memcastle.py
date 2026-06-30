"""Tests for MemCastle — the sqlite-vec local vector store."""
import importlib.util
import sys
from pathlib import Path

import pytest

_MC_PATH = Path(__file__).resolve().parent.parent / "control_plane" / "memcastle.py"
_spec = importlib.util.spec_from_file_location("memcastle", _MC_PATH)
memcastle = importlib.util.module_from_spec(_spec)
sys.modules["memcastle"] = memcastle
_spec.loader.exec_module(memcastle)


@pytest.fixture()
def castle(tmp_path):
    mc = memcastle.MemCastle(db_path=tmp_path / "mc.db", dim=128)
    yield mc
    mc.close()


def test_store_and_count(castle):
    castle.store("forge the cybertronia server", source="phase2", knight="codex")
    castle.store("wire runes to rust engines", source="phase3", knight="codex")
    assert castle.count() == 2


def test_knn_returns_nearest_first(castle):
    castle.store("deploy the go router via tailscale funnel", source="net")
    castle.store("strip context noise with the rust rtk engine", source="kinetic")
    castle.store("bananas and fruit smoothies", source="noise")
    hits = castle.search("rust engine for stripping noise", k=3)
    assert len(hits) == 3
    # The kinetic/rtk doc should rank above the unrelated smoothie doc.
    ranks = {h["text"]: i for i, h in enumerate(hits)}
    assert ranks["strip context noise with the rust rtk engine"] < ranks["bananas and fruit smoothies"]
    # distances are sorted ascending (nearest first)
    dists = [h["distance"] for h in hits]
    assert dists == sorted(dists)


def test_persists_across_reopen(tmp_path):
    p = tmp_path / "persist.db"
    mc1 = memcastle.MemCastle(db_path=p, dim=64)
    mc1.store("persistent knowledge crystal", source="vault")
    mc1.close()
    mc2 = memcastle.MemCastle(db_path=p, dim=64)
    assert mc2.count() == 1
    assert mc2.search("knowledge", k=1)[0]["text"] == "persistent knowledge crystal"
    mc2.close()


def test_dim_mismatch_rejected(castle):
    with pytest.raises(ValueError):
        castle.store("bad", embedding=[0.0] * 999)
