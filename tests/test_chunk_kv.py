import pytest
from 01_KERNEL.memory.chunk_kv import ChunkKVPolicy

def test_chunk_kv_boundary_integrity():
    policy = ChunkKVPolicy()
    text = "Merlin is wise. Arthur is king. Fragment"
    # Should prune to full sentences only
    pruned = policy.prune(text)
    assert pruned == "Merlin is wise. Arthur is king."

def test_chunk_kv_no_boundary():
    policy = ChunkKVPolicy()
    text = "No boundary here"
    assert policy.prune(text) == "No boundary here"

def test_chunk_kv_multiple_boundaries():
    policy = ChunkKVPolicy()
    text = "Sentence one! Sentence two? Fragment"
    assert policy.prune(text) == "Sentence one! Sentence two?"
