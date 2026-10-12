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

  it('renders Compiler Explorer shell at /htmx/explorer', async () => {
    const res = await new Promise<{ status: number; text: string }>((resolve) => {
      const server = app.listen(0, async () => {
        const addr = server.address();
        const port = typeof addr === 'object' && addr ? addr.port : 0;
        const resp = await fetch(`http://127.0.0.1:${port}/htmx/explorer`);
        const text = await resp.text();
        server.close(() => resolve({ status: resp.status, text }));
      });
    });

    expect(res.status).toBe(200);
    expect(res.text).toContain('CAMELOT CODE EXPLORER');
    expect(res.text).toContain('Godbolt Assimilated');
    expect(res.text).toContain('hx-post="/htmx/explorer/inspect"');
    expect(res.text).toContain('SANDLOCK SECCOMP ARMED');
  });

  it('compiles code to aarch64 assembly via /htmx/explorer/inspect', async () => {
    const res = await new Promise<{ status: number; text: string }>((resolve) => {
      const server = app.listen(0, async () => {
        const addr = server.address();
        const port = typeof addr === 'object' && addr ? addr.port : 0;
        const resp = await fetch(`http://127.0.0.1:${port}/htmx/explorer/inspect`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            code: 'pub fn square(x: i32) -> i32 { x * x }',
            language: 'rust',
            target: 'aarch64',
            demangle: true,
          }),
        });
        const text = await resp.text();
        server.close(() => resolve({ status: resp.status, text }));
      });
    });

    expect(res.status).toBe(200);
    expect(res.text).toContain('aarch64 Target');
    expect(res.text).toContain('mul');
    expect(res.text).toContain('w0');
    expect(res.text).toContain('solution::square:');
  });

  it('compiles code to WebAssembly WAT via /htmx/explorer/inspect', async () => {
    const res = await new Promise<{ status: number; text: string }>((resolve) => {
      const server = app.listen(0, async () => {
        const addr = server.address();
        const port = typeof addr === 'object' && addr ? addr.port : 0;
        const resp = await fetch(`http://127.0.0.1:${port}/htmx/explorer/inspect`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            code: 'function square(x) { return x * x; }',
            language: 'typescript',
            target: 'wasm',
          }),
        });
        const text = await resp.text();
        server.close(() => resolve({ status: resp.status, text }));
      });
    });

    expect(res.status).toBe(200);
    expect(res.text).toContain('wasm Target');
    expect(res.text).toContain('(module');
    expect(res.text).toContain('i32.mul');
  });

  it('quantizes code to Triple-QFT Symbolect via /htmx/explorer/inspect', async () => {
    const res = await new Promise<{ status: number; text: string }>((resolve) => {
      const server = app.listen(0, async () => {
        const addr = server.address();
        const port = typeof addr === 'object' && addr ? addr.port : 0;
        const resp = await fetch(`http://127.0.0.1:${port}/htmx/explorer/inspect`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            code: 'def square(n):\n    return n * n',
            language: 'python',
            target: 'symbolect',
          }),
        });
        const text = await resp.text();
        server.close(() => resolve({ status: resp.status, text }));
      });
    });

    expect(res.status).toBe(200);
    expect(res.text).toContain('symbolect Target');
    expect(res.text).toContain('COMPILER_EXPLORER_QUANTIZED');
    expect(res.text).toContain('Z3_FORMAL_SAT');
  });
});

