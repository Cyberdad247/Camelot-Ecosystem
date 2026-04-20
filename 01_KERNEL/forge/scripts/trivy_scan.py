# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Trivy Security Scanner Wrapper for Camelot OS
Knight: Sir Sentinel (Security & Compliance)
Version: 1.0.0
Date: 2026-01-27
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class TrivyScanner:
    """Wrapper for Trivy security scanner"""

    def __init__(self, trivy_path="trivy"):
        self.trivy_path = trivy_path
        self.forbidden_licenses = ["GPL-2.0", "GPL-3.0", "AGPL-3.0"]

    def scan_repository(self, repo_path: str, output_file: str = None) -> Tuple[int, List, List, List]:
        """
        Scan repository with Trivy

        Args:
            repo_path: Path to repository to scan
            output_file: Optional path to save JSON report

        Returns:
            Tuple of (score, vulnerabilities, secrets, licenses)
        """
        print(f"[TRIVY] Scanning {repo_path}...")

        cmd = [self.trivy_path, "fs", "--scanners", "vuln,secret,license", "--format", "json", "--quiet", repo_path]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0 and not result.stdout:
                print(f"[TRIVY] Warning: Scan completed with return code {result.returncode}")
                # Try to parse stderr for errors
                if result.stderr:
                    print(f"[TRIVY] Error: {result.stderr[:500]}")
                return 100, [], [], []  # Assume clean if no results

            data = json.loads(result.stdout) if result.stdout else {"Results": []}

            # Parse results
            score = self._calculate_security_score(data)
            vulns = self._extract_vulnerabilities(data)
            secrets = self._extract_secrets(data)
            licenses = self._extract_licenses(data)

            if output_file:
                self._save_report(data, output_file)

            print(f"[TRIVY] Scan complete. Score: {score}/100")
            print(f"[TRIVY]   Vulnerabilities: {len(vulns)}")
            print(f"[TRIVY]   Secrets: {len(secrets)}")
            print(f"[TRIVY]   License issues: {len(licenses)}")

            return score, vulns, secrets, licenses

        except subprocess.TimeoutExpired:
            print("[TRIVY] ERROR: Scan timed out after 5 minutes")
            return 0, [], [], []
        except json.JSONDecodeError as e:
            print(f"[TRIVY] ERROR: Failed to parse JSON output: {e}")
            return 0, [], [], []
        except Exception as e:
            print(f"[TRIVY] ERROR: {str(e)}")
            return 0, [], [], []

    def _calculate_security_score(self, data: Dict) -> int:
        """
        Calculate security score (0-100)

        Deductions:
        - CRITICAL vuln: -30 points each
        - HIGH vuln: -10 points each
        - MEDIUM vuln: -5 points each
        - SECRET found: -50 points each
        - Forbidden license: -20 points each
        """
        score = 100

        results = data.get("Results", [])
        for result in results:
            # Vulnerabilities
            vulns = result.get("Vulnerabilities", [])
            for vuln in vulns:
                severity = vuln.get("Severity", "UNKNOWN")
                if severity == "CRITICAL":
                    score -= 30
                elif severity == "HIGH":
                    score -= 10
                elif severity == "MEDIUM":
                    score -= 5

            # Secrets
            secrets = result.get("Secrets", [])
            score -= len(secrets) * 50

            # Licenses
            licenses = result.get("Licenses", [])
            for license_info in licenses:
                license_name = license_info.get("Name", "")
                if license_name in self.forbidden_licenses:
                    score -= 20

        return max(0, score)

    def _extract_vulnerabilities(self, data: Dict) -> List[Dict]:
        """Extract vulnerability details"""
        vulns = []
        results = data.get("Results", [])
        for result in results:
            for vuln in result.get("Vulnerabilities", []):
                vulns.append(
                    {
                        "id": vuln.get("VulnerabilityID", "UNKNOWN"),
                        "severity": vuln.get("Severity", "UNKNOWN"),
                        "package": vuln.get("PkgName", "UNKNOWN"),
                        "version": vuln.get("InstalledVersion", "UNKNOWN"),
                        "fixed_version": vuln.get("FixedVersion", "N/A"),
                        "title": vuln.get("Title", "No title"),
                    }
                )
        return vulns

    def _extract_secrets(self, data: Dict) -> List[Dict]:
        """Extract secret findings"""
        secrets = []
        results = data.get("Results", [])
        for result in results:
            for secret in result.get("Secrets", []):
                secrets.append(
                    {
                        "rule_id": secret.get("RuleID", "UNKNOWN"),
                        "category": secret.get("Category", "UNKNOWN"),
                        "severity": secret.get("Severity", "UNKNOWN"),
                        "title": secret.get("Title", "No title"),
                        "match": secret.get("Match", "")[:100],  # Truncate
                    }
                )
        return secrets

    def _extract_licenses(self, data: Dict) -> List[Dict]:
        """Extract license information"""
        licenses = []
        results = data.get("Results", [])
        for result in results:
            for license_info in result.get("Licenses", []):
                license_name = license_info.get("Name", "UNKNOWN")
                licenses.append(
                    {
                        "name": license_name,
                        "severity": license_info.get("Severity", "UNKNOWN"),
                        "file": license_info.get("FilePath", "UNKNOWN"),
                        "forbidden": license_name in self.forbidden_licenses,
                    }
                )
        return licenses

    def _save_report(self, data: Dict, output_file: str):
        """Save JSON report to file"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"[TRIVY] Report saved to {output_file}")
        except Exception as e:
            print(f"[TRIVY] ERROR: Failed to save report: {e}")

    def generate_sbom(self, repo_path: str, output_path: str):
        """Generate CycloneDX SBOM"""
        print(f"[TRIVY] Generating SBOM for {repo_path}...")

        cmd = [self.trivy_path, "fs", "--format", "cyclonedx", "--output", output_path, "--quiet", repo_path]

        try:
            subprocess.run(cmd, check=True, timeout=300)
            print(f"[TRIVY] SBOM saved to {output_path}")
        except subprocess.TimeoutExpired:
            print("[TRIVY] ERROR: SBOM generation timed out")
        except subprocess.CalledProcessError as e:
            print(f"[TRIVY] ERROR: SBOM generation failed: {e}")
        except Exception as e:
            print(f"[TRIVY] ERROR: {str(e)}")


def main():
    """Test the scanner"""
    if len(sys.argv) < 2:
        print("Usage: python trivy_scan.py <repo_path>")
        sys.exit(1)

    repo_path = sys.argv[1]

    scanner = TrivyScanner()
    score, vulns, secrets, licenses = scanner.scan_repository(repo_path)

    print("\n" + "=" * 60)
    print(f"SECURITY SCORE: {score}/100")
    print("=" * 60)

    if vulns:
        print(f"\nVulnerabilities ({len(vulns)}):")
        for v in vulns[:5]:  # Show first 5
            print(f"  - {v['id']} ({v['severity']}): {v['package']} {v['version']}")

    if secrets:
        print(f"\nSecrets ({len(secrets)}):")
        for s in secrets[:5]:
            print(f"  - {s['rule_id']} ({s['severity']}): {s['title']}")

    if licenses:
        print(f"\nLicenses ({len(licenses)}):")
        for l in licenses[:5]:
            forbidden_flag = " [FORBIDDEN]" if l["forbidden"] else ""
            print(f"  - {l['name']}{forbidden_flag}")


if __name__ == "__main__":
    main()