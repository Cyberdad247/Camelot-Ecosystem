import { describe, it, expect } from 'vitest';
import express from 'express';
import htmxRouter from './htmx_router';

describe('Bifrost HATEOAS / HTMX Router', () => {
  const app = express();
  app.use('/htmx', htmxRouter);

  it('renders dashboard shell with Luxora Gold accents', async () => {
    // Test endpoint via node request or express route inspection
    const res = await new Promise<{ status: number; text: string }>((resolve) => {
      const server = app.listen(0, async () => {
        const addr = server.address();
        const port = typeof addr === 'object' && addr ? addr.port : 0;
        const resp = await fetch(`http://127.0.0.1:${port}/htmx/dashboard`);
        const text = await resp.text();
        server.close(() => resolve({ status: resp.status, text }));
      });
    });

    expect(res.status).toBe(200);
    expect(res.text).toContain('#D4AF37');
    expect(res.text).toContain('CAMELOT-OS BIFROST GATEWAY');
    expect(res.text).toContain('hx-get="/htmx/knights"');
  });

  it('renders all knight cards with correct attributes', async () => {
    const res = await new Promise<{ status: number; text: string }>((resolve) => {
      const server = app.listen(0, async () => {
        const addr = server.address();
        const port = typeof addr === 'object' && addr ? addr.port : 0;
        const resp = await fetch(`http://127.0.0.1:${port}/htmx/knights`);
        const text = await resp.text();
        server.close(() => resolve({ status: resp.status, text }));
      });
    });

    expect(res.status).toBe(200);
    expect(res.text).toContain('SIR_HELIOS');
    expect(res.text).toContain('MERLIN_OMEGA');
    expect(res.text).toContain('ANYA_OMEGA');
    expect(res.text).toContain('hx-get="/htmx/knights/SIR_HELIOS/inspect"');
  });

  it('renders deep telemetry for a specific knight', async () => {
    const res = await new Promise<{ status: number; text: string }>((resolve) => {
      const server = app.listen(0, async () => {
        const addr = server.address();
        const port = typeof addr === 'object' && addr ? addr.port : 0;
        const resp = await fetch(`http://127.0.0.1:${port}/htmx/knights/sir_helios/inspect`);
        const text = await resp.text();
        server.close(() => resolve({ status: resp.status, text }));
      });
    });

    expect(res.status).toBe(200);
    expect(res.text).toContain('0xAB8AA3592B3B4BC1B41F34979CDC184E');
    expect(res.text).toContain('Global Law 03');
    expect(res.text).toContain('32 MB');
  });

  it('returns 404 for unknown knight inspection', async () => {
    const res = await new Promise<{ status: number; text: string }>((resolve) => {
      const server = app.listen(0, async () => {
        const addr = server.address();
        const port = typeof addr === 'object' && addr ? addr.port : 0;
        const resp = await fetch(`http://127.0.0.1:${port}/htmx/knights/unknown_knight/inspect`);
        const text = await resp.text();
        server.close(() => resolve({ status: resp.status, text }));
      });
    });

    expect(res.status).toBe(404);
    expect(res.text).toContain("Knight 'UNKNOWN_KNIGHT' not found");
  });
});
