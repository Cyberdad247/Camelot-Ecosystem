# 01_KERNEL: The Sovereign Core (L3-L7)

## 🏛️ OVERVIEW

The **Kernel Realm** contains the central intelligence, configuration, and security logic of Camelot OS. It is the "Brain" (Merlin) and "Shield" (Arthur).

## 📂 STRUCTURE

- `core/`: Main execution loops (`excalibur.py`).
- `config/`: System-wide manifests (`titan_ledger`, `mcp_servers`).
- `security/`: Auth & Vault logic (`chivalry_gate`, `vault_keeper`).
- `scripts/`: Maintenance & Audit tools (`nano_cli_auditor`).
- `memory/`: Vector DB & Graph logic (UKG).

## ⚡ QUICK START

```bash
# Verify Health
python scripts/verify_kinetic_chain.py

# Run Core Loop
python core/excalibur.py
```

## 📜 TITANIUM LAWS (KERNEL)

1. **Context is Compiler:** Logic is derived from context, not hardcoded.
2. **Security First:** No execution without Chivalry Gate approval.
3. **Kinetic Purity:** If a binary exists (Forge), use it.
