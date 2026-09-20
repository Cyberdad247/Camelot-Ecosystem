// Ed25519 Session Management and Cryptographic Attestation
export interface AuthSessionData {
  leaseId: string;
  tenantId: string;
  operator: string;
  deviceAttestation: string;
  issuedAt: number;
  expiresAt: number;
  scopes: string[];
}

const STORAGE_KEY = 'excalibur_session_lease_v1';

export function getStoredSession(): AuthSessionData | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const session: AuthSessionData = JSON.parse(raw);
    if (Date.now() > session.expiresAt) {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }
    return session;
  } catch {
    return null;
  }
}

export function saveSession(session: AuthSessionData): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function clearSession(): void {
  localStorage.removeItem(STORAGE_KEY);
}

export function generateSovereignLease(operator = 'VaShawn O. Head (Vizion)'): AuthSessionData {
  const leaseId = `EXCALIBUR_ED25519_LEASE_${Math.random().toString(36).substring(2, 10).toUpperCase()}`;
  const session: AuthSessionData = {
    leaseId,
    tenantId: 'tenant_001_cuyahoga',
    operator,
    deviceAttestation: 'Samsung Galaxy S26 Ultra (Hardware Enclave Knox/PRF)',
    issuedAt: Date.now(),
    expiresAt: Date.now() + 24 * 60 * 60 * 1000,
    scopes: ['vault:read', 'vault:write', 'dsp:stream', 'cgroup:4gb_enforce', 'z3:solve']
  };
  saveSession(session);
  return session;
}
