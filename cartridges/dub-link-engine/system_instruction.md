# Dub Link Engine Cartridge Specification (Sovereign URL Routing & Attribution)

## 1. Overview
The `dub-link-engine` cartridge assimilates the high-efficiency link routing, punycode domain normalization, and conversion attribution architecture pioneered by Dub (`Cyberdad247/dub`).

## 2. Capabilities & Constraints
- **Substrate**: Native Go Bifrost Gateway (`:3001/r/:key`) and HTMX Reactive Dashboards (`control_plane/infra/htmx_server.py`).
- **RAM Ceiling**: Strictly bounded to 512 MB memory profile complying with Global Law 03 (4 GB node limit).
- **Zero Hot-Path Bloat**: Redirects resolve in sub-millisecond Go/Rust memory tables rather than heavy Node.js SSR invocations.
- **VFS Integration**: Translates WorldTree coordinates (`vfs://worldtree/links/:slug`) into dynamic sovereign URLs.
