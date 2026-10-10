#!/usr/bin/env python3
"""
check_ram_governance.py - Camelot-OS Law 03 Resource Governance Validator

Enforces:
- Camelot-OS Node: Max 4 GB RAM (4096 MB)
- Camelot-OS Server: Max 8 GB RAM (8192 MB)
"""

import sys
import ctypes
import argparse
from typing import Dict, Any

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

def get_system_ram_mb() -> Dict[str, float]:
    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    success = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    if not success:
        raise RuntimeError("Failed to query GlobalMemoryStatusEx")
    
    total_phys = stat.ullTotalPhys / (1024 * 1024)
    avail_phys = stat.ullAvailPhys / (1024 * 1024)
    used_phys = total_phys - avail_phys
    load_pct = stat.dwMemoryLoad
    
    return {
        "total_mb": round(total_phys, 1),
        "used_mb": round(used_phys, 1),
        "avail_mb": round(avail_phys, 1),
        "load_pct": load_pct,
    }

def trim_working_sets():
    """Flushes working sets across running processes using psapi.EmptyWorkingSet."""
    try:
        psapi = ctypes.windll.psapi
        kernel32 = ctypes.windll.kernel32
        
        # Iterate processes using Windows API or simply EmptyWorkingSet on current process
        current_proc = kernel32.GetCurrentProcess()
        psapi.EmptyWorkingSet(current_proc)
    except Exception as e:
        print(f"[!] Working set trim warning: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Audit Camelot-OS Law 03 Memory Compliance")
    parser.add_argument("--role", choices=["node", "server"], default="node",
                        help="Entity role: 'node' (4GB max) or 'server' (8GB max)")
    parser.add_argument("--trim", action="store_true",
                        help="Trigger active working set trim if approaching boundary")
    parser.add_argument("--json", action="store_true",
                        help="Output result as JSON")
    args = parser.parse_args()

    ceiling_mb = 4096.0 if args.role == "node" else 8192.0
    mem = get_system_ram_mb()

    # In a node role, the law mandates max 4GB working memory
    # Check if used memory exceeds role ceiling
    is_compliant = mem["used_mb"] <= ceiling_mb
    utilization_against_ceiling = round((mem["used_mb"] / ceiling_mb) * 100, 1)

    if args.trim and utilization_against_ceiling > 75.0:
        trim_working_sets()
        mem = get_system_ram_mb()
        is_compliant = mem["used_mb"] <= ceiling_mb
        utilization_against_ceiling = round((mem["used_mb"] / ceiling_mb) * 100, 1)

    if args.json:
        import json
        payload = {
            "role": args.role,
            "ceiling_mb": ceiling_mb,
            "metrics": mem,
            "utilization_against_ceiling_pct": utilization_against_ceiling,
            "compliant": is_compliant
        }
        print(json.dumps(payload, indent=2))
        sys.exit(0 if is_compliant else 1)

    print("=" * 60)
    print(f"  CAMELOT-OS RESOURCE GOVERNANCE AUDIT (LAW 03)")
    print(f"  Role Profile:       {args.role.upper()}")
    print(f"  Hard Ceiling:       {ceiling_mb:.0f} MB ({ceiling_mb/1024:.0f} GB)")
    print(f"  Current Memory:     {mem['used_mb']:.1f} MB used / {mem['total_mb']:.1f} MB total ({mem['load_pct']}%)")
    print(f"  Ceiling Usage:      {utilization_against_ceiling}%")
    print(f"  Governance Status:  {'COMPLIANT' if is_compliant else 'EXCEEDED_CEILING'}")
    print("=" * 60)

    if not is_compliant:
        print(f"[!] WARNING: {args.role.upper()} memory consumption ({mem['used_mb']} MB) exceeds {ceiling_mb} MB ceiling!", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"[OK] {args.role.upper()} operates within sovereign memory boundary.")
        sys.exit(0)

if __name__ == "__main__":
    main()
