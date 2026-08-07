// Anya Console — governed reference client for the Camelot voice gateway.
//
// Boundary (ADR-001): every interaction goes through CamelotClient. This file
// contains rendering only; policy, leases, execution, and audit all live in
// the gateway. Phase 2 adds a push-to-talk voice path: capture/STT/TTS go
// through a VoiceProvider (Hermes adapter), but transcripts still enter
// Camelot ONLY via the existing VoiceTurn endpoint, and barge-in still runs
// through the existing barge-in event.

import {
  CamelotClient,
  FIXTURE_SESSION_ID,
  FIXTURE_UTTERANCES,
  MockVoiceProvider,
  fixtureTurn,
  initialSessionView,
  mockBargeIn,
  reduceSessionEvent,
} from '@camelot/contracts';
import type {
  CamelotTurnResponse,
  PolicyDecision,
  SessionView,
  VoiceProvider,
  VoiceTurn,
} from '@camelot/contracts';
import {
  approvalVisible,
  avatarBadge,
  bargeInAvailable,
  decisionCardModel,
  modelRouteLine,
  pendingLease,
} from './view-model.js';
import { HermesVoiceProvider } from './hermes-provider.js';
import { VoiceSessionController } from './voice-session.js';
import type { VoiceUiState } from './voice-session.js';

const params = new URLSearchParams(location.search);
const GATEWAY_URL = params.get('gateway') ?? `http://${location.hostname}:8788`;
const HERMES_URL = params.get('hermes') ?? `http://${location.hostname}:8790`;

const client = new CamelotClient({ baseUrl: GATEWAY_URL });

let view: SessionView = initialSessionView();
let turnCounter = 0;
let lastDecision: PolicyDecision | null = null;

const $ = <T extends HTMLElement>(id: string): T => {
  const el = document.getElementById(id);
  if (!el) throw new Error(`missing #${id}`);
  return el as T;
};

const transcriptEl = $('transcript');
const stateBadgeEl = $('state-badge');
const decisionCardEl = $('decision-card');
const approvalEl = $('approval');
const bargeInBtn = $<HTMLButtonElement>('barge-in');
const auditDrawerEl = $('audit-drawer');
const auditListEl = $('audit-list');
const auditDetailEl = $('audit-detail');
const inputEl = $<HTMLInputElement>('utterance');
const gatewayStatusEl = $('gateway-status');
const voiceBarEl = $('voice-bar');
const voiceNoticeEl = $('voice-notice');
const micStatusEl = $('mic-status');
const micDeviceEl = $<HTMLSelectElement>('mic-device');
const pttBtn = $<HTMLButtonElement>('ptt');
const stopSpeakingBtn = $<HTMLButtonElement>('stop-speaking');
const voiceStateEl = $('voice-state');

// ── transcript rendering ────────────────────────────────────────────────

function addBubble(role: 'user' | 'anya' | 'system', text: string, id?: string): HTMLElement {
  const el = document.createElement('div');
  el.className = `bubble bubble-${role}`;
  if (id) el.dataset['turn'] = id;
  el.textContent = text;
  transcriptEl.appendChild(el);
  transcriptEl.scrollTop = transcriptEl.scrollHeight;
  return el;
}

function anyaBubbleFor(turnId: string): HTMLElement {
  const existing = transcriptEl.querySelector<HTMLElement>(`[data-turn="anya-${turnId}"]`);
  return existing ?? addBubble('anya', '', `anya-${turnId}`);
}

// ── view rendering ──────────────────────────────────────────────────────

function render(): void {
  const badge = avatarBadge(view);
  stateBadgeEl.textContent = badge.label;
  stateBadgeEl.className = `badge ${badge.cssClass}`;

  const card = decisionCardModel(lastDecision);
  const routeLine = modelRouteLine(view);
  decisionCardEl.innerHTML = `
    <div class="card-title">Policy decision</div>
    <div class="effect ${card.effectClass}">${card.effectLabel}</div>
    <div class="skill-line">${card.skillLine}</div>
    <div class="reason">${card.reason}</div>
    ${routeLine ? `<div class="skill-line">${routeLine}</div>` : ''}`;

  const lease = pendingLease(view);
  if (approvalVisible(view) && lease) {
    approvalEl.style.display = 'block';
    approvalEl.querySelector('.lease-line')!.textContent =
      `${lease.capability} · expires ${lease.expiresAt}`;
  } else {
    approvalEl.style.display = 'none';
  }

  bargeInBtn.disabled = !bargeInAvailable(view) && voiceSession.speakingTurnId === null;
  stopSpeakingBtn.disabled = voiceSession.speakingTurnId === null;

  auditListEl.innerHTML = '';
  for (const auditId of view.auditIds) {
    const li = document.createElement('li');
    const btn = document.createElement('button');
    btn.textContent = auditId;
    btn.onclick = async () => {
      const event = await client.getAudit(auditId);
      auditDetailEl.textContent = JSON.stringify(event, null, 2);
    };
    li.appendChild(btn);
    auditListEl.appendChild(li);
  }
}

// ── turn submission (shared by text and voice paths) ────────────────────

async function submitUtterance(
  text: string,
  meta?: { audioSha256: string },
): Promise<CamelotTurnResponse | null> {
  if (!text.trim()) return null;
  turnCounter += 1;
  const base = fixtureTurn(text, turnCounter);
  const turn: VoiceTurn = meta
    ? { ...base, modality: 'voice', audioSha256: meta.audioSha256 }
    : base;
  addBubble('user', (meta ? '🎙 ' : '') + text, turn.turnId);
  try {
    const res = await client.submitTurn(turn);
    lastDecision = res.decision;
    if (res.reply.final) {
      anyaBubbleFor(turn.turnId).textContent = res.reply.text;
    }
    // Speak governed replies when voice is on. The transcript text stays
    // authoritative — TTS failure never hides it (controller guarantees).
    // Deterministic replies carry sync text; model-streamed replies are
    // spoken on reply.done instead.
    if (voiceEnabled && res.reply.text) {
      spokenTurns.add(turn.turnId);
      void voiceSession.speakReply(res.reply.text, turn.turnId);
    }
    render();
    return res;
  } catch (err) {
    addBubble('system', String(err));
    render();
    return null;
  }
}

// ── voice session (Phase 2) ─────────────────────────────────────────────

let voiceEnabled = false;

function showVoiceNotice(message: string): void {
  voiceNoticeEl.hidden = false;
  voiceNoticeEl.textContent = message;
}

function voiceStateLabel(state: VoiceUiState): string {
  switch (state) {
    case 'listening': return 'voice: listening';
    case 'transcribing': return 'voice: transcribing…';
    case 'review': return 'voice: review needed';
    case 'voice-error': return 'voice: error';
    case 'text-only': return 'voice: text-only fallback';
    default: return 'voice: idle';
  }
}

function makeProvider(): VoiceProvider {
  if (params.get('voice') === 'mock') return new MockVoiceProvider();
  return new HermesVoiceProvider(HERMES_URL);
}

const provider = makeProvider();
const voiceSession = new VoiceSessionController(provider, {
  submitTranscript: async (transcript, meta) => {
    const res = await submitUtterance(transcript, meta);
    return res ? { turnId: res.turnId } : undefined;
  },
  bargeIn: async (turnId) => {
    await client.bargeIn(mockBargeIn(turnId));
  },
  onState: (state) => {
    voiceStateEl.textContent = voiceStateLabel(state);
    voiceStateEl.className =
      'chip ' +
      (state === 'listening' ? 'ok' : state === 'voice-error' || state === 'text-only' ? 'err' : state === 'review' ? 'warn' : '');
    pttBtn.classList.toggle('listening', state === 'listening');
    render();
  },
  onNotice: (notice) => {
    showVoiceNotice(notice.message);
    addBubble('system', notice.message);
  },
  onReview: (transcript) => {
    // Low confidence: prefill only. The user must press Send themselves.
    inputEl.value = transcript;
    inputEl.focus();
    inputEl.select();
  },
});

async function initVoice(): Promise<void> {
  const health = await provider.health();
  if (!health.ok) {
    showVoiceNotice(
      `Voice disabled — Hermes adapter unreachable (${HERMES_URL}). Text mode is fully functional. ` +
        'Start it with ENABLE_HERMES_VOICE=true make dev-up.',
    );
    return;
  }
  if (!(navigator.mediaDevices?.getUserMedia) && !(provider instanceof MockVoiceProvider)) {
    showVoiceNotice('Voice disabled — no microphone API in this browser. Text mode is fully functional.');
    return;
  }
  voiceEnabled = true;
  voiceBarEl.hidden = false;
  micStatusEl.textContent = `mic: ready · stt=${health.stt} tts=${health.tts}`;
  micStatusEl.className = 'chip ok';

  try {
    const permission = await navigator.permissions?.query?.({ name: 'microphone' as PermissionName });
    if (permission) {
      const update = () => {
        micStatusEl.textContent = `mic: ${permission.state} · stt=${health.stt}`;
        micStatusEl.className = 'chip ' + (permission.state === 'denied' ? 'err' : 'ok');
      };
      permission.onchange = update;
      update();
    }
  } catch {
    /* permissions API optional */
  }

  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    for (const device of devices.filter((d) => d.kind === 'audioinput')) {
      const option = document.createElement('option');
      option.value = device.deviceId;
      option.textContent = device.label || `mic ${micDeviceEl.length}`;
      micDeviceEl.appendChild(option);
    }
  } catch {
    /* device labels appear after first grant */
  }
}

pttBtn.addEventListener('pointerdown', () => void voiceSession.pttDown(micDeviceEl.value || undefined));
pttBtn.addEventListener('pointerup', () => void voiceSession.pttUp());
pttBtn.addEventListener('pointerleave', () => void voiceSession.pttUp());
stopSpeakingBtn.onclick = () => void voiceSession.stopSpeaking();

// ── gateway wiring ──────────────────────────────────────────────────────

const spokenTurns = new Set<string>();

client.connectEvents(FIXTURE_SESSION_ID, (event) => {
  view = reduceSessionEvent(view, event);
  if (event.type === 'reply.chunk') {
    anyaBubbleFor(event.turnId).textContent = view.replies[event.turnId] ?? '';
    transcriptEl.scrollTop = transcriptEl.scrollHeight;
  }
  if (event.type === 'turn.cancelled') {
    anyaBubbleFor(event.turnId).classList.add('cancelled');
    addBubble('system', `Turn ${event.turnId} interrupted — response cancelled, unused leases revoked.`);
  }
  if (event.type === 'reply.done') {
    // Model-streamed replies have no sync text; speak the complete
    // accumulated reply now (sentence-safe: whole utterance at once).
    const text = view.replies[event.turnId];
    if (voiceEnabled && text && !spokenTurns.has(event.turnId)) {
      spokenTurns.add(event.turnId);
      void voiceSession.speakReply(text, event.turnId);
    }
  }
  render();
});

$('send').onclick = () => {
  void submitUtterance(inputEl.value);
  inputEl.value = '';
};
inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    void submitUtterance(inputEl.value);
    inputEl.value = '';
  }
});

for (const [id, text] of [
  ['quick-staging', FIXTURE_UTTERANCES.stagingRead],
  ['quick-review', FIXTURE_UTTERANCES.deploymentReview],
  ['quick-cr', FIXTURE_UTTERANCES.changeRequest],
] as const) {
  $(id).onclick = () => void submitUtterance(text);
}

bargeInBtn.onclick = async () => {
  // Voice playback stops immediately, then the gateway cancels the stream
  // and revokes unused leases (single barge-in path for voice and text).
  if (voiceSession.speakingTurnId !== null) {
    await voiceSession.stopSpeaking();
    render();
    return;
  }
  const turnId = view.streamingTurnId;
  if (!turnId) return;
  await client.bargeIn(mockBargeIn(turnId));
};

approvalEl.querySelector<HTMLButtonElement>('.approve')!.onclick = () => void resolveLease(true);
approvalEl.querySelector<HTMLButtonElement>('.deny')!.onclick = () => void resolveLease(false);

async function resolveLease(approve: boolean): Promise<void> {
  const lease = pendingLease(view);
  if (!lease) return;
  try {
    const res = await client.confirm({
      sessionId: FIXTURE_SESSION_ID,
      leaseId: lease.leaseId,
      approve,
    });
    view = reduceSessionEvent(view, approve
      ? { type: 'lease.consumed', leaseId: lease.leaseId }
      : { type: 'lease.revoked', leaseId: lease.leaseId, reason: 'denied by user' });
    if (!approve) {
      addBubble('system', `Change request denied — lease ${lease.leaseId} revoked.`);
      view = { ...view, uiState: 'idle' };
    } else if (res.artifact) {
      addBubble('system', `Executed under lease ${lease.leaseId}: ${res.artifact.summary}`);
      view = { ...view, uiState: 'speaking' };
      if (voiceEnabled && res.reply?.text) {
        void voiceSession.speakReply(res.reply.text, lease.turnId);
      }
    }
  } catch (err) {
    addBubble('system', String(err));
  }
  render();
}

$('audit-toggle').onclick = () => {
  auditDrawerEl.classList.toggle('open');
};

// ── health probes ───────────────────────────────────────────────────────

client
  .health()
  .then((h) => {
    gatewayStatusEl.textContent = `${h.service} ${h.version} · connected`;
    gatewayStatusEl.classList.add('ok');
  })
  .catch(() => {
    gatewayStatusEl.textContent = `gateway unreachable at ${GATEWAY_URL}`;
    gatewayStatusEl.classList.add('err');
  });

void initVoice();
render();
