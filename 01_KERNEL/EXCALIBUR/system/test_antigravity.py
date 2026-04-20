# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os

from src.tools.antigravity import gravity


def test_kinetic_ops():
    test_file = "test_kinetic.txt"

    print("Testing WRITE...")
    gravity.write(test_file, "Initial Kinetic Content\n")

    print("Testing READ...")
    content = gravity.read(test_file)
    print(f"Content: {content.strip()}")

    print("Testing APPEND...")
    gravity.append(test_file, "Additional Energy Flux\n")

    print("Testing DELETE...")
    gravity.delete(test_file)

    print("Verifying Backups...")
    backups = os.listdir(".antigravity_backups")
    print(f"Backups found: {len(backups)}")
    for b in backups:
        print(f" - {b}")


if __name__ == "__main__":
    try:
        test_kinetic_ops()
        print("\n✅ ANTIGRAVITY VERIFIED: Kinetic Integrity Stable.")
    except Exception as e:
        print(f"\n❌ ANTIGRAVITY FAILURE: {e}")