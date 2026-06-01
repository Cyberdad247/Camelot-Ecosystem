# -*- coding: utf-8 -*-
import json
import os
from pathlib import Path

UKG_DIR = Path("C:/Users/vizio/CAMELOT_OS/03_VAULT/UKG/nodes")

def compress_to_toon(node_data: dict) -> str:
    """Simple TOON_v2-like compression: key:val | key2:val2"""
    # Just a conceptual compression for now: strip JSON-LD overhead
    ukg = node_data.get("UKG_NODE", node_data)
    items = []
    for k, v in ukg.items():
        if isinstance(v, list):
            val = ",".join([str(i) for i in v[:3]]) # limit lists
        else:
            val = str(v)
        items.append(f"{k.lower()}:{val}")
    return " | ".join(items)

def main():
    if not UKG_DIR.exists():
        print("UKG dir not found.")
        return
        
    for f in UKG_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            toon = compress_to_toon(data)
            toon_file = f.with_suffix(".toon")
            toon_file.write_text(toon, encoding="utf-8")
            print(f"✅ Compressed: {f.name} -> {toon_file.name}")
        except Exception as e:
            print(f"❌ Error compressing {f.name}: {e}")

if __name__ == "__main__":
    main()
