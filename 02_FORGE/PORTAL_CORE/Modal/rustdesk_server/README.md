# camelot-rustdesk-server

Canonical repo-owned replacement for the deployed Modal app
`camelot-rustdesk-server`.

## Purpose

This service exposes the remote-access control surface used for RustDesk-style
session coordination.

## Ownership boundary

- Role: remote access / control
- Does not own long-term memory
- Does not own short-term NotebookLM state
- Must not be described as replacing `excalibur-brain`

## Entrypoints

- `POST /run_rustdesk`
- `GET /health`

## Env

- `RUSTDESK_RELAY_HOST` optional

## Deploy

```powershell
modal deploy CAMELOT_OS/02_FORGE/PORTAL_CORE/Modal/rustdesk_server/app.py
```
