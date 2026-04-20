# 03_VAULT: The Semantic Archive (L4)

## 🏛️ OVERVIEW

The **Vault Realm** is the secure storage and knowledge base of Camelot OS. It holds data, logs, external references, and the Nano-Knights extensions.

## 📂 STRUCTURE

- `00_SECURE_ARCHIVE/`: Quarantined secrets and sensitive backups.
- `data_store/`: Active application data (SQLite, Cache).
- `external/`: Documentation and code from external sources.
- `Nano-Knights/`: Chrome Extension & Swarm Intelligence Source.

## 🔒 SECURITY PROTOCOL

1. **Zero Trust:** Nothing enters the Vault unchecked.
2. **Quarantine:** Secrets found in audits are moved to `00_SECURE_ARCHIVE`.
3. **No Execution:** Code in `external/` is for reference only.
