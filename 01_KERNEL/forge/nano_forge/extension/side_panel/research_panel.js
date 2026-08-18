// SPDX-License-Identifier: MIT

// 🚀 RESEARCH PANEL LOGIC - Sovereign IDE Enhancement
// Features: Observer Pattern, Cognitive Cortex display, Mission Queue integration

/**
 * Observer Pattern: Reactive state management
 */
class Observer {
  constructor(initialState = {}) {
    this._state = initialState;
    this._listeners = new Set();
  }
  set(patch) {
    this._state = { ...this._state, ...patch };
    this.notify();
  }
  subscribe(callback) {
    this._listeners.add(callback);
    callback(this._state);
    return () => this._listeners.delete(callback);
  }
  notify() {
    this._listeners.forEach((cb) => cb(this._state));
  }
}

const UI_STATE = new Observer({
  missionStatus: 'IDLE',
  lastAgent: 'SYSTEM',
  activeProfile: null,
});

const feed = document.getElementById('feed');
const promptInput = document.getElementById('promptInput');
const btnSend = document.getElementById('btnSend');
const btnVision = document.getElementById('btnVision');
const btnQueue = document.getElementById('btnQueue');
const profileSelect = document.getElementById('quickProfileSelect');
const identityDetails = document.getElementById('identityDetails');
const btnVoice = document.getElementById('btnVoice');
const voiceStatus = document.getElementById('voiceStatus');
const voiceText = document.getElementById('voiceText');

import { TOONEncoder } from '../src/prometheus/index.js';
// Import VoiceSquire
import { VoiceSquire } from '../src/squires/voice_squire.js';
import { UIManager } from './ui_manager.js';
const voiceSquire = new VoiceSquire();

// New: Clip Current Page Logic
async function clipCurrentPage() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab || !tab.url.startsWith('http')) {
      voiceSquire.speak('Cannot clip this page.');
      return;
    }

    const [{ result }] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => ({
        content: document.body.innerText,
        title: document.title,
      }),
    });

    const article = TOONEncoder.encodeWebArticle(tab.url, result.title, result.content);

    // Send to Background for GraphRAG Indexing
    chrome.runtime.sendMessage({
      action: 'INDEX_TOON_NODE',
      node: article,
    });

    voiceSquire.speak('Page clipped and indexed.');
    return article;
  } catch (e) {
    console.error('Clip failed:', e);
    voiceSquire.speak('Failed to clip page.');
  }
}

// 1. Listen for Intel Broadcasts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'INTEL_READY') {
    addIntelCard(request.intel);
  }
  if (request.action === 'LOG_CONFIG_CHANGE') loadProfiles();
});

function addIntelCard(intel) {
  const card = document.createElement('div');
  card.className = 'intel-card';

  // Color coding by Skill/Agent
  const skill = intel.skill || 'GENERAL';
  if (skill.includes('NAV')) card.style.borderLeftColor = '#ffeb3b';
  if (skill.includes('VISION') || intel.agent === 'OCULAR') card.style.borderLeftColor = '#9d00ff';
  if (skill.includes('SENTRY')) card.style.borderLeftColor = '#f44336';

  const time = new Date(intel.timestamp).toLocaleTimeString();

  // Build Core Content
  let html = `
        <div class="meta">
            <span class="agent-tag">${intel.agent} | ${skill}</span>
            <span>${time}</span>
        </div>
        <div class="content">${formatContent(intel.content)}</div>
    `;

  // 🚀 COGNITIVE CORTEX (The Glass Box)
  if (intel.tags && Object.keys(intel.tags).length > 0) {
    html += `
            <div class="cognitive-cortex">
                <div class="cognitive-header">
                    🧠 Cognitive Trace <span>▼</span>
                </div>
                <div class="cognitive-tags" style="display:none;">
                    ${Object.entries(intel.tags)
                      .map(
                        ([tag, val]) => `
                        <div class="cognitive-item">
                            <span class="tag-label">${tag}</span>
                            <div class="tag-value">${val}</div>
                        </div>
                    `,
                      )
                      .join('')}
                </div>
            </div>
        `;
  }

  card.innerHTML = html;
  feed.prepend(card);
}

// Global Delegated Listeners
document.addEventListener('click', (e) => {
  // 1. Cognitive Cortex Toggle
  if (
    e.target.classList.contains('cognitive-header') ||
    e.target.parentElement.classList.contains('cognitive-header')
  ) {
    const header = e.target.classList.contains('cognitive-header')
      ? e.target
      : e.target.parentElement;
    const tags = header.nextElementSibling;
    const arrow = header.querySelector('span');
    if (tags.style.display === 'none') {
      tags.style.display = 'flex';
      arrow.textContent = '▲';
    } else {
      tags.style.display = 'none';
      arrow.textContent = '▼';
    }
  }

  // 2. Source Link Highlight
  if (e.target.classList.contains('source-link')) {
    const id = e.target.getAttribute('data-id');
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, {
          target: 'SENTRY',
          action: 'HIGHLIGHT_SOURCE',
          id: id,
        });
      }
    });
  }
});

function formatContent(content) {
  if (!content) return '...';
  try {
    if (typeof content === 'string' && (content.startsWith('{') || content.startsWith('['))) {
      const obj = JSON.parse(content);
      return `<pre>${formatJSON(obj)}</pre>`;
    }
  } catch (e) {}
  return content;
}

function formatJSON(obj) {
  return JSON.stringify(obj, null, 2).replace(/"_source":\s*"(\d+)"/g, (match, id) => {
    return `"_source": <span class="source-link" data-id="${id}" style="color:cyan; cursor:pointer;">⚓ ${id}</span>`;
  });
}

// 2. Command Logic
function sendCommand(isQueue = false) {
  const query = promptInput.value.trim();
  if (!query) return;

  const profileId = profileSelect.value;
  const profileName = profileSelect.options[profileSelect.selectedIndex]?.text || 'Default';

  promptInput.value = '';
  UI_STATE.set({ missionStatus: 'ACTIVE' });

  chrome.runtime.sendMessage(
    {
      action: 'START_MISSION',
      qfocus: query,
      device: document.getElementById('mobileToggle').checked ? 'MOBILE' : 'DESKTOP',
      queue: isQueue,
      profileId: profileId,
      profileName: profileName,
    },
    (res) => {
      if (res && res.status === 'QUEUED') updateQueueUI();
    },
  );
}

btnSend.onclick = () => sendCommand(false);
btnQueue.onclick = () => sendCommand(true);
promptInput.onkeypress = (e) => {
  if (e.key === 'Enter') sendCommand(false);
};

// Vision Lance
btnVision.onclick = () => {
  const goal = promptInput.value.trim() || 'Analyze screen.';
  chrome.runtime.sendMessage({ action: 'CAPTURE_VISIBLE_TAB' }, (res) => {
    if (res && res.status === 'SUCCESS') {
      chrome.runtime.sendMessage({
        action: 'REPORT_INTEL',
        agent: 'OCULAR',
        skill: 'ANALYZE_SCREENSHOT',
        data: { screenshot: res.screenshot, goal: goal },
      });
    }
  });
};

// Knight Squad Deployment
const btnSpawnSquad = document.getElementById('btnSpawnSquad');
const btnSynthesize = document.getElementById('btnSynthesize');
const squadStatus = document.getElementById('squadStatus');

if (btnSpawnSquad) {
  btnSpawnSquad.onclick = () => {
    // ... existing spawn logic ...
    const goal = promptInput.value.trim() || 'General Research';
    squadStatus.textContent = 'Deploying 3 Knights...';
    voiceSquire.speak(`Deploying Knight Squad for ${goal}`);

    chrome.runtime.sendMessage({ action: 'SPAWN_SQUAD', goal: goal }, (res) => {
      if (res && res.status === 'SUCCESS') {
        const knights = res.squad.conf.map((k) => k.role.split(' ')[1]).join(' • '); // "Apis • Syntax • Zenith"
        squadStatus.innerHTML = `
                    <span style="color:#0f0">ROUND TABLE ACTIVE</span> 
                    <span style="font-size:0.8em">(${res.squad.squadId.slice(0, 4)})</span>
                    <br/>
                    <span style="font-size:0.85em; color:#ddd">⚔️ ${knights}</span>
                `;
      } else {
        squadStatus.textContent = 'Deployment Failed.';
      }
    });
  };
}

if (btnSynthesize) {
  btnSynthesize.onclick = () => {
    const query = promptInput.value.trim() || 'Summarize all research';
    voiceSquire.speak('Synthesizing Intelligence Report...');
    squadStatus.textContent = 'Synthesizing...';

    chrome.runtime.sendMessage({ action: 'SYNTHESIZE_REPORT', query: query }, (res) => {
      if (res && res.status === 'SUCCESS') {
        voiceSquire.speak('Synthesis Complete.');
        squadStatus.innerHTML = `<span style="color:#0f0">REPORT READY</span>`;
        addIntelCard({
          agent: 'SYNTHESIS_ENGINE',
          skill: 'PATTERN_SYNTHESIS',
          content: res.report,
          timestamp: new Date().toISOString(),
          tags: { TYPE: 'REPORT' },
        });
      } else {
        squadStatus.textContent = 'Synthesis Failed.';
        voiceSquire.speak('Synthesis Failed.');
      }
    });
  };
}

// Voice Command Toggle
if (btnVoice) {
  // Sync UI with VoiceSquire reactive state
  voiceSquire.onStateChange = (isListening) => {
    if (!isListening) {
      btnVoice.classList.remove('recording');
      voiceStatus.style.display = 'none';
    } else {
      btnVoice.classList.add('recording');
      voiceStatus.style.display = 'flex';
    }
  };

  btnVoice.onclick = () => {
    if (!voiceSquire.isListening) {
      // Start listening
      const started = voiceSquire.startListening(
        (command) => {
          // Command detected
          voiceText.textContent = `Heard: "${command.command}"`;
          executeVoiceCommand(command);
          // Don't stop listening, it's continuous
        },
        (error) => {
          // Error handling
          voiceText.textContent = `Error: ${error}`;
        },
      );

      if (started) {
        voiceText.textContent = 'Listening for "Nano" or "Anya"...';
        voiceSquire.speak('Voice command activated.');
      }
    } else {
      // Stop listening
      voiceSquire.stopListening();
      voiceSquire.speak('Voice command deactivated.');
    }
  };
}

// Voice Command Logic
async function executeVoiceCommand(cmd) {
  const raw = cmd.command.toLowerCase();

  if (raw.includes('clip') || raw.includes('save this')) {
    voiceSquire.speak('Clipping page to Brain Notebook.');
    await clipCurrentPage();
    return;
  }

  if (
    raw.includes('research') ||
    raw.includes('look up') ||
    raw.includes('find') ||
    raw.includes('extract') ||
    raw.includes('search')
  ) {
    const query = raw.replace(/research|look up|find|extract|search/gi, '').trim();
    promptInput.value = query || cmd.command; // Use original command if query is empty after replacement
    voiceSquire.speak(`Researching ${query || cmd.command}`);
    btnSend.click();
    return;
  }

  if (raw.includes('queue') || raw.includes('schedule')) {
    promptInput.value = raw.replace(/queue|schedule/gi, '').trim();
    sendCommand(true);
    voiceSquire.speak('Mission queued.');
    return;
  }

  if (raw.includes('status')) {
    const queueCount = document.getElementById('queueContainer')?.children.length || 0;
    voiceSquire.speak(
      `Current status: ${UI_STATE._state.missionStatus}. Queue has ${queueCount} missions.`,
    );
    return;
  }

  if (raw.includes('clear') || raw.includes('reset')) {
    feed.innerHTML = '';
    chrome.storage.local.remove('research_history');
    voiceSquire.speak('Research feed cleared.');
  } else {
    // Default: treat as research query
    promptInput.value = cmd.command;
    sendCommand(false);
    voiceSquire.speak('Executing command.');
  }
}

function updateQueueUI() {
  chrome.runtime.sendMessage({ action: 'GET_QUEUE_STATUS' }, (res) => {
    const container = document.getElementById('queueContainer');
    if (!res || !res.queue || res.queue.length === 0) {
      container.style.display = 'none';
      return;
    }
    container.innerHTML =
      `<div style="padding:4px; font-weight:bold; color:#666;">MISSION QUEUE (${res.queue.length})</div>` +
      res.queue
        .map(
          (m, i) =>
            `<div style="font-size:0.8em; padding:2px 8px; border-top:1px solid #222; color:#aaa;">${i + 1}. [${m.profileName}] ${m.qfocus}</div>`,
        )
        .join('');
    container.style.display = 'block';
  });
}

function loadProfiles() {
  chrome.runtime.sendMessage({ action: 'GET_PROFILES' }, (res) => {
    if (res && res.profiles) {
      profileSelect.innerHTML = res.profiles
        .map((p) => `<option value="${p.id}">${p.name}</option>`)
        .join('');
      if (res.activeId) profileSelect.value = res.activeId;

      // Update Observer state for reactive UI
      UI_STATE.set({
        activeProfile: res.activeProfile,
        profiles: res.profiles,
      });
    }
  });
}

// Subscribe to state changes for identity details
UI_STATE.subscribe((state) => {
  if (state.activeProfile) {
    const ua = state.activeProfile.userAgent || 'Unknown';
    const shortUA = ua.includes('iPhone') ? 'Mobile' : 'Desktop';
    identityDetails.textContent = `Type: ${state.activeProfile.type || 'N/A'} | UA: ${shortUA}`;
  }
});

// Global Polls/Init
setInterval(updateQueueUI, 5000);
loadProfiles();

// Persistence - Load History
chrome.storage.local.get(['research_history'], (data) => {
  if (data.research_history) {
    // We recreate cards from historic data objects
    // To keep it simple for now, we just restore the innerHTML but that breaks events.
    // BETTER: Storage should hold the 'intel' objects.
    // For now, simple innerHTML restore but re-bind links?
    feed.innerHTML = data.research_history;
  }
});

// Clear History
document.getElementById('clearBtn').onclick = () => {
  feed.innerHTML = '';
  chrome.storage.local.remove('research_history');
};

// Export
document.getElementById('exportBtn').onclick = () => {
  const text = Array.from(document.querySelectorAll('.intel-card'))
    .map((c) => c.innerText)
    .join('\n---\n\n');
  const blob = new Blob([text], { type: 'text/markdown' });
  chrome.downloads.download({
    url: URL.createObjectURL(blob),
    filename: `research_${Date.now()}.md`,
  });
};

// Mutation Save
new MutationObserver(() => {
  chrome.storage.local.set({ research_history: feed.innerHTML });
}).observe(feed, { childList: true, subtree: true });
