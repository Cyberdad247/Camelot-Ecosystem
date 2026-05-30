"""EXCALIBUR CLI :: LUKAS_FORGE entrypoint. [STATUS: WIRED skeleton]"""
from __future__ import annotations
import argparse, os, subprocess, sys
from . import __version__
from .pii import redact, scan, dispatch_integrated_route

CORE = os.path.join(os.path.dirname(__file__), "..", "..", "core")

def _preflight(_a) -> int:
    root = os.environ.get("EXCALIBUR_ROOT", os.path.dirname(os.path.abspath(CORE)))
    env = {**os.environ, "EXCALIBUR_ROOT": root}
    subprocess.run(["bash", os.path.join(CORE, "excalibur_audit.sh")],
                   env=env, stdout=subprocess.DEVNULL)
    return subprocess.run(["bash", os.path.join(CORE, "excalibur_adjudicate.sh")], env=env).returncode

def _redact(a) -> int:
    print(redact(sys.stdin.read() if a.text == "-" else a.text)); return 0

def _scan(a) -> int:
    print(scan(sys.stdin.read() if a.text == "-" else a.text)); return 0

def _route(a) -> int:
    result = dispatch_integrated_route(a.intent)
    if result["success"]:
        print(f"[ROUTE:SUCCESS] knight='{result['knight_id']}' confidence={result['confidence']}")
        print(f"  Flow: {result['integrated_flow']}")
        print(f"  Mem:  {result['memory_status']} (KV_GROWTH={result['kv_growth']})")
        return 0
    else:
        print(f"[ROUTE:FAILED] {result['error']}")
        return 1

def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="excalibur", description="EXCALIBUR LUKAS_FORGE CLI")
    p.add_argument("--version", action="version", version=f"excalibur {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("preflight", help="run pre-flight GO/NO-GO gate").set_defaults(fn=_preflight)
    r = sub.add_parser("redact", help="redact PII from text"); r.add_argument("text", nargs="?", default="-"); r.set_defaults(fn=_redact)
    s = sub.add_parser("scan", help="count PII in text");      s.add_argument("text", nargs="?", default="-"); s.set_defaults(fn=_scan)
    rt = sub.add_parser("route", help="runic route an intent"); rt.add_argument("intent"); rt.set_defaults(fn=_route)
    a = p.parse_args(argv)
    return a.fn(a)

if __name__ == "__main__":
    raise SystemExit(main())
