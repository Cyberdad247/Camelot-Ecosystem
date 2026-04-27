import { render, screen, within } from '@testing-library/react';
import { describe, expect, it, beforeEach, vi } from 'vitest';
import type { ReactNode } from 'react';
import App from '../App';

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
  { label: 'Alex', path: '/alex' },
  { label: 'Research', path: '/research' },
  { label: 'Dev', path: '/dev' },
  { label: 'Cartridges', path: '/cartridge/cognitive' },
  { label: 'Map', path: '/openviking' },
] as const;

describe('App navigation and development portal', () => {
  beforeEach(() => {
    window.history.pushState({}, '', '/dev');
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
});
