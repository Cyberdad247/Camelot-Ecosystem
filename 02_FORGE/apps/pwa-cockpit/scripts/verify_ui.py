from __future__ import annotations

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "ui"
URL = os.environ.get("PWA_COCKPIT_URL", "http://localhost:3005")
TOKEN = os.environ.get("PWA_COCKPIT_TOKEN", "")


def pair_operator(page, capture_gate: bool = False) -> bool:
    page.wait_for_selector("#operator-token, .cockpit-shell", timeout=15_000)
    if not page.locator("#operator-token").count():
        return False

    assert len(TOKEN) >= 16, "PWA_COCKPIT_TOKEN is required for production verification"
    if capture_gate:
        page.screenshot(path=str(ARTIFACTS / "operator-pairing-gate.png"))
    page.locator("#operator-token").fill(TOKEN)
    page.locator(".pairing-form button").click()
    page.wait_for_selector("text=ANYA", timeout=15_000)
    return True


def verify_view(page, name: str) -> dict[str, object]:
    console_errors: list[str] = []
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
    response = page.goto(URL, wait_until="domcontentloaded", timeout=30_000)
    assert response and response.ok, f"{name}: page request failed"
    paired_through_ui = pair_operator(page, capture_gate=name.startswith("desktop"))
    page.wait_for_selector("text=ANYA", timeout=15_000)
    page.wait_for_selector("text=Sovereign Command", timeout=15_000)
    page.wait_for_function("document.body.innerText.toLowerCase().includes('runtime services')", timeout=15_000)
    page.wait_for_timeout(500)

    body_text = page.locator("body").inner_text().strip()
    overlay = page.locator('[data-nextjs-dialog], .vite-error-overlay, #webpack-dev-server-client-overlay').count()
    horizontal_overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
    status_response = page.request.get(f"{URL}/api/status")
    status_payload = status_response.json()

    assert len(body_text) > 400, f"{name}: rendered body is unexpectedly sparse"
    assert overlay == 0, f"{name}: framework error overlay detected"
    assert not horizontal_overflow, f"{name}: horizontal viewport overflow detected"
    assert status_response.ok, f"{name}: status API failed"
    assert status_payload.get("source") == "camelot-runtime-state+tcp-probes"

    screenshot = ARTIFACTS / f"{name}.png"
    page.screenshot(path=str(screenshot), full_page=not name.startswith("mobile"))
    return {
        "name": name,
        "title": page.title(),
        "body_chars": len(body_text),
        "console_errors": list(console_errors),
        "overlay_count": overlay,
        "horizontal_overflow": horizontal_overflow,
        "status_mode": status_payload.get("mode"),
        "paired_through_ui": paired_through_ui,
        "screenshot": str(screenshot),
    }


def verify_offline(browser) -> dict[str, object]:
    page = browser.new_page(viewport={"width": 1440, "height": 960}, device_scale_factor=1)
    response = page.goto(URL, wait_until="domcontentloaded", timeout=30_000)
    assert response and response.ok, "offline prewarm page failed"
    pair_operator(page)
    page.wait_for_selector('[data-cartridge="command"]', timeout=15_000)
    page.wait_for_function("document.documentElement.dataset.pwaPrewarmed === 'true'", timeout=20_000)
    page.evaluate("navigator.serviceWorker.ready.then(() => true)")
    page.reload(wait_until="domcontentloaded", timeout=30_000)
    page.wait_for_selector("text=ANYA", timeout=15_000)
    page.wait_for_timeout(750)
    assert page.evaluate("Boolean(navigator.serviceWorker.controller)"), "service worker did not control the page"

    page.context.set_offline(True)
    try:
      page.reload(wait_until="domcontentloaded", timeout=30_000)
      page.wait_for_selector("text=ANYA", timeout=15_000)
      page.wait_for_selector("text=Sovereign Command", timeout=15_000)
      assert "edge" in page.locator("body").inner_text().lower()
      page.wait_for_selector("text=Commands, events, and approvals are never retained offline", timeout=15_000)
      mounted = []
      for label, cartridge in [("Factory", "factory"), ("Intel", "intelligence"), ("Mesh", "mesh")]:
        page.locator(".rail-button", has_text=label).click()
        page.locator(f'[data-cartridge="{cartridge}"]').wait_for(timeout=15_000)
        mounted.append(cartridge)
      page.screenshot(path=str(ARTIFACTS / "desktop-offline.png"), full_page=True)
    finally:
      page.context.set_offline(False)
      page.close()

    return {"controlled": True, "offline_reload": True, "prewarmed_cartridges": mounted, "sanitized_snapshot": True}


def verify_voice_contract(browser) -> dict[str, object]:
    page = browser.new_page(viewport={"width": 980, "height": 760}, device_scale_factor=1)
    page.add_init_script("""
      window.__anyaVoiceProbe = { spoken: [], cancelCount: 0 };
      window.speechSynthesis.getVoices = () => [];
      window.speechSynthesis.cancel = () => { window.__anyaVoiceProbe.cancelCount += 1; };
      window.speechSynthesis.speak = (utterance) => {
        window.__anyaVoiceProbe.spoken.push({ text: utterance.text, voice: utterance.voice?.name ?? null });
        setTimeout(() => utterance.onstart?.(new Event('start')), 10);
        setTimeout(() => utterance.onend?.(new Event('end')), 1200);
      };
    """)
    response = page.goto(URL, wait_until="domcontentloaded", timeout=30_000)
    assert response and response.ok, "voice contract page failed"
    pair_operator(page)
    page.get_by_role("button", name="Enable spoken replies").click()
    page.locator("#anya-command").fill("//STATUS")
    page.locator("#anya-command").press("Enter")
    page.wait_for_selector("text=Speaking", timeout=15_000)
    probe = page.evaluate("window.__anyaVoiceProbe")
    assert probe["spoken"], "Anya did not invoke speech synthesis"
    assert probe["spoken"][0]["text"] == "Status refreshed from local runtime evidence."
    assert probe["spoken"][0]["voice"] is None
    page.get_by_role("button", name="Start voice input").click()
    page.wait_for_function("window.__anyaVoiceProbe.cancelCount >= 2", timeout=5_000)
    probe = page.evaluate("window.__anyaVoiceProbe")
    assert probe["cancelCount"] >= 2, "mic barge-in did not cancel active speech"
    if page.get_by_role("button", name="Stop listening").count():
        page.get_by_role("button", name="Stop listening").click()
    page.screenshot(path=str(ARTIFACTS / "anya-voice-contract.png"))
    page.close()
    return {
        "spoken_summary": probe["spoken"][0]["text"],
        "native_voice_fallback": probe["spoken"][0]["voice"] is None,
        "barge_in_cancelled": True,
    }


def main() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        desktop = browser.new_page(viewport={"width": 1440, "height": 960}, device_scale_factor=1)
        desktop_result = verify_view(desktop, "desktop-1440x960")
        mounted = []
        for label, cartridge in [("Factory", "factory"), ("Intel", "intelligence"), ("Mesh", "mesh")]:
            desktop.locator(".rail-button", has_text=label).click()
            desktop.locator(f'[data-cartridge="{cartridge}"]').wait_for()
            mounted.append(cartridge)
        desktop_result["mounted_cartridges"] = mounted
        desktop.locator(".rail-button", has_text="Factory").click()
        desktop.screenshot(path=str(ARTIFACTS / "desktop-factory.png"), full_page=True)
        results.append(desktop_result)
        desktop.close()

        results[0]["pwa"] = verify_offline(browser)
        results[0]["voice"] = verify_voice_contract(browser)

        mobile = browser.new_page(
            viewport={"width": 390, "height": 844},
            device_scale_factor=1,
            is_mobile=True,
            has_touch=True,
        )
        mobile_result = verify_view(mobile, "mobile-390x844")
        composer_box = mobile.locator(".command-composer").bounding_box()
        navigation_box = mobile.locator(".mobile-bottom-nav").bounding_box()
        metrics_box = mobile.locator(".metric-strip").bounding_box()
        assert composer_box and navigation_box and metrics_box, "mobile controls are missing layout boxes"
        assert composer_box["y"] + composer_box["height"] <= navigation_box["y"] + 1, "mobile composer overlaps bottom navigation"
        assert composer_box["y"] + composer_box["height"] <= metrics_box["y"] + 1, "mobile composer obscures runtime metrics"
        mobile_result["mobile_controls_separated"] = True
        mobile.locator(".mobile-bottom-nav").get_by_role("button", name="Intel", exact=True).click()
        mobile.wait_for_selector("text=Cloud Intelligence")
        mobile.wait_for_selector("text=Memory topology")
        mobile_result["intelligence_mount"] = True
        mobile.screenshot(path=str(ARTIFACTS / "mobile-intelligence.png"))
        results.append(mobile_result)
        mobile.close()

        browser.close()

    print(json.dumps({"status": "PASS", "results": results}, indent=2))


if __name__ == "__main__":
    main()
