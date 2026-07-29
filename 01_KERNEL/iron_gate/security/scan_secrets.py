# Copyright (c) 2026 CAMELOT OS. All rights reserved.
"""Secret Scanner -- Detects exposed credentials in the repository.

Used by CI/CD (verify_os.yml) and can be run manually:
    python scripts/scan_secrets.py [path]
"""

import os
import re
import sys

PATTERNS = [
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub PAT"),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth"),
    (r"sk-[a-zA-Z0-9]{32,}", "OpenAI/Stripe key"),
    (r"AIza[a-zA-Z0-9_\-]{35}", "Google API key"),
    (r"ak-[a-zA-Z0-9]{20,}", "Modal token ID"),
    (r"as-[a-zA-Z0-9]{20,}", "Modal token secret"),
    (r"xai-[a-zA-Z0-9]{20,}", "xAI/Grok key"),
    (r"hf_[a-zA-Z0-9]{20,}", "HuggingFace token"),
    (r"AKIA[A-Z0-9]{16}", "AWS access key"),
    (r"(?i)password\s*[:=]\s*[\"'][^\s\"']{8,}", "Hardcoded password"),
    (r"(?i)token_secret\s*[:=]\s*\"[a-zA-Z0-9\-]{16,}\"", "Token secret in config"),
]

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".secure",
             "target", "dist", "build", ".next"}

SCAN_EXTENSIONS = {".py", ".ts", ".js", ".json", ".yaml", ".yml", ".toml",
                   ".md", ".env", ".cfg", ".ini", ".conf", ".sh"}


def scan_path(root_path: str) -> list:
    """Scan a directory tree for exposed secrets."""
    violations = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in SCAN_EXTENSIONS:
                continue

            filepath = os.path.join(dirpath, fname)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for pattern, label in PATTERNS:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        # Get line number
                        line_num = content[:match.start()].count("\n") + 1
                        # Redact the actual value
                        val = match.group()
                        redacted = val[:6] + "***" + val[-3:]
                        rel_path = os.path.relpath(filepath, root_path)
                        violations.append({
                            "file": rel_path,
                            "line": line_num,
                            "type": label,
                            "match": redacted,
                        })
            except Exception:
                pass

    return violations


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    violations = scan_path(root)

    if violations:
        print(f"EXPOSED SECRETS DETECTED ({len(violations)}):")
        for v in violations:
            print(f"  {v['file']}:{v['line']} [{v['type']}] {v['match']}")
        sys.exit(1)
    else:
        print("[OK] No exposed secrets found")
        sys.exit(0)


if __name__ == "__main__":
    main()
