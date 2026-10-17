// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import React from 'react';
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { TacticalButton } from './TacticalButton';
import { BadgeGlyph } from './BadgeGlyph';
import { MetricStat } from './MetricStat';
import { CommandInput } from './CommandInput';
import { GlassPanel } from './GlassPanel';

describe('Excalibur UI Atoms Design System', () => {
  beforeEach(() => {
    vi.stubGlobal('navigator', {
      vibrate: vi.fn(),
    });
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  describe('TacticalButton', () => {
    it('renders with children and triggers click handler with haptics', () => {
      const handleClick = vi.fn();
      render(React.createElement(TacticalButton, { onClick: handleClick }, 'Engage'));

      const btn = screen.getByRole('button', { name: /engage/i });
      expect(btn).toBeInTheDocument();
      expect(btn).toHaveClass('min-h-[44px]'); // 44px touch target invariant

      fireEvent.click(btn);
      expect(handleClick).toHaveBeenCalledTimes(1);
      expect(navigator.vibrate).toHaveBeenCalledWith(14); // tap haptic
    });

    it('renders loading spinner and disables click', () => {
      const handleClick = vi.fn();
      render(React.createElement(TacticalButton, { loading: true, onClick: handleClick }, 'Submit'));

      const btn = screen.getByRole('button', { name: /submit/i });
      expect(btn).toBeDisabled();
      fireEvent.click(btn);
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('BadgeGlyph', () => {
    it('renders semantic status colors and glyphs', () => {
      render(React.createElement(BadgeGlyph, { status: 'ONLINE' }));
      const badge = screen.getByText('ONLINE');
      expect(badge).toBeInTheDocument();
      expect(screen.getByText('⚡')).toBeInTheDocument();
    });

    it('supports custom label and glyph overrides', () => {
      render(React.createElement(BadgeGlyph, { status: 'AIRGAP', label: 'OFFLINE VAULT', glyph: '🔒' }));
      expect(screen.getByText('OFFLINE VAULT')).toBeInTheDocument();
      expect(screen.getByText('🔒')).toBeInTheDocument();
    });
  });

  describe('MetricStat', () => {
    it('calculates percentage against ceiling and renders label', () => {
      render(
        React.createElement(MetricStat, {
          label: 'RAM ALLOCATION',
          value: 2048,
          ceiling: 4096,
          unit: 'MB',
          delta: 5,
        })
      );

      expect(screen.getByText('RAM ALLOCATION')).toBeInTheDocument();
      expect(screen.getByText('2048')).toBeInTheDocument();
      expect(screen.getByText('/ 4096 MB')).toBeInTheDocument();
      expect(screen.getByText('+5%')).toBeInTheDocument();
    });
  });

  describe('CommandInput', () => {
    it('renders prompt input and handles runic command submission', () => {
      const handleSubmit = vi.fn();
      render(
        React.createElement(CommandInput, {
          onSubmit: handleSubmit,
          placeholder: 'Type command...',
        })
      );

      const input = screen.getByPlaceholderText('Type command...');
      expect(input).toBeInTheDocument();

      fireEvent.change(input, { target: { value: '//STATUS' } });
      fireEvent.keyDown(input, { key: 'Enter' });

      expect(handleSubmit).toHaveBeenCalledWith('//STATUS');
    });
  });

  describe('GlassPanel', () => {
    it('renders with appropriate tier classes', () => {
      const { container } = render(
        React.createElement(
          GlassPanel,
          { tier: 'sovereign', density: 'compact' },
          React.createElement('div', null, 'Content')
        )
      );

      const panel = container.firstChild as HTMLElement;
      expect(panel).toHaveClass('glass-panel-sovereign');
      expect(panel).toHaveClass('p-3');
    });
  });
});
