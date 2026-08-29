/**
 * Camelot Sentinel Client — Zero-Trust Auth & Health Monitoring
 * Handles: Lease acquisition, Vault token refresh, mTLS WebSocket, circuit breaker
 */

class SentinelClient {
  constructor(config = {}) {
    this.vpsTailscaleIP = config.vpsIP || '100.110.180.18';
    this.vaultAddr = config.vaultAddr || 'http://127.0.0.1:8200';
    this.leaseTTL = config.leaseTTL || 30 * 60 * 1000;
    this.lease = null;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 5000;
    this.circuitOpen = false;
    this.circuitResetTimeout = 30000;
    this.latencyHistory = [];
    this.healthCheckInterval = null;
    this.statusCallbacks = new Map();
  }

  async init() {
    console.log('[SENTINEL] Initializing zero-trust client...');
    const tsHealth = await this.checkTailscale();
    this.emitStatus('network', tsHealth ? 'connected' : 'disconnected');
    if (!tsHealth) {
      console.error('[SENTINEL] Tailscale mesh not available');
      return false;
    }
    const leaseOk = await this.acquireLease();
    if (!leaseOk) {
      console.error('[SENTINEL] Lease acquisition failed');
      return false;
    }
    this.startHealthChecks();
    await this.connectWebSocket();
    return true;
  }

  async checkTailscale() {
    try {
      const response = await fetch('http://localhost:8088/healthz', {
        method: 'GET',
        signal: AbortSignal.timeout(3000)
      }).catch(() => null);
      return response !== null;
    } catch { return false; }
  }

  async acquireLease() {
    try {
      const deviceFP = await this.getDeviceFingerprint();
      const response = await fetch(`${this.vaultAddr}/v1/auth/tailscale/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_fp: deviceFP }),
        signal: AbortSignal.timeout(10000)
      });
      if (!response.ok) throw new Error(`Vault auth: ${response.status}`);
      const data = await response.json();
      this.lease = {
        id: data.auth.lease_id,
        token: data.auth.client_token,
        expiresAt: Date.now() + (data.auth.lease_duration * 1000),
        deviceFP: deviceFP
      };
      console.log(`[SENTINEL] Lease acquired: ${this.lease.id}`);
      this.emitStatus('auth', 'authenticated');
      setTimeout(() => this.refreshLease(), this.leaseTTL - 60000);
      return true;
    } catch (err) {
      console.error('[SENTINEL] Lease error:', err);
      this.emitStatus('auth', 'failed');
      return false;
    }
  }

  async refreshLease() {
    if (!this.lease) return false;
    console.log('[SENTINEL] Refreshing lease...');
    return this.acquireLease();
  }

  async connectWebSocket() {
    if (this.circuitOpen) {
      console.warn('[SENTINEL] Circuit breaker open');
      setTimeout(() => this.connectWebSocket(), this.circuitResetTimeout);
      return;
    }
    try {
      const wsUrl = `wss://${this.vpsTailscaleIP}:8443/v1/audio/stream`;
      this.ws = new WebSocket(wsUrl);
      this.ws.binaryType = 'arraybuffer';
      this.ws.onopen = () => {
        console.log('[SENTINEL] WebSocket connected');
        this.reconnectAttempts = 0;
        this.emitStatus('live', 'connected');
        this.ws.send(JSON.stringify({
          type: 'setup',
          lease_id: this.lease.id,
          device_fp: this.lease.deviceFP,
          trinity_mode: window.TrinityController?.activeMode || 'live'
        }));
      };
      this.ws.onmessage = (event) => this.handleMessage(event.data);
      this.ws.onerror = (err) => {
        console.error('[SENTINEL] WS error:', err);
        this.emitStatus('live', 'error');
      };
      this.ws.onclose = () => {
        console.warn('[SENTINEL] WebSocket closed');
        this.emitStatus('live', 'disconnected');
        this.scheduleReconnect();
      };
    } catch (err) {
      console.error('[SENTINEL] Connection failed:', err);
      this.scheduleReconnect();
    }
  }

  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[SENTINEL] Max reconnect reached — circuit open');
      this.circuitOpen = true;
      this.emitStatus('live', 'circuit_open');
      setTimeout(() => {
        this.circuitOpen = false;
        this.reconnectAttempts = 0;
        console.log('[SENTINEL] Circuit breaker reset');
      }, this.circuitResetTimeout);
      return;
    }
    const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts);
    this.reconnectAttempts++;
    console.log(`[SENTINEL] Reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
    setTimeout(() => this.connectWebSocket(), delay);
  }

  handleMessage(data) {
    const startTime = performance.now();
    try {
      const msg = JSON.parse(data);
      switch (msg.type) {
        case 'audio':
          window.AudioPipeline?.playAudio(msg.opus_payload);
          break;
        case 'transcript':
          window.HUDRenderer?.addMessage(msg.text, 'ai');
          break;
        case 'pong':
          this.recordLatency(startTime);
          break;
        case 'error':
          console.error('[SENTINEL] Server error:', msg.error);
          break;
        default:
          console.log('[SENTINEL] Unknown message type:', msg.type);
      }
    } catch (err) {
      window.AudioPipeline?.playAudio(data);
    }
  }

  recordLatency(startTime) {
    const rtt = performance.now() - startTime;
    this.latencyHistory.push(rtt);
    if (this.latencyHistory.length > 100) this.latencyHistory.shift();
    const avg = this.latencyHistory.reduce((a, b) => a + b, 0) / this.latencyHistory.length;
    const el = document.getElementById('latencyValue');
    if (el) el.textContent = `${Math.round(avg)}ms`;
  }

  startHealthChecks() {
    this.healthCheckInterval = setInterval(async () => {
      const health = await this.checkBackendHealth();
      this.emitStatus('health', health ? 'healthy' : 'degraded');
    }, 30000);
  }

  async checkBackendHealth() {
    try {
      const response = await fetch(`https://${this.vpsTailscaleIP}:8443/healthz`, {
        signal: AbortSignal.timeout(5000)
      });
      return response.ok;
    } catch { return false; }
  }

  async getDeviceFingerprint() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.fillText('Camelot', 0, 0);
    return btoa(canvas.toDataURL()).slice(0, 32);
  }

  sendAudioFrame(opusData) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'audio',
        ts: Date.now(),
        opus: btoa(String.fromCharCode(...new Uint8Array(opusData))),
        speech: true
      }));
    }
  }

  onStatusChange(service, callback) {
    if (!this.statusCallbacks.has(service)) {
      this.statusCallbacks.set(service, []);
    }
    this.statusCallbacks.get(service).push(callback);
  }

  emitStatus(service, status) {
    const callbacks = this.statusCallbacks.get(service) || [];
    callbacks.forEach(cb => cb(status));
    const chip = document.querySelector(`[data-service="${service}"]`);
    if (chip) {
      const dot = chip.querySelector('.status-dot');
      const label = chip.querySelector('span');
      dot.className = 'status-dot';
      if (status === 'connected' || status === 'authenticated' || status === 'healthy') {
        dot.classList.add(service === 'live' ? 'live' : service === 'spark' ? 'spark' : 'assist');
        label.textContent = service === 'live' ? 'GEMINI LIVE' : service === 'spark' ? 'SPARK ACTIVE' : 'VAULT LINKED';
      } else if (status === 'error' || status === 'failed' || status === 'circuit_open') {
        dot.classList.add('error');
        label.textContent = service === 'live' ? 'LIVE ERROR' : 'AUTH FAILED';
      }
    }
  }

  destroy() {
    if (this.healthCheckInterval) clearInterval(this.healthCheckInterval);
    if (this.ws) this.ws.close();
    console.log('[SENTINEL] Client destroyed');
  }
}

window.SentinelClient = new SentinelClient();
