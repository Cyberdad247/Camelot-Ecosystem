# SPDX-License-Identifier: MIT

import json

from control_plane.provenance import VerificationRun


def debug():
    data = {
        "run_id": "run_1",
        "timestamp_utc": "2026-05-23T11:00:00Z",
        "operator": "sir_helio",
        "command": "ls",
        "results": {},
        "success": True,
        "entry_id": 1,
        "parent_hash": None,
        "entry_hash": "dummy"
    }
    
    run = VerificationRun(**data)
    run.compute_hash()
    
    print(f"Data in: {data}")
    
    # Dump for hash
    dumped = run.model_dump(exclude={"entry_hash"})
    print(f"Dumped for hash: {dumped}")
    
    json_str = json.dumps(dumped, sort_keys=True)
    print(f"JSON str: {json_str}")
    
    # Check if entry_hash was removed
    if "entry_hash" in dumped:
        print("FAIL: entry_hash still in dump!")
    else:
        print("OK: entry_hash excluded.")
        
if __name__ == "__main__":
    debug()
