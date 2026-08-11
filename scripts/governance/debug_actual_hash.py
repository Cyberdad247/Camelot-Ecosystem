import json

from control_plane.infra.provenance import VerificationRun


def debug_actual():
    line = '{"run_id": "run_1776212438", "timestamp_utc": "2026-04-15T00:20:38.970464+00:00", "operator": "default", "command": "cloudbrain status", "results": {"id": "887d96d00609", "type": "status", "source": "control_plane", "target": "user", "timestamp": "2026-04-15T00:20:38.861682+00:00", "payload": {"status": "COMPLETE", "task": "cloudbrain status", "service": "cloudbrain_status", "source": "local", "result": {"service": "long_term_cloudbrain", "repo_root": "C:\\\\Users\\\\vizio\\\\CAMELOT_OS", "open_notebook_root": "C:\\\\Users\\\\vizio\\\\CAMELOT_OS\\\\01_KERNEL\\\\agora\\\\Squires\\\\open_notebook", "notebook_api_root": "C:\\\\Users\\\\vizio\\\\CAMELOT_OS\\\\01_KERNEL\\\\agora\\\\Squires\\\\Notebook_Brain", "runtime": {"api_base_url": "http://127.0.0.1:5055", "surreal_url": "ws://localhost:8000/rpc", "surreal_user": "root", "surreal_pass": "root", "surreal_namespace": "camelot", "surreal_database": "notebook"}, "appwrite": {"configured": false, "database_id": "sovereign_db", "collection_id": "memory_spine", "endpoint_present": false, "project_present": false, "api_key_present": false}}, "error": null}, "correlation_id": "9970e4d389fd"}, "success": true, "entry_id": 1, "parent_hash": null, "entry_hash": "ec12fc828f9626639ad5d6636136f3c02af19618dfbac1d801254b1b94e4d6d6"}'
    
    data = json.loads(line)
    stored_hash = data.get("entry_hash")
    
    run = VerificationRun(**data)
    computed_hash = run.compute_hash()
    
    print(f"Stored:   {stored_hash}")
    print(f"Computed: {computed_hash}")
    
    if stored_hash == computed_hash:
        print("MATCH!")
    else:
        print("MISMATCH!")
        # Find the difference
        dumped = run.model_dump(exclude={"entry_hash"})
        # We need to compare against the data without entry_hash
        data_to_compare = data.copy()
        data_to_compare.pop("entry_hash")
        
        # Sort both
        s1 = json.dumps(dumped, sort_keys=True)
        s2 = json.dumps(data_to_compare, sort_keys=True)
        
        if s1 == s2:
            print("Strings match, but hash doesn't? Impossible.")
        else:
            print("String Mismatch!")
            print(f"Dumped: {s1}")
            print(f"Orig:   {s2}")

if __name__ == "__main__":
    debug_actual()
