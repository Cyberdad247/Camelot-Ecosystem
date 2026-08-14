// SPDX-License-Identifier: MIT

import { describe, expect, it } from 'vitest';
import { ageLabel } from './formatters';

describe('formatters', () => {
  it('formats seconds and minutes ago', () => {
    const now = Date.now();
    expect(ageLabel(new Date(now - 30_000).toISOString(), now)).toBe('30s ago');
    expect(ageLabel(new Date(now - 2 * 60_000).toISOString(), now)).toBe('2m ago');
  });

  it('formats hours ago', () => {
    const now = Date.now();
    expect(ageLabel(new Date(now - 3 * 3_600_000).toISOString(), now)).toBe('3h ago');
  });
});
