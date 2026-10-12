# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import argparse
import os
import sys

# Add 01_KERNEL to path
kernel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(kernel_path)

from assimilation.core.handlers import assimilate_repo  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Camelot Repo Assimilation CLI")
    parser.add_argument("repo_path", help="Path to the repository")
    parser.add_argument("--tags", nargs="+", default=[], help="Tags to apply")
    parser.add_argument("--origin", default="local", help="Origin source")

    args = parser.parse_args()

    print(f"[CAMELOT] Assimilating: {args.repo_path}")
    result = assimilate_repo(args.repo_path, args.tags, args.origin)
    print(f"[RESULT] Status: {result.status}")
    print(f"[REPORT] {result.report_path}")


if __name__ == "__main__":
    main()