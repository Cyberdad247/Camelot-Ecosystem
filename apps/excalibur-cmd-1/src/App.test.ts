// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App';

vi.mock('./components/TelemetryHeader', () => ({
  TelemetryHeader: () => React.createElement('div', { 'data-testid': 'telemetry-header' }),
}));

vi.mock('./components/NodeInventory', () => ({
  NodeInventory: () => React.createElement('div', { 'data-testid': 'node-inventory' }),
}));

vi.mock('./components/HolographicGlobe', () => ({
  HolographicGlobe: () => React.createElement('div', { 'data-testid': 'holographic-globe' }),
}));

vi.mock('./components/SovereignActions', () => ({
  SovereignActions: () => React.createElement('div', { 'data-testid': 'sovereign-actions' }),
}));

vi.mock('./components/AlfredDock', () => ({
  AlfredDock: () => React.createElement('div', { 'data-testid': 'alfred-dock' }),
}));

vi.mock('./components/ExcaliburAuthCartridge', () => ({
  ExcaliburAuthCartridge: () => React.createElement('div', { 'data-testid': 'excalibur-auth-cartridge' }),
}));

vi.mock('./components/auth/OnboardingFlow', () => ({
  OnboardingFlow: () => React.createElement('div', { 'data-testid': 'onboarding-flow' }),
}));

vi.mock('./components/dashboard/DesktopGrid', () => ({
  DesktopGrid: () => React.createElement('div', { 'data-testid': 'desktop-grid' }),
}));

vi.mock('./components/TenantCarousel', () => ({
  TenantCarousel: ({ leaseId, operator }: { leaseId: string | null; operator: string }) =>
    React.createElement(
      'nav',
      { 'data-testid': 'tenant-carousel' },
      `${operator}:${leaseId}`,
    ),
}));

vi.mock('./components/CartridgeLoadingFallback', () => ({
  CartridgeLoadingFallback: () => React.createElement('div', { 'data-testid': 'cartridge-loading' }),
}));

vi.mock('./components/ErrorBoundary', () => ({
  ErrorBoundary: ({ children }: { children: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'error-boundary' }, children),
}));

vi.mock('./state/useEcosystemStore', () => ({
  useEcosystemStore: () => ({ deviceMode: 'desktop' }),
}));

class StubEventSource {
  onmessage: ((event: MessageEvent) => void) | null = null;

  close = vi.fn();
}

describe('App operator access', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => [],
      }),
    );
    vi.stubGlobal('EventSource', StubEventSource);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('mounts the operator console immediately with the default Hermes lease', async () => {
    render(React.createElement(App));

    expect(screen.queryByTestId('onboarding-flow')).not.toBeInTheDocument();
    expect(screen.queryByTestId('excalibur-auth-cartridge')).not.toBeInTheDocument();
    expect(await screen.findByTestId('tenant-carousel')).toHaveTextContent(
      'VaShawn O. Head (Vizion):EXCALIBUR_LEASE_SOVEREIGN_V1000',
    );
    expect(screen.getByTestId('holographic-globe')).toBeInTheDocument();
    expect(screen.getByTestId('sovereign-actions')).toBeInTheDocument();
  });
});
