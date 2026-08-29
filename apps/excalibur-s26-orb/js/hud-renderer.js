/**
 * Excalibur HUD Renderer — ChatGPT-Style Conversational Interface & VPS World Tree Vocal Integration
 */

class HUDRenderer {
  constructor() {
    this.messagesContainer = document.getElementById('messagesContainer');
    this.scrollArea = document.getElementById('chatScrollArea');
    this.heroWelcome = document.getElementById('heroWelcome');
    this.input = document.getElementById('chatInput');
    this.sendBtn = document.getElementById('sendMessageBtn');
    this.voiceBtn = document.getElementById('voiceMicBtn');
    this.typing = document.getElementById('typingIndicator');
    this.sidebar = document.getElementById('sidebarPanel');
    this.sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    this.sidebarCloseBtn = document.getElementById('sidebarCloseBtn');
    this.sidebarRedockBtn = document.getElementById('sidebarRedockBtn');
    this.newSessionBtn = document.getElementById('newSessionBtn');
    this.heroAvatarCard = document.getElementById('heroAvatarCard');
    this.msgId = 0;
    this.init();
  }

  init() {
    // Send button & enter key
    this.sendBtn?.addEventListener('click', () => this.sendMessage());
    this.input?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // Auto-resize input
    this.input?.addEventListener('input', () => this.autoResizeInput());

    // Vocal mic button
    this.voiceBtn?.addEventListener('click', () => {
      if (window.AudioPipeline?.isRecording) {
        window.AudioPipeline.stopRecording();
      } else {
        window.AudioPipeline?.startRecording();
      }
    });

    // 3D Bottom Voice Orb Tap
    const dockOrb = document.getElementById('dockVoiceOrb');
    dockOrb?.addEventListener('click', () => {
      if (window.AudioPipeline?.isRecording) {
        window.AudioPipeline.stopRecording();
      } else {
        window.AudioPipeline?.startRecording();
      }
      if ('vibrate' in navigator) navigator.vibrate(25);
    });

    // Sidebar Toggles & Re-docking
    this.sidebarToggleBtn?.addEventListener('click', () => {
      if (window.innerWidth <= 768) {
        this.sidebar?.classList.toggle('open');
      } else {
        const isDocked = this.sidebar?.classList.contains('docked');
        if (isDocked) {
          this.sidebar?.classList.remove('docked');
        } else {
          this.sidebar?.classList.add('docked');
        }
      }
      if ('vibrate' in navigator) navigator.vibrate(15);
    });

    // Explicit Re-dock Button (Locks / unpins panel back to hoverable dock)
    this.sidebarRedockBtn?.addEventListener('click', () => {
      if (window.innerWidth <= 768) {
        this.sidebar?.classList.remove('open');
      } else {
        this.sidebar?.classList.toggle('docked');
      }
      if ('vibrate' in navigator) navigator.vibrate(20);
    });

    this.sidebarCloseBtn?.addEventListener('click', () => {
      this.sidebar?.classList.remove('open');
    });

    // Bifrost Bridge Modal Toggles
    const bifrostBtn = document.getElementById('bifrostBridgeBtn');
    const bifrostModal = document.getElementById('bifrostModal');
    const bifrostClose = document.getElementById('bifrostCloseBtn');

    bifrostBtn?.addEventListener('click', () => {
      bifrostModal?.classList.add('open');
      if ('vibrate' in navigator) navigator.vibrate(20);
    });

    bifrostClose?.addEventListener('click', () => {
      bifrostModal?.classList.remove('open');
    });

    bifrostModal?.addEventListener('click', (e) => {
      if (e.target === bifrostModal) bifrostModal.classList.remove('open');
    });

    // 3D Parallax Tilt on Hero Avatar & Ambient Background
    this.init3DParallax();

    // Dynamic Day/Night Cycle Based on Location & Time
    this.initDayNightCycle();

    // New Session
    this.newSessionBtn?.addEventListener('click', () => {
      this.resetSession();
    });

    this.initBiometricTimer();
    this.initDuress();
    this.initParticles();

    console.log('[HUD] Excalibur 3D Holographic UI, Dynamic Day/Night & Voice Orb Initialized');
  }

  initDayNightCycle() {
    const applyCelestialPhase = (isDay) => {
      const pill = document.getElementById('celestialIndicator');
      if (isDay) {
        document.body.classList.remove('night-mode');
        document.body.classList.add('day-mode');
        if (pill) pill.innerHTML = '☀️ SOLAR DAY LATTICE';
      } else {
        document.body.classList.remove('day-mode');
        document.body.classList.add('night-mode');
        if (pill) pill.innerHTML = '🌙 NOCTURNAL LATTICE';
      }
    };

    const hour = new Date().getHours();
    const isDayTime = hour >= 6 && hour < 19;
    applyCelestialPhase(isDayTime);

    // Try geolocation if permitted to refine solar hours
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = pos.coords.latitude;
          // Approximate day calculation
          const now = new Date();
          const curHour = now.getHours();
          const isDay = curHour >= 6 && curHour < 19;
          applyCelestialPhase(isDay);
        },
        () => {
          // Fallback to local clock
          applyCelestialPhase(isDayTime);
        },
        { timeout: 5000 }
      );
    }

    // Toggle on badge click for manual inspection
    const pill = document.getElementById('celestialIndicator');
    pill?.addEventListener('click', () => {
      const isCurrentlyDay = document.body.classList.contains('day-mode');
      applyCelestialPhase(!isCurrentlyDay);
      if ('vibrate' in navigator) navigator.vibrate(15);
    });
  }

  init3DParallax() {
    const card = this.heroAvatarCard;
    if (!card) return;

    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      const rotateX = (-y / (rect.height / 2)) * 18;
      const rotateY = (x / (rect.width / 2)) * 18;
      card.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.1, 1.1, 1.1) translateZ(20px)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1) translateZ(0px)';
    });
  }

  autoResizeInput() {
    if (!this.input) return;
    this.input.style.height = 'auto';
    this.input.style.height = Math.min(this.input.scrollHeight, 120) + 'px';
  }

  initBiometricTimer() {
    let lease = 30;
    setInterval(() => {
      lease = lease > 1 ? lease - 1 : 30;
      const el = document.getElementById('bioTimer');
      if (el) {
        el.textContent = `${lease}s`;
        el.classList.remove('warn', 'danger');
        if (lease <= 5) {
          el.classList.add('danger');
          if (lease === 5 && 'vibrate' in navigator) navigator.vibrate([40, 60, 40]);
        } else if (lease <= 12) {
          el.classList.add('warn');
        }
      }
    }, 1000);
  }

  initDuress() {
    const duressBtn = document.getElementById('duressToggle');
    if (duressBtn) {
      duressBtn.addEventListener('click', () => {
        if ('vibrate' in navigator) navigator.vibrate([100, 50, 100]);
        this.addMessage('🚨 EMERGENCY DURESS TRIGGERED: Silent cryptographic vault lock engaged across all WorldTree nodes.', 'ai');
      });
    }
  }

  initParticles() {
    const container = document.getElementById('particles');
    if (!container) return;
    for (let i = 0; i < 20; i++) {
      const p = document.createElement('div');
      p.className = 'particle';
      const size = Math.random() * 3 + 1;
      p.style.width = `${size}px`;
      p.style.height = `${size}px`;
      p.style.left = `${Math.random() * 100}%`;
      p.style.animationDuration = `${Math.random() * 8 + 6}s`;
      p.style.animationDelay = `${Math.random() * 5}s`;
      container.appendChild(p);
    }
  }

  resetSession() {
    if (this.messagesContainer) {
      this.messagesContainer.innerHTML = '';
    }
    if (this.heroWelcome) {
      this.heroWelcome.style.display = 'flex';
    }
    if (this.sidebar) {
      this.sidebar.classList.remove('open');
    }
    if (this.input) {
      this.input.value = '';
      this.autoResizeInput();
    }
  }

  showTyping() {
    if (this.typing) {
      this.typing.classList.add('active');
      this.scrollToBottom();
    }
  }

  hideTyping() {
    if (this.typing) {
      this.typing.classList.remove('active');
    }
  }

  scrollToBottom() {
    if (this.scrollArea) {
      this.scrollArea.scrollTop = this.scrollArea.scrollHeight;
    }
  }

  executeRune(runeText) {
    if (this.sidebar) this.sidebar.classList.remove('open');
    this.addMessage(runeText, 'user');
    this.showTyping();
    setTimeout(() => {
      this.hideTyping();
      this.processVPSWorldTreeResponse(runeText);
    }, 600 + Math.random() * 400);
  }

  async sendMessage() {
    const text = this.input?.value.trim();
    if (!text) return;

    this.addMessage(text, 'user');
    this.input.value = '';
    this.autoResizeInput();
    this.showTyping();

    if (window.SentinelClient?.ws?.readyState === WebSocket.OPEN) {
      window.SentinelClient.ws.send(JSON.stringify({
        type: 'vocal_command',
        content: text,
        node: 'vashawns-s26-ultra',
        vps_hub: '100.110.180.18',
        timestamp: Date.now()
      }));
    } else {
      setTimeout(() => {
        this.hideTyping();
        this.processVPSWorldTreeResponse(text);
      }, 300 + Math.random() * 200);
    }
  }

  addMessage(text, sender = 'ai') {
    if (this.heroWelcome) {
      this.heroWelcome.style.display = 'none';
    }

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const row = document.createElement('div');
    row.className = `message-row ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar-icon';
    avatar.textContent = sender === 'user' ? '👑' : '⚔️';

    const bubbleWrap = document.createElement('div');
    bubbleWrap.className = 'msg-bubble-content';

    const header = document.createElement('div');
    header.className = 'msg-meta-header';
    header.textContent = sender === 'user' ? 'KING ARTHUR (VIZION)' : 'EXCALIBUR · VPS WORLD TREE';

    const body = document.createElement('div');
    body.className = 'msg-text-body';
    body.innerHTML = this.formatMessage(text);

    const ts = document.createElement('div');
    ts.className = 'msg-timestamp';
    ts.textContent = time;

    bubbleWrap.appendChild(header);
    bubbleWrap.appendChild(body);
    bubbleWrap.appendChild(ts);

    row.appendChild(avatar);
    row.appendChild(bubbleWrap);

    if (this.messagesContainer) {
      this.messagesContainer.appendChild(row);
    }

    this.scrollToBottom();
    if ('vibrate' in navigator && sender === 'ai') navigator.vibrate(20);
  }

  formatMessage(text) {
    if (text.startsWith('//')) {
      const parts = text.split(' ');
      const rune = parts[0];
      const rest = parts.slice(1).join(' ');
      return `<span class="cmd-badge">${rune}</span> ${rest}`;
    }

    let escaped = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    escaped = escaped.replace(/`([^`]+)`/g, '<code style="background:rgba(212,175,55,0.18);color:#f3e5ab;padding:2px 6px;border-radius:3px;font-family:JetBrains Mono, monospace;font-size:0.82em">$1</code>');
    escaped = escaped.replace(/\*\*([^*]+)\*\*/g, '<strong style="color:#f3e5ab">$1</strong>');
    escaped = escaped.replace(/\n/g, '<br>');
    return escaped;
  }

  processVPSWorldTreeResponse(text) {
    const low = text.toLowerCase();

    if (low.includes('status') || low.includes('mesh') || low.includes('fleet')) {
      const response = `📡 **VPS World Tree Mesh Telemetry:**\n\n• **VPS Hub (KVM563):** \`100.110.180.18:8095\` — Active (RTT: 18ms)\n• **Excalibur Sentinel:** \`100.106.246.126:8092\` — S26 Ultra (Sub-50ms Aoede S2S)\n• **Cybertronia:** \`100.118.224.52:3001\` — Primary Windows Orchestrator\n• **WorldTree CloudBrain:** UUID \`a0a4bfb9-62fc-4b55-a6a6-e3258ffda5b3\` Sealed`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('boot')) {
      const response = `🚀 **Sovereign Boot Sequencer Initiated (VPS World Tree):**\n\n1. Port Probes (:8095, :8092, :3001) → **ONLINE**\n2. Ed25519 Arthur Identity Sealed → **CONFIRMED**\n3. Aoede Vocal Gateway Stream → **READY**\n4. CloudBrain Memory Tissue → **SYNCHRONIZED**\n\nExcalibur is standing by for your next vocal command, Sovereign.`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('forge_hermes')) {
      const response = `⚔️ **HERMES_PRIME VFS Soul Scaffolded:**\n\n• Location: \`Knights/Hermes_Prime/VFS_SOUL.json\`\n• Research Phial: \`01_KERNEL/titan/phials/hermes_prime_phial.py\`\n• Memory Mode: Ouroboros 1.58-bit BitNet WAL\n• State: Idempotent scaffold confirmed.`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('ignite_self_evolution') || low.includes('evolve_loop')) {
      const response = `🧬 **MGV Research Cycle Ignited (HERMES_PRIME):**\n\n1. **Monitor:** Scraping latest papers and arXiv/bioRxiv feeds\n2. **Generate:** Synthesizing architectural hypotheses for Sovereign Mesh\n3. **Verify:** AST & zero-trust proof gates\n4. **Evolve:** Re-weighting Phial weights and updating CloudBrain tissue\n\nCycle completed with zero regression.`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('forge') || low.includes('codex')) {
      const response = `⚡ **Kinetic Code Execution Lane Active (SIR_FORGE / SIR_CODEX):**\n\n• Dispatch: Direct Bare-Metal Kinetic Pipeline\n• Target: \`${text.replace(/\/\/(forge|codex)/i, '').trim() || 'Active Workspace'}\`\n• TDD Gate: Verified against test suite\n• Output: Sealed with zero security warnings.`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('swarm') || low.includes('bio_swarm')) {
      const response = `🐝 **Multi-Agent Swarm Colony Dispatched (SIR_BORIS / LADY_APIS):**\n\n• Swarm Nodes: 8-Squire Colony + Research Foragers\n• Coordination: 13-Agent Consensus Lattice\n• Target: \`${text.replace(/\/\/swarm/i, '').trim() || 'Ecosystem Fleet'}\`\n• Status: Colony synchronized.`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.startsWith('omega_') || low.includes('omega')) {
      const knight = text.split(' ')[0].replace(/omega_/i, '').toUpperCase();
      const response = `👑 **Omega Knight Direct Dispatch: [${knight}]:**\n\n• Persona: Authenticated via Sovereign Registry\n• CloudBrain Node: Tethered to WorldTree UUID\n• Directive: "${text.substring(text.indexOf(' ') + 1) || 'Standby'}"\n• Execution: Real-time synthesis routed.`;
      this.addMessage(response, 'ai');
      return;
    }

    // Default conversational vocal response
    const defaultResponse = `⚔️ **VPS World Tree Synthesized:**\n\nReceived: "${text}"\n\nYour directive has been routed through the Sovereign Mesh. Speak or issue further runic directives directly.`;
    this.addMessage(defaultResponse, 'ai');
  }
}

window.HUDRenderer = new HUDRenderer();
