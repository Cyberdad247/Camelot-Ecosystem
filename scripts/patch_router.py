# SPDX-License-Identifier: MIT

from pathlib import Path


def patch_router():
    path = Path("control_plane/runic_router.py")
    content = path.read_text(encoding="utf-8")
    
    # 1. Add new runic commands
    old_cmds = '''    "//NANO_SWARM_EXPAND": {
        "knight": "sir_boris",
        "description": "6-phase UKG_NANO_SWARM_V1000 expansion: SAT-gate → CvRDT mesh → Ouroboros seed → Aegis bind → AST audit → Anya seal",
        "mode": "SWARM",
        "priority": 1,
        "handler": "_handle_nano_swarm_expand",
    },
}'''
    new_cmds = '''    "//NANO_SWARM_EXPAND": {
        "knight": "sir_boris",
        "description": "6-phase UKG_NANO_SWARM_V1000 expansion: SAT-gate → CvRDT mesh → Ouroboros seed → Aegis bind → AST audit → Anya seal",
        "mode": "SWARM",
        "priority": 1,
        "handler": "_handle_nano_swarm_expand",
    },
    "//BIFROST_LOCK": {
        "knight": "sir_heimdall",
        "description": "Emergency Bifrost perimeter lockdown",
        "mode": "SENTINEL",
        "priority": 1,
        "handler": "_handle_bifrost_lock",
    },
    "//SCAN_VECTORS": {
        "knight": "sir_heimdall",
        "description": "Deep 4-vector fingerprint scan",
        "mode": "SENTINEL",
        "priority": 2,
        "handler": "_handle_scan_vectors",
    },
}'''
    
    # Normalize line endings for replacement
    content = content.replace(old_cmds.replace('\n', '\r\n'), new_cmds.replace('\n', '\r\n'))
    content = content.replace(old_cmds, new_cmds)
    
    # 2. Add Omega_BIFROST
    old_omega = '''    "Omega_CODEX":      {"knight": "sir_codex",    "description": "Direct SIR_CODEX execution lane"},
}'''
    new_omega = '''    "Omega_CODEX":      {"knight": "sir_codex",    "description": "Direct SIR_CODEX execution lane"},
    "Omega_BIFROST":    {"knight": "sir_heimdall", "description": "Bifrost Sentinel operations"},
}'''
    content = content.replace(old_omega.replace('\n', '\r\n'), new_omega.replace('\n', '\r\n'))
    content = content.replace(old_omega, new_omega)
    
    # 3. Add handlers
    old_handlers = '''def _handle_think(param: str, context: dict) -> dict:
    return {"action": "got_reasoning", "param": param, "knight": "merlin_omega"}'''
    
    new_handlers = '''def _handle_think(param: str, context: dict) -> dict:
    return {"action": "got_reasoning", "param": param, "knight": "merlin_omega"}

def _handle_bifrost_lock(param: str, context: dict) -> dict:
    return {"action": "bifrost_lockdown", "status": "AIR_GAPPED"}

def _handle_scan_vectors(param: str, context: dict) -> dict:
    return {"action": "4_vector_scan", "target": param or "project_root"}'''
    
    content = content.replace(old_handlers.replace('\n', '\r\n'), new_handlers.replace('\n', '\r\n'))
    content = content.replace(old_handlers, new_handlers)
    
    # 4. Update handler map
    old_map = '''    "_handle_think": _handle_think,
    "_handle_nano_swarm_expand": _handle_nano_swarm_expand,'''
    new_map = '''    "_handle_think": _handle_think,
    "_handle_bifrost_lock": _handle_bifrost_lock,
    "_handle_scan_vectors": _handle_scan_vectors,
    "_handle_nano_swarm_expand": _handle_nano_swarm_expand,'''
    
    content = content.replace(old_map.replace('\n', '\r\n'), new_map.replace('\n', '\r\n'))
    content = content.replace(old_map, new_map)
    
    path.write_text(content, encoding="utf-8", newline='\n')
    print("Runic Router patched.")

if __name__ == "__main__":
    patch_router()
