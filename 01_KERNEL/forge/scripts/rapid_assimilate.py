# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import os
import sys
from typing import Any, Dict

# Ensure we can import the engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Engines")))

try:
    from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
    from crawl4ai.async_webcrawler import AsyncWebCrawler
    from crawl4ai.cache_context import CacheMode
except ImportError as e:
    print(f"CRITICAL: Could not import crawl4ai engine: {e}")
    print("Ensure '01_KERNEL/Engines/crawl4ai' is populated.")
    sys.exit(1)

# Import Trivy scanner (optional - graceful fallback if not available)
try:
    from trivy_scan import TrivyScanner  # noqa: F401

    TRIVY_AVAILABLE = True
    print("[SECURITY] Trivy scanner loaded successfully")
except ImportError:
    TRIVY_AVAILABLE = False
    print("[WARNING] Trivy scanner not available - security scanning disabled")


class OmegaAuditPrime:
    def __init__(self):
        # Lightpanda CDP endpoint — zero local Chromium overhead (Titanium Law T6)
        lightpanda_cdp = os.environ.get("LIGHTPANDA_CDP_URL", "http://127.0.0.1:9222")
        use_lightpanda = os.environ.get("CAMELOT_USE_LIGHTPANDA", "1") == "1"

        self.browser_config = BrowserConfig(
            headless=True,
            verbose=False,
            java_script_enabled=True,
            text_mode=True,
            cdp_url=lightpanda_cdp if use_lightpanda else None,
        )
        self.crawler = AsyncWebCrawler(config=self.browser_config)
        engine_label = "Lightpanda CDP" if use_lightpanda else "Local Chromium"
        print(f"[SHIELD] OMEGA AUDIT PRIME: Initializing Rapid Assimilation Protocol (8GB Profile, {engine_label})...")

    async def audit_url(self, url: str) -> Dict[str, Any]:
        """
        Rapidly audit a target URL (GitHub repo or documentation) using the assimilation engine.
        """
        print(f"[SCAN] SCANNING TARGET: {url}")

        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=5,
            verbose=False,
            # 8GB Optimization: Limit extraction depth and waiting
            wait_for="",  # Minimize wait times
        )

        async with self.crawler as crawler:
            content = ""
            success = False

            # 🔄 Try 1-3: Rapid Engine (Crawl4AI)
            for attempt in range(1, 4):
                print(f"[ATTEMPT {attempt}/3] Engaging Phantom Engine...")
                result = await crawler.arun(url=url, config=config)

                if result.success:
                    content = result.markdown
                    success = True
                    break
                else:
                    print(f"[WARNING] Attempt {attempt} Failed: {result.error_message}")
                    await asyncio.sleep(1)

            # 🛡️ Fallback: Original Pipeline (Git Clone)
            if not success:
                print(
                    "[ALERT] Phantom Engine Exhausted. Initiating Fallback Protocol: ORIGINAL PIPELINE (Git Clone)..."
                )
                content = self._fallback_git_clone(url)
                if not content:
                    return {"score": 0, "status": "FAILED", "verdict": "UNREACHABLE"}
                success = True

            # Basic Heuristic Analysis (Protocol 95 - Early Warning System)

            # 1. Security Scan
            secrets_found = []
            if "API_KEY" in content or "SECRET_KEY" in content:
                secrets_found.append("Potential Secrets in Text")

            # 2. Quality Scan
            has_tests = "test" in content.lower()
            has_docs = "documentation" in content.lower() or "monitor" in content.lower()

            # 3. Synergy Scan
            stack_match = "python" in content.lower() or "javascript" in content.lower() or "next.js" in content.lower()

            # Scoring (Simplified)
            score = 100
            if secrets_found:
                score -= 30
            if not has_tests:
                score -= 10
            if not has_docs:
                score -= 10
            if not stack_match:
                score -= 20

            # 🛡️ TRIVY SECURITY SCAN (if available and repo is cloned)
            security_score = 100
            trivy_vulns = []
            trivy_secrets = []
            trivy_licenses = []

            if TRIVY_AVAILABLE:
                # Note: Trivy requires a filesystem path, not a URL
                # This would be integrated after Anti-Gravity Chamber cloning
                print("[SECURITY] Trivy scan would run on cloned repository")
                # For now, we'll add a placeholder for future integration
                # security_score, trivy_vulns, trivy_secrets, trivy_licenses = scanner.scan_repository(repo_path)

            # Combine scores (weighted average: 70% heuristic, 30% security)
            final_score = int(score * 0.7 + security_score * 0.3)

            report = {
                "target": url,
                "score": final_score,
                "verdict": "PURE" if final_score >= 95 else "TAINTED",
                "findings": {
                    "secrets": secrets_found,
                    "tests_detected": has_tests,
                    "docs_detected": has_docs,
                    "stack_synergy": stack_match,
                    "security_score": security_score,
                    "trivy_vulns": len(trivy_vulns),
                    "trivy_secrets": len(trivy_secrets),
                    "trivy_licenses": len(trivy_licenses),
                    "preview": content[:500] + "...",
                },
            }

            self._print_report(report)
            return report

    def _fallback_git_clone(self, url: str) -> str:
        """
        Executes the 'Original Pipeline' logic: Git Clone -> Read README -> Purge.
        """
        import shutil
        import subprocess
        import time

        try:
            repo_name = url.split("/")[-1].replace(".git", "")
            temp_dir = f"temp_fallback_{repo_name}_{int(time.time())}"

            print(f"[FALLBACK] Cloning into {temp_dir}...")
            subprocess.run(
                ["git", "clone", "--depth", "1", url, temp_dir],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Find README
            content = ""
            for root, _dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().startswith("readme"):
                        readme_path = os.path.join(root, file)
                        print(f"[FALLBACK] Found Manifest: {readme_path}")
                        with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        break
                if content:
                    break

            # Purge
            print(f"[FALLBACK] Purging {temp_dir}...")
            shutil.rmtree(temp_dir, ignore_errors=True)

            if not content:
                print("[FALLBACK] No README found in repository.")
                return ""

            return content

        except Exception as e:
            print(f"[FALLBACK ERROR] Original Pipeline Failed: {e}")
            return ""

    def _print_report(self, report: Dict[str, Any]):
        print("\n" + "=" * 60)
        print(f"[REPORT] RAPID ASSIMILATION REPORT for {report['target']}")
        print("=" * 60)
        print(f"SCORE: {report['score']} / 100")
        print(f"VERDICT: {report['verdict']}")
        print("-" * 30)
        for k, v in report["findings"].items():
            print(f"- {k}: {v}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rapid_assimilate.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    auditor = OmegaAuditPrime()
    asyncio.run(auditor.audit_url(url))