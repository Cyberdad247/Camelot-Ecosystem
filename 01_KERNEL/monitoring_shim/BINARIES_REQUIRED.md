# Observability Binaries — Manual Fetch Required

Docker is outlawed on this host (Titanium Law I — Kinetic Purity). These are
standalone Go binaries that run natively. **Sir Boris will not auto-download
them** — network fetches exceed Iron Gate scope without your explicit approval.

## Targets

Place binaries at:

```
CAMELOT_OS/02_FORGE/kinetic/bin/prometheus/prometheus.exe
CAMELOT_OS/02_FORGE/kinetic/bin/grafana/bin/grafana-server.exe
```

## Prometheus — Windows amd64

Download: https://github.com/prometheus/prometheus/releases/latest
File:     `prometheus-<ver>.windows-amd64.zip`
Size:     ~100 MB zipped, ~180 MB extracted
RAM:      ~80 MB resident at idle

## Grafana OSS — Windows standalone

Download: https://grafana.com/grafana/download?platform=windows
File:     `grafana-<ver>.windows-amd64.zip` (standalone, NOT the installer)
Size:     ~120 MB zipped, ~350 MB extracted
RAM:      ~150 MB resident at idle

## Combined RAM Budget

Prometheus (~80 MB) + Grafana (~150 MB) + tsdb headroom (~100 MB) = **~330 MB**.
Current available RAM must be ≥ 1.5 GB before launch (launcher enforces this).

## Launch

```powershell
pwsh monitoring/start_observability.ps1
```

- Prometheus UI → http://localhost:9090
- Grafana UI    → http://localhost:3000  (default admin/admin, change on first login)
