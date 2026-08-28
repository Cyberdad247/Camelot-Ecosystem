/**
 * HUD Renderer — Message display, input handling, 3D effects
 */

class HUDRenderer {
  constructor() {
    this.chat = document.getElementById('kotrChat');
    this.input = document.getElementById('kotrInput');
    this.sendBtn = document.getElementById('sendBtnKotr');
    this.voiceBtn = document.getElementById('voiceBtnKotr');
    this.typing = document.getElementById('typingKotr');
    this.emptyState = document.getElementById('emptyState');
    this.msgId = 0;
    this.init();
  }

  init() {
    this.sendBtn?.addEventListener('click', () => this.sendMessage());
    this.input?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
    this.voiceBtn?.addEventListener('click', () => {
      if (window.AudioPipeline?.isRecording) {
        window.AudioPipeline.stopRecording();
      } else {
        window.AudioPipeline?.startRecording();
      }
    });
    this.initParallax();
    this.initParticles();
    setTimeout(() => {
      this.addMessage(
        'The Gemini Trinity is forged into the Lattice. I am your interface to the order. Speak, and I shall execute.',
        'ai'
      );
    }, 800);
    console.log('[HUD] Renderer initialized');
  }

  initParallax() {
    const container = document.getElementById('sovereignContainer');
    if (!container) return;
    container.addEventListener('mousemove', (e) => {
      const rect = container.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      container.style.transform = `perspective(1200px) rotateY(${x * 2}deg) rotateX(${-y * 2}deg)`;
    });
    container.addEventListener('mouseleave', () => {
      container.style.transform = 'perspective(1200px) rotateY(0deg) rotateX(0deg)';
    });
  }

  initParticles() {
    const container = document.getElementById('particles');
    if (!container) return;
    for (let i = 0; i < 20; i++) {
      const p = document.createElement('div');
      p.className = 'particle';
      p.style.left = Math.random() * 100 + '%';
      p.style.animationDuration = (8 + Math.random() * 12) + 's';
      p.style.animationDelay = Math.random() * 10 + 's';
      const size = 1 + Math.random() * 2;
      p.style.width = size + 'px';
      p.style.height = size + 'px';
      container.appendChild(p);
    }
  }

  addMessage(text, sender) {
    if (this.emptyState) this.emptyState.style.display = 'none';
    const div = document.createElement('div');
    div.className = `message-kotr ${sender}`;
    div.id = `msg-${++this.msgId}`;
    let body = text;
    if (sender === 'ai' && text.startsWith('/')) {
      const cmd = text.split(' ')[0];
      body = `<div class="cmd-highlight">${cmd}</div>${text.substring(cmd.length).trim()}`;
    }
    const metaIcon = sender === 'user' ? '◆' : '⚔';
    const metaName = sender === 'user' ? 'You' : 'The Round';
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    div.innerHTML = `
      <div class="msg-meta"><span style="font-size:10px">${metaIcon}</span> ${metaName}</div>
      ${body}
      <div class="msg-time">${time}</div>
    `;
    this.chat?.appendChild(div);
    this.chat?.scrollTo({ top: this.chat.scrollHeight, behavior: 'smooth' });
    return div;
  }

  showTyping() {
    this.typing?.classList.add('active');
    this.chat?.scrollTo({ top: this.chat.scrollHeight, behavior: 'smooth' });
  }

  hideTyping() {
    this.typing?.classList.remove('active');
  }

  async sendMessage() {
    const text = this.input?.value.trim();
    if (!text) return;
    this.addMessage(text, 'user');
    this.input.value = '';
    this.showTyping();
    if (window.SentinelClient?.ws?.readyState === WebSocket.OPEN) {
      window.SentinelClient.ws.send(JSON.stringify({
        type: 'text',
        content: text,
        mode: window.TrinityController?.activeMode || 'live',
        timestamp: Date.now()
      }));
    } else {
      setTimeout(() => {
        this.hideTyping();
        this.addMessage(this.processCommand(text), 'ai');
      }, 900 + Math.random() * 700);
    }
  }

  processCommand(text) {
    const low = text.toLowerCase();
    const mode = window.TrinityController?.activeMode || 'live';
    const prefix = mode === 'live' ? '[LIVE] ' : mode === 'spark' ? '[SPARK] ' : '[ASSISTANT] ';
    if (low.includes('search') || low.includes('archives')) {
      const q = text.replace(/search|find|the archives for|look up/gi, '').trim();
      return `/search ${prefix}The archives have been scoured.\n\n"${q}" yields:\n• htmx.org/docs — Official Documentation\n• htmx.org/examples — Pattern Library\n• github.com/bigskysoftware/htmx — Source Code`;
    }
    if (low.includes('weather')) {
      return `/weather ${prefix}Atmospheric readings from the dome:\n\n🌤️ Partly Cloudy\n72°F / 22°C\nHumidity: 45%\nWind: 8 mph from the North`;
    }
    if (low.includes('remind')) {
      return `/reminder ${prefix}A scroll has been inscribed. Your reminder is bound to the chronometer.`;
    }
    if (low.includes('time')) {
      return `/time ${prefix}The chronometer reads: ${new Date().toLocaleTimeString()}.`;
    }
    if (low.includes('help') || low.includes('aid')) {
      return `/help ${prefix}The Round recognizes these commands:\n\n• "Search the archives for [query]"\n• "Summon the weather"\n• "Set a reminder for [time]"\n• "What hour is it?"\n• "Call for aid" — display this scroll`;
    }
    if (low.includes('hello') || low.includes('hail')) {
      return `${prefix}Hail, Sovereign. The Round stands ready. Speak your will, and the order shall act upon it.`;
    }
    return `${prefix}The Round has heard: "${text}"\n\nSpeak "call for aid" to see the recognized commands, or issue your will directly.`;
  }
}

window.HUDRenderer = new HUDRenderer();
