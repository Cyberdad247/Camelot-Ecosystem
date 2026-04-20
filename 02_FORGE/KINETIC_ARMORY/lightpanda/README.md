# Lightpanda — Ultra-Low-Memory Headless Browser

Zig-compiled headless browser for AI-driven web scraping. 16x lighter than Chromium.
Exposes a CDP (Chrome DevTools Protocol) endpoint at `ws://127.0.0.1:9222`.

## Why Lightpanda

- Chromium headless: ~300-500MB RAM per instance
- Lightpanda: ~20-30MB RAM per instance
- Critical for Titanium Law T6 (8GB RAM ceiling)

## Installation

### Linux / WSL
```bash
curl -L -o lightpanda https://github.com/lightpanda-io/browser/releases/download/nightly/lightpanda-x86_64-linux
chmod a+x ./lightpanda
```

### Windows (via WSL)
```powershell
wsl curl -L -o /usr/local/bin/lightpanda https://github.com/lightpanda-io/browser/releases/download/nightly/lightpanda-x86_64-linux
wsl chmod a+x /usr/local/bin/lightpanda
```

## Usage
```bash
./lightpanda serve --host 127.0.0.1 --port 9222 --obey-robots --log-format pretty --log-level info
```

## Integration
Lady Apis and mcp_web_search connect via:
```python
browser = await playwright.chromium.connect_over_cdp("ws://127.0.0.1:9222")
```
