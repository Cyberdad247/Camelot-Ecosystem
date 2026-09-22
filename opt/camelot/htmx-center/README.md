# ⚜️ Camelot-OS HTMX Command Center

A pure **Go + HTMX + SSE** single-page application dashboard running 100% Docker-free as a native binary.

## Architecture
- **Backend:** Native Go standard library (`net/http`, `html/template`, `sync`)
- **Frontend:** HTMX with SSE streaming + Obsidian/Gold/Purple CSS theme
- **Footprint:** <= 256MB memory cap, low CPU overhead
- **Deployment:** Systemd service on `/opt/camelot/htmx-center`

## Commands
```bash
# Build & run locally
go run main.go

# Install systemd service
sudo ./deploy/install.sh
```

⚜️_SOVEREIGN_TRUTH
