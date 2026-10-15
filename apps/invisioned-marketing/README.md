# Invisioned Marketing Inc. — Sovereign Digital Factory

Autonomous multi-agent digital marketing agency, B2B lead generation engine, and real-time fulfillment platform compiled under Camelot-OS.

## Cartridge Inventory

1. **Midas Lead Funnel** (`src/components/MidasLeadCapture.tsx`): B2B lead capture funnel with Doherty threshold responsiveness (<140ms).
2. **Command Nexus** (`src/components/SovereignCommandDashboard.tsx`): Real-time multi-agent swarm telemetry deck.
3. **Interactive B2B Proposal** (`src/components/InteractiveB2BProposal.tsx`): 2.5D spatial ROI calculator with cryptographic agreement locking.
4. **Tenant Cartridge Hypervisor** (`src/components/TenantCartridgeManager.tsx`): Hardware-bounded tenant resource manager enforcing 512MB WASM limits.
5. **Omni-Fulfillment Canvas** (`src/components/OmniFulfillmentCanvas.tsx`): Visual DAG node workflow production line.
6. **Holographic Client Oracle** (`src/components/HolographicClientOracle.tsx`): 2.5D audio-reactive avatar with 16-bar frequency visualizer.
7. **Client Oracle Portal** (`src/components/ClientOraclePortal.tsx`): VIP client lounge with GraphRAG knowledge queries.

## Edge API Endpoints

- `POST /api/invisioned/lead`: Sanitizes and persists leads to `03_VAULT/runtime_state/invisioned_leads.jsonl`.
- `GET /api/invisioned/telemetry`: Exposes live CPU, memory, and swarm metrics bounded by the 4GB node ceiling.
- `POST /api/invisioned/proposal`: Cryptographically signs and persists executed agreements with SHA-256 hashes.
- `POST /api/invisioned/oracle`: Resolves GraphRAG queries and delivers Web Audio stream configuration.

## Development & Deployment

```bash
# Run locally on port 3005
npm run dev

# Run typecheck
npm run typecheck

# Build for production
npm run build
```
