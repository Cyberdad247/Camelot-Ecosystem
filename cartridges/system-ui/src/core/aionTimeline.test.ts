import { describe, expect, it } from 'vitest';
import { AionTimelineCache } from './aionTimeline';

describe('AionTimelineCache', () => {
  it('should cache state frames and recall state at specific timeline timestamp', () => {
    const timeline = new AionTimelineCache(3);
    timeline.push({ cpu: 15, ram: 42 });
    timeline.push({ cpu: 25, ram: 43 });

    expect(timeline.getHistory().length).toBe(2);
    expect(timeline.getFrame(0)?.cpu).toBe(15);
  });

  it('should evict oldest frames when limit is exceeded', () => {
    const timeline = new AionTimelineCache(2);
    timeline.push({ cpu: 10, ram: 40 });
    timeline.push({ cpu: 20, ram: 41 });
    timeline.push({ cpu: 30, ram: 42 });

    expect(timeline.getHistory().length).toBe(2);
    expect(timeline.getFrame(0)?.cpu).toBe(20);
  });
});
