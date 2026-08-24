// SPDX-License-Identifier: MIT

// 🔐 AUTH MANAGER (Sovereign Identity)
// Manages: Login, 2FA, Session State, and GitHub Identity

class AuthManager {
  constructor() {
    this.isAuthenticated = false;
    this.currentUser = null;
    this.githubToken = null;
    this.sessionStart = null;
  }

  async init() {
    const data = await chrome.storage.local.get(['auth_session']);
    if (data.auth_session && !this.isSessionExpired(data.auth_session)) {
      this.currentUser = data.auth_session.user;
      this.githubToken = data.auth_session.githubToken;
      this.isAuthenticated = true;
      this.sessionStart = data.auth_session.start;
      console.log(`[AUTH] Session Restored: ${this.currentUser}`);
    }
  }

  async login(email, password, code2fa, githubToken) {
    // SIMULATION: Real auth would hit a backend
    // We validate against the specific Sovereign Identity requested

    if (email === 'cyberdad247@gmail.com') {
      // Verify 2FA (Mock check for now, can perform logic if needed)
      if (code2fa && code2fa.length === 6) {
        this.isAuthenticated = true;
        this.currentUser = email;
        this.githubToken = githubToken;
        this.sessionStart = Date.now();

        await this.saveSession();
        console.log('[AUTH] Sovereign Identity Verified.');
        return { status: 'SUCCESS' };
      } else {
        return { status: 'FAILED', reason: 'Invalid 2FA Code' };
      }
    }
    return { status: 'FAILED', reason: 'Unauthorized User' };
  }

  async logout() {
    this.isAuthenticated = false;
    this.currentUser = null;
    this.githubToken = null;
    await chrome.storage.local.remove('auth_session');
    console.log('[AUTH] Session Terminated.');
  }

  async saveSession() {
    // Store minimal session data
    await chrome.storage.local.set({
      auth_session: {
        user: this.currentUser,
        githubToken: this.githubToken, // Encrypt in prod
        start: this.sessionStart,
      },
    });
  }

  isSessionExpired(session) {
    // 24 Hour Session
    const ONE_DAY = 24 * 60 * 60 * 1000;
    return Date.now() - session.start > ONE_DAY;
  }

  // Gated Access Check
  requireAuth() {
    if (!this.isAuthenticated) {
      throw new Error('ACCESS_DENIED: Sovereign Authentication Required');
    }
  }
}

const authManager = new AuthManager();
self.AuthManager = authManager;
