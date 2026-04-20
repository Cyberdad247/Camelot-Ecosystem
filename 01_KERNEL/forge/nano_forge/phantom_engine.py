# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
PHANTOM ENGINE v2.0: Multi-Login Clone
Advanced anti-detect browser driver with rich fingerprinting.
"""

import json
import os
from typing import Dict, Optional

from playwright.async_api import BrowserContext, async_playwright

try:
    from nano_forge.profile_manager import ProfileManager
except ImportError:
    from profile_manager import ProfileManager


class PhantomEngine:
    def __init__(self, profile_manager: ProfileManager = None):
        self.profile_manager = profile_manager or ProfileManager()

        # Load injection script
        injection_path = os.path.join(os.path.dirname(__file__), "phantom_injection.js")
        with open(injection_path, "r") as f:
            self.injection_script = f.read()

    async def launch_context(
        self, p, profile_id: str, headless: bool = True, proxy: Optional[Dict] = None
    ) -> BrowserContext:
        """Launches browser context with profile-specific fingerprint.

        Prefers Lightpanda CDP (ws://127.0.0.1:9222) when available,
        falls back to local Chromium launch. Set CAMELOT_USE_LIGHTPANDA=0 to disable.
        """

        # Load fingerprint
        fingerprint = self.profile_manager.load_profile(profile_id)
        profile_dir = self.profile_manager.get_profile_path(profile_id)

        print(f"[PHANTOM v2.0] Spawning Context: {profile_id}")

        # Prefer Lightpanda CDP to avoid local Chromium RAM overhead
        lightpanda_cdp = os.environ.get("LIGHTPANDA_CDP_URL", "http://127.0.0.1:9222")
        use_lightpanda = os.environ.get("CAMELOT_USE_LIGHTPANDA", "1") == "1"

        if use_lightpanda:
            try:
                browser = await p.chromium.connect_over_cdp(lightpanda_cdp)
                print(f"[PHANTOM v2.0] Connected to Lightpanda CDP at {lightpanda_cdp}")
            except Exception as e:
                print(f"[PHANTOM v2.0] Lightpanda unavailable ({e}), falling back to local Chromium")
                browser = await p.chromium.launch(headless=headless)
        else:
            browser = await p.chromium.launch(headless=headless)

        # Context config from fingerprint
        context_options = {
            "user_agent": fingerprint.get("user_agent"),
            "viewport": fingerprint.get("viewport"),
            "locale": fingerprint.get("locale"),
            "timezone_id": fingerprint.get("timezone"),
            "geolocation": fingerprint.get("geolocation"),
            "permissions": ["geolocation"] if fingerprint.get("geolocation") else [],
            "storage_state": (
                str(profile_dir / "storage_state.json") if (profile_dir / "storage_state.json").exists() else None
            ),
        }

        # Add proxy if provided
        if proxy:
            context_options["proxy"] = proxy

        context = await browser.new_context(**{k: v for k, v in context_options.items() if v is not None})

        # INJECTION: Load full fingerprint script with profile config
        fingerprint_config = f"window.__PHANTOM_FINGERPRINT__ = {json.dumps(fingerprint)};"
        full_injection = fingerprint_config + "\n" + self.injection_script

        await context.add_init_script(full_injection)

        print(f"[PHANTOM v2.0] Fingerprint injected: Canvas={fingerprint['canvas']['noiseSeed'][:8]}...")

        return context

    async def save_session(self, context: BrowserContext, profile_id: str):
        """Saves cookies and storage state to profile."""
        profile_dir = self.profile_manager.get_profile_path(profile_id)
        await context.storage_state(path=str(profile_dir / "storage_state.json"))
        print(f"[PHANTOM v2.0] Session saved: {profile_id}")


if __name__ == "__main__":
    import asyncio

    async def test():
        # Create test profile
        mgr = ProfileManager()
        try:
            profile = mgr.create_profile("phantom_test_v2")
        except ValueError:
            print("[TEST] Profile already exists, loading...")
            profile = mgr.load_profile("phantom_test_v2")

        print(f"[TEST] Using profile: {profile['id']}")
        print(f"[TEST] Canvas Seed: {profile['canvas']['noiseSeed']}")

        # Test Phantom Engine v2.0
        phantom = PhantomEngine(mgr)
        async with async_playwright() as p:
            context = await phantom.launch_context(p, "phantom_test_v2", headless=True)
            page = await context.new_page()

            print("[TEST] Navigating to bot detection site...")
            await page.goto("https://bot.sannysoft.com/")

            # Screenshot
            screenshot_path = "phantom_v2_test.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"[TEST] Screenshot saved: {screenshot_path}")

            # Save session
            await phantom.save_session(context, "phantom_test_v2")
            await context.close()

    asyncio.run(test())