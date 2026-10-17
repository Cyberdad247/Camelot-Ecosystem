// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest';
import { render, screen, cleanup } from '@testing-library/react';
import React from 'react';
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import {
  MicroSparkline,
  MicroRadialGauge,
  MicroPingBadge,
  MicroFPSMeter,
  MicroTelemetryStrip,
} from './index';

describe('Micro Telemetry Component Suite', () => {
  beforeEach(() => {
    vi.stubGlobal('requestAnimationFrame', (cb: FrameRequestCallback) => setTimeout(cb, 16));
    vi.stubGlobal('cancelAnimationFrame', (id: number) => clearTimeout(id));
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  describe('MicroSparkline', () => {
    it('renders SVG sparkline path with data points', () => {
      const data = [10, 25, 40, 30, 60, 50];
      const { container } = render(
        React.createElement(MicroSparkline, { data, color: 'cyan', height: 28, width: 80 })
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
      expect(svg).toHaveAttribute('aria-label', expect.stringContaining('50'));

      const paths = container.querySelectorAll('path');
      expect(paths.length).toBeGreaterThanOrEqual(1); // line path and area path
    });

    it('gracefully handles empty data array', () => {
      const { container } = render(React.createElement(MicroSparkline, { data: [] }));
      expect(container.firstChild).toBeInTheDocument();
    });
  });

  describe('MicroRadialGauge', () => {
    it('renders progressbar with computed percentage and center readout', () => {
      render(
        React.createElement(MicroRadialGauge, {
          value: 2048,
          ceiling: 4096,
          label: 'RAM SCARCITY',
          unit: '%',
          size: 'md',
        })
      );

      const progressbar = screen.getByRole('progressbar');
      expect(progressbar).toBeInTheDocument();
      expect(progressbar).toHaveAttribute('aria-valuenow', '2048');
      expect(progressbar).toHaveAttribute('aria-valuemax', '4096');
      expect(screen.getByText('50')).toBeInTheDocument();
      expect(screen.getByText('RAM SCARCITY')).toBeInTheDocument();
    });

    it('triggers critical color styling when exceeding threshold', () => {
      const { container } = render(
        React.createElement(MicroRadialGauge, {
          value: 3800,
          ceiling: 4096,
          criticalThreshold: 90,
        })
      );

      const circles = container.querySelectorAll('circle');
      expect(circles.length).toBe(2);
      expect(circles[1]).toHaveAttribute('stroke', '#DE4258'); // Garnet critical
    });
  });

  describe('MicroPingBadge', () => {
    it('renders node name and latency with nominal state', () => {
      render(
        React.createElement(MicroPingBadge, {
          nodeName: 'CYBERTRONIA',
          latencyMs: 14,
          status: 'nominal',
        })
      );

      expect(screen.getByText('CYBERTRONIA')).toBeInTheDocument();
      expect(screen.getByText('14ms')).toBeInTheDocument();
    });

    it('renders offline indicator when latency is negative or status is offline', () => {
      render(
        React.createElement(MicroPingBadge, {
          nodeName: 'DRONE-04',
          latencyMs: -1,
          status: 'offline',
        })
      );

      expect(screen.getByText('DRONE-04')).toBeInTheDocument();
      expect(screen.getByText('OFFLINE')).toBeInTheDocument();
    });
  });

  describe('MicroFPSMeter', () => {
    it('renders FPS readout and target rate', () => {
      render(React.createElement(MicroFPSMeter, { targetFps: 120 }));
      expect(screen.getByText('FPS:')).toBeInTheDocument();
      expect(screen.getByText('/120')).toBeInTheDocument();
    });
  });

  describe('MicroTelemetryStrip', () => {
    it('renders composite telemetry strip with gauges and sparklines', () => {
      const mockTelemetry = {
        timestamp: Date.now(),
        globalLoad: 32.5,
        activeLeases: 2,
        networkEgress: 240.2,
        ramUsageMB: 1650,
        ramCeilingMB: 4096,
        ramPercent: 40.3,
        madvReclaimedMB: 310,
        hardwareCeiling: '4GB_RAM_STRICT',
        alerts: [],
      };

      render(React.createElement(MicroTelemetryStrip, { telemetry: mockTelemetry }));

      expect(screen.getByText('RAM SCARCITY')).toBeInTheDocument();
      expect(screen.getAllByText('1650').length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('CPU')).toBeInTheDocument();
      expect(screen.getByText('32.5%')).toBeInTheDocument();
      expect(screen.getByText('EGRESS')).toBeInTheDocument();
      expect(screen.getByText('240.2')).toBeInTheDocument();
      expect(screen.getByText('S26-ULTRA')).toBeInTheDocument();
    });
  });
});
