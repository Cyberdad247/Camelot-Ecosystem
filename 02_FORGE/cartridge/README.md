# 📦 Cartridge — Cryptographic Packaging & Verification System

> **STATUS:** Production · Python + Rust

The Cartridge system is CAMELOT-OS's secure software packaging pipeline. It provides Ed25519 cryptographic signing, SHA-256 content hashing, publisher trust registry with RBAC, sandbox resource constraints, and WASM orchestration — all wrapped in a verifiable `.cartridge` archive format.

## Stack

| Layer | Technology |
|-------|-----------|
| CLI | Python 3 (`cartridge_cli.py`) |
| Crypto | Ed25519 (keypair generation, signing, verification) |
| Hashing | SHA-256 content integrity |
| Archive | ZIP-based `.cartridge` format (V2) |
| Trust | Publisher registry, key management, revocation |
| Sandbox | Resource-constrained execution environment |
| WASM | Wasmtime orchestration via `rustclaw/` |
| Browser | Exportable publisher bundles for PWA Cockpit |

## Commands

> **Working directory:** All commands must be run from the `02_FORGE/` root (parent of `cartridge/`), as the module uses relative imports.

```bash
# Generate an Ed25519 keypair
python -m cartridge.cartridge_cli keygen

# Pack a source directory into a signed .cartridge
python -m cartridge.cartridge_cli pack \
  --source packages/AGENT_FLEET \
  --manifest packages/AGENT_FLEET/manifest.json \
  --output dist/AGENT_FLEET.cartridge \
  --publisher acme-cartridge-works

# Verify a .cartridge archive
python -m cartridge.cartridge_cli verify dist/AGENT_FLEET.cartridge

# Register a trusted publisher
python -m cartridge.cartridge_cli add-publisher my-publisher --kids key-1 key-2

# Export publisher bundle for browser loading
python -m cartridge.cartridge_cli export-bundle --output ./publishers.json
```

## Architecture

```
cartridge/
├── cartridge_cli.py        # CLI entry point (pack, verify, keygen, add-publisher, export-bundle)
├── cartridge_archive.py    # .cartridge format pack/unpack engine
├── cartridge_schemas.py    # Pydantic V2 manifest schema
├── cartridge_crypto.py     # Ed25519 keypair generation and signing
├── cartridge_trust.py      # Publisher registry, trust manager, revocation
├── cartridge_rbac.py       # Role-based access control
├── cartridge_v2_adapter.py # V2 format adapter
├── sandbox.py              # Resource-constrained sandbox
├── bifrost_bridge.py       # Bifrost P2P tunnel integration
├── fabrication_engine.py   # Cartridge fabrication pipeline
├── tool_registry.py        # Registered tool manifest
├── wasm_orchestrator.json  # WASM orchestration config
├── kba_tools.py            # Knowledge base agent tools
├── rustclaw/               # Rust WASM runtime (Cargo)
├── packages/               # Cartridge packages
└── data/                   # Runtime data and trust stores
```

## Tests

```bash
# Run from 02_FORGE/ root
cd 02_FORGE && pytest cartridge/test_*.py -v
```

Test files: `test_bifrost_bridge.py`, `test_cartridge_v2.py`, `test_fabrication.py`, `test_rbac.py`, `test_sandbox.py`, `test_trust.py`
