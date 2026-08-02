# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# Add KERNEL to path to import UKGRuntime
import importlib.util
import json
import os
from pathlib import Path

# Dynamically import UKGRuntime to handle '01_KERNEL' directory name
spec = importlib.util.spec_from_file_location(
    "ukg_runtime", 
    os.path.join(os.getcwd(), "01_KERNEL", "Engines", "ukg_runtime.py")
)
ukg_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ukg_module)
UKGRuntime = ukg_module.UKGRuntime

def harvest_persona_library():
    ukg = UKGRuntime()
    library_path = Path("03_VAULT/knowledge/persona_library")
    library_path.mkdir(parents=True, exist_ok=True)
    
    core_roles = [
        "System Engineer",
        "Security Auditor",
        "Strategy Oracle",
        "UX Guardian",
        "Legal Lawkeeper",
        "Kinetic Architect",
        "Swarm Conductor"
    ]
    
    inventory = []
    
    for role in core_roles:
        print(f"🧙‍♂️ Merlin forging persona: {role}...")
        payload = ukg.execute(f"Forge persona for {role}", mode="LOWER")
        manifest = payload["tal_manifest"]
        
        # Add metadata for JSON-LD compliance
        manifest["@context"] = "https://schema.org"
        manifest["@type"] = "SoftwareAgent"
        manifest["name"] = role
        
        file_name = role.lower().replace(" ", "_") + ".jsonld"
        file_path = library_path / file_name
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
            
        inventory.append({
            "role": role,
            "id": manifest["root"]["id"],
            "file": str(file_path)
        })
    
    # Create Registry index
    registry = {
        "title": "Merlin v2 Persona Registry",
        "version": "2.0.0",
        "personas": inventory
    }
    
    with open(library_path / "registry_index.json", 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)

    print(f"✅ Persona Library Harvested: {len(inventory)} experts specialized.")

if __name__ == "__main__":
    try:
        harvest_persona_library()
    except Exception as e:
        print(f"❌ Error harvesting library: {e}")
        # Fallback if import fails due to path issues
        os.makedirs("03_VAULT/knowledge/persona_library", exist_ok=True)
        print("Manual directory creation fallback triggered.")