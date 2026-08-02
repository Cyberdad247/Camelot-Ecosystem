# ⚔️ Kinetic Sovereign — Omni-Modal TUI

> **STATUS:** Active · Go 1.25

Kinetic Sovereign is the unified Go interface for CAMELOT-OS — an omni-modal terminal UI built with Bubble Tea and Lip Gloss. Provides live voice interaction (Anya), system pulse monitoring (Squire), remote desktop bridging (Bifrost/RustDesk over Tailscale), and cryptographic vault access — all from a single terminal pane.

## Stack

| Layer | Technology |
|-------|-----------|
| Language | Go 1.25 |
| TUI Framework | Bubble Tea (charmbracelet) |
| Styling | Lip Gloss |
| WebSocket | gorilla/websocket |
| LiveKit | server-sdk-go (LiveKit protocol) |
| Redis | go-redis v9 |

## Tabs

| Tab | Key | Description |
|-----|-----|-------------|
| Anya (Live) | `1` | Voice interaction via camelot-nexus (LiveKit) |
| Pulse | `2` | System status, load index, A2A event stream |
| Remote | `3` | Bifrost Bridge — RustDesk encrypted P2P over Tailscale |
| Vault | `4` | Cryptographic key and token management |

## Keybindings

| Key | Action |
|-----|--------|
| `1-4` | Switch tabs |
| `v` | Toggle Anya voice listening |
| `c` | Connect to remote RustDesk target |
| `q` / `Ctrl+C` | Quit |

## Setup

```bash
cd 02_FORGE/kinetic_sovereign
go build -o sovereign.exe .
./sovereign.exe
```

## Turborepo

```bash
# From 02_FORGE/
npx turbo run go:build --filter=@camelot/kinetic-sovereign
npx turbo run go:test --filter=@camelot/kinetic-sovereign
```
