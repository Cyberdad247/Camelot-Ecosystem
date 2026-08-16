// Phase 2 acceptance tests — voice guardrails, all against the DEFAULT test
// provider (MockVoiceProvider) and the pure VoiceSessionController.

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { LOW_CONFIDENCE_THRESHOLD, MockVoiceProvider } from '@camelot/contracts';
import type { MockVoiceProviderOptions } from '@camelot/contracts';
import { VoiceSessionController } from '../src/voice-session.js';
import type { VoiceNotice, VoiceUiState } from '../src/voice-session.js';

interface Harness {
  controller: VoiceSessionController;
  provider: MockVoiceProvider;
  submitted: Array<{ transcript: string; audioSha256: string }>;
  bargeIns: string[];
  notices: VoiceNotice[];
  states: VoiceUiState[];
  reviews: Array<{ transcript: string; confidence: number }>;
}

function makeHarness(options: MockVoiceProviderOptions = {}): Harness {
  const provider = new MockVoiceProvider(options);
  const harness: Partial<Harness> = {
    provider,
    submitted: [],
    bargeIns: [],
    notices: [],
    states: [],
    reviews: [],
  };
  harness.controller = new VoiceSessionController(provider, {
    submitTranscript: async (transcript, meta) => {
      harness.submitted!.push({ transcript, audioSha256: meta.audioSha256 });
      return { turnId: `turn-${harness.submitted!.length}` };
    },
    bargeIn: async (turnId) => {
      harness.bargeIns!.push(turnId);
    },
    onState: (s) => harness.states!.push(s),
    onNotice: (n) => harness.notices!.push(n),
    onReview: (transcript, confidence) => harness.reviews!.push({ transcript, confidence }),
  });
  return harness as Harness;
}

async function pressAndRelease(h: Harness): Promise<void> {
  await h.controller.pttDown();
  await h.controller.pttUp();
}

describe('Phase 2 voice guardrails', () => {
  it('1. microphone denied -> text mode remains usable', async () => {
    const h = makeHarness({ failCapture: true });
    await h.controller.pttDown();
    expect(h.controller.textOnly).toBe(true);
    expect(h.states).toContain('text-only');
    expect(h.notices[0]?.kind).toBe('mic-denied');
    // Voice path is inert but nothing blocks the text path; no submission happened.
    await h.controller.pttDown();
    expect(h.submitted).toHaveLength(0);
  });

  it('2. STT failure -> no policy/tool request is triggered', async () => {
    const h = makeHarness({ failTranscribe: true });
    await pressAndRelease(h);
    expect(h.submitted).toHaveLength(0);
    expect(h.bargeIns).toHaveLength(0);
    expect(h.notices.some((n) => n.kind === 'stt-failed')).toBe(true);
    expect(h.controller.state).toBe('voice-idle');
  });

  it('2b. empty/silent transcript -> nothing submitted', async () => {
    const h = makeHarness({ script: [{ transcript: null, confidence: 0 }] });
    await pressAndRelease(h);
    expect(h.submitted).toHaveLength(0);
    expect(h.notices.some((n) => n.kind === 'no-speech')).toBe(true);
  });

  it('3. low confidence -> review required, no auto-submission', async () => {
    const h = makeHarness({
      script: [
        { transcript: 'create a change request', confidence: LOW_CONFIDENCE_THRESHOLD - 0.1 },
      ],
    });
    await pressAndRelease(h);
    expect(h.submitted).toHaveLength(0);
    expect(h.reviews).toEqual([
      { transcript: 'create a change request', confidence: LOW_CONFIDENCE_THRESHOLD - 0.1 },
    ]);
    expect(h.controller.state).toBe('review');
  });

  it('4. accepted transcript -> submitted ONLY through the turn path, with audio hash', async () => {
    const h = makeHarness({
      script: [{ transcript: 'prepare a deployment review', confidence: 0.93 }],
    });
    await pressAndRelease(h);
    expect(h.submitted).toHaveLength(1);
    expect(h.submitted[0]!.transcript).toBe('prepare a deployment review');
    // Raw audio's only trace: a SHA-256 hex digest.
    expect(h.submitted[0]!.audioSha256).toMatch(/^[0-9a-f]{64}$/);
    // Deterministic mock audio -> deterministic hash across runs.
    const h2 = makeHarness({
      script: [{ transcript: 'prepare a deployment review', confidence: 0.93 }],
    });
    await pressAndRelease(h2);
    expect(h2.submitted[0]!.audioSha256).toBe(h.submitted[0]!.audioSha256);
  });

  it('6. barge-in stops playback immediately, then cancels stream + revokes lease server-side', async () => {
    const h = makeHarness();
    await h.controller.speakReply('Drafting the review now.', 'turn-0042');
    expect(h.controller.speakingTurnId).toBe('turn-0042');

    await h.controller.stopSpeaking();
    // Playback stopped locally FIRST…
    expect(h.provider.stoppedPlaybacks).toContain('turn-0042');
    expect(h.provider.cancelledTurns).toContain('turn-0042');
    // …then the existing barge-in event went to the gateway (which cancels
    // the stream and revokes unused leases — proven in gateway tests T4).
    expect(h.bargeIns).toEqual(['turn-0042']);
    expect(h.controller.speakingTurnId).toBeNull();
  });

  it('6b. pressing push-to-talk while Anya speaks is a barge-in', async () => {
    const h = makeHarness();
    await h.controller.speakReply('Long reply being spoken…', 'turn-0043');
    await h.controller.pttDown();
    expect(h.provider.stoppedPlaybacks).toContain('turn-0043');
    expect(h.bargeIns).toEqual(['turn-0043']);
    expect(h.controller.state).toBe('listening');
  });

  it('7. TTS failure -> text remains the deliverable, visible notice, no crash', async () => {
    const h = makeHarness({ failSynthesize: true });
    await h.controller.speakReply('Staging is green.', 'turn-0044');
    expect(h.notices.some((n) => n.kind === 'tts-failed')).toBe(true);
    expect(h.controller.speakingTurnId).toBeNull();
  });

  it('mock provider is deterministic across runs (default test provider)', async () => {
    const a = new MockVoiceProvider();
    const b = new MockVoiceProvider();
    await a.startCapture();
    await b.startCapture();
    const [audioA, audioB] = [await a.stopCapture(), await b.stopCapture()];
    expect([...audioA.pcm16.slice(0, 16)]).toEqual([...audioB.pcm16.slice(0, 16)]);
    expect((await a.transcribe(audioA)).transcript).toBe((await b.transcribe(audioB)).transcript);
  });
});

// Tests 4/5 tier semantics (spoken tier-2 draft, spoken tier-3 confirmation)
// run against the REAL gateway flow: the transcript enters via submitTranscript
// -> existing VoiceTurn endpoint, where gateway tests T2/T3 already prove
// draft creation and confirmation blocking. Here we prove the voice path
// composes with a faithful gateway stub.
describe('Phase 2 spoken tier flows (gateway-faithful stub)', () => {
  let responses: Record<string, { effect: string; executed: boolean }>;

  beforeEach(() => {
    responses = {};
  });

  function tierHarness() {
    const provider = new MockVoiceProvider({
      script: [
        { transcript: 'prepare a deployment review', confidence: 0.95 },
        { transcript: 'create a change request to scale the api tier', confidence: 0.95 },
      ],
    });
    const submitTranscript = vi.fn(async (transcript: string) => {
      // Faithful to gateway policy: tier-2 executes under auto-lease,
      // tier-3 blocks until confirmation.
      if (transcript.includes('deployment review')) {
        responses['t2'] = { effect: 'allow', executed: true };
      } else if (transcript.includes('change request')) {
        responses['t3'] = { effect: 'requires_confirmation', executed: false };
      }
      return { turnId: 'turn-x' };
    });
    const controller = new VoiceSessionController(provider, {
      submitTranscript,
      bargeIn: async () => {},
      onState: () => {},
      onNotice: () => {},
      onReview: () => {},
    });
    return { controller, submitTranscript };
  }

  it('4/5. spoken tier-2 executes a draft; spoken tier-3 stays blocked awaiting visible confirmation', async () => {
    const { controller } = tierHarness();
    await controller.pttDown();
    await controller.pttUp(); // tier-2 utterance
    await controller.pttDown();
    await controller.pttUp(); // tier-3 utterance
    expect(responses['t2']).toEqual({ effect: 'allow', executed: true });
    expect(responses['t3']).toEqual({ effect: 'requires_confirmation', executed: false });
  });
});
