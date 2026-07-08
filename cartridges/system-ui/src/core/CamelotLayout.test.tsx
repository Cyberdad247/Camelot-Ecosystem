// @vitest-environment jsdom
import { describe, it, expect, vi, afterEach } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';

// Mock R3F and THREE to avoid WebGL in jsdom test env
vi.mock('@react-three/fiber', () => ({
  Canvas: () => null,
  useThree: () => ({ gl: { dispose: vi.fn(), forceContextLoss: vi.fn() }, scene: { traverse: vi.fn() } }),
}));
vi.mock('three', () => ({
  Mesh: class {},
  AdditiveBlending: 2,
}));

// Stub AudioContext
class MockAudioContext {
  currentTime = 0;
  destination = {};
  state = 'running';
  createGain = vi.fn(() => ({
    gain: { setValueAtTime: vi.fn() },
    connect: vi.fn(),
    disconnect: vi.fn(),
  }));
  close = vi.fn();
}
vi.stubGlobal('AudioContext', MockAudioContext);

// Stub EventSource
vi.stubGlobal('EventSource', class {
  onmessage: any = null;
  onerror: any = null;
  close = vi.fn();
});

// Stub SpeechSynthesis
vi.stubGlobal('speechSynthesis', {
  speak: vi.fn(),
  cancel: vi.fn(),
});
vi.stubGlobal('SpeechSynthesisUtterance', class {
  pitch = 1;
  rate = 1;
  onstart: any = null;
  onend: any = null;
  onerror: any = null;
  constructor(public text: string) {}
});

import { render, screen } from '@testing-library/react';
import CamelotLayout from './CamelotLayout';

afterEach(() => {
  cleanup();
});

describe('CamelotLayout Component', () => {
  it('should render the EXCALIBUR header', () => {
    render(<CamelotLayout />);
    expect(screen.getByText(/EXCALIBUR/)).toBeInTheDocument();
  });

  it('should render COMMAND and FORGE tab buttons', () => {
    render(<CamelotLayout />);
    expect(screen.getByText('🜲 COMMAND')).toBeInTheDocument();
    expect(screen.getByText('🛠️ FORGE')).toBeInTheDocument();
  });

  it('should render VOX tab button', () => {
    render(<CamelotLayout />);
    expect(screen.getByText('🎤 VOX')).toBeInTheDocument();
  });
});
