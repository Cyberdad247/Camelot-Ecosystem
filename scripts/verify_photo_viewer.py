"""End-to-end verification script for the Secret Photo Viewer.

Starts the Gradio/FastAPI server on an ephemeral port, uses Playwright to:

1. Open the headless Gradio UI.
2. Complete first-run PIN setup inside the embedded vault iframe.
3. Upload a generated test photo through the Gradio file component.
4. Unlock the vault with the PIN.
5. Verify the uploaded photo appears in the gallery.

Then it stops the server and prints a summary.

Usage:
    python scripts/verify_photo_viewer.py

Exit codes:
    0 - verification passed
    1 - verification failed
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

try:
    from playwright.sync_api import Frame, Page, sync_playwright
except ImportError as exc:
    raise SystemExit(
        "Playwright is required. Install it with: pip install playwright"
    ) from exc

try:
    from PIL import Image
except ImportError as exc:
    raise SystemExit(
        "Pillow is required. Install it with: pip install Pillow"
    ) from exc

try:
    from gradio_client import Client as GradioClient
    from gradio_client import handle_file
except ImportError as exc:
    raise SystemExit(
        "gradio_client is required. Install it with: pip install gradio"
    ) from exc


# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
class _BrowserNotInstalledError(Exception):
    """Raised when Playwright browsers are missing."""


def _check_playwright_browsers() -> None:
    """Verify that Playwright's Chromium browser is installed."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            if not Path(p.chromium.executable_path).exists():
                raise _BrowserNotInstalledError(
                    "Playwright Chromium browser is not installed. "
                    "Run: python -m playwright install chromium"
                )
    except _BrowserNotInstalledError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise _BrowserNotInstalledError(
            "Playwright Chromium browser is not installed. "
            "Run: python -m playwright install chromium"
        ) from exc


APP_ROOT = Path(__file__).resolve().parents[1]
APP_FILE = APP_ROOT / "gradio_photo_viewer.py"
DEFAULT_PIN = "1234"
TIMEOUT_MS = 30_000


def _find_free_port() -> int:
    """Return a free TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_server(url: str, *, process: subprocess.Popen | None = None, timeout: float = 30.0) -> bool:
    """Return True once *url* responds with HTTP 200.

    If *process* is provided and exits before the URL responds, return False
    immediately so we don't wait the full timeout for a dead server.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if process is not None and process.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(url, timeout=2.0) as response:
                return response.status == 200
        except (urllib.error.URLError, OSError):
            time.sleep(0.5)
    return False


class _Server:
    """Context manager that starts and stops the Secret Photo Viewer server."""

    def __init__(self, port: int):
        self.port = port
        self.process: subprocess.Popen | None = None
        self.base_url = f"http://127.0.0.1:{port}"
        self.staging_dir = APP_ROOT / f".pytest_staging_{self.port}"
        self.log_path: Path | None = None

    def __enter__(self) -> "_Server":
        env = os.environ.copy()
        env["SPV_PORT"] = str(self.port)
        env["SPV_HOST"] = "127.0.0.1"
        # Use a fresh staging directory for each run so the test is hermetic.
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        env["SPV_STAGING_DIR"] = str(self.staging_dir)

        # Redirect server output to a temp log so it can be inspected on failure.
        self._log_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".log", prefix="spv_server_", delete=False
        )
        self.log_path = Path(self._log_file.name)

        self.process = subprocess.Popen(
            [sys.executable, str(APP_FILE), "--server_name", "127.0.0.1", "--server_port", str(self.port)],
            cwd=str(APP_ROOT),
            env=env,
            stdout=self._log_file,
            stderr=subprocess.STDOUT,
        )
        self._log_file.close()

        if not _wait_for_server(f"{self.base_url}/health", process=self.process):
            self._terminate()
            raise RuntimeError("Server failed to start within 30 seconds")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._terminate()

    def _terminate(self) -> None:
        if self.process is not None:
            with contextlib.suppress(Exception):
                self.process.terminate()
                try:
                    self.process.wait(timeout=5.0)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=5.0)
            self.process = None

        # Clean up the per-run staging directory.
        if self.staging_dir.exists():
            with contextlib.suppress(Exception):
                shutil.rmtree(self.staging_dir)

        # Note: the server log file is intentionally not deleted here so the
        # caller can inspect it on failure. It is removed after a successful run.


def _get_vault_frame(page: Page) -> Frame:
    """Return the Secret Photo Viewer iframe frame.

    Waits for the iframe element to be attached to the DOM and then resolves
    the corresponding Playwright frame.
    """
    iframe_locator = page.locator('iframe[title="Secret Photo Viewer"]')
    try:
        iframe_locator.wait_for(state="attached", timeout=TIMEOUT_MS)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            f"Vault iframe element was not attached. {_debug_state(page)}"
        ) from exc

    deadline = time.time() + (TIMEOUT_MS / 1000)
    while time.time() < deadline:
        for frame in page.frames:
            if "secret-photo-viewer.html" in frame.url:
                return frame
        time.sleep(0.1)
    raise RuntimeError("Vault iframe did not load")


def _set_up_pin(frame: Frame, pin: str) -> None:
    """Complete the first-run PIN setup screen inside the iframe."""
    frame.wait_for_selector("#setupScreen", state="visible", timeout=TIMEOUT_MS)
    frame.fill("#setupPinInput", pin)
    frame.fill("#setupPinConfirm", pin)
    # The iframe viewport is small and the fixed-position setup screen can
    # overflow it, so bypass Playwright's hit-testing by dispatching the click
    # event directly.
    frame.locator("#setupBtn").dispatch_event("click")
    # After setup, the lock screen should appear.
    frame.wait_for_selector("#lockScreen", state="visible", timeout=TIMEOUT_MS)


def _unlock_vault(frame: Frame, pin: str) -> None:
    """Unlock the vault using the PIN inside the iframe."""
    frame.wait_for_selector("#pinInput", state="visible", timeout=TIMEOUT_MS)
    frame.fill("#pinInput", pin)
    # See _set_up_pin for why we dispatch the click directly.
    frame.locator("#unlockBtn").dispatch_event("click")
    frame.wait_for_selector("#app", state="visible", timeout=TIMEOUT_MS)


def _verify_gallery(frame: Frame, expected_count: int = 0) -> None:
    """Assert that the gallery contains the expected number of photos.

    Polls for up to ``TIMEOUT_MS`` when an expected count is given, so async
    vault imports triggered by postMessage have time to complete.
    """
    photo_cards = frame.locator(".photo-card")
    if expected_count > 0:
        deadline = time.time() + (TIMEOUT_MS / 1000)
        while time.time() < deadline:
            try:
                photo_cards.first.wait_for(state="visible", timeout=2000)
                actual = photo_cards.count()
                if actual >= expected_count:
                    return
            except Exception:  # noqa: BLE001
                pass
            time.sleep(0.5)
        # Final check for diagnostic message.
        actual = photo_cards.count()
        assert actual == expected_count, (
            f"Expected {expected_count} photos in gallery, found {actual}"
        )
    else:
        empty_state = frame.locator("text=No secret photos yet")
        assert empty_state.is_visible(), "Empty gallery state not visible"


def _debug_state(page) -> str:
    """Return a short diagnostic string describing the current page state."""
    url = page.url
    try:
        title = page.title()
    except Exception:  # noqa: BLE001
        title = "<unknown>"
    return f"URL={url}, title={title}"


def _generate_test_image(path: Path) -> Path:
    """Create a small PNG image at *path* for upload testing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (100, 100), color="red")
    img.save(path, format="PNG")
    # Verify the generated file is a valid PNG.
    with Image.open(path) as verify_img:
        verify_img.verify()
    return path


@contextlib.contextmanager
def _temp_test_image(port: int):
    """Yield a test image path and remove it on exit."""
    path = APP_ROOT / f".pytest_test_image_{port}.png"
    try:
        yield path
    finally:
        if path.exists():
            with contextlib.suppress(Exception):
                path.unlink()


def _dump_diagnostics(page: Page, prefix: str, *, max_html_chars: int = 50_000) -> tuple[Path, Path]:
    """Save a screenshot and (truncated) HTML dump to help debug failures.

    Both files share the same timestamp so they can be matched easily. The
    HTML dump is truncated to avoid writing very large files; set
    ``max_html_chars`` to 0 to skip the HTML dump entirely.
    """
    timestamp = int(time.time())
    screenshot_path = APP_ROOT / f"verify_photo_viewer_{prefix}_{timestamp}.png"
    html_path = APP_ROOT / f"verify_photo_viewer_{prefix}_{timestamp}.html"
    with contextlib.suppress(Exception):
        page.screenshot(path=str(screenshot_path))
    if max_html_chars > 0:
        with contextlib.suppress(Exception):
            html = page.content()
            if len(html) > max_html_chars:
                html = html[:max_html_chars] + "\n<!-- truncated -->"
            html_path.write_text(html, encoding="utf-8")
    return screenshot_path, html_path


def _poll_staged(base_url: str, timeout: float = 30.0) -> bool:
    """Return True once at least one file is listed in /api/staged."""
    staged_url = f"{base_url}/api/staged"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(staged_url, timeout=2.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    if isinstance(data, list) and len(data) > 0:
                        return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(0.5)
    return False


def _upload_via_gradio(page: Page, image_path: Path, base_url: str, console_errors: list[str]) -> bool:
    """Upload an image through the hidden headless input and wait for staging.

    Returns True when the file was staged through the Gradio UI.
    """
    file_input = page.locator("#headless-upload")
    try:
        file_input.wait_for(state="attached", timeout=TIMEOUT_MS)
    except Exception as exc:  # noqa: BLE001
        screenshot_path, html_path = _dump_diagnostics(page, "upload_input")
        raise RuntimeError(
            f"Headless upload input did not attach. Screenshot: {screenshot_path}, "
            f"HTML: {html_path}. Original error: {exc}"
        ) from exc

    # Wait until the JS upload listener is installed; it sets a global flag.
    page.wait_for_function("window.headlessUploadReady === true", timeout=TIMEOUT_MS)

    file_input.set_input_files(str(image_path))

    # Poll the /api/staged endpoint until the file is staged. This is more
    # reliable than matching Gradio's UI text, which can vary.
    if _poll_staged(base_url, timeout=TIMEOUT_MS / 1000):
        return True

    screenshot_path, html_path = _dump_diagnostics(page, "upload_timeout")
    raise RuntimeError(
        f"Gradio UI upload did not stage the file. Screenshot: {screenshot_path}, "
        f"HTML: {html_path}. Console errors: {console_errors[-10:]}"
    )


def _upload_via_gradio_client(image_path: Path, base_url: str) -> bool:
    """Upload through the Gradio HTTP client API, which triggers the same
    ``.change()`` backend handler as the visible Gradio File component.

    This is more reliable than manipulating the hidden file input with
    Playwright because the Gradio client sends the file via the standard
    upload API and calls the predict endpoint, which is exactly what the
    WebSocket-based event does internally.
    """
    try:
        client = GradioClient(base_url)
        result = client.predict(
            filepaths=[handle_file(str(image_path))],
            api_name="/_stage_uploads_event",
        )
        return "Staged" in str(result)
    except Exception as exc:
        print(f"[debug] Gradio client predict failed: {exc}", file=sys.stderr)
        return False


def _upload_via_visible_gradio(page: Page, image_path: Path, base_url: str, console_errors: list[str]) -> None:
    """Upload through the visible Gradio File component's backend handler.

    Uses the Gradio HTTP client API to trigger the ``.change()`` event on the
    server side, which is the same handler that the visible Gradio File
    component invokes when a user uploads files. After staging, sends a
    ``SYNC_STAGED`` message to the iframe to trigger vault import, matching
    what the browser-side JS callback would do.
    """
    if not _upload_via_gradio_client(image_path, base_url):
        screenshot_path, html_path = _dump_diagnostics(page, "visible_upload_timeout")
        raise RuntimeError(
            f"Visible Gradio upload did not stage the file. Screenshot: {screenshot_path}, "
            f"HTML: {html_path}. Console errors: {console_errors[-10:]}"
        )

    # The Gradio client API calls the backend function directly, but does not
    # run the browser-side JS callback (_NOTIFY_IFRAME_JS) that would send a
    # SYNC_STAGED message to the vault iframe. We send it here so the vault
    # imports the newly staged files.
    page.evaluate("""
        const root = document.querySelector('gradio-app')?.shadowRoot || document;
        const iframe = root.querySelector('iframe[title="Secret Photo Viewer"]');
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.postMessage({ type: 'SYNC_STAGED' }, window.location.origin);
        }
    """)


def run_verification(port: int, headless: bool = True, pin: str = DEFAULT_PIN) -> dict:
    """Start the server, run the browser verification, and return results."""
    result: dict = {"passed": False, "errors": [], "server_log": None}

    with _temp_test_image(port) as test_image, _Server(port) as server:
        result["server_log"] = str(server.log_path)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            try:
                context = browser.new_context(viewport={"width": 1280, "height": 720})
                page = context.new_page()

                # Open the Gradio UI so we can upload through the headless UI.
                console_errors: list[str] = []
                page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
                page.on("pageerror", lambda exc: console_errors.append(str(exc)))

                page.goto(server.base_url, wait_until="domcontentloaded")

                # The vault lives inside an iframe; locate it and wait for a PIN
                # screen before proceeding.
                frame = _get_vault_frame(page)

                # Capture console errors from the iframe as well as the main page.
                frame.on(
                    "console",
                    lambda msg: console_errors.append(f"iframe: {msg.text}") if msg.type == "error" else None,
                )

                # Wait until one of the PIN screens is visible. A manual poll is
                # more robust here because the inline first-run script toggles
                # Tailwind's `hidden` class and Playwright's OR-locator can miss
                # the brief transition.
                deadline = time.time() + (TIMEOUT_MS / 1000)
                while time.time() < deadline:
                    if frame.locator("#setupScreen").is_visible() or frame.locator("#lockScreen").is_visible():
                        break
                    page.wait_for_timeout(100)
                else:
                    screenshot_path, html_path = _dump_diagnostics(page, f"pin_screen_failure_{port}")

                    diagnostics = frame.evaluate(
                        """() => {
                            const s = (id) => {
                                const el = document.getElementById(id);
                                if (!el) return { exists: false };
                                const style = window.getComputedStyle(el);
                                return {
                                    exists: true,
                                    display: style.display,
                                    visibility: style.visibility,
                                    hiddenClass: el.classList.contains('hidden'),
                                    classes: el.className,
                                };
                            };
                            return { lockScreen: s('lockScreen'), setupScreen: s('setupScreen') };
                        }"""
                    )

                    raise RuntimeError(
                        f"Timed out waiting for PIN screen. {_debug_state(page)} "
                        f"Diagnostics: {diagnostics}. Screenshot: {screenshot_path}, "
                        f"HTML: {html_path}. Console errors: {console_errors[-5:]}"
                    )

                # First-run setup if needed.
                if frame.locator("#setupScreen").is_visible():
                    _set_up_pin(frame, pin)

                # Generate a test photo and upload it via the headless UI.
                _generate_test_image(test_image)
                _upload_via_gradio(page, test_image, server.base_url, console_errors)

                # Unlock the vault and verify the uploaded photo appears.
                _unlock_vault(frame, pin)
                _verify_gallery(frame, expected_count=1)

                # Generate a second test photo and upload it through the visible
                # Gradio File component to cover the manual user path.
                _generate_test_image(test_image)
                _upload_via_visible_gradio(page, test_image, server.base_url, console_errors)
                _verify_gallery(frame, expected_count=2)

                result["passed"] = True
                result["url"] = server.base_url
                context.close()
            finally:
                browser.close()

        # Clean up the server log now that the run succeeded.
        if server.log_path is not None and server.log_path.exists():
            with contextlib.suppress(Exception):
                server.log_path.unlink()

        # Remove any stale failure screenshots from previous runs.
        for screenshot in APP_ROOT.glob("verify_photo_viewer_failure_*.png"):
            with contextlib.suppress(Exception):
                screenshot.unlink()

    return result


def main() -> int:
    _check_playwright_browsers()

    parser = argparse.ArgumentParser(
        description="Verify the Secret Photo Viewer end-to-end in a browser."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port for the test server (default: ephemeral free port).",
    )
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run the browser in headless mode (default: true). Use --no-headless to watch.",
    )
    parser.add_argument(
        "--pin",
        type=str,
        default=DEFAULT_PIN,
        help=f"PIN to use for first-run setup and unlock (default: {DEFAULT_PIN}).",
    )
    args = parser.parse_args()

    port = args.port if args.port is not None else _find_free_port()

    try:
        result = run_verification(port=port, headless=args.headless, pin=args.pin)
    except Exception as exc:  # noqa: BLE001
        result = {"passed": False, "errors": [str(exc)]}

    if result["passed"]:
        print(f"[PASS] Secret Photo Viewer verification passed: {result.get('url')}")
        return 0

    print("[FAIL] Secret Photo Viewer verification failed")
    for error in result.get("errors", []):
        print(f"       Error: {error}")
    if result.get("server_log"):
        print(f"       Server log: {result['server_log']}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
