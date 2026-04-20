"""
KNIGHT: {{KNIGHT_ID}}
OWNER: {{OWNER}}
ARCHETYPE: NANO_KNIGHT (Phantom)
"""

import asyncio
import os
import sys
import json
from playwright.async_api import async_playwright

# Import Phantom Engine (Defensive Import)
try:
    from phantom_engine import PhantomEngine
except ImportError:
    # If running standalone, assume relative path (up 2 levels from dist/nano_knights)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    forge_root = os.path.dirname(os.path.dirname(current_dir))
    sys.path.append(forge_root)
    try:
        from phantom_engine import PhantomEngine
    except ImportError:
        print("[CRITICAL] Phantom Engine not found. Stealth systems offline.")
        sys.exit(1)

class NanoKnight:
    def __init__(self):
        self.id = "{{KNIGHT_ID}}"
        self.phantom = PhantomEngine()
        self.active_context = None

    async def initialize(self):
        print(f"[{self.id}] Systems Initializing...")
        # Handshake with Saltare Gateway (Simulation)
        print(f"[{self.id}] connecting to Saltare MCP Gateway...")
        await asyncio.sleep(0.5)
        print(f"[{self.id}] Handshake ACK. Iron Gate: BLUE.")

    async def execute_phantom_browse(self, url: str):
        """Executes a stealth browsing session."""
        print(f"[{self.id}] Engaging Phantom Protocol -> {url}")
        
        async with async_playwright() as p:
            # Launch via Phantom Engine
            context = await self.phantom.launch_context(p, headless=True)
            page = await context.new_page()
            
            print(f"[{self.id}] Navigating...")
            await page.goto(url)
            title = await page.title()
            print(f"[{self.id}] Target Acquired: {title}")
            
            # Basic Evidence
            screenshot_path = f"{self.id}_evidence.png"
            await page.screenshot(path=screenshot_path)
            print(f"[{self.id}] Evidence Secured: {screenshot_path}")
            
            await context.close()

    async def run(self):
        await self.initialize()
        # Default mission for Scout
        await self.execute_phantom_browse("https://example.com")

if __name__ == "__main__":
    knight = NanoKnight()
    try:
        asyncio.run(knight.run())
    except KeyboardInterrupt:
        print(f"\n[{knight.id}] SIGINT Detected. Engaging Kill Switch.")
        sys.exit(0)
