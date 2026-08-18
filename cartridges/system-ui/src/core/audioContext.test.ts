import { beforeEach, describe, expect, it, vi } from 'vitest';
import { KickboxAudioController } from './audioContext';

// Mock Web Audio API as a proper class for Node test environment
const mockGainNode = {
  gain: { setValueAtTime: vi.fn() },
  connect: vi.fn(),
  disconnect: vi.fn(),
};

class MockAudioContext {
  currentTime = 0;
  destination = {};
  state = 'running';
  createGain = vi.fn(() => mockGainNode);
  close = vi.fn();
}

vi.stubGlobal('AudioContext', MockAudioContext);

describe('KickboxAudioController', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize AudioContext and set gain node volume', () => {
    const controller = new KickboxAudioController();
    controller.init();
    expect(controller.ctx).not.toBeNull();

    controller.setVolume(0.7);
    expect(controller.getVolume()).toBe(0.7);
    expect(mockGainNode.gain.setValueAtTime).toHaveBeenCalledWith(0.7, 0);
  });

  it('should clamp volume between 0.0 and 1.0', () => {
    const controller = new KickboxAudioController();
    controller.init();

    controller.setVolume(-0.5);
    expect(controller.getVolume()).toBe(0.0);

    controller.setVolume(1.5);
    expect(controller.getVolume()).toBe(1.0);
  });

  it('should default volume to 1.0', () => {
    const controller = new KickboxAudioController();
    expect(controller.getVolume()).toBe(1.0);
  });

  it('should connect gain node to destination on init', () => {
    const controller = new KickboxAudioController();
    controller.init();
    expect(mockGainNode.connect).toHaveBeenCalled();
  });

  it('should dispose cleanly', () => {
    const controller = new KickboxAudioController();
    controller.init();
    controller.dispose();
    expect(controller.ctx).toBeNull();
    expect(mockGainNode.disconnect).toHaveBeenCalled();
  });
});
