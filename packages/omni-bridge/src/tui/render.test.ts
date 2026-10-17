import { describe, expect, it } from 'vitest';
import { PiMonoRenderer } from './render';

describe('pi-mono TUI Render', () => {
  it('should batch render calls under 200ms latency cap', async () => {
    const renderer = new PiMonoRenderer();
    let callCount = 0;
    let lastRendered = '';
    renderer.onRender = (output: string) => {
      callCount++;
      lastRendered = output;
    };

    renderer.updateFrame('stream1_data');
    renderer.updateFrame('stream2_data');

    await new Promise((r) => setTimeout(r, 260));
    expect(callCount).toBe(1);
    expect(lastRendered).toBe('stream1_datastream2_data');
  });

  it('should flush immediately when requested', () => {
    const renderer = new PiMonoRenderer();
    let rendered = '';
    renderer.onRender = (output: string) => {
      rendered = output;
    };

    renderer.updateFrame('immediate_data');
    renderer.flush();

    expect(rendered).toBe('immediate_data');
  });
});
