import { render, screen, within } from '@testing-library/react';
import { describe, expect, it, beforeEach, vi } from 'vitest';
import type { ReactNode } from 'react';
import App from '../App';

const camelotOsFixture = {
  status: 'OK',
  generated_utc: '2026-05-13T18:00:00Z',
  repo_root: 'C:\\Users\\vizio\\CAMELOT_OS',
  version: 'v701.0',
  summary: {
    architecture_layers: 7,
    schematic_edges: 10,
    active_cartridges: 9,
    knights: 31,
    codex_surfaces_online: 5,
    cloudbrain_queue_pending: 0,
  },
  orchestration: {
    layers: [],
    edges: [],
    codex_surfaces: { cli: true, boot: true, ledger: true, dashboard: true, cloudbrain: true },
    switchboard_terminals: [],
    cartridges: { active_count: 9, names: [] },
    roster: { count: 31, agents: [] },
  },
  memory_tiers: [],
  ledgers: {
    root: { exists: true, path: 'PROVENANCE_LEDGER.md' },
    verification: { exists: true, path: '03_VAULT/Missions/verification_ledger.jsonl' },
    cloudbrain_manifest: { exists: true, path: '03_VAULT/runtime_state/camelot_cloudbrain_v701_manifest.json' },
    codex_integration: { exists: true, path: '03_VAULT/runtime_state/codex_integration_latest.json' },
    knight_configuration: { exists: true, path: '03_VAULT/runtime_state/knight_configuration_latest.json' },
    latest_root_excerpt: '',
  },
  outputs: {},
  frontier: {
    schema: 'camelot.frontier_nodes.v1',
    generated_utc: '2026-05-13T18:00:00Z',
    artifact_path: '03_VAULT/runtime_state/frontier_nodes_latest.json',
    nodes: [
      {
        node_id: 'chatgpt_frontier',
        provider: 'openai',
        surface: 'ChatGPT / OpenAI API',
        role: 'strategic_planner',
        permissions: ['status', 'route'],
        memory_tiers: ['flash', 'short'],
        status: 'available',
      },
    ],
    support: {
      status: 'disabled',
      active_session: null,
      sessions: [],
    },
    events: [],
  },
};

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  function BrowserRouterMock({ children }: { children: ReactNode }) {
    return (
      <actual.MemoryRouter initialEntries={[window.location.pathname || '/']}>
        {children}
      </actual.MemoryRouter>
    );
  }

  return {
    ...actual,
    BrowserRouter: BrowserRouterMock,
  };
});

const navItems = [
  { label: 'Hub', path: '/' },
  { label: 'OS', path: '/camelot-os' },
  { label: 'Alex', path: '/alex' },
  { label: 'Research', path: '/research' },
  { label: 'Dev', path: '/dev' },
  { label: 'Defense', path: '/defense-grid' },
] as const;

describe('App navigation and development portal', () => {
  beforeEach(() => {
    window.history.pushState({}, '', '/dev');
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes('/api/camelot-os/status')) {
        return new Response(JSON.stringify(camelotOsFixture), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('{}', { status: 200, headers: { 'Content-Type': 'application/json' } });
    }));
  });

  it('renders the development portal headings, live status, and affordances', async () => {
    render(<App />);

    expect(
      await screen.findByRole('heading', { name: /camelot command deck/i }),
    ).toBeInTheDocument();
    expect((await screen.findAllByText(/development portal/i)).length).toBeGreaterThan(0);

    expect(await screen.findByRole('heading', { name: /route health/i })).toBeInTheDocument();
    expect(await screen.findByRole('heading', { name: /command console/i })).toBeInTheDocument();
    expect(await screen.findByRole('heading', { name: /bridge transcript/i })).toBeInTheDocument();
    expect(await screen.findByRole('heading', { name: /console log/i })).toBeInTheDocument();
    expect(await screen.findByRole('heading', { name: /operational readiness/i })).toBeInTheDocument();

    expect(await screen.findByText(/development console/i)).toBeInTheDocument();
    expect(await screen.findByText(/websocket linked|websocket offline/i)).toBeInTheDocument();
  });

  it('renders the intended bottom navigation and marks dev as the active route', async () => {
    window.innerWidth = 480;
    window.innerHeight = 900;
    render(<App />);

    const nav = await screen.findByRole('navigation');

    navItems.forEach(({ label, path }) => {
      const link = within(nav).getByRole('link', { name: label });
      expect(link).toHaveAttribute('href', path);
    });

    expect(within(nav).getByRole('link', { name: 'Dev' })).toHaveAttribute('aria-current', 'page');
    expect(within(nav).getAllByRole('link')).toHaveLength(navItems.length);
  });

  it('renders the Defense Grid user console route', async () => {
    window.history.pushState({}, '', '/defense-grid');
    render(<App />);

    expect(await screen.findByRole('heading', { name: /defense grid console/i })).toBeInTheDocument();
    expect(await screen.findByRole('heading', { name: /user console/i })).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /^run$/i })).toBeInTheDocument();
    expect(await screen.findByText(/lockdown requires typed confirmation/i)).toBeInTheDocument();
  });

  it('renders the Camelot OS command route', async () => {
    window.history.pushState({}, '', '/camelot-os');
    render(<App />);

    expect(await screen.findByRole('heading', { name: /camelot os command/i })).toBeInTheDocument();
    expect(await screen.findByText(/whole-system map/i)).toBeInTheDocument();
  });
});
