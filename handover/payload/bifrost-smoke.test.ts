import assert from 'node:assert/strict';
import { runAntigravity } from '../execution/antigravity-engine';
import { signDag, verifyDagSignature } from '../provenance/dag-signer';
import { InMemoryCommandQueue } from '../runtime/command-queue';
import { buildPromptDependencyGraph, enforceAgentArmor } from '../security/agentarmor-pdg';

const secret = 'test-secret-that-is-long-enough';

const envelope = signDag(
  {
    dagId: 'dag_test',
    root: 'a',
    nodes: {
      a: { id: 'a', kind: 'test', intent: 'verify' },
    },
  },
  secret,
);
assert.equal(verifyDagSignature(envelope, secret), true);

const graph = buildPromptDependencyGraph({
  sourceLabel: 'web_page',
  sourceIntegrity: 'LOW_INTEGRITY',
  transforms: ['APEE'],
  sink: 'file_delete',
});
const armor = enforceAgentArmor(graph);
assert.equal(armor.allowed, false);

const ag = runAntigravity({ action: 'delete_path', targetPath: '/tmp/x', approved: false });
assert.equal(ag.ok, false);
assert.equal(ag.status, 'approval_required');

const queue = new InMemoryCommandQueue();
const cmd = await queue.enqueue({ input: 'test command' });
assert.equal(cmd.status, 'queued');
await queue.updateStatus(cmd.commandId, 'complete');
const done = await queue.get(cmd.commandId);
assert.equal(done?.status, 'complete');

// ── Bifrost trust plane ──────────────────────────────────────────
import('../bifrost/bifrost-envelope').then(async ({ sealEnvelope, verifyEnvelope }) => {
  const { HeimdallFsm } = await import('../bifrost/heimdall-fsm');
  const { reconcileTrust, gateIntent } = await import('../bifrost/bifrost-gateway');

  const bsecret = 'bifrost-mesh-secret';
  const env = sealEnvelope(
    { intent: 'status_check' },
    {
      type: 'intent',
      src: 'excalibur',
      dst: 'cybertronia',
      realm: 'camelot',
      node: 'console',
      seq: 1,
      secret: bsecret,
    },
  );

  // Valid envelope verifies
  assert.equal(verifyEnvelope(env, { secret: bsecret }).valid, true);

  // Tampered payload → quarantine
  const tampered = { ...env, payload: { intent: 'rm -rf /' } };
  const tv = verifyEnvelope(tampered, { secret: bsecret });
  assert.equal(tv.valid, false);
  assert.equal(tv.trust_band, 'quarantine');

  // Version mismatch → fail closed
  const vm = verifyEnvelope({ ...env, header: { ...env.header, ver: '0.9' } }, { secret: bsecret });
  assert.equal(vm.valid, false);
  assert.equal(vm.trust_band, 'block');

  // Nonce replay
  const seen = new Set<string>();
  verifyEnvelope(env, { secret: bsecret, seenNonces: seen });
  const replay = verifyEnvelope(env, { secret: bsecret, seenNonces: seen });
  assert.equal(replay.valid, false);

  // Heimdall FSM: ragnarok guarantees
  const fsm = new HeimdallFsm('cybertronia');
  fsm.dispatch('critical_breach');
  assert.equal(fsm.state, 'ragnarok');
  const caps = fsm.capabilities;
  assert.deepEqual(
    [caps.sessions, caps.commits, caps.upgrades, caps.forward, caps.recoveryOnly],
    [false, false, false, false, true],
  );
  fsm.dispatch('recovery_verified');
  assert.equal(fsm.state, 'recovered');

  // Trust reconciliation lattice
  assert.equal(reconcileTrust(['allow', 'allow', 'allow']), 'allow');
  assert.equal(reconcileTrust(['allow', 'review', 'warn']), 'review');
  assert.equal(reconcileTrust(['allow', 'quarantine', 'block']), 'quarantine');

  // End-to-end gate: healthy node + signed envelope + benign intent → allow
  const healthy = new HeimdallFsm('console');
  const decision = gateIntent(
    {
      intent: 'status',
      payload: { text: 'show system status' },
      requiresApproval: false,
      riskLevel: 'low',
    } as any,
    env2(),
    { secret: bsecret },
    healthy,
  );
  assert.equal(decision.proceed, true);

  function env2() {
    return sealEnvelope(
      { intent: 'status' },
      {
        type: 'intent',
        src: 'excalibur',
        dst: 'console',
        realm: 'camelot',
        node: 'console',
        seq: 2,
        secret: bsecret,
      },
    );
  }

  // ── Bifrost phase 2: FFI policy, queues, ledger chain, registration gate ──
  const { degradeTrustBand, evaluateSidecar } = await import('../bifrost/ffi-policy');
  const { BifrostQueue } = await import('../bifrost/bifrost-queue');
  const { ProvenanceChain } = await import('../bifrost/provenance-chain');
  const { runRegistrationGate } = await import('../bifrost/registration-gate');

  // FFI fallback logic: allow/warn+timeout→review, review stays, block/quarantine unchanged
  assert.equal(degradeTrustBand('allow', 'ffi_timeout'), 'review');
  assert.equal(degradeTrustBand('warn', 'ffi_timeout'), 'review');
  assert.equal(degradeTrustBand('review', 'ffi_timeout'), 'review');
  assert.equal(degradeTrustBand('block', 'ffi_timeout'), 'block');
  assert.equal(degradeTrustBand('quarantine', 'ffi_compute_failed'), 'quarantine');
  assert.equal(degradeTrustBand('allow', 'ffi_version_mismatch'), 'block');
  assert.equal(degradeTrustBand('allow', 'ffi_compute_failed', true), 'block');

  // Sidecar automation
  assert.equal(evaluateSidecar({ health: 'ok', routeReady: true }).scoring, 'proceed');
  assert.equal(evaluateSidecar({ health: 'degraded', routeReady: true }).scoring, 'review_only');
  assert.equal(evaluateSidecar({ health: 'failed', routeReady: true }).scoring, 'no_grant');
  assert.equal(evaluateSidecar({ health: 'ok', routeReady: false }).blockNewGrants, true);

  // Queue: overflow policy per class
  const q = new BifrostQueue(2, { secret: bsecret });
  const mk = (priority: any, type = 'telemetry', policy?: string) =>
    sealEnvelope(
      { t: type },
      {
        type,
        src: 'excalibur',
        dst: 'cybertronia',
        realm: 'camelot',
        node: 'console',
        seq: 1,
        secret: bsecret,
        priority,
        policyDecision: policy,
      },
    );
  q.enqueue(mk('normal'), 'p1');
  q.enqueue(mk('normal'), 'p1');
  assert.equal(q.enqueue(mk('high'), 'p1').audit, 'queue.backpressure_applied');
  assert.equal(q.enqueue(mk('normal'), 'p1').audit, 'queue.delayed');
  assert.equal(q.enqueue(mk('low'), 'p1').audit, 'queue.shed');
  assert.equal(q.deadLetter.length, 1);
  // Signed critical quarantine event bypasses at capacity
  const bypassed = q.enqueue(mk('critical', 'quarantine', 'allow_direct'), 'p1');
  assert.equal(bypassed.bypass, true);
  assert.equal(bypassed.audit, 'queue.bypass_used');
  // Unsigned-ineligible critical (wrong type) is force-enqueued, never dropped
  const forced = q.enqueue(mk('critical', 'telemetry'), 'p1');
  assert.equal(forced.accepted, true);
  assert.equal(forced.bypass, false);
  // Drain: critical first, partition FIFO preserved
  const drained = q.drain();
  assert.equal(drained[0].envelope.header.priority, 'critical');

  // Ledger chain: append, tamper detection, buffer+retry with quarantine-first
  const chain = new ProvenanceChain(bsecret);
  const ref1 = chain.append(mk('normal', 'telemetry'));
  assert.ok(ref1?.startsWith('ledger://camelot/'));
  chain.append(mk('normal', 'telemetry'));
  assert.equal(chain.verifyChain().valid, true);
  chain.simulateFailure();
  assert.equal(chain.append(mk('normal', 'telemetry')), null); // no commit claimed
  chain.append(mk('critical', 'quarantine', 'allow_direct'));
  assert.equal(chain.bufferedCount, 1);
  assert.equal(chain.retryBuffered(), 1);
  assert.equal(chain.verifyChain().valid, true);
  assert.equal(chain.length, 4);

  // Registration gate: no scoring for invalid nodes; conservative reconciliation
  const okScore = () => ({ band: 'allow' as const });
  const badId = runRegistrationGate(
    {
      nodeId: 'n1',
      identityValid: false,
      schemaValid: true,
      sidecar: { health: 'ok', routeReady: true },
      realmBands: [],
    },
    okScore,
  );
  assert.equal(badId.scoringInvoked, false);
  assert.equal(badId.stage, 'registration');
  const granted = runRegistrationGate(
    {
      nodeId: 'n2',
      identityValid: true,
      schemaValid: true,
      sidecar: { health: 'ok', routeReady: true },
      realmBands: ['allow'],
    },
    okScore,
  );
  assert.equal(granted.granted, true);
  const crossRealm = runRegistrationGate(
    {
      nodeId: 'n3',
      identityValid: true,
      schemaValid: true,
      sidecar: { health: 'ok', routeReady: true },
      realmBands: ['allow', 'quarantine'],
    },
    okScore,
  );
  assert.equal(crossRealm.finalBand, 'quarantine');
  assert.equal(crossRealm.granted, false);
  const ffiDown = runRegistrationGate(
    {
      nodeId: 'n4',
      identityValid: true,
      schemaValid: true,
      sidecar: { health: 'ok', routeReady: true },
      realmBands: [],
    },
    () => ({ error: 'ffi_timeout' as const }),
  );
  assert.equal(ffiDown.finalBand, 'review');

  // Heimdall spec alignment: soft_quarantine → recovered via full revalidation
  const fsm2 = new HeimdallFsm('n5');
  fsm2.dispatch('anomaly');
  fsm2.dispatch('anomaly_confirmed');
  fsm2.dispatch('threshold_breach');
  assert.equal(fsm2.state, 'soft_quarantine');
  fsm2.dispatch('recovery_verified');
  assert.equal(fsm2.state, 'recovered');

  // ── Ω_NANO master crystal: microfish predictive + Yggdrasil Merkle root ──
  const { MicrofishSeries, feedHeimdall } = await import('../bifrost/microfish');

  // Trend: strictly rising series
  const rising = new MicrofishSeries();
  for (let i = 0; i < 10; i++) rising.push(i * 2);
  assert.equal(rising.trend().direction, 'rising');

  // Capacity forecast: at value 18, slope 2, limit 30 → 6 samples
  assert.equal(rising.capacity(30).samplesToCapacity, 6);
  assert.equal(rising.capacity(10).samplesToCapacity, 0); // already over

  // Anomaly: stable baseline then a spike → Heimdall containment
  const cpu = new MicrofishSeries();
  for (let i = 0; i < 20; i++) cpu.push(50 + (i % 2)); // ~50±1
  cpu.push(500); // spike
  const report = cpu.anomaly();
  assert.equal(report.severity, 'critical');
  const nodeFsm = new HeimdallFsm('cybertronia');
  const dispatched = feedHeimdall(report, nodeFsm);
  assert.equal(dispatched, 'critical_breach');
  assert.equal(nodeFsm.state, 'ragnarok');
  assert.equal(nodeFsm.capabilities.recoveryOnly, true);

  // No-op on clean signal
  const calm = new MicrofishSeries();
  for (let i = 0; i < 10; i++) calm.push(50);
  assert.equal(feedHeimdall(calm.anomaly(), new HeimdallFsm('x')), null);

  // Yggdrasil Merkle root: deterministic, and any tamper shifts it
  const yg = new ProvenanceChain(bsecret);
  yg.append(mk('normal', 'telemetry'));
  yg.append(mk('normal', 'telemetry'));
  yg.append(mk('normal', 'telemetry')); // odd leaf count exercises duplication
  const root1 = yg.merkleRoot();
  assert.ok(root1 && root1.length === 64);
  yg.append(mk('critical', 'quarantine', 'allow_direct'));
  const root2 = yg.merkleRoot();
  assert.notEqual(root1, root2);
  assert.equal(yg.verifyChain().valid, true);

  console.log('Camelot smoke tests passed (trust plane + control plane + predictive + Yggdrasil).');
});
