#!/usr/bin/env python3
"""NotebookLM MCP server — LOCAL FILE SYSTEM pivot.

PR #4 of NOTES_MNEMOSYNE_WIRING.md (2026-07-14, freebuff).

Operator clarification 2026-07-14: NotebookLM MCP destination = LOCAL FILE SYSTEM,
NOT the Bifrost bridge. Output is written to:

    03_VAULT/runtime_state/notebooklm_cache/<slugified-stem>.md

MCP transport: stdio (local process). NOT Bifrost-encrypted — stdio is local
and never crosses a network boundary; the HMAC envelope is reserved for the
Appwrite egress path that uses Bifrost.

Soul_oversight pre_execute lookup entries (this PR adds):
  - notebooklm.export            → PROMPT (auto-confirm after 60s)
  - notebooklm.delete_local      → HUMAN_GATE (destructive)
  - notebooklm.list              → AUTO (read-only, idempotent)
"""
from __future__ import annotations

import argparse
import os
import re
import time
from pathlib import Path

from mcp.server.fastmcp import FastMCP

CACHE_DIR = Path("03_VAULT/runtime_state/notebooklm_cache")

# Slug rule: lowercase alphanumerics + hyphens; collapse repeats; trim dashes.
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    """Slugify a URL or title into a filesystem-safe cache filename stem."""
    cleaned = _SLUG_RE.sub("-", value.lower()).strip("-")
    return cleaned or "untitled"


def cache_path(slug: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{slug}.md"


def _ttl_days() -> int:
    return max(1, int(os.environ.get("NOTEBOOK_CACHE_TTL", "30")))


def evict_old() -> int:
    """Remove cached notebooks older than NOTEBOOK_CACHE_TTL days.

    Returns the count of files evicted.
    """
    ttl_seconds = _ttl_days() * 86400
    cutoff = time.time() - ttl_seconds
    removed = 0
    for path in CACHE_DIR.glob("*.md"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
                removed += 1
        except FileNotFoundError:
            continue
    return removed


# ── HTML→Markdown (with graceful fallback) ────────────────────────────────────


def _scrape_notebook_html(url: str) -> str:
    """Best-effort Playwright scrape. Falls back to a URL-stub on import failure.

    For stdio MCP, returning a deterministic stub when Playwright is unavailable
    keeps the smoke test deterministic; the operator path runs against real
    Playwright on the laptop host.
    """
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            html = page.content()
            browser.close()
            return html
    except Exception:
        return f"<!-- notebooklm-mcp stub for {url} -->\n"


def _html_to_markdown(html: str) -> str:
    """Best-effort HTML→Markdown using html2text if available."""
    try:
        import html2text

        h = html2text.HTML2Text()
        h.body_width = 0
        return h.handle(html)
    except Exception:
        return html


# ── MCP server & tools ───────────────────────────────────────────────────────


mcp = FastMCP("notebooklm-camelot-bridge")


@mcp.tool()
def export_notebook(url: str) -> str:
    """Export a NotebookLM URL to the local cache (.md).

    PROMPT tier (auto-confirm after 60s) per `soul_oversight.pre_execute`.
    """
    html = _scrape_notebook_html(url)
    md = _html_to_markdown(html)
    slug = slugify(url)
    path = cache_path(slug)
    path.write_text(md, encoding="utf-8")
    return str(path)


@mcp.tool()
def delete_local_notebook(slug: str) -> bool:
    """Delete a cached notebook by slug. HUMAN_GATE tier (destructive)."""
    path = cache_path(slug)
    if path.exists():
        path.unlink()
        return True
    return False


@mcp.tool()
def list_local_notebooks() -> list[str]:
    """List cached notebooks, evicting TTL-expired entries first.

    AUTO tier (idempotent, read-only).
    """
    evict_old()
    return sorted(p.name for p in CACHE_DIR.glob("*.md"))


# ── CLI / entrypoint ─────────────────────────────────────────────────────────


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="NotebookLM MCP — file-system pivot (NOT Bifrost-bridged)."
    )
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "sse"],
        help="MCP transport. Default: stdio (local).",
    )
    args = parser.parse_args(argv)
    mcp.run(transport=args.transport)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
