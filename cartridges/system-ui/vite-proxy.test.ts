import { describe, it, expect } from 'vitest';
import config from './vite.config';

describe('Vite Proxy Configuration', () => {
  it('should map Chatterbox TTS server to port 8300 and rewrite prefix', () => {
    const proxy = (config as any).server?.proxy;
    const rule = proxy['/api/chatterbox'];
    expect(rule?.target).toBe('http://127.0.0.1:8300');
    expect(typeof rule?.rewrite).toBe('function');
    expect(rule.rewrite('/api/chatterbox/synthesize')).toBe('/synthesize');
    expect(rule.rewrite('/api/chatterbox')).toBe('/');
  });

  it('should map Multivoice router to port 8001 and rewrite prefix', () => {
    const proxy = (config as any).server?.proxy;
    const rule = proxy['/api/multivoice'];
    expect(rule?.target).toBe('http://127.0.0.1:8001');
    expect(typeof rule?.rewrite).toBe('function');
    expect(rule.rewrite('/api/multivoice/intent')).toBe('/intent');
    expect(rule.rewrite('/api/multivoice')).toBe('/');
  });

  it('should list specific endpoints before catch-all /api', () => {
    const proxyKeys = Object.keys((config as any).server?.proxy || {});
    const chatterboxIdx = proxyKeys.indexOf('/api/chatterbox');
    const multivoiceIdx = proxyKeys.indexOf('/api/multivoice');
    const apiIdx = proxyKeys.indexOf('/api');

    expect(chatterboxIdx).toBeGreaterThan(-1);
    expect(multivoiceIdx).toBeGreaterThan(-1);
    expect(apiIdx).toBeGreaterThan(-1);
    expect(chatterboxIdx).toBeLessThan(apiIdx);
    expect(multivoiceIdx).toBeLessThan(apiIdx);
  });
});
