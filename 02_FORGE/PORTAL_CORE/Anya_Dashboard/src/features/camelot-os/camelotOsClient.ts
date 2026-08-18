import type { CamelotOsState } from './types';

function operatorHeaders() {
  const token = window.sessionStorage.getItem('camelot.operatorToken') ?? '';
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'X-Camelot-Operator-Token': token } : {}),
  };
}

export async function loadCamelotOsState(): Promise<CamelotOsState> {
  const response = await fetch('/api/camelot-os/status', { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`Camelot OS status unavailable (${response.status})`);
  }
  return response.json() as Promise<CamelotOsState>;
}

export async function activateSupportSession(
  reason: string,
  durationMinutes = 120,
): Promise<CamelotOsState> {
  const response = await fetch('/api/camelot-os/support/activate', {
    method: 'POST',
    headers: operatorHeaders(),
    body: JSON.stringify({ reason, duration_minutes: durationMinutes }),
  });
  if (!response.ok) {
    throw new Error(`Support activation failed (${response.status})`);
  }
  const frontier = await response.json();
  const state = await loadCamelotOsState();
  return { ...state, frontier: { ...state.frontier, ...frontier } };
}

export async function revokeSupportSession(sessionId?: string): Promise<CamelotOsState> {
  const response = await fetch('/api/camelot-os/support/revoke', {
    method: 'POST',
    headers: operatorHeaders(),
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!response.ok) {
    throw new Error(`Support revoke failed (${response.status})`);
  }
  return loadCamelotOsState();
}
