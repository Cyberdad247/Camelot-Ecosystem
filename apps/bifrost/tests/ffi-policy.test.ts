import { describe, it, expect } from 'vitest';
import { degradeTrustBand } from '../../../handover/payload/bifrost/ffi-policy';
import { TrustBand } from '../../../handover/payload/bifrost/bifrost-envelope';

describe('degradeTrustBand', () => {
  it('should not change block or quarantine trust bands', () => {
    expect(degradeTrustBand('block', 'ffi_timeout')).toBe('block');
    expect(degradeTrustBand('quarantine', 'ffi_timeout')).toBe('quarantine');
  });

  it('should fail closed for version mismatch', () => {
    expect(degradeTrustBand('allow', 'ffi_version_mismatch')).toBe('block');
    expect(degradeTrustBand('review', 'ffi_version_mismatch')).toBe('block');
  });

  it('should not change band for invalid input', () => {
    expect(degradeTrustBand('allow', 'ffi_invalid_input')).toBe('allow');
    expect(degradeTrustBand('review', 'ffi_invalid_input')).toBe('review');
  });

  it('should handle compute failed based on high risk flag', () => {
    expect(degradeTrustBand('allow', 'ffi_compute_failed', true)).toBe('block');
    expect(degradeTrustBand('allow', 'ffi_compute_failed', false)).toBe('review');
  });

  it('should degrade to review for other errors', () => {
    expect(degradeTrustBand('allow', 'ffi_timeout')).toBe('review');
    expect(degradeTrustBand('allow', 'ffi_transport_failed')).toBe('review');
    expect(degradeTrustBand('allow', 'ffi_batch_too_large')).toBe('review');
  });
});
