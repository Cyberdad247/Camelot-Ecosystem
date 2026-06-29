import sys
from pathlib import Path

# Add vault configs to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "03_VAULT" / "training" / "configs"))
from knights.sentinel import SirSentinel

def main():
    sentinel = SirSentinel()
    # Runs the full security audit and writes to logs/sentinel_audit_latest.md
    res = sentinel.execute("Omega_AUDIT", {}, write=True)
    print("Audit status:", res.get("status"))
    if "files_created" in res:
        print("Created report file(s):", res["files_created"])

if __name__ == "__main__":
    main()
