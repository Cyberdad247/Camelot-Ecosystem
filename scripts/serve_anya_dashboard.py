"""Serve the built Anya Dashboard with SPA route fallback."""

from __future__ import annotations

import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIST = REPO_ROOT / "02_FORGE" / "PORTAL_CORE" / "Anya_Dashboard" / "dist"


class SpaHandler(SimpleHTTPRequestHandler):
    """Static file handler that falls back to index.html for client routes."""

    def send_head(self):  # noqa: N802 - stdlib override
        requested = Path(self.translate_path(self.path))
        if requested.exists() or "." in Path(self.path.split("?", 1)[0]).name:
            return super().send_head()
        self.path = "/index.html"
        return super().send_head()


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve Anya Dashboard dist with SPA fallback.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5173)
    parser.add_argument("--dist", type=Path, default=DEFAULT_DIST)
    args = parser.parse_args()

    dist = args.dist.resolve()
    if not (dist / "index.html").exists():
        raise SystemExit(f"Missing built dashboard at {dist}. Run npm run build in Anya_Dashboard first.")

    handler = functools.partial(SpaHandler, directory=str(dist))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Anya Dashboard serving {dist} at http://{args.host}:{args.port}/", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
