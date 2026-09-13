/**
 * Trinity Controller — Mode switching between Gemini Live/Spark/Assistant
 */

class TrinityController {
  constructor() {
    this.activeMode = 'live';
    this.modes = {
      live: {
        name: 'LIVE',
        description: 'Full-duplex voice — Aoede',
        endpoint: '/v1/audio/stream',
        capabilities: ['voice', 'audio_reply']
      },
      spark: {
        name: 'SPARK',
        description: '24/7 background automation',
        endpoint: '/v1/spark/execute',
        capabilities: ['async', 'workspace', 'workflow']
      },
      assistant: {
        name: 'ASSISTANT',
        description: 'Cognitive text routing',
        endpoint: '/v1/assistant/chat',
        capabilities: ['text', 'image', 'function_call']
      }
    };
    this.init();
  }

  init() {
    const selector = document.getElementById('trinitySelector');
    if (!selector) return;
    selector.querySelectorAll('.trinity-mode').forEach(btn => {
      btn.addEventListener('click', () => this.switchMode(btn.dataset.mode));
    });
    console.log('[TRINITY] Controller initialized — mode: live');
  }

  switchMode(mode) {
    if (!this.modes[mode]) {
      console.error(`[TRINITY] Unknown mode: ${mode}`);
      return;
    }
    if ('vibrate' in navigator) navigator.vibrate(20);
    const prevMode = this.activeMode;
    this.activeMode = mode;
    document.querySelectorAll('.trinity-mode').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.mode === mode);
    });
    const input = document.getElementById('kotrInput');
    if (input) {
      const placeholders = {
        live: 'Speak your command, Sovereign...',
        spark: 'Dispatch workflow, Sovereign...',
        assistant: 'Query the archives, Sovereign...'
      };
      input.placeholder = placeholders[mode];
    }
    if (window.SentinelClient?.ws?.readyState === WebSocket.OPEN) {
      window.SentinelClient.ws.send(JSON.stringify({
        type: 'mode_switch',
        mode: mode,
        timestamp: Date.now()
      }));
    }
    console.log(`[TRINITY] Switched: ${prevMode} -> ${mode}`);
    this.showModeNotification(mode);
  }

  showModeNotification(mode) {
    const config = this.modes[mode];
    const banner = document.createElement('div');
    banner.className = 'message-kotr ai';
    banner.style.animation = 'msg3DEnter 0.4s ease-out';
    banner.innerHTML = `
      <div class="cmd-highlight">/mode ${mode.toUpperCase()}</div>
      <div style="font-size:13px">${config.description}</div>
      <div style="font-size:10px;color:var(--text-secondary);margin-top:4px">
        Capabilities: ${config.capabilities.join(' · ')}
      </div>
    `;
    const chat = document.getElementById('kotrChat');
    if (chat) {
      chat.appendChild(banner);
      chat.scrollTop = chat.scrollHeight;
    }
  }

  switchTab(tabId) {
    if (window.HUDRenderer?.switchTab) {
      window.HUDRenderer.switchTab(tabId);
    }
  }

  getActiveConfig() {
    return this.modes[this.activeMode];
  }
}

window.TrinityController = new TrinityController();
