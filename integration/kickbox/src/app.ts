// Anya Console — text-first reference client for the Camelot voice gateway.
//
// Boundary (ADR-001): every interaction goes through CamelotClient. This file
// contains rendering only; policy, leases, execution, and audit all live in
// the gateway. Barge-in uses the mock fixture event — the voice phase will
// swap it for a VAD trigger without changing this wiring.

import {
  CamelotClient,
  FIXTURE_SESSION_ID,
  FIXTURE_UTTERANCES,
  fixtureTurn,
  initialSessionView,
  mockBargeIn,
  reduceSessionEvent,
} from '@camelot/contracts';
import type {
  CamelotTurnResponse,
  PolicyDecision,
  SessionView,
} from '@camelot/contracts';
import {
  approvalVisible,
  avatarBadge,
  bargeInAvailable,
  decisionCardModel,
  pendingLease,
} from './view-model.js';

const GATEWAY_URL =
  new URLSearchParams(location.search).get('gateway') ?? `http://${location.hostname}:8788`;

const client = new CamelotClient({ baseUrl: GATEWAY_URL });

let view: SessionView = initialSessionView();
let turnCounter = 0;
let lastDecision: PolicyDecision | null = null;
let lastTurnResponse: CamelotTurnResponse | null = null;

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
  decisionCardEl.innerHTML = `
    <div class="card-title">Policy decision</div>
    <div class="effect ${card.effectClass}">${card.effectLabel}</div>
    <div class="skill-line">${card.skillLine}</div>
    <div class="reason">${card.reason}</div>`;

  const lease = pendingLease(view);
  if (approvalVisible(view) && lease) {
    approvalEl.style.display = 'block';
    approvalEl.querySelector('.lease-line')!.textContent =
      `${lease.capability} · expires ${lease.expiresAt}`;
  } else {
    approvalEl.style.display = 'none';
  }

  bargeInBtn.disabled = !bargeInAvailable(view);

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

// ── gateway wiring ──────────────────────────────────────────────────────

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
  render();
});

async function submitUtterance(text: string): Promise<void> {
  if (!text.trim()) return;
  turnCounter += 1;
  const turn = fixtureTurn(text, turnCounter);
  addBubble('user', text, turn.turnId);
  try {
    lastTurnResponse = await client.submitTurn(turn);
    lastDecision = lastTurnResponse.decision;
    if (lastTurnResponse.reply.final) {
      anyaBubbleFor(turn.turnId).textContent = lastTurnResponse.reply.text;
    }
  } catch (err) {
    addBubble('system', String(err));
  }
  render();
}

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
    }
  } catch (err) {
    addBubble('system', String(err));
  }
  render();
}

$('audit-toggle').onclick = () => {
  auditDrawerEl.classList.toggle('open');
};

// ── health probe ────────────────────────────────────────────────────────

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

render();
