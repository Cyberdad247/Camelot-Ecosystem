import { describe, it, expect } from 'vitest';
import { evaluateSidecar, SidecarStatus } from './ffi-policy';

describe('ffi-policy', () => {
  describe('evaluateSidecar', () => {
    it('should proceed and advertise when health is ok and routeReady is true', () => {
      const status: SidecarStatus = { health: 'ok', routeReady: true };
      const advisory = evaluateSidecar(status);
      expect(advisory).toEqual({
        scoring: 'proceed',
        advertise: true,
        blockNewGrants: false
      });
    });

    it('should proceed and blockNewGrants when health is ok and routeReady is false', () => {
      const status: SidecarStatus = { health: 'ok', routeReady: false };
      const advisory = evaluateSidecar(status);
      expect(advisory).toEqual({
        scoring: 'proceed',
        advertise: false,
        blockNewGrants: true
      });
    });

    it('should review_only and advertise when health is degraded and routeReady is true', () => {
      const status: SidecarStatus = { health: 'degraded', routeReady: true };
      const advisory = evaluateSidecar(status);
      expect(advisory).toEqual({
        scoring: 'review_only',
        advertise: true,
        blockNewGrants: false
      });
    });

    it('should review_only and blockNewGrants when health is degraded and routeReady is false', () => {
      const status: SidecarStatus = { health: 'degraded', routeReady: false };
      const advisory = evaluateSidecar(status);
      expect(advisory).toEqual({
        scoring: 'review_only',
        advertise: false,
        blockNewGrants: true
      });
    });

    it('should no_grant and blockNewGrants when health is failed and routeReady is true', () => {
      const status: SidecarStatus = { health: 'failed', routeReady: true };
      const advisory = evaluateSidecar(status);
      expect(advisory).toEqual({
        scoring: 'no_grant',
        advertise: false,
        blockNewGrants: true
      });
    });

    it('should no_grant and blockNewGrants when health is failed and routeReady is false', () => {
      const status: SidecarStatus = { health: 'failed', routeReady: false };
      const advisory = evaluateSidecar(status);
      expect(advisory).toEqual({
        scoring: 'no_grant',
        advertise: false,
        blockNewGrants: true
      });
    });
  });
});
