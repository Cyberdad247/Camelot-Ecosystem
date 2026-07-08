import { describe, it, expect } from 'vitest';
import config from './vite.config';

describe('Vite Proxy Configuration', () => {
  it('should map Chatterbox TTS server to port 8300', () => {
    const proxy = (config as any).server?.proxy;
    expect(proxy['/api/chatterbox']?.target).toBe('http://127.0.0.1:8300');
  });

  it('should map Multivoice router to port 8001', () => {
    const proxy = (config as any).server?.proxy;
    expect(proxy['/api/multivoice']?.target).toBe('http://127.0.0.1:8001');
  });
});
