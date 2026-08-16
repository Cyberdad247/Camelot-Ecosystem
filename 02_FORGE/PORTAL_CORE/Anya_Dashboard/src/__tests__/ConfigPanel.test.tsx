import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import ConfigPanel from '@/features/hub/ConfigPanel';

describe('ConfigPanel', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('loads the persisted sync interval and query from /cognitive/config', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(
        async () =>
          new Response(JSON.stringify({ sync_interval: 30, sync_query: 'summarize the lattice' }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          }),
      ),
    );

    render(<ConfigPanel />);

    expect(await screen.findByDisplayValue('30')).toBeInTheDocument();
    expect(screen.getByDisplayValue('summarize the lattice')).toBeInTheDocument();
  });

  it('saves an edited interval + query via POST and reflects the persisted value', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      if (init?.method === 'POST') {
        return new Response(JSON.stringify({ sync_interval: 60, sync_query: 'new query' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response(JSON.stringify({ sync_interval: 30, sync_query: 'old query' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    });
    vi.stubGlobal('fetch', fetchMock);

    const user = userEvent.setup();
    render(<ConfigPanel />);

    const input = await screen.findByDisplayValue('30');
    await user.clear(input);
    await user.type(input, '60');

    const queryInput = screen.getByDisplayValue('old query');
    await user.clear(queryInput);
    await user.type(queryInput, 'new query');

    await user.click(screen.getByRole('button', { name: /save/i }));

    await waitFor(() => expect(screen.getByLabelText('Saved')).toBeInTheDocument());
    const postCall = fetchMock.mock.calls.find(
      ([, init]) => (init as RequestInit | undefined)?.method === 'POST',
    );
    expect(postCall?.[1]?.body).toBe(
      JSON.stringify({ sync_interval: 60, sync_query: 'new query' }),
    );
  });

  it('shows an error state when the cognitive service is unreachable', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        throw new Error('network down');
      }),
    );

    render(<ConfigPanel />);

    expect(await screen.findByText(/Cognitive Service unreachable/i)).toBeInTheDocument();
  });
});
