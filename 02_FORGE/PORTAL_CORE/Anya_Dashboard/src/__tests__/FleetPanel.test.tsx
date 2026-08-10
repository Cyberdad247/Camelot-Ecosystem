import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import FleetPanel from '@/features/hub/FleetPanel';

const fleetFixture = {
  daemons: [
    { name: 'go_router', role: 'SSE rune router (Go)', up: true },
    { name: 'bifrost_sidecar', role: 'Bifrost bridge (Go)', up: true },
    { name: 'cognitive_service', role: 'Graphify/MemCastle/sync (Python)', up: false },
  ],
  tailnet: {
    tailnet: 'camelot.ts.net',
    nodes: [
      { name: 'cybertronia', ip: '100.1.1.1', os: 'linux', online: true, self: true },
      { name: 'forge-node', ip: '100.1.1.2', os: 'windows', online: false, self: false },
    ],
  },
  vault_items: 42,
  cloud_reachable: true,
  cloud: 'ok',
};

describe('FleetPanel', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes('/cognitive/fleet')) {
        return new Response(JSON.stringify(fleetFixture), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('{}', { status: 404 });
    }));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('renders daemon health and tailnet nodes from /cognitive/fleet', async () => {
    render(<FleetPanel />);

    expect(await screen.findByText('go_router')).toBeInTheDocument();
    expect(screen.getByText('bifrost_sidecar')).toBeInTheDocument();
    expect(screen.getByText('cognitive_service')).toBeInTheDocument();

    await waitFor(() => expect(screen.getByText('2/3 daemons up')).toBeInTheDocument());

    expect(screen.getByText('cybertronia')).toBeInTheDocument();
    expect(screen.getByText('forge-node')).toBeInTheDocument();
    expect(screen.getByText('(self)')).toBeInTheDocument();
    expect(screen.getByText(/Vault 42/)).toBeInTheDocument();
  });

  it('shows an error state when the cognitive service is unreachable', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => {
      throw new Error('network down');
    }));

    render(<FleetPanel />);

    expect(
      await screen.findByText(/Cognitive Service unreachable/i),
    ).toBeInTheDocument();
  });
});
