"""Browser test for the upload -> unlock -> import flow.

This script:
1. Launches gradio_photo_viewer.py in a subprocess.
2. Stages a test image via the HTTP API.
3. Uses Playwright to set up a PIN on first run, unlock the Secret Photo
   Viewer, and verify the staged photo is imported.
4. Shuts down the server and cleans up staged files.

Run with:
    python tests/test_browser_upload.py
"""

from __future__ import annotations

import io
import random
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from PIL import Image as PILImage
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
STAGING_DIR = PROJECT_ROOT / "staged_uploads"
# Use a temp file for the generated test image to avoid mutating the repo.
TEST_IMAGE = Path(tempfile.gettempdir()) / "spv_test_image.jpg"


PIN = "1234"


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])  # type: ignore[no-any-return]


def _encode_multipart_file(field_name: str, filename: str, content_type: str, data: bytes) -> tuple[dict[str, str], bytes]:
    """Build a minimal multipart/form-data body using only stdlib."""
    boundary = "----WebKitFormBoundary" + "".join(
        random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=16)
    )
    body = b"\r\n".join([
        f"--{boundary}".encode(),
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"'.encode(),
        f"Content-Type: {content_type}".encode(),
        b"",
        data,
        f"--{boundary}--".encode(),
    ])
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    return headers, body


PORT = _find_free_port()
BASE_URL = f"http://127.0.0.1:{PORT}"


def wait_for_server(timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"{BASE_URL}/", timeout=2).close()
            urllib.request.urlopen(f"{BASE_URL}/secret-photo-viewer.html", timeout=2).close()
            return True
        except Exception:
            time.sleep(0.5)
    return False


def clean_staging() -> None:
    if not STAGING_DIR.exists():
        return
    for f in STAGING_DIR.iterdir():
        if f.is_file():
            f.unlink()


def _print_server_logs(proc: subprocess.Popen) -> None:  # type: ignore[type-arg]
    try:
        stdout = proc.stdout.read().decode() if proc.stdout else ""  # type: ignore[union-attr]
        stderr = proc.stderr.read().decode() if proc.stderr else ""  # type: ignore[union-attr]
        if stdout:
            print("--- server stdout ---\n", stdout)
        if stderr:
            print("--- server stderr ---\n", stderr)
    except Exception:
        pass


def _make_test_image(path: Path) -> Path:
    """Generate a small valid JPEG and write it to *path*."""
    img = PILImage.new("RGB", (100, 100), color="red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    path.write_bytes(buf.getvalue())
    return path


def main() -> int:
    # Always generate a fresh valid image for the test.
    _make_test_image(TEST_IMAGE)

    STAGING_DIR.mkdir(exist_ok=True)
    clean_staging()

    proc = subprocess.Popen(
        [sys.executable, str(PROJECT_ROOT / "gradio_photo_viewer.py"), "--server_port", str(PORT), "--server_name", "127.0.0.1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(PROJECT_ROOT),
    )

    try:
        if not wait_for_server():
            _print_server_logs(proc)
            print("Server did not become ready")
            return 1

        print("Server ready, staging test image via API...")
        image_bytes = TEST_IMAGE.read_bytes()
        headers, body = _encode_multipart_file(
            "upload", TEST_IMAGE.name, "image/jpeg", image_bytes
        )
        req = urllib.request.Request(
            f"{BASE_URL}/api/staged",
            data=body,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(resp.read().decode())

        return _run_browser_test()
    finally:
        clean_staging()
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        _print_server_logs(proc)


def _run_browser_test() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Fresh browser context so localStorage from a previous run is not reused.
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        try:
            page.goto(f"{BASE_URL}/secret-photo-viewer.html", wait_until="load")

            # First-run setup: create a PIN if the setup screen is shown.
            setup_screen = page.locator("#setupScreen")
            if setup_screen.is_visible(timeout=5000):
                page.locator("#setupPinInput").fill(PIN)
                page.locator("#setupPinConfirm").fill(PIN)
                page.locator("#setupBtn").click()
                page.wait_for_selector("#lockScreen", state="visible", timeout=10000)

            # Unlock the vault.
            page.locator("#lockScreen").wait_for(state="visible", timeout=20000)
            pin_input = page.locator("#pinInput")
            pin_input.wait_for(state="visible", timeout=10000)
            pin_input.fill(PIN)
            page.locator("#unlockBtn").click()

            # Wait for the gallery to show at least one imported photo card.
            photo_card = page.locator("#gallery .photo-card").first
            photo_card.wait_for(state="visible", timeout=20000)

            card_count = page.locator("#gallery .photo-card").count()
            print(f"Gallery card count: {card_count}")

            if card_count < 1:
                print("FAIL: No photo cards found in gallery.")
                return 1

            # Verify the staged file was cleaned up after import.
            staged = [f for f in STAGING_DIR.iterdir() if f.is_file()]
            if staged:
                print(f"FAIL: {len(staged)} staged file(s) left after import")
                return 1

            print("PASS: Upload -> unlock -> import flow worked end-to-end.")
            return 0

        except PlaywrightTimeout as exc:
            print(f"FAIL: Browser timed out - {exc}")
            try:
                page.screenshot(path="test_browser_upload_failure.png", full_page=True)
                with open("test_browser_upload_failure.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                print("Saved test_browser_upload_failure.png and .html for debugging.")
            except Exception:
                pass
            return 1
        finally:
            browser.close()


if __name__ == "__main__":
    sys.exit(main())
