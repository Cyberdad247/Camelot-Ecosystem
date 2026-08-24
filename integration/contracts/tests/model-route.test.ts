// Phase 3: model.route session events fold into the view; fallback is
// visible, never silent.

import { describe, expect, it } from 'vitest';
import { initialSessionView, reduceSessionEvent } from '../src/index.js';

describe('model.route events', () => {
  it('records the narrating provider', () => {
    const view = reduceSessionEvent(initialSessionView(), {
      type: 'model.route',
      turnId: 'turn-1',
      provider: 'testprov',
    });
    expect(view.lastModelRoute).toEqual({ turnId: 'turn-1', provider: 'testprov', fallback: false });
  });

  it('a fallback route overwrites the primary route visibly', () => {
    let view = reduceSessionEvent(initialSessionView(), {
      type: 'model.route',
      turnId: 'turn-1',
      provider: 'testprov',
    });
    view = reduceSessionEvent(view, {
      type: 'model.route',
      turnId: 'turn-1',
      provider: 'deterministic',
      fallback: true,
      reason: 'provider failed: timeout',
    });
    expect(view.lastModelRoute).toEqual({
      turnId: 'turn-1',
      provider: 'deterministic',
      fallback: true,
    });
  });

  it('unknown-to-old-clients events do not disturb other state', () => {
    const base = initialSessionView();
    const view = reduceSessionEvent(base, {
      type: 'model.route',
      turnId: 'turn-1',
      provider: 'x',
    });
    expect(view.uiState).toBe(base.uiState);
    expect(view.replies).toEqual(base.replies);
  });
});
