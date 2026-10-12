# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json
import os
import secrets
import string
import sys

# Setup paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "01_KERNEL"))

from security.vault_keeper import keeper  # noqa: E402


def update_sovereign_identity():
    # 1. Generate Randomized Password
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    new_password = "".join(secrets.choice(alphabet) for i in range(16))

    # 2. Update Vault
    try:
        # Load current secrets
        secrets_data = keeper.decrypt_vault()

        # Update identity fields
        secrets_data["SOVEREIGN_USER"] = "vizion711@gmail.com"
        secrets_data["SOVEREIGN_PASSWORD"] = new_password
        secrets_data["CREATOR"] = "VaShawn O. Head"
        secrets_data["COMPANY"] = "Invisioned Marketing inc."

        # Save back to secrets.json (temporarily as raw to be encrypted by encrypt_vault)
        secrets_path = "01_KERNEL/config/secrets.json"
        with open(secrets_path, "w") as f:
            json.dump(secrets_data, f, indent=2)

        # Re-encrypt
        keeper.encrypt_vault()

        print("[REFORGE] Sovereign Identity Updated.")
        print("[REFORGE] User: vizion711@gmail.com")
        print(f"[REFORGE] Password: {new_password}")
        print("[REFORGE] Creator: VaShawn O. Head")
        print("[REFORGE] Company: Invisioned Marketing inc.")
    except Exception as e:
        print(f"[ERROR] Failed to update vault: {e}")


if __name__ == "__main__":
    update_sovereign_identity()