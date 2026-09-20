<!-- Copyright © 2026 Invisioned Marketing inc. All Rights Reserved. -->
# System Instruction: vps-operator-console
**Cartridge ID**: `vps-operator-console` | **Risk Tier Cap**: `T1`  
**Bound Knights**: `SIR_BORIS`, `HERMES_PRIME`, `SIR_HELIOS`  
**CloudBrain Node UUID**: `a0a4bfb9-e847-4c38-be39-7aee398f0795` (WorldTree Root)

---

## 1. Cartridge Mandate

`vps-operator-console` is a dedicated, zero-dependency Go/HTMX administrative cockpit designed for headless VPS and edge deployment:
- Serves an ultra-low overhead Web interface on `:3004`.
- Employs HTMX polling/SSE streams to display active mission DAGs, real-time cryptographic receipts, and cgroup hardware health metrics.
- Mounts an interactive WebGL Three.js spatial view (`WorldTreeScene.js`) rendering the 3D memory node orbit.
- Operates strictly under the 8GB Scarcity Protocol without requiring Node.js or Python runtime overhead in the serving layer.

---

## 2. Invariants & Governance

1. **Pure Go Hotpath**: Serving layer uses standard library `net/http` and static HTML templates.
2. **Scarcity Respect**: Omarchy health checks monitor memory usage across systemd slices (`camelot-critical`, `camelot-control`, etc.).
3. **No Cross-Package Collision**: Lives in an isolated module root (`go.mod`), never colliding with Next.js PWA (`apps/pwa`).
