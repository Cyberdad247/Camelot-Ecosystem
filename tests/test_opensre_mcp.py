import pytest
import importlib.util
import unittest.mock
from pathlib import Path

def test_opensre_mcp_integration():
    repo_root = Path(__file__).resolve().parent.parent
    module_path = repo_root / "control_plane" / "symbiotic_maintenance.py"
    spec = importlib.util.spec_from_file_location("symbiotic_maintenance", module_path)
    sm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sm)
    
    # Check if MCPHiveLink class exists
    if not hasattr(sm, "MCPHiveLink"):
        pytest.fail("MCPHiveLink class not found in symbiotic_maintenance.py")
    
    link = sm.MCPHiveLink(endpoint="http://localhost:8080/mcp")
    assert link.endpoint == "http://localhost:8080/mcp"
    
    # Test query (should return a mock or actual response if server is up)
    # We'll use a mock for the unit test
    class MockResponse:
        def json(self): return {"status": "HEALTHY", "pods": 12}
        @property
        def status_code(self): return 200
        
    with unittest.mock.patch("requests.post", return_value=MockResponse()):
        result = link.query_cluster("list pods")
        assert result["status"] == "HEALTHY"
        assert result["pods"] == 12
