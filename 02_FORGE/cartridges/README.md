# 📦 Cartridges

> **STATUS:** Active

Cartridge distribution and deployment packages for CAMELOT-OS.

## Contents

| Package | Description | Status |
|---------|-------------|--------|
| [`kba_drone/`](kba_drone/) | KBA Drone cartridge (`.cartridge.zip`) | Active |

## Usage

Cartridges are verified and deployed using the [`cartridge/`](../cartridge/) subsystem:

```bash
python -m cartridge.cartridge_cli verify cartridges/kba_drone/camelot_kba_drone.zip
```
