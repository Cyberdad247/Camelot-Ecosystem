# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# -*- coding: utf-8 -*-
"""
ZERO-TRUST VAULT MANAGER
Implements AES-256-GCM encrypted credential storage with audit logging.

USAGE:
    from vault_manager import VaultManager
    vault = VaultManager()
    vault.set("GITHUB_TOKEN", "ghp_...")
    token = vault.get("GITHUB_TOKEN")
"""
import base64
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class VaultManager:
    """Zero-Trust Vault for secure credential management."""
    
    VAULT_DIR = Path(__file__).parent / ".secure"
    VAULT_FILE = VAULT_DIR / "vault.enc"
    KEY_FILE = VAULT_DIR / "vault_master.key"
    LEDGER_PATH = Path(__file__).parent.parent / "PROVENANCE_LEDGER.md"
    
    def __init__(self):
        """Initialize the vault manager."""
        self.VAULT_DIR.mkdir(exist_ok=True)
        self._ensure_gitignore()
        
        if not self.KEY_FILE.exists():
            raise FileNotFoundError(
                f"Master key not found at {self.KEY_FILE}. "
                "Run 'python vault_manager.py init' first."
            )
        
        self.master_key = self._load_master_key()
        self.cipher = AESGCM(self.master_key)
    
    def _ensure_gitignore(self):
        """Ensure .secure/ is gitignored."""
        gitignore = self.VAULT_DIR / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*\n!.gitignore\n", encoding="utf-8")
    
    def _load_master_key(self) -> bytes:
        """Load the master encryption key."""
        return self.KEY_FILE.read_bytes()
    
    def _generate_master_key(self) -> bytes:
        """Generate a new 256-bit master key."""
        return AESGCM.generate_key(bit_length=256)
    
    def _encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext using AES-256-GCM."""
        nonce = os.urandom(12)  # 96-bit nonce
        ciphertext = self.cipher.encrypt(nonce, plaintext.encode("utf-8"), None)
        # Combine nonce + ciphertext and base64 encode
        return base64.b64encode(nonce + ciphertext).decode("utf-8")
    
    def _decrypt(self, encrypted: str) -> str:
        """Decrypt ciphertext using AES-256-GCM."""
        data = base64.b64decode(encrypted.encode("utf-8"))
        nonce = data[:12]
        ciphertext = data[12:]
        plaintext = self.cipher.decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")
    
    def _load_vault(self) -> Dict[str, Any]:
        """Load and decrypt the vault."""
        if not self.VAULT_FILE.exists():
            return {
                "credentials": {},
                "metadata": {
                    "version": "1.0.0",
                    "cipher": "AES-256-GCM",
                    "created_by": "CAMELOT_ARCHITECT",
                    "created_at": datetime.now().isoformat()
                }
            }
        
        encrypted_data = self.VAULT_FILE.read_text(encoding="utf-8")
        decrypted_json = self._decrypt(encrypted_data)
        return json.loads(decrypted_json)
    
    def _save_vault(self, vault_data: Dict[str, Any]):
        """Encrypt and save the vault."""
        json_str = json.dumps(vault_data, indent=2)
        encrypted = self._encrypt(json_str)
        self.VAULT_FILE.write_text(encrypted, encoding="utf-8")
    
    def _log_to_ledger(self, action: str, credential_name: str, status: str = "SUCCESS"):
        """Log vault operations to the provenance ledger."""
        timestamp = datetime.now().isoformat()
        entry = f"| {timestamp} | VAULT_MANAGER | {action}: {credential_name} | {status} |\n"
        
        try:
            with open(self.LEDGER_PATH, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            print(f"⚠️ [VAULT] Ledger Write Failed: {e}")
    
    def init(self):
        """Initialize a new vault with a fresh master key."""
        if self.KEY_FILE.exists():
            raise FileExistsError(
                f"Master key already exists at {self.KEY_FILE}. "
                "Use 'rotate-key' to regenerate."
            )
        
        # Generate and save master key
        master_key = self._generate_master_key()
        self.KEY_FILE.write_bytes(master_key)
        
        # Create empty vault
        self.master_key = master_key
        self.cipher = AESGCM(master_key)
        self._save_vault(self._load_vault())
        
        self._log_to_ledger("INIT", "VAULT", "SUCCESS")
        print(f"[OK] Vault initialized at {self.VAULT_DIR}")
        print(f"[KEY] Master key: {self.KEY_FILE}")
        print("[WARNING] NEVER commit the master key to git!")
    
    def set(self, name: str, value: str):
        """Store a credential in the vault."""
        vault = self._load_vault()
        
        vault["credentials"][name] = {
            "value": value,
            "created_at": datetime.now().isoformat(),
            "last_accessed": None,
            "access_count": 0
        }
        
        self._save_vault(vault)
        self._log_to_ledger("SET", name)
        print(f"[OK] Credential '{name}' stored securely.")
    
    def get(self, name: str) -> Optional[str]:
        """Retrieve a credential from the vault."""
        vault = self._load_vault()
        
        if name not in vault["credentials"]:
            self._log_to_ledger("GET", name, "NOT_FOUND")
            return None
        
        # Update access metadata
        vault["credentials"][name]["last_accessed"] = datetime.now().isoformat()
        vault["credentials"][name]["access_count"] += 1
        self._save_vault(vault)
        
        self._log_to_ledger("GET", name)
        return vault["credentials"][name]["value"]
    
    def list_credentials(self) -> Dict[str, Dict[str, Any]]:
        """List all credentials (metadata only, no values)."""
        vault = self._load_vault()
        return {
            name: {
                "created_at": cred["created_at"],
                "last_accessed": cred["last_accessed"],
                "access_count": cred["access_count"]
            }
            for name, cred in vault["credentials"].items()
        }
    
    def delete(self, name: str):
        """Delete a credential from the vault."""
        vault = self._load_vault()
        
        if name in vault["credentials"]:
            del vault["credentials"][name]
            self._save_vault(vault)
            self._log_to_ledger("DELETE", name)
            print(f"[OK] Credential '{name}' deleted.")
        else:
            print(f"[WARNING] Credential '{name}' not found.")
    
    def rotate_key(self):
        """Rotate the master key by re-encrypting the vault."""
        # Load vault with old key
        vault = self._load_vault()
        
        # Generate new key
        new_key = self._generate_master_key()
        self.KEY_FILE.write_bytes(new_key)
        
        # Re-encrypt vault with new key
        self.master_key = new_key
        self.cipher = AESGCM(new_key)
        self._save_vault(vault)
        
        self._log_to_ledger("ROTATE_KEY", "VAULT", "SUCCESS")
        print("[OK] Master key rotated. Vault re-encrypted.")


def main():
    """CLI interface for vault operations."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python vault_manager.py <command> [args]")
        print("Commands: init, set, get, list, delete, rotate-key")
        return
    
    command = sys.argv[1]
    
    if command == "init":
        vault = VaultManager.__new__(VaultManager)
        vault.VAULT_DIR.mkdir(exist_ok=True)
        vault._ensure_gitignore = VaultManager._ensure_gitignore.__get__(vault)
        vault._ensure_gitignore()
        vault.init()
    
    elif command == "set":
        if len(sys.argv) < 4:
            print("Usage: python vault_manager.py set <name> <value>")
            return
        vault = VaultManager()
        vault.set(sys.argv[2], sys.argv[3])
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: python vault_manager.py get <name>")
            return
        vault = VaultManager()
        value = vault.get(sys.argv[2])
        if value:
            print(f"{sys.argv[2]}: {value}")
        else:
            print(f"Credential '{sys.argv[2]}' not found.")
    
    elif command == "list":
        vault = VaultManager()
        creds = vault.list_credentials()
        for name, meta in creds.items():
            print(f"{name}:")
            print(f"  Created: {meta['created_at']}")
            print(f"  Last Accessed: {meta['last_accessed']}")
            print(f"  Access Count: {meta['access_count']}")
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: python vault_manager.py delete <name>")
            return
        vault = VaultManager()
        vault.delete(sys.argv[2])
    
    elif command == "rotate-key":
        vault = VaultManager()
        vault.rotate_key()
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()