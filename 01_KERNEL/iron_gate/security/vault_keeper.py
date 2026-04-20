# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json

from cryptography.fernet import Fernet
from src.tools.antigravity import gravity


class VaultKeeper:
    """
    The Keeper of the Sovereign Keychain.
    Handles AES-256 encryption/decryption of the secrets.json file.
    """

    def __init__(self, key_path: str = "01_KERNEL/security/master.key"):
        self.key_path = key_path
        self.secrets_path = "01_KERNEL/config/secrets.json"
        self._load_or_generate_key()

    def _load_or_generate_key(self):
        """Loads the encryption key from disk or generates a new one."""
        try:
            # Try to read via gravity (safe read)
            key_b64 = gravity.read(self.key_path)
            self.fernet = Fernet(key_b64.encode())
        except Exception:
            # Generate new key
            print("[VAULT] Generating new Master Key...")
            key = Fernet.generate_key()
            gravity.write(self.key_path, key.decode())
            self.fernet = Fernet(key)

    def encrypt_vault(self):
        """Encrypts the secrets.json file in place."""
        try:
            raw_content = gravity.read(self.secrets_path)
            # Verify it's valid JSON first
            json.loads(raw_content)

            encrypted_data = self.fernet.encrypt(raw_content.encode())
            gravity.write(self.secrets_path, encrypted_data.decode())  # Save as string
            print("[VAULT] Secrets Encrypted.")
            return True
        except json.JSONDecodeError:
            print("[VAULT] (WARN) Secrets already encrypted or invalid JSON.")
            return False
        except Exception as e:
            print(f"[VAULT] (FAIL) Encryption Failed: {e}")
            return False

    def decrypt_vault(self) -> dict:
        """Decrypts and returns the secrets as a dictionary."""
        try:
            encrypted_content = gravity.read(self.secrets_path)
            decrypted_data = self.fernet.decrypt(encrypted_content.encode())
            return json.loads(decrypted_data.decode())
        except Exception as e:
            # Fallback: Maybe it's not encrypted yet?
            try:
                raw = gravity.read(self.secrets_path)
                return json.loads(raw)
            except:
                print(f"[VAULT] (FAIL) Decryption Failed: {e}")
                return {}

    def get_secret(self, key: str) -> str:
        """Retrieves a single secret."""
        secrets = self.decrypt_vault()
        return secrets.get(key, "")


# Singleton Instance
keeper = VaultKeeper()