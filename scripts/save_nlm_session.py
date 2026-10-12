"""
Headed Playwright re-auth using the notebooklm browser_profile.
The profile has DPAPI-encrypted Google cookies that Playwright can use in headed mode.
Auto-detects login completion and saves session.
"""
import asyncio
import time
from pathlib import Path

from playwright.async_api import async_playwright

STORAGE = Path.home() / ".notebooklm" / "storage_state.json"
PROFILE  = Path.home() / ".notebooklm" / "browser_profile"
STORAGE.parent.mkdir(parents=True, exist_ok=True)

async def main():
    async with async_playwright() as p:
        print(f"Launching with profile: {PROFILE}")
        ctx = await p.chromium.launch_persistent_context(
            str(PROFILE),
            headless=False,
            args=["--no-sandbox", "--disable-gpu"],
            slow_mo=500,
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        print("Navigating to NotebookLM...")
        await page.goto("https://notebooklm.google.com", timeout=60000)

        print("Waiting for auth (may need Google sign-in in browser)...")
        deadline = time.time() + 180  # 3 min
        while time.time() < deadline:
            url = page.url
            if "notebooklm.google.com" in url and "accounts.google.com" not in url and "/login" not in url:
                # Check that actual notebook content loaded (not just a redirect page)
                await asyncio.sleep(2)
                if "notebooklm.google.com" in page.url:
                    break
            await asyncio.sleep(2)
            print(f"  URL: {page.url[:80]}")
        else:
            print("Timeout — closing")
            await ctx.close()
            return

        print("Authenticated — saving session...")
        await page.wait_for_load_state("networkidle", timeout=10000)
        await ctx.storage_state(path=str(STORAGE))
        sz = STORAGE.stat().st_size
        print(f"Saved: {STORAGE} ({sz:,} bytes)")
        await ctx.close()
        print("Done.")

asyncio.run(main())
