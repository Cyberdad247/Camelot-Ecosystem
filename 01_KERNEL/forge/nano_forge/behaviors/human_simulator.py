# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
BEHAVIORAL CLOAKING: Human Simulation Module
Implements randomized delays, scroll patterns, and interaction presets.
"""

import asyncio
import random
from dataclasses import dataclass
from typing import Literal

BehaviorPreset = Literal["bot_like", "normal_user", "power_user"]


@dataclass
class BehaviorConfig:
    """Configuration for behavioral simulation."""

    min_delay_ms: int
    max_delay_ms: int
    scroll_speed: float  # pixels per second
    typing_speed: int  # chars per minute
    actions_per_minute: int
    jitter_enabled: bool
    random_pauses: bool


PRESETS: dict[BehaviorPreset, BehaviorConfig] = {
    "bot_like": BehaviorConfig(
        min_delay_ms=50,
        max_delay_ms=100,
        scroll_speed=5000,
        typing_speed=900,
        actions_per_minute=120,
        jitter_enabled=False,
        random_pauses=False,
    ),
    "normal_user": BehaviorConfig(
        min_delay_ms=500,
        max_delay_ms=2000,
        scroll_speed=800,
        typing_speed=180,
        actions_per_minute=15,
        jitter_enabled=True,
        random_pauses=True,
    ),
    "power_user": BehaviorConfig(
        min_delay_ms=200,
        max_delay_ms=800,
        scroll_speed=1500,
        typing_speed=350,
        actions_per_minute=40,
        jitter_enabled=True,
        random_pauses=False,
    ),
}


class HumanSimulator:
    """
    Behavioral cloaking for Nano-Knights.
    Mimics human interaction patterns to evade bot detection.
    """

    def __init__(self, preset: BehaviorPreset = "normal_user"):
        self.config = PRESETS[preset]
        self.preset_name = preset
        self.action_count = 0
        self.last_action_time = 0

    async def delay(self):
        """Random delay between actions."""
        delay_ms = random.randint(self.config.min_delay_ms, self.config.max_delay_ms)

        # Add jitter
        if self.config.jitter_enabled:
            jitter = random.randint(-50, 100)
            delay_ms = max(50, delay_ms + jitter)

        await asyncio.sleep(delay_ms / 1000)

    async def random_pause(self):
        """Occasional longer pause (simulates thinking/reading)."""
        if not self.config.random_pauses:
            return

        if random.random() < 0.15:  # 15% chance
            pause_ms = random.randint(2000, 5000)
            print(f"[BEHAVIOR] Random pause: {pause_ms}ms")
            await asyncio.sleep(pause_ms / 1000)

    async def type_text(self, page, selector: str, text: str):
        """Human-like typing with variable speed."""
        await page.click(selector)
        await self.delay()

        for char in text:
            await page.type(selector, char, delay=self._typing_delay())

            # Occasional typo simulation (2% chance)
            if random.random() < 0.02:
                wrong_char = random.choice("qwertyuiop")
                await page.type(selector, wrong_char, delay=50)
                await asyncio.sleep(random.randint(100, 300) / 1000)
                await page.keyboard.press("Backspace")

        await self.random_pause()

    def _typing_delay(self) -> int:
        """Calculate delay between keystrokes in ms."""
        base_delay = 60000 / self.config.typing_speed  # ms per char
        jitter = random.randint(-20, 40) if self.config.jitter_enabled else 0
        return int(max(20, base_delay + jitter))

    async def scroll(self, page, direction: str = "down", distance: int = None):
        """Human-like scrolling with variable speed."""
        if distance is None:
            distance = random.randint(200, 600)

        scroll_time = distance / self.config.scroll_speed  # seconds
        steps = max(5, int(scroll_time * 60))  # ~60fps simulation
        step_distance = distance / steps

        for _ in range(steps):
            if direction == "down":
                await page.mouse.wheel(0, step_distance)
            else:
                await page.mouse.wheel(0, -step_distance)
            await asyncio.sleep(1 / 60)

        await self.delay()

    async def move_mouse(self, page, x: int, y: int):
        """Human-like mouse movement with curve."""
        # Get current position (if possible)
        current_x = random.randint(100, 500)
        current_y = random.randint(100, 500)

        # Calculate bezier-like path
        steps = random.randint(10, 25)
        for i in range(steps):
            progress = i / steps
            # Ease-in-out curve
            eased = progress * progress * (3 - 2 * progress)

            new_x = int(current_x + (x - current_x) * eased)
            new_y = int(current_y + (y - current_y) * eased)

            # Add micro-jitter
            if self.config.jitter_enabled:
                new_x += random.randint(-2, 2)
                new_y += random.randint(-2, 2)

            await page.mouse.move(new_x, new_y)
            await asyncio.sleep(random.randint(5, 15) / 1000)

        await page.mouse.move(x, y)

    async def click(self, page, selector: str):
        """Human-like click with pre-movement and delay."""
        element = await page.query_selector(selector)
        if not element:
            raise ValueError(f"Element not found: {selector}")

        box = await element.bounding_box()
        if box:
            # Click within element bounds with some randomness
            click_x = box["x"] + box["width"] * random.uniform(0.3, 0.7)
            click_y = box["y"] + box["height"] * random.uniform(0.3, 0.7)

            await self.move_mouse(page, int(click_x), int(click_y))
            await self.delay()
            await page.mouse.click(click_x, click_y)
        else:
            await page.click(selector)

        await self.random_pause()

    async def viewport_jitter(self, page):
        """Slight viewport resize to simulate window adjustment."""
        if not self.config.jitter_enabled:
            return

        if random.random() < 0.05:  # 5% chance
            current = page.viewport_size
            new_width = current["width"] + random.randint(-10, 10)
            new_height = current["height"] + random.randint(-5, 5)
            await page.set_viewport_size({"width": max(800, new_width), "height": max(600, new_height)})


if __name__ == "__main__":
    # Test presets
    for preset_name, config in PRESETS.items():
        print(f"\n[{preset_name.upper()}]")
        print(f"  Delay: {config.min_delay_ms}-{config.max_delay_ms}ms")
        print(f"  Typing: {config.typing_speed} CPM")
        print(f"  Actions/min: {config.actions_per_minute}")