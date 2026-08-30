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

  // Knight Registry & API Routing Architecture
  getKnightRouterTable() {
    return {
      'SIR_BORIS': {
        role: 'Crucible Conductor & Master Architect',
        harness: 'claude-code / antigravity',
        model: 'Gemini 1.5 Pro / Claude 3.5 Sonnet',
        tts_engine: 'kokoro_onnx (calm architect)',
        stt_engine: 'Aoede S2S / Whisper-v3',
        api_endpoint: 'https://100.110.180.18:8095/v1/crucible/evaluate',
        cloudbrain_uuid: 'f7707daa-2d10-4db8-8fda-be4661a27793',
        runes: ['//BOOT', '//STATUS', '//FLEET', '//DAWNING', 'Omega_Boris']
      },
      'SIR_ALEX': {
        role: 'Task Planner & DAG Orchestrator',
        harness: 'kimi-code / antigravity',
        model: 'Gemini 1.5 Pro',
        tts_engine: 'kokoro_onnx (sharp strategist)',
        stt_engine: 'Aoede S2S',
        api_endpoint: 'https://100.110.180.18:8095/v1/dag/plan',
        cloudbrain_uuid: 'f490c05e-d8c4-4008-87e1-5f901bf57c6a',
        runes: ['//PLAN', '//THINK', '//OMX_PLAN', 'Omega_Alex']
      },
      'SIR_FORGE': {
        role: 'Kinetic Code Execution & Build Pipeline',
        harness: 'codex / swe-agent',
        model: 'Gemini 1.5 Flash / Claude 3.5 Sonnet',
        tts_engine: 'kokoro_onnx (kinetic executor)',
        stt_engine: 'Aoede S2S',
        api_endpoint: 'https://100.110.180.18:8095/v1/forge/compile',
        cloudbrain_uuid: '91c5da8b-e2de-4a56-b7fd-c8b76c00afc7',
        runes: ['//FORGE', '//CONTRACT', '//GENESIS', 'Omega_Forge']
      },
      'SIR_CODEX': {
        role: 'High-Velocity Implementation & AST Builder',
        harness: 'codex / deepseek-tui',
        model: 'GPT-5.5 Codex / OpenAI AST Provider',
        tts_engine: 'kokoro_onnx (rapid builder)',
        stt_engine: 'Aoede S2S',
        api_endpoint: 'https://100.110.180.18:8095/v1/codex/dispatch',
        cloudbrain_uuid: '8c656cfa-a189-409e-a72d-07692a47f17e',
        runes: ['//CODEX', '//REZERO_CODE', 'Omega_Codex']
      },
      'SIR_SENTINEL': {
        role: 'AgentArmor, mTLS Zero-Trust & Iron Gate',
        harness: 'minimal / local-rules',
        model: 'Gemini 1.5 Flash / Local Rules',
        tts_engine: 'kokoro_onnx (security sentinel)',
        stt_engine: 'Aoede S2S',
        api_endpoint: 'https://100.110.180.18:8443/v1/sentinel/gate',
        cloudbrain_uuid: '07cbb441-f008-424c-820a-85676210be39',
        runes: ['//BIFROST_LOCK', '//DEFENSE_INIT', 'Omega_Sentinel']
      },
      'SIR_DEBUG': {
        role: 'PIV Self-Healing & Anomaly Repair',
        harness: 'deepseek-tui / codewhale',
        model: 'Gemini 1.5 Pro',
        tts_engine: 'kokoro_onnx (diagnostic repair)',
        stt_engine: 'Aoede S2S',
        api_endpoint: 'https://100.110.180.18:8095/v1/debug/heal',
        cloudbrain_uuid: 'fdc42a4a-3060-4eac-b57c-8e6009ed634a',
        runes: ['//HEAL', '//REZERO', '//TRIAGE', 'Omega_Debug']
      },
      'SIR_GHOST': {
        role: 'Air-Gapped Privacy & Secrets Scanner',
        harness: 'minimal / offline-gguf',
        model: 'Ollama Local (qwen2.5-coder / mistral)',
        tts_engine: 'offline_wav',
        stt_engine: 'offline_whisper',
        api_endpoint: 'http://127.0.0.1:11434/api/generate',
        cloudbrain_uuid: '422a184b-93e7-4dfd-8a12-75d2268b6c60',
        runes: ['//SCAN', '//PURGE_MEMORY', 'Omega_Ghost']
      },
      'LADY_APIS': {
        role: 'BASHR Context Forager & Literature Search',
        harness: 'antigravity / research-forager',
        model: 'Gemini 1.5 Pro',
        tts_engine: 'kokoro_onnx (evidence researcher)',
        stt_engine: 'Aoede S2S',
        api_endpoint: 'https://100.110.180.18:8095/v1/forage/search',
        cloudbrain_uuid: '378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f',
        runes: ['//SWARM', '//BIO_SWARM', '//SCAVENGE', 'Omega_Apis']
      },
      'MERLIN_OMEGA': {
        role: 'System 2 Deep Reasoning & Tree-of-Thought',
        harness: 'claude-code / antigravity',
        model: 'Gemini 1.5 Pro (Thinking Mode)',
        tts_engine: 'kokoro_onnx (oracle explainer)',
        stt_engine: 'Aoede S2S',
        api_endpoint: 'https://100.110.180.18:8095/v1/reasoning/crucible',
        cloudbrain_uuid: 'af927fde-d7eb-42ee-8c79-51b3e78ef39b',
        runes: ['//THINK', '//OMX_AUTOPILOT', 'Omega_Merlin']
      },
      'SIR_HELIO': {
        role: 'Voice OS & Sub-50ms Aoede S2S Pipeline',
        harness: 'multivoice / real-time-s2s',
        model: 'Gemini Live Multimodal Audio',
        tts_engine: 'gemini_live / kokoro_onnx',
        stt_engine: 'Aoede S2S (<50ms)',
        api_endpoint: 'wss://100.110.180.18:8095/v1/audio/stream',
        cloudbrain_uuid: '56820318-bb91-451f-aac4-4b46424898cf',
        runes: ['//vocal', '//EMULATE', 'Omega_Helio']
      },
      'HERMES_PRIME': {
        role: 'High-Velocity R&D, VFS Synthesis & MGV Loop',
        harness: 'hermes (nous research)',
        model: 'Gemini 1.5 Pro / Nous Research',
        tts_engine: 'kokoro_onnx / edge-tts',
        stt_engine: 'Aoede S2S',
        api_endpoint: 'https://100.110.180.18:8095/v1/hermes/synthesize',
        cloudbrain_uuid: '28f89cb6-5048-4b5d-9e94-376082d24744',
        runes: ['//SYNC_VFS_WORKSPACE', '//FORGE_HERMES_PRIME_FILES', '//IGNITE_SELF_EVOLUTION_LOOP', 'Omega_HermesPrime']
      },
      'ANYA_OMEGA': {
        role: 'Arch-Sovereign Compiler & Quality Gate',
        harness: 'claude-code / symbollect',
        model: 'Symbollect Quantum Compiler',
        tts_engine: 'gemini_live (warm operator)',
        stt_engine: 'Aoede S2S',
        api_endpoint: 'https://100.110.180.18:8095/v1/anya/compile',
        cloudbrain_uuid: '32d38906-5ae8-4ecc-b77e-705d12c89f4a',
        runes: ['//NANO_SWARM_EXPAND', 'Omega_Anya']
      },
      'SIR_HUGGINGFACE': {
        role: 'HuggingFace Hub & Spaces Conductor (Valkyrie HF)',
        harness: 'qwen-code / transformers-cli',
        model: 'Transformers / HuggingFace Hub API',
        tts_engine: 'kokoro_onnx',
        stt_engine: 'Aoede S2S',
        api_endpoint: 'https://100.110.180.18:8095/v1/huggingface/inspect',
        cloudbrain_uuid: 'a0a4bfb9-e847-4c38-be39-7aee398f0795',
        runes: ['//HUGGINGFACE', 'Omega_HuggingFace']
      },
      'LADY_MNEMOSYNE': {
        role: 'Arch-Archivist & Memory Oracle (Lady M)',
        harness: 'antigravity / cloudbrain-governor',
        model: 'Gemini 1.5 Pro / CloudBrain Core',
        tts_engine: 'notebooklm_audio / kokoro_onnx',
        stt_engine: 'Aoede S2S',
        api_endpoint: 'https://100.110.180.18:8095/v1/mnemosyne/sync',
        cloudbrain_uuid: 'a0a4bfb9-e847-4c38-be39-7aee398f0795',
        runes: ['Omega_SYNC', 'Omega_ARCHETYPE']
      },
      'SIR_SONUS': {
        role: 'Phonetic Acoustic & Multivoice Conductor',
        harness: 'multivoice / suno-audio',
        model: 'Gemini Multimodal / Edge-TTS',
        tts_engine: 'suno / edge-tts (sonic narrator)',
        stt_engine: 'Aoede S2S',
        api_endpoint: 'https://100.110.180.18:8095/v1/audio/synthesize',
        cloudbrain_uuid: '6272aa35-c285-4edc-81bc-2824ab519edf',
        runes: ['Omega_VOICE', '//VOICE_ROUTER']
      }
    };
  }

  processVPSWorldTreeResponse(text) {
    const low = text.toLowerCase();
    const routerTable = this.getKnightRouterTable();

    // Direct Omega Knight Dispatch
    if (low.startsWith('omega_') || low.includes('omega')) {
      const matchKey = Object.keys(routerTable).find(k => low.includes(k.toLowerCase().replace('sir_', '').replace('lady_', '')) || low.includes(k.toLowerCase()));
      const knight = routerTable[matchKey] || {
        role: 'Sovereign Knight Specialist',
        harness: 'antigravity / general',
        model: 'Gemini 1.5 Pro',
        tts_engine: 'kokoro_onnx',
        stt_engine: 'Aoede S2S',
        api_endpoint: 'https://100.110.180.18:8095/v1/knight/dispatch',
        cloudbrain_uuid: 'a0a4bfb9-e847-4c38-be39-7aee398f0795'
      };
      const knightName = matchKey || text.split(' ')[0].replace(/omega_/i, '').toUpperCase();
      const response = `👑 **Omega Knight Router Dispatched: [${knightName}]**\n\n• **Knight Role:** ${knight.role}\n• **Emulated Harness:** \`${knight.harness}\`\n• **LLM Engine:** \`${knight.model}\`\n• **TTS Engine:** \`${knight.tts_engine}\`\n• **STT Engine:** \`${knight.stt_engine}\`\n• **API Gateway:** \`${knight.api_endpoint}\`\n• **CloudBrain Node:** UUID \`${knight.cloudbrain_uuid}\`\n• **Directive:** "${text.substring(text.indexOf(' ') + 1) || 'Standby Execution'}"\n\nExecution telemetry confirmed across the Bifrost Bridge.`;
      this.addMessage(response, 'ai');
      window.AudioPipeline?.speakText(`Omega Knight ${knightName} dispatched via ${knight.harness} harness.`);
      return;
    }

    if (low.includes('status') || low.includes('mesh') || low.includes('fleet')) {
      const k = routerTable['SIR_BORIS'];
      const response = `📡 **VPS World Tree Mesh Telemetry (Routed via ${k.role}):**\n\n• **VPS Hub (KVM563):** \`100.110.180.18:8095\` — Active (RTT: 18ms)\n• **Excalibur Sentinel:** \`100.106.246.126:8092\` — S26 Ultra (Sub-50ms Aoede S2S)\n• **Cybertronia:** \`100.118.224.52:3001\` — Primary Windows Orchestrator\n• **API Router:** \`${k.api_endpoint}\`\n• **WorldTree CloudBrain:** UUID \`${k.cloudbrain_uuid}\` Sealed`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('boot')) {
      const k = routerTable['SIR_BORIS'];
      const response = `🚀 **Sovereign Boot Sequencer Initiated (Routed via ${k.role}):**\n\n1. Port Probes (:8095, :8092, :3001) → **ONLINE**\n2. Ed25519 Arthur Identity Sealed → **CONFIRMED**\n3. Aoede Vocal Gateway Stream → **READY**\n4. CloudBrain Memory Tissue → UUID \`${k.cloudbrain_uuid}\`\n\nExcalibur is standing by for your next vocal command, Sovereign.`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('forge_hermes')) {
      const k = routerTable['HERMES_PRIME'];
      const response = `⚔️ **HERMES_PRIME VFS Soul Scaffolded:**\n\n• Location: \`Knights/Hermes_Prime/VFS_SOUL.json\`\n• API Route: \`${k.api_endpoint}\`\n• Model Provider: \`${k.model}\`\n• CloudBrain UUID: \`${k.cloudbrain_uuid}\`\n• Memory Mode: Ouroboros 1.58-bit BitNet WAL`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('ignite_self_evolution') || low.includes('evolve_loop')) {
      const k = routerTable['HERMES_PRIME'];
      const response = `🧬 **MGV Research Cycle Ignited (${k.role}):**\n\n1. **Monitor:** Scraping latest papers and arXiv/bioRxiv feeds\n2. **Generate:** Synthesizing architectural hypotheses for Sovereign Mesh\n3. **Verify:** AST & zero-trust proof gates (\`${k.api_endpoint}\`)\n4. **Evolve:** Re-weighting Phial weights and updating CloudBrain tissue (\`${k.cloudbrain_uuid}\`)\n\nCycle completed with zero regression.`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('sync_vfs') || low.includes('vfs') || low.includes('cloudbrain')) {
      const k = routerTable['HERMES_PRIME'];
      const response = `🌳 **VPS World Tree VFS Synchronized:**\n\n• Local digital factory: \`Knights/Hermes_Prime/\`\n• API Bridge: \`${k.api_endpoint}\`\n• NotebookLM CloudBrain tissue: UUID \`${k.cloudbrain_uuid}\`\n• Memory WAL status: 0 uncommitted frames\n• Vocal routing: Live stream unobstructed.`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('plan')) {
      const k = routerTable['SIR_ALEX'];
      const response = `🧠 **AST Plan Mode Dispatched to [SIR_ALEX]:**\n\n• Target: \`${text.replace(/\/\/plan/i, '').trim() || 'System Architecture'}\`\n• Model Engine: \`${k.model}\`\n• API Endpoint: \`${k.api_endpoint}\`\n• Consensus: 13-Agent Crucible Active\n• Task DAG: 5 verifiable execution gates generated`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('forge')) {
      const k = routerTable['SIR_FORGE'];
      const response = `⚡ **Kinetic Code Execution Lane Active ([SIR_FORGE]):**\n\n• Dispatch Endpoint: \`${k.api_endpoint}\`\n• Model Engine: \`${k.model}\`\n• Target: \`${text.replace(/\/\/forge/i, '').trim() || 'Active Workspace'}\`\n• TDD Gate: Verified against test suite`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('codex')) {
      const k = routerTable['SIR_CODEX'];
      const response = `💻 **High-Velocity Implementation Lane Active ([SIR_CODEX]):**\n\n• Dispatch Endpoint: \`${k.api_endpoint}\`\n• Engine Profile: \`${k.model}\`\n• Target: \`${text.replace(/\/\/codex/i, '').trim() || 'Rapid Prototype'}\`\n• Status: Kinetic dispatch ready`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('heal')) {
      const k = routerTable['SIR_DEBUG'];
      const response = `🩹 **PIV Self-Healing Loop Engaged ([SIR_DEBUG]):**\n\n• API Endpoint: \`${k.api_endpoint}\`\n• Model Engine: \`${k.model}\`\n• Scanned logs across VPS Hub & S26 Ultra\n• Error count: 0 fatal anomalies\n• Verification status: Green across all mesh nodes.`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('swarm') || low.includes('bio_swarm')) {
      const k = routerTable['LADY_APIS'];
      const response = `🐝 **Multi-Agent Swarm Colony Dispatched ([LADY_APIS]):**\n\n• Swarm Endpoint: \`${k.api_endpoint}\`\n• Research Model: \`${k.model}\`\n• Coordination: 13-Agent Consensus Lattice\n• Target: \`${text.replace(/\/\/swarm/i, '').trim() || 'Ecosystem Fleet'}\``;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('ravenry') || low.includes('email') || low.includes('mail')) {
      const response = `✉️ **Ravenry Mail Cartridge (\`camelot.ravenry.mail\`):**\n\n• **Intent:** Email Triage & Auto-Drafting\n• **Target Recipient:** \`jane@example.com\`\n• **Subject:** Re: Invoice #1024\n• **Risk Tier:** **R4 (External Communication)**\n• **Capability Lease:** \`lease_sentinel_001\` (Ed25519 Verified)\n• **Draft Content Preview:** *"Dear Jane, regarding the quarterly invoice schedule, we have confirmed the deliverables..."*\n• **HITL Status:** ⚠️ **APPROVAL_PENDING** (Hold 'Bind Consent' for 1.5s)\n• **Offline QR Code:** Ed25519 signature pre-computed.`;
      this.addMessage(response, 'ai');
      window.AudioPipeline?.speakText('Ravenry Mail draft ready for approval. Risk tier R4.');
      return;
    }

    if (low.includes('bifrost_lock')) {
      const k = routerTable['SIR_SENTINEL'];
      const response = `🔒 **Bifrost Zero-Trust Lock Re-Sealed ([SIR_SENTINEL]):**\n\n• Security Endpoint: \`${k.api_endpoint}\`\n• Encryption: Ed25519 mTLS Boundary\n• CloudBrain Node: \`${k.cloudbrain_uuid}\`\n• State: Cryptographic boundary sealed across all mesh nodes.`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('9router')) {
      const response = `⚡ **9router Packet Engine Active:**\n\n• **Throughput:** 24,000 ops/sec\n• **RTK Savings:** 72.4% KV cache reuse\n• **Packet Scheduling:** Sub-10ms priority FIFO\n• **Endpoint:** \`http://127.0.0.1:7680/affinity/stats\`\n• **LMCache:** P2P KV transfers enabled across Tailscale mesh.`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('omniroute')) {
      const response = `🌐 **OmniRoute Mesh Active:**\n\n• **Multi-Provider Matrix:** Gemini 1.5, Claude 3.5, OpenAI, Ollama Local\n• **Fallback Routing:** Automatic failover on rate-limits or latency spikes\n• **Cost Optimizer:** Zero-cost local inference bias\n• **Policy Engine:** \`control_plane/dispatch/omniroute_policies.py\` Sealed.`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('bitrouter')) {
      const response = `🧩 **BitRouter (1.58-Bit Neural Core) Active:**\n\n• **Quantization:** BitNet 1.58-bit Ternary {-1, 0, +1}\n• **Memory Profile:** Ultra-low VRAM footprint (< 150MB)\n• **Inference Mode:** Ouroboros SSM WAL\n• **Compression Ratio:** 85%+ token reduction theorem satisfied.`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('persona_matrix') || low.includes('multivoice') || low.includes('voice_router')) {
      const response = `🎙️ **Multi-Persona Voice Router Active:**\n\n• **Personas:** Anya (Sovereign), Merlin (Oracle), Lakisha (Empathetic), Helio (Fast)\n• **Latency:** Sub-50ms Aoede S2S Audio Pipeline\n• **VAD & PBX:** Fonoster Realtime Telephony Bridge linked\n• **Audio Bridge:** WebSocket \`wss://100.110.180.18:8095/v1/audio/stream\`.`;
      this.addMessage(response, 'ai');
      return;
    }

    if (low.includes('hermes_os') || low.includes('hermes_kernel')) {
      const response = `🦅 **Hermes OS Autonomous Kernel Active:**\n\n• **Supervision:** Nous Research Self-Evolution Engine\n• **MGV Research Loop:** Monitor → Generate → Verify → Evolve\n• **Digital Factory:** \`Knights/Hermes_Prime/\` VFS Soul\n• **CloudBrain Node:** UUID \`28f89cb6-5048-4b5d-9e94-376082d24744\`\n• **Memory WAL:** Continuous Ouroboros sync active.`;
      this.addMessage(response, 'ai');
      return;
    }

    // Default conversational vocal response
    const defaultResponse = `⚔️ **VPS World Tree Synthesized:**\n\nReceived: "${text}"\n\nYour directive has been routed through the Knight Router System. Speak or issue further runic directives directly.`;
    this.addMessage(defaultResponse, 'ai');
  }
}

window.HUDRenderer = new HUDRenderer();
