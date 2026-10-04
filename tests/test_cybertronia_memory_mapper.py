# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import pytest
from pathlib import Path
from scripts.ops.cybertronia_memory_mapper import (
    CybertroniaMemoryMapper,
    categorize_process,
    ProcessMemoryRecord,
    MemoryTopologyMap,
)


def test_categorize_process():
    assert categorize_process("agy") == "CAMELOT_AGENTIC_SUITE"
    assert categorize_process("python.exe") == "CAMELOT_AGENTIC_SUITE"
    assert categorize_process("MsMpEng") == "SECURITY_AV"
    assert categorize_process("chrome") == "BROWSERS_WEBVIEW"
    assert categorize_process("tailscaled") == "HARDWARE_OEM_UTILITIES"
    assert categorize_process("explorer") == "WINDOWS_CORE_SYSTEM"


def test_mapper_generation(tmp_path):
    mapper = CybertroniaMemoryMapper(home=tmp_path)
    topo = mapper.generate_map(execute_trim=False)
    assert isinstance(topo, MemoryTopologyMap)
    assert topo.total_physical_mb > 0
    assert topo.free_physical_mb > 0
    assert len(topo.categories) > 0
    assert (tmp_path / "03_VAULT" / "runtime_state" / "cybertronia_memory_map.json").exists()
