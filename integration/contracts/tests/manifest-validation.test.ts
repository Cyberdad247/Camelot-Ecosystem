// The generator is the first gate on the skill catalog, and the docs claim it
// refuses manifests that weaken policy. That claim was untested, and one of
// the rules was in fact missing: a tier-1 `local_effect` generated cleanly as
// `Effectful:false, Durable:true`, which the gateway runs through the
// NO-LEASE branch — a real side effect with no authorization.
//
// Each case runs the real generator against a mutated manifest in a temp dir.

import { execFile } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';
import { describe, expect, it } from 'vitest';

const run = promisify(execFile);
const contractsDir = fileURLToPath(new URL('../', import.meta.url));
const GENERATOR = join(contractsDir, 'gen', 'generate.mjs');
const MANIFEST = join(contractsDir, 'skills.manifest.json');

const pristine = readFileSync(MANIFEST, 'utf8');

/** Run the generator against a mutated COPY of the manifest. The committed
 *  file is never written, so this cannot race a parallel suite reading it. */
async function generateWith(mutate: (m: any) => void): Promise<{ code: number; stderr: string }> {
  const m = JSON.parse(pristine);
  mutate(m);
  const work = mkdtempSync(join(tmpdir(), 'gen-'));
  const candidate = join(work, 'skills.manifest.json');
  writeFileSync(candidate, JSON.stringify(m, null, 2));
  try {
    await run('node', [GENERATOR, work], {
      env: { ...process.env, CAMELOT_SKILLS_MANIFEST: candidate },
    });
    return { code: 0, stderr: '' };
  } catch (e: any) {
    return { code: e.code ?? 1, stderr: String(e.stderr ?? '') };
  }
}

const durable = () => ({
  id: 'probe.skill',
  version: 1,
  tier: 2,
  effect: 'local_effect',
  confirmationRequired: false,
  intent: { phrases: ['probe phrase'], priority: 0 },
  idempotency: 'lease_single_use',
  retry: 'never',
  artifactKind: 'probe',
  audit: { kind: 'tool.executed', redactTranscript: true },
});

describe('manifest validation', () => {
  it('accepts the committed manifest', async () => {
    const { code } = await generateWith(() => {});
    expect(code).toBe(0);
  });

  // The one that was missing. Tier is what the broker gates on.
  it('refuses a durable skill below tier 2 (it would run without a lease)', async () => {
    const { code, stderr } = await generateWith((m) => {
      m.skills.push({ ...durable(), tier: 1 });
    });
    expect(code).toBe(1);
    expect(stderr).toMatch(/tier >= 2/);
  });

  it('refuses a durable skill that is retryable', async () => {
    const { code, stderr } = await generateWith((m) => {
      m.skills.push({ ...durable(), retry: 'safe' });
    });
    expect(code).toBe(1);
    expect(stderr).toMatch(/retry/);
  });

  it('refuses a durable skill without single-use idempotency', async () => {
    const { code } = await generateWith((m) => {
      m.skills.push({ ...durable(), idempotency: 'natural' });
    });
    expect(code).toBe(1);
  });

  it('refuses tier 3 without confirmation', async () => {
    const { code, stderr } = await generateWith((m) => {
      m.skills.push({ ...durable(), tier: 3, effect: 'read_only', retry: 'safe', idempotency: 'natural' });
    });
    expect(code).toBe(1);
    expect(stderr).toMatch(/confirmationRequired/);
  });

  it('refuses a phrase claimed by two skills', async () => {
    const { code, stderr } = await generateWith((m) => {
      m.skills.push({ ...durable(), intent: { phrases: ['staging'], priority: 0 } });
    });
    expect(code).toBe(1);
    expect(stderr).toMatch(/already claimed/);
  });

  it('refuses a non-lower-cased phrase (matching lower-cases the transcript)', async () => {
    const { code } = await generateWith((m) => {
      m.skills.push({ ...durable(), intent: { phrases: ['Probe Phrase'], priority: 0 } });
    });
    expect(code).toBe(1);
  });

  it('refuses a duplicate skill id', async () => {
    const { code, stderr } = await generateWith((m) => {
      m.skills.push({ ...durable(), id: 'ops.staging.read' });
    });
    expect(code).toBe(1);
    expect(stderr).toMatch(/duplicate id/);
  });

  it('refuses a skill with no intent phrases (it would be unreachable)', async () => {
    const { code } = await generateWith((m) => {
      m.skills.push({ ...durable(), intent: { phrases: [], priority: 0 } });
    });
    expect(code).toBe(1);
  });
});
